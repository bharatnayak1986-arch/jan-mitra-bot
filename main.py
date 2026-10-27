import os
import io
import requests
from PIL import Image
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = FastAPI()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT = """
model = genai.GenerativeModel("gemini-1.5-flash-8b")


इस दस्तावेज़/कागज़ की तस्वीर देखकर एकदम सरल, आम बोलचाल की हिंदी में बताएं:
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
    MediaUrl0: str = Form(default="")
):
    resp = MessagingResponse()
    msg = resp.message()

    try:
        if MediaUrl0 and MediaUrl0.strip():
            media_response = requests.get(
                MediaUrl0,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            )
            image = Image.open(io.BytesIO(media_response.content))
            ai_output = model.generate_content([PROMPT, image])
            msg.body(ai_output.text)
        elif Body and Body.strip():
            text_prompt = f"आप 'जन-मित्र AI' हैं। नागरिक के इस सवाल का सरल और स्पष्ट हिंदी में उत्तर दें:\n\n{Body}"
            ai_output = model.generate_content(text_prompt)
            msg.body(ai_output.text)
        else:
            msg.body("कृपया अपना सवाल लिखकर भेजें या किसी कागज़ की साफ़ फोटो भेजें।")

    except Exception as e:
        msg.body(f"तकनीकी समस्या: {str(e)}")

    return Response(content=str(resp), media_type="application/xml")
    
