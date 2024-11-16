import http.client
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_text(text, target_language='sw'):
    conn = http.client.HTTPSConnection("google-translate1.p.rapidapi.com")
    
    payload = {
        "q": text,
        "target": target_language,
        "source": "en"
    }
    
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'x-rapidapi-host': "google-translate1.p.rapidapi.com",
        'x-rapidapi-key': "c4dea7299emsh0c0ae99be693b65p1053ffjsnc9f66b5a4874"
    }
    
    try:
        conn.request("POST", "/language/translate/v2", json.dumps(payload), headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        return data['data']['translations'][0]['translatedText']
    except Exception as e:
        print(f"Translation error: {e}")
        return text
def get_health_insights(bmi_data):
    # Handle when BMI shows as "--" in the template
    if bmi_data == "--":
        return {
            'nutrition': 'Start your wellness journey by tracking your daily meals. Explore new healthy recipes that excite your taste buds. Fill your plate with colorful whole foods.',
            'exercise': 'Discover activities that bring you joy and energy. Create an activity log to track your movement patterns. Build momentum with consistent daily movement.'
        }

    conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com", timeout=180)
    
    message = (
        f"As a health expert, provide nutrition recommendations and "
        f"exercise suggestions for someone with a BMI of {bmi_data}. "
        f"Format the response in two sections: "
        f"1. Nutrition Recommendations "
        f"2. Exercise Suggestions"
        f"for nutrition, focus on the recommended diet portions for a well balanced meal"
    )
    
    payload = json.dumps({
        "message": message,
        "conversation_id": None,
        "tone": "BALANCED",
        "markdown": False,
        "photo_url": None
    })

    headers = {
    'x-rapidapi-key': "c4dea7299emsh0c0ae99be693b65p1053ffjsnc9f66b5a4874",
    'x-rapidapi-host': "copilot5.p.rapidapi.com",
    'Content-Type': "application/json"
}

    try:
        logger.info(f"Making API request for BMI: {bmi_data}")
        conn.request("POST", "/copilot", payload, headers)
        res = conn.getresponse()
        
        if res.status != 200:
            logger.error(f"API returned non-200 status: {res.status}")
            raise Exception(f"API error: {res.status}")

        raw_data = res.read().decode("utf-8")
        data = json.loads(raw_data)
        response_text = data['data']['message']
            
        sections = response_text.split('2.')
        nutrition = sections[0].replace('1. Nutrition Recommendations', '').strip()
        exercise = sections[1].replace('Exercise Suggestions', '').strip()
        
        return {
            'nutrition': nutrition,
            'exercise': exercise
        }
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        if bmi_data == 0:
            return {
                'nutrition': 'Let\'s start with tracking your daily meals in a food diary. Aim for colorful fruits and vegetables at each meal. Keep yourself energized with regular balanced meals.',
                'exercise': 'Begin recording your favorite physical activities. Choose movement that brings you joy like dancing, walking or swimming. Build consistency with activities you enjoy most.'
            }
        else:
            return {
                'nutrition': 'Focus on portion control. Increase vegetable intake. Reduce processed foods.',
                'exercise': 'Start with 30-minute daily walks. Add strength training twice weekly. Include flexibility exercises.'
            }
    finally:
        conn.close()

def get_chatbot_response(user_message):
    conn = http.client.HTTPSConnection("chatgpt-gpt4-ai-chatbot.p.rapidapi.com")
    
    payload = json.dumps({
        "query": user_message
    })
    
    headers = {
        'x-rapidapi-key': "c4dea7299emsh0c0ae99be693b65p1053ffjsnc9f66b5a4874",
        'x-rapidapi-host': "chatgpt-gpt4-ai-chatbot.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    
    try:
        conn.request("POST", "/ask", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        logging.error(f"Error in chatbot response: {str(e)}")
        return {"response": "Let me fetch that information for you."}
    finally:
        conn.close()

