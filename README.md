# NL Calorie & Macros Tracker

A simple calorie and macronutrient tracker that uses Google's Gemini AI to parse natural language food descriptions and web search for accurate nutritional data.

## Features

- 👥 **Multi-User Support**: Track calories and macros for 2 separate users with individual macro targets
- 🗣️ Natural language food input (e.g., "1 bowl of matar paneer total weight 250g containing 100g protein")
- 🤖 AI-powered macro calculation using Google Gemini 2.0 Flash with web search cross-verification
- 📅 Manual date and time selection for flexible meal logging
- 📊 Daily tracking for the last 7 days
- 📈 Visual progress bars with color-coded macro targets (customizable per user)
- ✅ Two-step verification: Calculate macros first, then confirm before saving
- 🌐 Internet search integration for more precise nutritional values
- 🍛 Optimized for Indian household foods
- 💾 Local JSON storage

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```
   Or use the provided script:
   ```bash
   ./run.sh
   ```

## Usage

1. **Select User**: Choose between User 1 and User 2 in the sidebar
2. **Set your macro targets** in the sidebar (customizable per user, default: Protein 120g, Carbs 200g, Fat 50g, Fiber 30g)
3. Select the date and time for your meal entry
4. Enter your food description in natural language
5. Click "**Calculate Macros**" to see the AI-calculated nutritional values with web search verification
6. **Review the preview** - check if the macros look reasonable and see confidence level
7. Click "**Add Entry**" to save the entry to your records
8. **View progress bars** in the "View Records" tab - green for good progress, yellow for approaching target, red for over target

## Progress Bar Color Coding

- 🟢 **Green**: 0-80% of target (good progress)
- 🟡 **Yellow**: 80-100% of target (approaching goal)
- 🔴 **Red**: Over 100% of target (exceeded goal)

## Multi-User Features

- **Separate Profiles**: Each user has their own food entries and macro targets
- **Individual Targets**: Set different macro goals for each user
- **Isolated Data**: User data is completely separate and secure
- **Easy Switching**: Switch between users instantly in the sidebar

## Example Inputs

- "1 bowl of matar paneer total weight 250g (excluding bowl weight) which contains 100g protein and rest gravy and peas home cooked"
- "Safolla choco crunch muesli 40g in 250ml Amul gold milk red packet"
- "2 rotis with ghee and mixed vegetable curry 200g"

## Macros Calculated

- Protein (grams)
- Fat (grams)
- Carbohydrates (grams)
- Fiber (grams)
- Total Calories
- Confidence Level (with agentic mode)
- Data Sources (with agentic mode)

## Testing

You can test the Gemini API integration separately:
```bash
python3 test_gemini.py
```

## Data Migration

If you had existing data before the multi-user update, it has been automatically migrated to User 1. User 2 starts with empty data.p

1. Clone ## Featur## Features

## Features

- 🗣️ Natural language food input (e.g., "1 bowl of matar paneer total weight 250g containing 100g protein and rest gravy and peas")
- 🤖 AI-powered macro calculation using Google Gemini 2.0 Flash
- 📅 Manual date and time selection for flexible meal logging
- 📊 Daily tracking for the last 7 days
- 📈 Visual progress bars with color-coded macro targets (Protein: 120g, Carbs: 200g, Fat: 50g, Fiber: 30g)
- ✅ **Two-step verification**: Calculate macros first, then confirm before saving
- 🍛 Optimized for Indian household foods
- 💾 Local JSON storage 🗣️ Natural language food input (e.g., "1 bowl of matar paneer total weight 250g containing 100g protein and rest gravy and peas")
- 🤖 AI-powered macro calculation using Google Gemini 2.0 Flash
- � Manual date and time selection for flexible meal logging
- �📊 Daily tracking for the last 7 days
- 🍛 Optimized for Indian household foods
- 💾 Local JSON storagepository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```
   Or use the provided script:
   ```bash
   ./run.sh
   ```

## Testing

You can test the Gemini API integration separately:
```bash
python3 test_gemini.py
```A simple calorie and macronutrient tracker that uses Google's Gemini AI to parse natural language food descriptions.

## Features

- 🗣️ Natural language food input (e.g., "1 bowl of matar paneer total weight 250g containing 100g protein")
- 🤖 AI-powered macro calculation using Google Gemini
- 📊 Daily tracking for the last 7 days
- 🍛 Optimized for Indian household foods
- 💾 Local JSON storage

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Set your macro targets** in the sidebar (default: Protein 120g, Carbs 200g, Fat 50g, Fiber 30g)
2. Select the date and time for your meal entry
3. Enter your food description in natural language
4. Click "**Calculate Macros**" to see the AI-calculated nutritional values
5. **Review the preview** - check if the macros look reasonable
6. Click "**Add Entry**" to save the entry to your records
7. **View progress bars** in the "View Records" tab - green for good progress, yellow for approaching target, red for over target

## Progress Bar Color Coding

- 🟢 **Green**: 0-80% of target (good progress)
- 🟡 **Yellow**: 80-100% of target (approaching goal)
- 🔴 **Red**: Over 100% of target (exceeded goal)

## Example Inputs

- "1 bowl of matar paneer total weight 250g (excluding bowl weight) which contains 100g protein and rest gravy and peas home cooked"
- "Safolla choco crunch muesli 40g in 250ml Amul gold milk red packet"
- "2 rotis with ghee and mixed vegetable curry 200g"

## Macros Calculated

- Protein (grams)
- Fat (grams)
- Carbohydrates (grams)
- Fiber (grams)
- Total Calories