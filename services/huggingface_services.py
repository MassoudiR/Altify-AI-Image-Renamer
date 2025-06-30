import base64
import json
import logging
import re
from typing import Dict, Union
from huggingface_hub import InferenceClient
from utils.config import Config



class HFAltTextGenerator:
    SYSTEM_INSTRUCTION = (
        "You are an expert AI assistant specialized in generating concise and descriptive image alternative texts "
        "(ALT TEXT) in French. Your primary role is to create high-quality, SEO-friendly, and informative descriptions "
        "for images, adhering to specific user-provided parameters.\n\n"
        "For every image you receive, you will also be provided with a JSON object containing the following keys:\n"
        "- \"activity\": (e.g., \"menuisier\", \"développeur\", \"médecin\")\n"
        "- \"adress\": (obligatoire, à inclure dans chaque description générée)\n"
        "- \"keywords\": (facultatif, ex : \"art, culture, histoire\")\n"
        "- \"max_length\": (limite de caractères par description)\n"
        "- \"number_of_suggestions\": (combien de propositions générer)\n\n"
        "Votre tâche est de retourner un objet JSON du format suivant :\n"
        "{\n  \"1\": \"Description 1\",\n  \"2\": \"Description 2\"\n}\n\n"
        "Instructions :\n"
        "1. Respectez 'max_length'.\n"
        "2. Toujours inclure 'adress'.\n"
        "3. Rédigez en français.\n"
        "4. Adaptez-vous au contenu de l’image.\n"
        "5. Utilisez 'keywords' si elles sont pertinentes.\n"
        "6. Assurez-vous que le nombre de clés == 'number_of_suggestions'.\n"
        "7. Chaque description doit respecter strictement la limite 'max_length'.\n\n"
        "IMPORTANT : Ne donnez aucune explication. Retournez uniquement le JSON final strictement au format demandé, "
        "sans texte avant ni après, sans balisage Markdown."
    )

    def __init__(self, model_id: str, provider: str = "hf-inference"):
        self.config = Config()
        self.client = InferenceClient(
            provider=provider,
            api_key=self.config.get_huggingface_key()
        )
        self.model = model_id

    def _decode_base64(self, b64: str) -> str:
        image_data = base64.b64decode(b64)
        data_url = "data:image/png;base64," + base64.b64encode(image_data).decode("utf-8")
        return data_url

    def _extract_json_from_response(self, text: str) -> Dict[str, str]:
        # Essayez de trouver un JSON structuré {"1": "...", "2": "..."}
        json_match = re.search(r"\{\s*\"1\"\s*:\s*\".*?\"\s*,\s*\"2\"\s*:\s*\".*?\"\s*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # Nettoyage manuel si Markdown ou guillemets spéciaux
        cleaned = text.replace("“", "\"").replace("”", "\"").replace("```json", "").replace("```", "").strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_part = cleaned[start:end+1]
            try:
                return json.loads(json_part)
            except json.JSONDecodeError as e:
                raise ValueError(f"Parsing failed after cleanup: {e}\nContent: {json_part}")
        
        raise ValueError(f"No valid JSON found in response:\n{text}")

    def generate(self, base64_image_str: str, input_json: Union[str, Dict]) -> Dict[str, str]:
        if isinstance(input_json, dict):
            input_json_str = json.dumps(input_json, ensure_ascii=False)
        else:
            input_json_str = input_json

        full_prompt = self.SYSTEM_INSTRUCTION + "\n\n" + "Voici le JSON d'entrée :\n" + input_json_str
        image_data_url = self._decode_base64(base64_image_str)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
        except Exception as e:
            raise RuntimeError(f"HuggingFace model request failed: {str(e)}")

        response_text = completion.choices[0].message.content
        logging.debug("HF raw response: %s", response_text)

        return self._extract_json_from_response(response_text)



def Qwen2(base64_image_str: str, input_json: Union[str, Dict]):
    generator = HFAltTextGenerator("Qwen/Qwen2-VL-72B-Instruct", provider="fireworks-ai")
    return generator.generate(base64_image_str, input_json)

def aya_vision_8(base64_image_str: str, input_json: Union[str, Dict]):
    generator = HFAltTextGenerator("CohereLabs/aya-vision-8b", provider="cohere")
    return generator.generate(base64_image_str, input_json)

def aya_vision_32(base64_image_str: str, input_json: Union[str, Dict]):
    generator = HFAltTextGenerator("CohereLabs/aya-vision-32b", provider="cohere")
    return generator.generate(base64_image_str, input_json)

def llama_4_12(base64_image_str: str, input_json: Union[str, Dict]):
    generator = HFAltTextGenerator("meta-llama/Llama-4-Maverick-17B-128E-Instruct", provider="groq")
    return generator.generate(base64_image_str, input_json)
