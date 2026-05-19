# DentAI — Interactive Educational Application in Odontogenic Oral Pathology

**Bahria University, Lahore Campus — Computer Vision Assignment 3**  
BSCS 8th Semester | CLO2: AI-based image analysis for computer vision problems

---

## Prompts Used to Build This Project (with Claude AI)

This project was built using Claude Code (AI assistant). Below are the prompts used — in order — to generate the full application.

---

### Prompt 1 — Project Initialization

> "I have a Computer Vision assignment for BSCS 8th semester at Bahria University. I need to build an interactive educational application on Odontogenic Oral Pathology. The app needs: student and faculty login roles, PDF upload by faculty, AI-based quiz generation from PDFs, sample quizzes for students, AR/3D viewer for dental models, a chatbot for oral pathology Q&A, computer vision image analysis for dental conditions, student progress tracking, notes and bookmarks, and performance reports for faculty. Use FastAPI for backend, SQLite for database, and vanilla JS with Jinja2 for frontend. Make it a full-stack deployable web app."

---

### Prompt 2 — Authentication System

> "Set up JWT authentication with two roles: student and faculty. Use bcrypt for password hashing. Students and faculty should have separate dashboards after login. Include a register page where users can choose their role."

---

### Prompt 3 — Computer Vision Model

> "Add a dental image classifier using MobileNetV2 (transfer learning). It should classify uploaded dental images into: Healthy Teeth, Dental Caries, Periodontitis, Dental Abscess, and Oral Lesion. Include confidence scores and condition descriptions in the response. Add a fallback color/texture heuristic if no trained weights are available."

---

### Prompt 4 — AI Chatbot (DentAI Tutor)

> "Integrate the Anthropic Claude API to create a chatbot called DentAI Tutor. It should answer questions specifically about oral pathology and dental conditions. Use claude-haiku for speed. Include a fallback response if the API key is not set."

---

### Prompt 5 — PDF Upload and AI Quiz Generation

> "Add a PDF upload feature for faculty. Use pdfplumber to extract text from uploaded PDFs. Then add a quiz generation endpoint that sends the extracted text to Claude API (claude-opus for quality) and returns MCQ questions with options and correct answers. Store generated quizzes in the database."

---

### Prompt 6 — Sample Quizzes

> "Add pre-built sample quizzes that don't require a PDF upload. Include quizzes on Dental Caries and Periodontitis fundamentals. Students should be able to pick a topic, take the quiz, get instant per-question feedback, and see their final score."

---

### Prompt 7 — Student Dashboard

> "Build a full student dashboard with: quiz attempt history, average score, a Chart.js progress chart over time, topic grid showing available subjects, notes section to save personal study notes with topic tags, and a bookmarks system. All data should be user-specific and loaded via API."

---

### Prompt 8 — Faculty Dashboard

> "Build a faculty dashboard showing: total student count, total quizzes, total attempts, class average score (with a Chart.js bar chart), a table of all students with their attempt count and average score and pass/fail status, quiz analytics (select a quiz to see attempts, average, highest, lowest score, pass rate), and a PDF management section."

---

### Prompt 9 — 3D AR Viewer

> "Add a Three.js interactive 3D dental model viewer. Include models for: healthy tooth, dental caries, abscess, periodontitis, and dental crown. Users should be able to rotate, zoom, and toggle wireframe mode. Add an AR marker detection option. Make it work entirely in the browser with no external dependencies."

---

### Prompt 10 — Database Seeder and Demo Accounts

> "Create a database initialization script (scripts/init_db.py) that seeds: a demo student account (student@demo.com / demo1234), a demo faculty account (faculty@demo.com / demo1234), and 2 pre-built quizzes on Dental Caries and Periodontitis."

---

### Prompt 11 — API Tests

> "Write pytest tests covering: user registration, login, getting quiz topics, submitting a sample quiz, accessing the chatbot endpoint, uploading an image for CV analysis, and checking the student progress report. All 7 tests should pass."

---

### Prompt 12 — Bug Fix (JWT and bcrypt)

> "The login is failing. Fix the JWT token — the `sub` field must be a string (python-jose requirement), so convert the user ID to string when creating the token and convert back to int when reading it in deps.py. Also fix bcrypt — replace passlib with direct bcrypt calls because passlib has a version incompatibility with Python 3.12."

---

### Prompt 13 — Final README and Documentation

> "Write a complete README.md covering: what the project does, full project structure with explanations, manual setup steps (env file, venv, init_db), how to run, all page URLs, full feature walkthrough for both student and faculty, CV model details, all API endpoints, tech stack table, troubleshooting table, and assignment requirement coverage checklist."

---

---

## What This Project Does

A full-stack, AI-powered web application for dental education covering:

| Feature | Description |
|---|---|
| **CV-based Image Analysis** | Upload dental images → AI classifies oral pathology conditions (MobileNetV2) |
| **AI Chatbot (DentAI Tutor)** | Claude-powered chatbot for oral pathology Q&A |
| **Quiz Generation** | Upload PDFs → Claude auto-generates MCQ quizzes |
| **Sample Quizzes** | Pre-built quizzes on Dental Caries & Periodontitis |
| **AR 3D Viewer** | Three.js interactive 3D dental models (tooth, caries, abscess, periodontitis, crown) |
| **Student Dashboard** | Take quizzes, track scores, view progress charts, notes & bookmarks |
| **Faculty Dashboard** | Upload PDFs, manage quizzes, view student performance reports |
| **JWT Authentication** | Separate student / faculty login roles |

---

## Project Structure

```
dentist_cv/
├── app/                    ← FastAPI backend
│   ├── main.py             ← App entry point, routes pages
│   ├── config.py           ← Settings (reads .env)
│   ├── database.py         ← SQLAlchemy SQLite setup
│   ├── core/
│   │   └── security.py     ← bcrypt password hashing, JWT tokens
│   ├── models/             ← SQLAlchemy ORM models
│   │   ├── user.py         ← User (student / faculty)
│   │   ├── quiz.py         ← Quiz, QuizAttempt, UploadedPDF
│   │   └── notes.py        ← Note, Bookmark
│   ├── routers/            ← API route handlers
│   │   ├── auth.py         ← POST /api/auth/register, /login
│   │   ├── quiz.py         ← Quiz CRUD + generation
│   │   ├── pdf.py          ← PDF upload (faculty only)
│   │   ├── chatbot.py      ← POST /api/chat/message
│   │   ├── cv_analysis.py  ← POST /api/cv/analyze
│   │   ├── reports.py      ← Faculty/student performance
│   │   └── notes.py        ← Notes & bookmarks
│   ├── services/           ← Business logic
│   │   ├── auth_service.py
│   │   ├── cv_service.py
│   │   ├── quiz_service.py ← AI quiz generation + sample questions
│   │   ├── chatbot_service.py ← Claude API wrapper
│   │   └── pdf_service.py  ← pdfplumber text extraction
│   └── schemas/            ← Pydantic request/response models
├── cv/
│   └── dental_analyzer.py  ← MobileNetV2 dental image classifier
├── frontend/
│   ├── static/
│   │   ├── css/style.css   ← Full custom CSS design system
│   │   └── js/             ← app.js, chatbot.js, quiz.js
│   └── templates/          ← Jinja2 HTML pages
│       ├── index.html          ← Landing page
│       ├── login.html
│       ├── register.html
│       ├── student_dashboard.html
│       ├── faculty_dashboard.html
│       ├── quiz.html
│       ├── cv_analysis.html
│       └── ar_viewer.html      ← Three.js 3D + AR marker
├── data/
│   └── uploads/            ← Uploaded PDFs and images (auto-created)
├── scripts/
│   └── init_db.py          ← Database seeder (run once)
├── tests/
│   └── test_api.py         ← 7 API tests (all passing)
├── requirements.txt
├── .env.example
└── main.py                 ← python main.py entry point
```

---

## Deploy to Render.com (Free — Full App, No GitHub Pages Limit)

GitHub Pages only hosts static files — it cannot run the FastAPI backend, database, or AI models.  
**Render.com** hosts the full app for free.

### Steps

**1. Push your code to GitHub**
```bash
git add .
git commit -m "add render deployment config"
git push origin main
```

**2. Create a free Render account**  
Go to [render.com](https://render.com) and sign up (free, no credit card needed for web services).

**3. Create a new Web Service**
- Click **New → Web Service**
- Connect your GitHub account and select this repository
- Render will auto-detect `render.yaml` and fill in all settings

**4. Set your Groq API key** (for chatbot + quiz generation)
- In the Render dashboard → your service → **Environment**
- Add: `GROQ_API_KEY` = your key from [console.groq.com](https://console.groq.com) (free)
- `SECRET_KEY` is auto-generated by Render — no action needed

**5. Click Deploy**  
Render will install dependencies and start the server. First deploy takes ~5 minutes.  
Your app will be live at: `https://dentai.onrender.com` (or similar URL Render assigns).

> **Note:** The free tier spins down after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up. This is normal for free hosting.

> **SQLite note:** The database resets on each redeploy. Demo accounts (student@demo.com / faculty@demo.com) are re-seeded automatically by the start command.

---

## What You Need to Do Manually (Local Setup)

### 1. Copy the `.env` file
```bash
cp .env.example .env
```
Then open `.env` and set:
```
SECRET_KEY=any-random-long-string-here
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxx   # get from console.anthropic.com
```

> **Without `ANTHROPIC_API_KEY`:** The chatbot and AI quiz generation use built-in fallback responses. All other features work normally.

### 2. Activate the virtual environment
The virtual environment is already created and all dependencies installed. Just activate it:
```bash
source venv/bin/activate   # Linux/Mac
# or
venv\Scripts\activate      # Windows
```

### 3. Initialize the database (run once)
```bash
python scripts/init_db.py
```
This creates:
- `dentist_cv.db` SQLite database
- Demo student account: `student@demo.com` / `demo1234`
- Demo faculty account: `faculty@demo.com` / `demo1234`
- 2 pre-built quizzes (Dental Caries & Periodontitis fundamentals)

---

## How to Run the Project

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Start the server
python main.py
# OR
uvicorn app.main:app --reload --port 8000
```

Then open your browser at **http://localhost:8000**

### Pages and Their URLs

| URL | Description |
|---|---|
| `http://localhost:8000/` | Landing page |
| `http://localhost:8000/login` | Login page |
| `http://localhost:8000/register` | Registration |
| `http://localhost:8000/student` | Student dashboard (requires student login) |
| `http://localhost:8000/faculty` | Faculty dashboard (requires faculty login) |
| `http://localhost:8000/cv-analysis` | Dental image CV analysis |
| `http://localhost:8000/ar-viewer` | 3D AR model viewer |
| `http://localhost:8000/docs` | Auto-generated Swagger API docs |

---

## Running Tests

```bash
source venv/bin/activate
pytest tests/ -v
```
Expected output: **7 passed** ✅

---

## Full Feature Walkthrough

### Student Login (`student@demo.com` / `demo1234`)
1. **Dashboard** — See quiz attempts, average score, progress chart, topic grid
2. **Sample Quiz** — Select a topic (Dental Caries / Periodontitis), answer questions with instant feedback
3. **All Quizzes** — List of faculty-generated quizzes from PDFs
4. **My Results** — Full history of attempts with scores and time taken
5. **AI Tutor** — Chat with DentAI chatbot about oral pathology
6. **Notes** — Save personal study notes with topic tags
7. **Bookmarks** — Save topic references
8. **CV Diagnosis** (top menu) — Upload dental images for AI analysis
9. **AR Viewer** (top menu) — Interactive 3D dental models with rotate/zoom/wireframe

### Faculty Login (`faculty@demo.com` / `demo1234`)
1. **Overview** — Student count, total quizzes, attempts, average class score + chart
2. **Upload PDF** — Upload course material PDFs; text is auto-extracted with pdfplumber
3. **Generate Quiz** — After uploading PDF, click "Generate Quiz with AI" (uses Claude API)
4. **Manage Quizzes** — View all quizzes in a table
5. **Student Performance** — Table of all students with attempt count, avg score, pass/fail status
6. **Quiz Analytics** — Select a quiz to see attempts, avg/high/low score, pass rate

---

## CV Model Details

The dental image classifier (`cv/dental_analyzer.py`) uses:
- **Architecture**: MobileNetV2 (transfer learning base) + Dense layers
- **Classes**: Healthy Teeth, Dental Caries, Periodontitis, Dental Abscess, Oral Lesion
- **Preprocessing**: 224×224 resize, ImageNet normalization
- **Fallback**: Color/texture heuristic if model weights not trained

> **Note for Full CV Performance:** To achieve clinical-grade accuracy, fine-tune the model on a labeled dental image dataset (e.g., from Kaggle or TCIA). Save the trained model to `cv/saved_model/` — the app will auto-load it.

---

## API Endpoints Summary

```
POST /api/auth/register          Register new user
POST /api/auth/login             Login → JWT token

GET  /api/quiz/topics            List oral pathology topics
POST /api/quiz/sample            Get sample quiz questions (no DB save)
POST /api/quiz/generate          Generate quiz from PDF (faculty)
GET  /api/quiz/list              List all quizzes
GET  /api/quiz/{id}              Get specific quiz
POST /api/quiz/submit            Submit quiz answers → score
GET  /api/quiz/my/attempts       My quiz history

POST /api/pdf/upload             Upload PDF + extract text (faculty)
GET  /api/pdf/list               List uploaded PDFs

POST /api/chat/message           Chat with AI tutor

POST /api/cv/analyze             Analyze dental image (multipart/form-data)
GET  /api/cv/conditions          List detectable conditions

GET  /api/reports/faculty/overview      Faculty stats
GET  /api/reports/faculty/students      All student performance
GET  /api/reports/faculty/quiz/{id}     Quiz-specific analytics
GET  /api/reports/student/my-progress   My progress

POST /api/notes/create           Save note
GET  /api/notes/list             List my notes
DELETE /api/notes/{id}          Delete note
POST /api/notes/bookmark         Add bookmark
GET  /api/notes/bookmarks/list   List my bookmarks
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | SQLite + SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt |
| AI/LLM | Anthropic Claude API (claude-haiku for chat, claude-opus for quiz) |
| Computer Vision | TensorFlow/Keras MobileNetV2 + OpenCV |
| PDF Processing | pdfplumber |
| 3D/AR | Three.js (web-based, cross-platform) |
| Charts | Chart.js |
| Frontend | Vanilla JS + Custom CSS (no framework) |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError` | Make sure venv is activated: `source venv/bin/activate` |
| Chatbot says "error" | Add `ANTHROPIC_API_KEY` to `.env` |
| Quiz generation fails | Add `ANTHROPIC_API_KEY` to `.env` (uses fallback questions otherwise) |
| Database errors | Delete `dentist_cv.db` and re-run `python scripts/init_db.py` |
| TensorFlow warnings | Normal — TF prints deprecation warnings but works correctly |
| Port in use | Change port: `uvicorn app.main:app --port 8001` |

---

## Assignment Coverage

| Requirement | Status |
|---|---|
| Interactive Educational App (Oral Pathology) | ✅ Full web app with 3D models |
| PDF Uploading (Faculty) | ✅ `/api/pdf/upload` |
| Quiz Generation from PDF | ✅ AI-powered with Claude |
| Quiz Performance Reports (Faculty login) | ✅ Student table + quiz analytics |
| Student Login: Reading/Prompting | ✅ AI Tutor chatbot |
| Student Login: Sample Quiz | ✅ Topic-based sample quizzes |
| Student Login: AR-based Topics | ✅ Three.js interactive 3D models |
| Student Login: Give Quiz + Check Result | ✅ Full quiz with scoring |
| Chatbot Feature | ✅ DentAI assistant (dental-specialized) |
| Computer Vision Image Analysis | ✅ MobileNetV2 classifier |
| Bookmarking | ✅ Notes + bookmarks system |
| Cross-platform | ✅ Web-based (works on any browser/device) |
