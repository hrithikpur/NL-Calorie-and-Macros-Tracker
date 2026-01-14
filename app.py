import streamlit as st
import google.generativeai as genai
import json
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

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

# Data file for storing records
DATA_FILE = "calorie_data.json"

# Knowledge base for standard nutritional values per 100g
try:
    with open('knowledge_base.json', 'r') as f:
        KNOWLEDGE_BASE = json.load(f)
except FileNotFoundError:
    KNOWLEDGE_BASE = {}
except json.JSONDecodeError:
    KNOWLEDGE_BASE = {}

def load_data():
    """Load calorie tracking data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Ensure both users exist in the data structure
            if 'user1' not in data:
                data['user1'] = {'entries': {}, 'targets': {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}}
            if 'user2' not in data:
                data['user2'] = {'entries': {}, 'targets': {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}}
            
            # Migrate old data structure if needed
            for user in ['user1', 'user2']:
                if user in data and isinstance(data[user], dict):
                    if 'entries' not in data[user]:
                        # Old structure - migrate
                        old_entries = data[user]
                        data[user] = {
                            'entries': old_entries,
                            'targets': {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}
                        }
                    elif 'targets' not in data[user]:
                        data[user]['targets'] = {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}
            
            return data
    return {
        'user1': {'entries': {}, 'targets': {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}},
        'user2': {'entries': {}, 'targets': {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}}
    }

def save_data(data):
    """Save calorie tracking data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_user_data(data, user):
    """Get data for a specific user"""
    user_data = data.get(user, {'entries': {}, 'targets': {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30}})
    return user_data

def save_user_data(data, user, user_data):
    """Save data for a specific user"""
    data[user] = user_data
    save_data(data)

def get_user_entries(user_data):
    """Get entries for a specific user"""
    return user_data.get('entries', {})

def get_user_targets(user_data):
    """Get targets for a specific user"""
    return user_data.get('targets', {'protein': 120, 'fat': 50, 'carbs': 200, 'fiber': 30})

def get_gemini_macros(food_description):
    """Use Gemini API to extract macros from food description"""
    if not GEMINI_API_KEY:
        return {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0}

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

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
        error_str = str(e)
        print(f"DEBUG: Gemini API Error: {error_str}")  # Debug print
        if "API_KEY_INVALID" in error_str or "API key expired" in error_str:
            st.error("🔑 **API Key Error**: Your Gemini API key has expired. Please get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey) and update your `.env` file.")
        else:
            st.error(f"Error getting macros from Gemini: {e}")
        return {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0}

def get_agentic_macros(food_description):
    """Use an agentic AI system with knowledge base check first, then web search to cross-verify nutritional facts"""
    if not GEMINI_API_KEY:
        return {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0, "confidence": 0, "sources": "No API key"}

    try:
        # Initialize the LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )

        # First, parse the food description to extract food name and quantity
        parse_prompt = f"""
        Parse this food description: "{food_description}"

        Extract the main food item name and the quantity consumed in grams.
        If no quantity is specified, assume 100 grams.
        If quantity is in other units (like cups, bowls, etc.), try to estimate in grams based on common serving sizes.

        Return ONLY a JSON object with these exact fields:
        {{
            "food_name": "the main food item name (string)",
            "quantity_g": quantity in grams (number)
        }}
        """

        parse_response = llm.invoke(parse_prompt)
        parse_text = parse_response.content.strip()

        # Clean up parse response
        if parse_text.startswith('```json'):
            parse_text = parse_text[7:]
        if parse_text.startswith('```'):
            parse_text = parse_text[3:]
        if parse_text.endswith('```'):
            parse_text = parse_text[:-3]
        parse_text = parse_text.strip()

        parsed = json.loads(parse_text)
        food_name = parsed.get('food_name', '').strip().lower()
        quantity_g = parsed.get('quantity_g', 100)

        # Check knowledge base first
        if food_name in KNOWLEDGE_BASE:
            base_macros = KNOWLEDGE_BASE[food_name]
            factor = quantity_g / 100.0
            macros = {
                "protein": base_macros.get("protein", 0) * factor,
                "fat": base_macros.get("fat", 0) * factor,
                "carbs": base_macros.get("carbs", 0) * factor,
                "fiber": base_macros.get("fiber", 0) * factor,
                "calories": base_macros.get("calories", 0) * factor,
                "confidence": 100,
                "sources": "Knowledge base (standard values per 100g)"
            }
            return macros

        # If not in knowledge base, proceed with web search

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
        error_str = str(e)
        print(f"DEBUG: Agentic API Error: {error_str}")  # Debug print
        if "API_KEY_INVALID" in error_str or "API key expired" in error_str:
            st.error("🔑 **API Key Error**: Your Gemini API key has expired. Please get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey) and update your `.env` file.")
        else:
            st.error(f"Error in agentic analysis: {e}")
        return {
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0,
            "calories": 0,
            "confidence": 0,
            "sources": f"Error: {str(e)}"
        }

def create_macro_progress_bar(current, target, macro_name):
    """Create a progress bar with color coding for macro tracking"""
    if target == 0:
        return

    percentage = min(current / target, 1.0)

    # Color coding logic
    if percentage <= 0.8:
        color = "🟢"  # Green - good progress
    elif percentage <= 1.0:
        color = "🟡"  # Yellow - approaching target
    else:
        color = "🔴"  # Red - over target

    # Create progress bar
    bar_length = 20
    filled_length = int(bar_length * min(percentage, 1.0))
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    # Display
    st.write(f"{color} **{macro_name}**: {current:.1f}g / {target}g ({percentage*100:.1f}%)")
    st.write(f"{bar}")

def main():
    st.title("🍎 NL Calorie & Macros Tracker")

    # Load data
    data = load_data()

    # User selection
    st.sidebar.header("👤 User Selection")
    selected_user = st.sidebar.selectbox(
        "Select User",
        ["user1", "user2"],
        format_func=lambda x: "User 1" if x == "user1" else "User 2",
        help="Choose which user profile to track"
    )

    # Get user-specific data
    user_data = get_user_data(data, selected_user)
    user_entries = get_user_entries(user_data)
    user_targets = get_user_targets(user_data)

    # Sidebar for API key input
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Gemini API Key", type="password", value=GEMINI_API_KEY or "")
        if api_key != GEMINI_API_KEY:
            os.environ["GEMINI_API_KEY"] = api_key
            genai.configure(api_key=api_key)

        st.header("Daily Macro Targets")
        col1, col2 = st.columns(2)
        with col1:
            protein_target = st.number_input("Protein (g)", value=user_targets.get('protein', 120), min_value=0, step=5, key="protein_target")
            carbs_target = st.number_input("Carbs (g)", value=user_targets.get('carbs', 200), min_value=0, step=10, key="carbs_target")
        with col2:
            fat_target = st.number_input("Fat (g)", value=user_targets.get('fat', 50), min_value=0, step=5, key="fat_target")
            fiber_target = st.number_input("Fiber (g)", value=user_targets.get('fiber', 30), min_value=0, step=5, key="fiber_target")
        
        # Save targets if changed
        new_targets = {
            'protein': protein_target,
            'fat': fat_target,
            'carbs': carbs_target,
            'fiber': fiber_target
        }
        if new_targets != user_targets:
            user_data['targets'] = new_targets
            save_user_data(data, selected_user, user_data)
            st.success("Targets updated!")

    # Main interface
    tab1, tab2 = st.tabs(["Add Food", "View Records"])

    with tab1:
        st.header("Add Food Entry")

        # Date selection
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            help="Choose the date for this food entry"
        )
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # Time selection
        selected_time = st.time_input(
            "Select Time",
            value=datetime.now().time(),
            help="Choose the time for this food entry"
        )
        selected_time_str = selected_time.strftime("%H:%M")

        food_input = st.text_area(
            "Describe your food (e.g., '1 bowl of matar paneer total weight 250g containing 100g protein and rest gravy and peas')",
            height=100
        )

        # Initialize session state for calculated macros
        if 'calculated_macros' not in st.session_state:
            st.session_state.calculated_macros = None
        if 'calculated_food' not in st.session_state:
            st.session_state.calculated_food = ""

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Calculate Macros", type="primary"):
                if food_input.strip():
                    with st.spinner("Calculating macros with web search..."):
                        macros = get_agentic_macros(food_input)
                        st.session_state.calculated_macros = macros
                        st.session_state.calculated_food = food_input
                    st.success("Macros calculated! Review below and click 'Add Entry' to save.")
                else:
                    st.error("Please enter a food description")

        with col2:
            if st.button("➕ Add Entry", disabled=st.session_state.calculated_macros is None):
                if st.session_state.calculated_macros and st.session_state.calculated_food == food_input:
                    # Use selected date instead of current date
                    entry_date = selected_date_str

                    # Initialize date data if not exists
                    if entry_date not in user_entries:
                        user_entries[entry_date] = []

                    # Add entry
                    entry = {
                        "time": selected_time_str,
                        "description": food_input,
                        "macros": st.session_state.calculated_macros
                    }

                    user_entries[entry_date].append(entry)
                    save_user_data(data, selected_user, user_data)

                    # Clear session state
                    st.session_state.calculated_macros = None
                    st.session_state.calculated_food = ""

                    st.success("Entry added successfully!")
                else:
                    st.error("Please calculate macros first")

        # Show macro preview if calculated
        if st.session_state.calculated_macros and st.session_state.calculated_food == food_input:
            st.subheader("📊 Macro Preview")
            preview_macros = st.session_state.calculated_macros

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Protein", f"{preview_macros.get('protein', 0):.1f}g")
                st.metric("Carbs", f"{preview_macros.get('carbs', 0):.1f}g")
            with col2:
                st.metric("Fat", f"{preview_macros.get('fat', 0):.1f}g")
                st.metric("Fiber", f"{preview_macros.get('fiber', 0):.1f}g")

            st.metric("Calories", f"{preview_macros.get('calories', 0):.0f} kcal")

            # Show confidence and sources if available (agentic mode)
            if 'confidence' in preview_macros:
                confidence = preview_macros.get('confidence', 0)
                sources = preview_macros.get('sources', 'Unknown')
                
                # Color code confidence
                if confidence >= 80:
                    conf_color = "🟢"
                elif confidence >= 60:
                    conf_color = "🟡"
                else:
                    conf_color = "🔴"
                
                st.write(f"{conf_color} **Confidence:** {confidence}%")
                st.write(f"📚 **Sources:** {sources}")

            # Show progress bars for today's totals + this entry
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_totals = {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0}

            # Add existing entries
            if today_str in user_entries:
                for entry in user_entries[today_str]:
                    for macro in today_totals:
                        today_totals[macro] += entry['macros'].get(macro, 0)

            # Add preview macros
            for macro in today_totals:
                today_totals[macro] += preview_macros.get(macro, 0)

            st.write("**Projected Daily Totals (including this entry):**")
            col1, col2 = st.columns(2)
            with col1:
                create_macro_progress_bar(today_totals["protein"], protein_target, "Protein")
                create_macro_progress_bar(today_totals["carbs"], carbs_target, "Carbs")
            with col2:
                create_macro_progress_bar(today_totals["fat"], fat_target, "Fat")
                create_macro_progress_bar(today_totals["fiber"], fiber_target, "Fiber")

            st.write(f"**Total Calories**: {today_totals['calories']:.0f}")

    with tab2:
        st.header("Daily Records (Last 7 Days)")

        # Show today's progress prominently
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in user_entries and user_entries[today_str]:
            st.subheader("📊 Today's Progress")
            today_totals = {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0}
            for entry in user_entries[today_str]:
                for macro in today_totals:
                    today_totals[macro] += entry['macros'].get(macro, 0)

            col1, col2 = st.columns(2)
            with col1:
                create_macro_progress_bar(today_totals["protein"], protein_target, "Protein")
                create_macro_progress_bar(today_totals["carbs"], carbs_target, "Carbs")
            with col2:
                create_macro_progress_bar(today_totals["fat"], fat_target, "Fat")
                create_macro_progress_bar(today_totals["fiber"], fiber_target, "Fiber")

            st.write(f"**Total Calories**: {today_totals['calories']:.0f}")
            st.divider()

        # Get last 7 days
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        for date in dates:
            if date in user_entries and user_entries[date]:
                with st.expander(f"📅 {date} ({len(user_entries[date])} entries)"):
                    total_macros = {"protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "calories": 0}

                    for entry in user_entries[date]:
                        st.write(f"🕐 {entry['time']}: {entry['description']}")
                        st.json(entry['macros'])

                        for key in total_macros:
                            total_macros[key] += entry['macros'].get(key, 0)

                    st.write("**Daily Totals:**")
                    st.json(total_macros)

                    # Show progress bars for this day
                    st.write("**Macro Progress:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        create_macro_progress_bar(total_macros["protein"], protein_target, "Protein")
                        create_macro_progress_bar(total_macros["carbs"], carbs_target, "Carbs")
                    with col2:
                        create_macro_progress_bar(total_macros["fat"], fat_target, "Fat")
                        create_macro_progress_bar(total_macros["fiber"], fiber_target, "Fiber")

if __name__ == "__main__":
    main()