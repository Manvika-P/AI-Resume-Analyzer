import google.generativeai as genai
import sys
import os

try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "your-api-key-here"))
    print(f"genai version: {genai.__version__}")
    model = genai.GenerativeModel("gemini-1.5-flash") # Testing standard name
    print("Model 1.5 created.")
    
    # Testing the model from app.py
    model_25 = genai.GenerativeModel("gemini-2.5-flash")
    print("Model 2.5 created.")
    response = model_25.generate_content("Hello, this is a test.")
    print("Response 2.5:", response.text)
except Exception as e:
    print("Error:", type(e).__name__, str(e))
    sys.exit(1)
