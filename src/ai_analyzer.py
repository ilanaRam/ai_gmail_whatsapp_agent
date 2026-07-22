import os
import json
import inspect
import datetime
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

    today_date = datetime.datetime.now().strftime('%Y-%m-%d')

    client = None

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(f"[{func_name}]: GEMINI_API_KEY is not set in .env or environment variables!")
    try:
        client = genai.Client(api_key=gemini_api_key)
        print(f"[{func_name}]: Google GenAI Client initialized successfully!")

        # # List available models
        # models = client.models.list()
        # print("Available models:")
        # for model in models:
        #     print(f"- {model.name}")  # Only print the model name

        # model = client.models.generate_content(model="gemini-1.5-flash", contents="Hello, world!")
        # print("API key is valid!")
    except Exception as e:
        print(f"[{func_name}]: API key is invalid: {e}")
        return None

    my_prompt = f"""
    You are a smart calendar assistant that understands Hebrew speech.
    Today's date is: {today_date}
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
        print(f"[{func_name}]: Preparing model ...")
        model = client.models.generate_content(model=GEMINI_MODEL,
                                               contents=my_prompt)
        if not model:
            raise ValueError(f"[{func_name}]: Returned empty model")
        response = model.text # response is of type: GenerateContentResponse
        print(f"[{func_name}]: AI Analyzed text is ready: {response}")

        # contains                   type          meaning
        # ------------------------------------------------------------------------------------------
        # response.text              str           the actual text response from Gemini ← most used
        # response.candidates        list          list of possible responses
        # response.prompt_feedback   object        info about the prompt
        # response.usage_metadata    object        token usage info

        # clean response returned as str, here we clean a word 'JSON' bring only structure itself without a word json
        clean_response = response.strip().replace('```json', '').replace('```', '').strip()

        # json.loads is deserializing = creating Python object from a string. string -> python obj DICT
        event_data = json.loads(clean_response)
        # result = validity_check(event_data)
        # if not result:
        #     raise ValueError(f"[{func_name}]: Error found during creating event structure, some data is missing")

        print(f"[{func_name}]: Extracted event into python dict:\n{event_data}")
        # we return python obj DICT
        return event_data
    except Exception as e:
        print(f"[{func_name}]: Error during content generation or JSON parsing: {e}")
        return None





if __name__ == "__main__":
    test_text = "היום אנו בתאריך 01/06/2026 בוא נקבע פגישה עם אלכס מחר בשעה שלוש אחר הצהריים לדון בפרויקט"
    result = analyze_text(test_text)