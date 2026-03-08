import google.generativeai as genai
import sys

try:
    genai.configure(api_key="AIzaSyCpbHDXn0lNuZLSsuj-9i-Y09JO_V_pIz0")
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
