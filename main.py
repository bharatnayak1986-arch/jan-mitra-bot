main.py
import os
import io
import requests
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from PIL import Image

app = FastAPI()

# एनवायरनमेंट से कीज़ लोड होंगी (सुरक्षित तरीका)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT = """
आप 'जन-मित्र AI' हैं। 
इस दस्तावेज़/कागज़ की तस्वीर को देखकर एकदम सरल, आम बोलचाल की हिंदी में बताएं:
1. यह दस्तावेज़ किस बारे में है? (1-2 लाइन)
2. क्या इसमें कोई भुगतान करना है या पैसा मिलना है?
3. यूज़र को आगे क्या 2-3 कदम उठाने चाहिए?
4. अंतिम तारीख (Deadline), यदि कोई हो।
भारी कानूनी या कठिन शब्दों का इस्तेमाल बिल्कुल न करें।
"""

@app.get("/")
def home():
    return {"status": "जन-मित्र AI बॉट चालू है!"}

@app.post("/whatsapp")
async def reply_whatsapp(
    Body: str = Form(default=""),
    NumMedia: int = Form(default=0),
    MediaUrl0: str = Form(default="")
):
    resp = MessagingResponse()
    msg = resp.message()

    try:
        # अगर फोटो आई है
        if NumMedia > 0 and MediaUrl0:
            media_response = requests.get(
                MediaUrl0, 
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            )
            image = Image.open(io.BytesIO(media_response.content))
            ai_output = model.generate_content([PROMPT, image])
            msg.body(ai_output.text)

        # अगर सिर्फ मैसेज आया है
        elif Body.strip():
            text_prompt = f"आप 'जन-मित्र AI' हैं। आम नागरिक के इस सवाल का सरल हिंदी में उत्तर दें: {Body}"
            ai_output = model.generate_content(text_prompt)
            msg.body(ai_output.text)

        else:
            msg.body("कृपया किसी कागज़/नोटिस की साफ फोटो भेजें या अपना सवाल लिखकर पूछें।")

    except Exception:
        msg.body("कागज़ को पढ़ने में तकनीकी दिक्कत आई। कृपया साफ फोटो दोबारा भेजें।")

    return Response(content=str(resp), media_type="application/xml")
