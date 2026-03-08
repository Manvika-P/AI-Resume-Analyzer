from flask import Flask, render_template, request, jsonify
import PyPDF2
import os
import json
import spacy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from google import genai

# ----------------------------------------------------------
# 1️⃣  Configure Flask app and Gemini API key
# ----------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize the new genai client using environment variable or explicit string
client = genai.Client(api_key="AIzaSyCpbHDXn0lNuZLSsuj-9i-Y09JO_V_pIz0")

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'resume_analyzer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load NLP Model
print("Loading SpaCy Model...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading English model for spaCy...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
print("SpaCy Model Loaded Successfully.")

# Database Model
class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(100), nullable=False)
    ats_score = db.Column(db.Integer, nullable=False)
    skills_extracted = db.Column(db.Text, nullable=False) # JSON string
    overall_summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

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
# 3️⃣  Function to extract NLP skills using SpaCy
# ----------------------------------------------------------
def extract_nlp_skills(text):
    doc = nlp(text)
    # Extract noun chunks, entities (GPE, ORG, PRODUCT), and deduplicate
    skills = set()
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'ORG', 'PRODUCT', 'PERSON']:
            skills.add(ent.text.title())
    
    # Very basic static common tech skills matching as fallback/enhancement
    common_skills = ['python', 'java', 'c++', 'javascript', 'react', 'node.js', 'sql', 'machine learning', 'data analysis', 'aws', 'docker', 'kubernetes', 'html', 'css', 'flask', 'django', 'pandas', 'numpy', 'spacy', 'tensorflow', 'pytorch']
    
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    for skill in common_skills:
        if skill in text.lower() or skill in tokens:
            skills.add(skill.title())
            
    return list(skills)

# ----------------------------------------------------------
# 4️⃣  Function to analyze the resume using Gemini
# ----------------------------------------------------------
def analyze_resume(resume_text, role):
    try:
        # Step 1: Extract NLP skills
        nlp_skills = extract_nlp_skills(resume_text)
        nlp_skills_str = ", ".join(nlp_skills)

        prompt = f"""
        You are a professional career coach and ATS (Applicant Tracking System) expert.
        Analyze the following resume text for the role of '{role}'. 
        We have already extracted some baseline skills using NLP: {nlp_skills_str}.
        
        Provide a detailed analysis in JSON format ONLY, with exactly the following keys (Make sure to wrap everything in a valid JSON object, DO NOT INCLUDE MARKDOWN BACKTICKS or any other text before or after the JSON):
        
        {{
        "Overall Summary": "A string containing a 2-3 line summary.",
        "Strengths": ["list", "of", "strings"],
        "Weaknesses / Improvement Areas": ["list", "of", "strings"],
        "Skills Mentioned": ["list", "of", "strings" - include both NLP and LLM discovered skills],
        "Missing or Suggested Keywords": ["list", "of", "strings"],
        "Suggested Changes": ["list of strings detailing specific changes to tailor the resume for the '{role}' role"],
        "NLP Skill Match Progress": "A string representing a percentage 0-100 indicating how well their extracted skills match common requirements for this role",
        "Final ATS Readability Score": "String representing score, e.g. 85"
        }}

        Resume content:
        {resume_text}
        """
        
        # Use the new API client
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        text = response.text.strip()
        # Clean up markdown formatting if present
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        raise Exception(f"Error analyzing resume: {str(e)}")


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
    
    role = request.form.get('role', '').strip()
    if not role:
        return jsonify({'error': 'Job role is required. Please enter the role you are applying for.'}), 400
        
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
            sections = analyze_resume(resume_text, role)
            
            # Save to Database
            extracted_score = 0
            try:
                score_str = sections.get("Final ATS Readability Score", "0")
                import re
                numbers = re.findall(r'\d+', str(score_str))
                if numbers:
                    extracted_score = int(numbers[0])
            except Exception:
                extracted_score = 0
                
            history_record = AnalysisHistory(
                job_role=role,
                ats_score=extracted_score,
                skills_extracted=json.dumps(sections.get("Skills Mentioned", [])),
                overall_summary=sections.get("Overall Summary", "N/A")
            )
            db.session.add(history_record)
            db.session.commit()
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'sections': sections
            })
            
        except Exception as e:
            # Clean up file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

@app.route('/dashboard_data', methods=['GET'])
def dashboard_data():
    try:
        # Get last 10 records
        history = AnalysisHistory.query.order_by(AnalysisHistory.created_at.desc()).limit(10).all()
        data = []
        for r in history:
            data.append({
                'id': r.id,
                'job_role': r.job_role,
                'ats_score': r.ats_score,
                'skills': json.loads(r.skills_extracted),
                'summary': r.overall_summary,
                'date': r.created_at.strftime("%Y-%m-%d %H:%M")
            })
        return jsonify({'success': True, 'history': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
