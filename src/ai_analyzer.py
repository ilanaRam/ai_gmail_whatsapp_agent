import os
import json
import inspect
# to use ai generative model
from google import genai
# depricated ---> import google.generativeai as genai
# to work with environment variables (that are saved in .env)
from dotenv import load_dotenv

load_dotenv()

# Use Gemini Flash - free and fast model
GEMINI_MODEL = "gemini-2.5-flash"


def analyze_text(my_text: str):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    client = None

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    print(f"the API_KEY is: {gemini_api_key}")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env or environment variables!")

    try:
        client = genai.Client(api_key=gemini_api_key)
        print("Google GenAI Client initialized successfully!")

        # # List available models
        # models = client.models.list()
        # print("Available models:")
        # for model in models:
        #     print(f"- {model.name}")  # Only print the model name

        # model = client.models.generate_content(model="gemini-1.5-flash", contents="Hello, world!")
        # print("API key is valid!")
    except Exception as e:
        print(f"API key is invalid: {e}")

    my_prompt = f"""
    You are a smart calendar assistant that understands Hebrew speech.
    Please extract the current Data and Time from user's text

    The user said: "{my_text}"

    Extract the following information from the text arrange the information ikn the json structure and return ONLY a JSON object, no other text:
    {{
        "title": "event title in Hebrew",
        "date": "YYYY-MM-DD",
        "time": "HH:MM",
        "duration_minutes": 60,
        "description": "event description",
        "participants": [],
        "my_calendar": true,
        "alex_calendar": false,
        "is_urgent": false,
        "alert_minutes_before": 30
    }}

    Rules:
    - If user corrects himself — recognize it and use the corrected version only
    - If Alex's calendar is mentioned — set alex_calendar to true
    - If Ilana's calendar is mentioned or my calendar is mentioned — set ilana_calendar (my calendar) to true
    - Use the date mentioned in the text 
    - Use the time mentioned in the text    
    - If urgent words mentioned — set is_urgent to true
    - Return ONLY JSON, no explanation
    """
    try:
        model = client.models.generate_content(model=GEMINI_MODEL,
                                               contents=my_prompt)
        response = model.text # response is of type: GenerateContentResponse

        # contains                   type          meaning
        # ------------------------------------------------------------------------------------------
        # response.text              str           the actual text response from Gemini ← most used
        # response.candidates        list          list of possible responses
        # response.prompt_feedback   object        info about the prompt
        # response.usage_metadata    object        token usage info

        # clean response and parse JSON bring only json structure itself without a word json
        clean_response = response.strip().replace('```json', '').replace('```', '').strip()

        # parse it to Python dict:
        event_data = json.loads(clean_response)

        print(f"[{func_name}]: Extracted event into python dict:\n{event_data}")
        return calendar_event_data
    except Exception as e:
        print(f"Error during content generation or JSON parsing: {e}")
        return None




if __name__ == "__main__":
    test_text = "היום אנו בתאריך 01/06/2026 בוא נקבע פגישה עם אלכס מחר בשעה שלוש אחר הצהריים לדון בפרויקט"
    calendar_event_data = analyze_text(test_text)