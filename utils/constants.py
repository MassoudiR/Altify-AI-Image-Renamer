from services import gemini_services  , huggingface_services , g4f_services

class Constants:

    ACTIVITY_TYPES = [
    "Motorcycle Mechanic",
    "Car Mechanic",
    "Gardener",
    "Electrician",
    "Plumber",
    "Carpenter",
    "House Painter",
    "Blacksmith",
    "Welder",
    "Bricklayer",
    "Tiler",
    "Air Conditioning Technician",
    "Refrigeration Technician",
    "Truck Driver",
    "Bus Driver",
    "Taxi Driver",
    "Baker",
    "Butcher",
    "Fisherman",
    "Farmer",
    "Tailor",
    "Shoemaker",
    "Glass Installer",
    "Furniture Assembler",
    "Building Guard",
    "Cleaning Worker",
    "Construction Worker",
    "Heavy Machinery Operator",
    "Mechanic Assistant",
]


    ALT_MAX_LENGTH_MIN = 15
    ALT_MAX_LENGTH_MAX = 50
    ALT_MAX_LENGTH_DEFAULT = 25
    RESULT_NUMBER_MIN = 1
    RESULT_NUMBER_MAX = 3
    RESULT_NUMBER_DEFAULT = 2

    # Image processing constants
    MAX_DIMENSION = 700
    MAX_FILE_SIZE_KB = 500

    # Ai model dictionary
    AI_MODELS_DICT = {
        "Gemini 1.5 Flash": gemini_services.gemini_flash,
        "learnlm 2.0": gemini_services.learnlm_2_0,
        "llama 4 12b": huggingface_services.llama_4_12,
        "Gpt 4o": g4f_services.gpt_4o,
        "Gpt 4.1 Mini": g4f_services.gpt_4_1_mini,
        "Qwen 2": huggingface_services.Qwen2,
        "Qwen 2.5 Vision 72b": g4f_services.qwen_vision_72b,
        "gemma 3 27b (Beta)": gemini_services.gemma_3,
        "gemma 3 4b (Beta)": gemini_services.gemma_3_4b,
        "aya vision 32b (Beta)": huggingface_services.aya_vision_32,
        "aya vision 8b (Beta)" : huggingface_services.aya_vision_8,
        "Gpt O4 (Slow)": g4f_services.gpt_o4_mini,
    }   
    