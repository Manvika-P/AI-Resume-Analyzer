# 🤖 AI Resume Analyzer

A beautiful, modern web application that uses Google's Gemini AI to analyze resumes and provide detailed insights, strengths, weaknesses, and ATS optimization tips.

## ✨ Features

- **Beautiful Dark Theme**: Modern, elegant UI with gradient effects and smooth animations
- **AI-Powered Analysis**: Uses Google Gemini AI for comprehensive resume analysis
- **Drag & Drop Upload**: Easy file upload with drag and drop support
- **Detailed Insights**: Get analysis on strengths, weaknesses, skills, and ATS optimization
- **Real-time Processing**: Fast analysis with loading indicators
- **Responsive Design**: Works perfectly on desktop and mobile devices

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
AI-Resume-Analyzer/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Beautiful dark-themed UI
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎨 UI Features

- **Gradient Backgrounds**: Beautiful dark theme with purple/blue gradients
- **Animated Elements**: Floating icons, hover effects, and smooth transitions
- **Glass Morphism**: Modern glass-effect cards with backdrop blur
- **Responsive Grid**: Adaptive layout for all screen sizes
- **Interactive Elements**: Hover effects, loading spinners, and smooth animations

## 🔧 Technical Details

- **Backend**: Flask with secure file handling
- **AI**: Google Gemini 2.5 Flash model
- **PDF Processing**: PyPDF2 for text extraction
- **Frontend**: Modern HTML5, CSS3, and JavaScript
- **Styling**: Custom CSS with Inter font and Font Awesome icons

## 📋 Analysis Features

The AI analyzer provides:

1. **Overall Summary** - Brief overview of the resume
2. **Strengths** - Key positive aspects identified
3. **Weaknesses** - Areas for improvement
4. **Skills Mentioned** - Technical and soft skills listed
5. **Missing Keywords** - ATS optimization suggestions
6. **ATS Score** - Readability score (0-100)

## 🛡️ Security Features

- File type validation (PDF only)
- File size limits (16MB max)
- Secure filename handling
- Automatic file cleanup after processing

## 🌟 Usage

1. Open the application in your browser
2. Drag and drop your PDF resume or click to select
3. Click "Analyze Resume" to start the AI analysis
4. View detailed results with actionable insights

Enjoy your AI-powered resume analysis! 🚀
