# -*- coding: utf-8 -*-
# g4f_services.py

import base64
import json
from typing import Dict, Union
import g4f
from g4f import Provider


class G4FBaseAltTextGenerator:
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
        "6. Ensure number of keys == 'number_of_suggestions'.\n"
        "7. IMPORTANT: Each description MUST strictly adhere to the 'max_length' limit. If necessary, shorten sentences without losing the meaning."
    )

    def __init__(self, model: str, provider: Provider):
        self.model = model
        self.provider = provider

    @staticmethod
    def _normalize_json(input_json: Union[str, Dict]) -> str:
        if input_json is None:
            raise ValueError("input_json cannot be None.")
        return input_json if isinstance(input_json, str) else json.dumps(input_json, ensure_ascii=False, indent=2)

    @staticmethod
    def _decode_image(base64_image_str: Union[str, Dict]) -> str:
        if isinstance(base64_image_str, dict):
        # Try to extract value if user passed {'image': base64_str}
            base64_image_str = base64_image_str.get("image")

        if not isinstance(base64_image_str, str):
            raise ValueError("Image must be a base64 string.")

        try:
            base64.b64decode(base64_image_str) 
            return base64_image_str
        except base64.binascii.Error as e:
            raise ValueError("Invalid base64 image data.") from e


    def generate(self, base64_image_str: str, input_json: Union[str, Dict]) -> Dict[str, str]:
        input_json_str = self._normalize_json(input_json)
        image_base64 = self._decode_image(base64_image_str)

        try:
            response = g4f.ChatCompletion.create(
                model=self.model,
                provider=self.provider,
                messages=[
                    {"role": "system", "content": self.SYSTEM_INSTRUCTION},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Voici les paramètres utilisateur :\n{input_json_str}"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            )
        except Exception as e:
            raise RuntimeError(f"g4f request failed: {str(e)}") from e

        print(f"g4f raw response: {response}")  # Debug
        try:
            cleaned = str(response).replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON response:\n{response}")


# Wrappers for specific providers and models
def qwen_vision_72b(base64_image_str: str, input_json: Union[str, Dict]):
    generator = G4FBaseAltTextGenerator(
        model="qwen-2.5-vl-72b",
        provider=Provider.Together
    )
    return generator.generate(base64_image_str, input_json)


def gpt_4o(base64_image_str: str, input_json: Union[str, Dict]):
    generator = G4FBaseAltTextGenerator(
        model="gpt-4o-mini",
        provider= Provider.OIVSCodeSer2
    )
    return generator.generate(base64_image_str, input_json)

def gpt_4_1_mini(base64_image_str: str, input_json: Union[str, Dict]):
    generator = G4FBaseAltTextGenerator(
        model="gpt-4.1-mini",
        provider= Provider.OIVSCodeSer0501
    )
    return generator.generate(base64_image_str, input_json)


def gpt_o4_mini(base64_image_str: str, input_json: Union[str, Dict]):
    generator = G4FBaseAltTextGenerator(
        model="o4-mini",
        provider=Provider.PollinationsAI
    )
    return generator.generate(base64_image_str, input_json)