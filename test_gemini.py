#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""
import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Suppress Google Cloud logging warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_LOG_SEVERITY_LEVEL'] = 'ERROR'
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.cloud').setLevel(logging.ERROR)
logging.getLogger('google.auth.transport').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Error: GEMINI_API_KEY not found in environment variables")
    exit(1)

def get_gemini_macros(food_description):
    """Use Gemini API to extract macros from food description"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Analyze this food description and provide nutritional information.
        Food: {food_description}

        Please respond with ONLY a JSON object containing the following fields:
        - protein: grams of protein
        - fat: grams of fat
        - carbs: grams of carbohydrates
        - fiber: grams of fiber
        - calories: total calories

        Focus on Indian household foods and provide realistic estimates.
        If quantities are mentioned, use them for calculations.
        """

        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # Clean up the response to extract JSON
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]

        result = json.loads(result_text.strip())
        return result

    except Exception as e:
        print(f"Error getting macros from Gemini: {e}")
        return {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0}

def test_food_descriptions():
    """Test with sample Indian food descriptions"""
    test_foods = [
        "1 bowl of matar paneer total weight 250g (excluding bowl weight) which contains 100g protein and rest gravy and peas home cooked",
        "Safolla choco crunch muesli 40g in 250ml Amul gold milk red packet",
        "2 rotis with ghee and mixed vegetable curry 200g",
        "1 cup rice with dal tadka and vegetable sabzi"
    ]

    print("Testing Gemini API integration with sample Indian foods:\n")

    for food in test_foods:
        print(f"Food: {food}")
        macros = get_gemini_macros(food)
        print(f"Macros: {json.dumps(macros, indent=2)}")
        print("-" * 50)

if __name__ == "__main__":
    test_food_descriptions()