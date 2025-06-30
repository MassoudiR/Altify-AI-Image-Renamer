# -*- coding: utf-8 -*-
# gemini_services.py


import base64
import json
from typing import Dict, Union
from google import genai
from google.genai import types
from utils.config import Config


class BaseAltTextGenerator:
    SYSTEM_INSTRUCTION = (
        "You are an expert AI assistant specialized in generating concise and descriptive image alternative texts "
        "(ALT TEXT) in French. Your primary role is to create high-quality, SEO-friendly, and informative descriptions "
        "for images, adhering to specific user-provided parameters.\n\n"
        "For every image you receive, you will also be provided with a JSON object containing the following keys:\n"
        "- \"activity\": (e.g., \"joiner\", \"software developer\", \"doctor\")\n"
        "- \"adress\": (mandatory location that MUST be included in every generated description)\n"
        "- \"keywords\": (optional, e.g., \"art, culture, history\")\n"
        "- \"max_length\": (character limit per suggestion)\n"
        "- \"number_of_suggestions\": (how many ALT text suggestions to generate)\n\n"
        "Your task is to return a JSON object like:\n"
        "{\n  \"1\": \"Description 1\",\n  \"2\": \"Description 2\"\n}\n\n"
        "Guidelines:\n"
        "1. Respect 'max_length'.\n"
        "2. Always include the 'adress'.\n"
        "3. Write in French.\n"
        "4. Match the image context.\n"
        "5. Use 'keywords' only if they fit.\n"
        "6. Ensure number of keys == 'number_of_suggestions'."
        "7. IMPORTANT: Each description MUST strictly adhere to the 'max_length' limit. If necessary, shorten sentences without losing the meaning."


    )

    def __init__(self, model: str):
        self.config = Config()
        self.client = genai.Client(api_key=self.config.get_gemini_key())
        self.model = model

    @staticmethod
    def _normalize_json(input_json: Union[str, Dict]) -> str:
        if input_json is None:
            raise ValueError("input_json cannot be None.")
        return input_json if isinstance(input_json, str) else json.dumps(input_json, ensure_ascii=False, indent=2)

    @staticmethod
    def _decode_image(base64_image_str: str) -> bytes:
        try:
            return base64.b64decode(base64_image_str)
        except base64.binascii.Error as e:
            raise ValueError("Invalid base64 image data.") from e

    def _prepare_request(
        self, image_data: bytes, input_json_str: str
    ) -> (list):
        """
        To be overridden in subclasses!
        Should return (contents, generation_config)
        """
        raise NotImplementedError

    def generate(self, base64_image_str: str, input_json: Union[str, Dict]) -> Dict[str, str]:
        input_json_str = self._normalize_json(input_json)
        image_data = self._decode_image(base64_image_str)

        contents, generation_config = self._prepare_request(image_data, input_json_str)

        response_text = ""
        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model, contents=contents, config=generation_config
            ):
                response_text += getattr(chunk, "text", "") or ""
        except Exception as e:
            raise RuntimeError(f"Model request failed: {str(e)}") from e
        print(f"Gemini response: {response_text}")  # Debugging output
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        print(f"Cleaned response: {cleaned}")  # Debugging output
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON response:\n{cleaned}")


class GemmaAltTextGenerator(BaseAltTextGenerator):
    def _prepare_request(self, image_data: bytes, input_json_str: str):
        instruction = self.SYSTEM_INSTRUCTION + f"\n\nHere is the JSON object:\n{input_json_str}"
        contents = [
            types.Content(role="user", parts=[
                types.Part.from_text(text=instruction),
                types.Part.from_bytes(mime_type="image/png", data=image_data)
            ])
        ]
        generation_config = types.GenerateContentConfig(
            temperature=0.7, max_output_tokens=1000, response_mime_type="text/plain"
        )
        return contents, generation_config


class GeminiAltTextGenerator(BaseAltTextGenerator):
    def _prepare_request(self, image_data: bytes, input_json_str: str):
        contents = [
            types.Content(role="user", parts=[
                types.Part.from_bytes(mime_type="image/png", data=image_data),
                types.Part.from_text(text=input_json_str)
            ])
        ]
        generation_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1000,
            response_mime_type="text/plain",
            system_instruction=types.Content(role="system", parts=[
                types.Part.from_text(text=self.SYSTEM_INSTRUCTION)
            ])
        )
        return contents, generation_config


# Example usage wrappers
def gemini_flash(base64_image_str: str, input_json: Union[str, Dict]):
    generator = GeminiAltTextGenerator("gemini-1.5-flash")
    return generator.generate(base64_image_str, input_json)


def learnlm_2_0(base64_image_str: str, input_json: Union[str, Dict]):
    generator = GeminiAltTextGenerator("learnlm-2.0-flash-experimental")
    return generator.generate(base64_image_str, input_json)


def gemma_3(base64_image_str: str, input_json: Union[str, Dict]):
    generator = GemmaAltTextGenerator("gemma-3-27b-it")
    return generator.generate(base64_image_str, input_json)


def gemma_3_4b(base64_image_str: str, input_json: Union[str, Dict]):
    generator = GemmaAltTextGenerator("gemma-3-4b-it")
    return generator.generate(base64_image_str, input_json)
