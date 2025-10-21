from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PyPDF2
import os
from werkzeug.utils import secure_filename

# ----------------------------------------------------------
# 1️⃣  Configure Flask app and Gemini API key
# ----------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
genai.configure(api_key="AIzaSyCpbHDXn0lNuZLSsuj-9i-Y09JO_V_pIz0")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------------------------------------
# 2️⃣  Function to extract text from a PDF
# ----------------------------------------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

# ----------------------------------------------------------
# 3️⃣  Function to analyze the resume using Gemini
# ----------------------------------------------------------
def analyze_resume(resume_text):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        You are a professional career coach and ATS (Applicant Tracking System) expert.
        Analyze this resume text and provide a detailed analysis with these sections:

        1. **Overall Summary:** (2–3 lines)
        2. **Strengths:** (short bullet points)
        3. **Weaknesses / Improvement Areas:** (short bullet points)
        4. **Skills Mentioned:** (list clearly)
        5. **Missing or Suggested Keywords:** (important ATS or job-relevant terms)
        6. **Final ATS Readability Score (0–100)**

        Resume content:
        {resume_text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Error analyzing resume: {str(e)}")

# ----------------------------------------------------------
# 4️⃣  Function to parse analysis results into structured format
# ----------------------------------------------------------
def parse_analysis(analysis_text):
    sections = {}
    current_section = None
    current_content = []
    
    lines = analysis_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header
        if line.startswith('**') and line.endswith('**'):
            # Save previous section if exists
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line.replace('**', '').replace(':', '').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

# ----------------------------------------------------------
# 5️⃣  Flask Routes
# ----------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from PDF
            resume_text = extract_text_from_pdf(filepath)
            
            if not resume_text:
                os.remove(filepath)  # Clean up
                return jsonify({'error': 'Could not extract text from PDF. Make sure your PDF is not scanned.'}), 400
            
            # Analyze resume
            analysis_text = analyze_resume(resume_text)
            sections = parse_analysis(analysis_text)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'analysis': analysis_text,
                'sections': sections
            })
            
        except Exception as e:
            # Clean up file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
