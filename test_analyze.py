from app import analyze_resume
import sys
import json

fake_resume = """
John Doe
Software Engineer
Experience: 5 years at Google
Skills: Python, Java, C++, Machine Learning, React
Education: BS in Computer Science
"""

try:
    print("Sending text to analyze_resume...")
    analysis = analyze_resume(fake_resume, "Senior Software Engineer")
    print("Raw Analysis received (JSON dict):")
    print(json.dumps(analysis, indent=2))
    
    print("\n--- Keys ---")
    for k, v in analysis.items():
        print(f"[{k}] => {str(v)[:50]}...")
except Exception as e:
    print("Error:", str(e))
    sys.exit(1)
