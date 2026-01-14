#!/usr/bin/env python3
"""
Test script for agentic macro analysis with web search
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
import json

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_agentic_macros(food_description):
    """Use an agentic AI system with web search to cross-verify nutritional facts"""
    if not GEMINI_API_KEY:
        return {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0, "confidence": 0, "sources": "No API key"}

    try:
        # Initialize the LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )

        # Create web search tool
        search_tool = DuckDuckGoSearchRun()

        # Search for nutritional data
        try:
            search_results = search_tool.run(f"nutritional information {food_description} calories protein fat carbs fiber per serving")
        except Exception as e:
            search_results = f"Search failed: {str(e)}"

        # Use AI to analyze and extract reliable data
        analysis_prompt = f"""
        Based on this food description: "{food_description}"

        Here are web search results for nutritional information:
        {search_results}

        Please analyze the search results and provide accurate nutritional estimates.
        Focus on reliable sources like USDA, nutrition databases, or established health websites.
        For Indian foods, consider traditional preparation methods and common serving sizes.

        Return ONLY a JSON object with these exact fields:
        {{
            "protein": grams of protein (number),
            "fat": grams of fat (number),
            "carbs": grams of carbohydrates (number),
            "fiber": grams of fiber (number),
            "calories": total calories (number),
            "confidence": confidence level 0-100 (number),
            "sources": brief description of data sources used (string)
        }}
        """

        response = llm.invoke(analysis_prompt)
        result_text = response.content.strip()

        # Clean up the response - remove markdown code blocks
        if result_text.startswith('```json'):
            result_text = result_text[7:]  # Remove ```json
        if result_text.startswith('```'):
            result_text = result_text[3:]  # Remove ```
        if result_text.endswith('```'):
            result_text = result_text[:-3]  # Remove ```

        # Remove any leading/trailing whitespace and newlines
        result_text = result_text.strip()

        result = json.loads(result_text)

        # Ensure we have the required fields
        required_fields = ['protein', 'fat', 'carbs', 'fiber', 'calories']
        for field in required_fields:
            if field not in result:
                result[field] = 0

        # Add default values if missing
        if 'confidence' not in result:
            result['confidence'] = 70
        if 'sources' not in result:
            result['sources'] = 'AI analysis with web search'

        return result

    except Exception as e:
        print(f"Error in agentic analysis: {e}")
        return {
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0,
            "calories": 0,
            "confidence": 0,
            "sources": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    # Test with some Indian foods
    test_foods = [
        "100g chicken biryani",
        "1 bowl dal makhani",
        "2 aloo paratha",
        "1 cup masala chai"
    ]

    print("🧪 Testing Agentic Macro Analysis with Web Search")
    print("=" * 50)

    for food in test_foods:
        print(f"\n🍽️  Testing: {food}")
        result = get_agentic_macros(food)

        if result['confidence'] > 0:
            print("✅ Success!")
            print(f"   📊 Protein: {result['protein']:.1f}g")
            print(f"   🥑 Fat: {result['fat']:.1f}g")
            print(f"   🌾 Carbs: {result['carbs']:.1f}g")
            print(f"   🥦 Fiber: {result['fiber']:.1f}g")
            print(f"   🔥 Calories: {result['calories']:.0f}")
            print(f"   🎯 Confidence: {result['confidence']}%")
            print(f"   📚 Sources: {result['sources']}")
        else:
            print("❌ Failed to get results")

    print("\n" + "=" * 50)
    print("✨ Agentic testing complete!")