import json
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.quiz import Quiz, QuizAttempt
from app.config import settings


DENTAL_TOPICS = {
    "dental_caries": "Dental Caries (Tooth Decay)",
    "periodontitis": "Periodontitis (Gum Disease)",
    "oral_lesions": "Oral Lesions and Ulcers",
    "dental_abscess": "Dental Abscess",
    "malocclusion": "Malocclusion",
    "oral_cancer": "Oral Cancer",
    "pulpitis": "Pulpitis",
    "gingivitis": "Gingivitis",
}

SAMPLE_QUESTIONS: Dict[str, List[Dict]] = {
    "dental_caries": [
        {
            "question": "What bacterium is primarily responsible for dental caries?",
            "options": ["Streptococcus mutans", "Staphylococcus aureus", "Lactobacillus acidophilus", "Porphyromonas gingivalis"],
            "correct_index": 0,
            "explanation": "Streptococcus mutans is the primary etiological agent of dental caries, producing acids that demineralize enamel.",
        },
        {
            "question": "Which tooth surface is most susceptible to dental caries?",
            "options": ["Labial surface", "Occlusal pits and fissures", "Root surface", "Lingual surface"],
            "correct_index": 1,
            "explanation": "Occlusal pits and fissures trap food and bacteria, making them the most susceptible sites for caries development.",
        },
        {
            "question": "What is the first visible sign of dental caries?",
            "options": ["Cavitation", "White spot lesion", "Brown discoloration", "Tooth sensitivity"],
            "correct_index": 1,
            "explanation": "A white spot lesion (subsurface demineralization) is the earliest clinically visible sign of caries.",
        },
        {
            "question": "Which mineral is primarily lost during early caries?",
            "options": ["Calcium phosphate", "Magnesium", "Fluoride", "Zinc"],
            "correct_index": 0,
            "explanation": "Dental caries results from acid-mediated dissolution of hydroxyapatite (calcium phosphate) in enamel.",
        },
        {
            "question": "Fluoride prevents dental caries primarily by:",
            "options": ["Killing bacteria directly", "Forming fluorapatite which is more acid-resistant", "Increasing saliva flow", "Blocking sugar absorption"],
            "correct_index": 1,
            "explanation": "Fluoride replaces hydroxyl groups in hydroxyapatite to form fluorapatite, which is more resistant to acid dissolution.",
        },
    ],
    "periodontitis": [
        {
            "question": "Periodontitis is characterized by loss of:",
            "options": ["Enamel", "Dentin", "Periodontal attachment", "Cementum only"],
            "correct_index": 2,
            "explanation": "Periodontitis involves irreversible loss of periodontal attachment including bone, PDL, and cementum.",
        },
        {
            "question": "What is the key difference between gingivitis and periodontitis?",
            "options": ["Gingivitis involves bone loss", "Periodontitis is reversible", "Periodontitis involves alveolar bone loss", "Gingivitis requires surgery"],
            "correct_index": 2,
            "explanation": "Periodontitis involves irreversible alveolar bone loss, while gingivitis is limited to gingival inflammation without bone loss.",
        },
        {
            "question": "Which bacteria is strongly associated with aggressive periodontitis?",
            "options": ["Streptococcus mutans", "Aggregatibacter actinomycetemcomitans", "Candida albicans", "Treponema pallidum"],
            "correct_index": 1,
            "explanation": "Aggregatibacter actinomycetemcomitans (Aa) is strongly associated with aggressive periodontitis.",
        },
        {
            "question": "A pocket depth greater than how many mm indicates periodontitis?",
            "options": ["1 mm", "2 mm", "3 mm", "4 mm or more"],
            "correct_index": 3,
            "explanation": "Healthy sulcus depth is 1-3 mm; pockets ≥4 mm indicate periodontal disease.",
        },
        {
            "question": "Which systemic condition is most strongly linked to periodontitis?",
            "options": ["Hypertension", "Diabetes mellitus", "Hypothyroidism", "Anemia"],
            "correct_index": 1,
            "explanation": "Diabetes mellitus has a bidirectional relationship with periodontitis—each worsens the other.",
        },
    ],
}


async def get_sample_quiz(topic: str, num_questions: int) -> List[Dict]:
    topic_name = DENTAL_TOPICS.get(topic, topic.replace("_", " ").title())
    
    if not settings.GROQ_API_KEY:
        # Fallback to static questions if no API key
        questions = SAMPLE_QUESTIONS.get(topic, SAMPLE_QUESTIONS["dental_caries"])
        return questions[:num_questions]

    from openai import OpenAI
    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    
    prompt = f"""You are a dental education expert. Generate exactly {num_questions} multiple-choice questions about the topic: '{topic_name}'.

Return ONLY valid JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Brief explanation of the correct answer."
  }}
]

Rules:
- Each question must have exactly 4 options
- correct_index is 0-based (0=A, 1=B, 2=C, 3=D)
- Focus on clinically relevant concepts for BSCS 8th semester level students (Computer Vision in Dentistry)
- Ensure questions are varied and unique."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"AI Sample Quiz Generation Error: {e}")
    
    # Final fallback if AI fails
    questions = SAMPLE_QUESTIONS.get(topic, SAMPLE_QUESTIONS["dental_caries"])
    return questions[:num_questions]


async def generate_quiz_from_text(
    text: str,
    num_questions: int,
    topic: str,
) -> List[Dict[str, Any]]:
    if not settings.GROQ_API_KEY:
        return get_sample_quiz(topic or "dental_caries", num_questions)

    from openai import OpenAI

    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    prompt = f"""You are a dental education expert. Generate exactly {num_questions} multiple-choice questions based on the following dental/oral pathology text.

TEXT:
{text[:6000]}

Return ONLY valid JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Brief explanation of the correct answer."
  }}
]

Rules:
- Each question must have exactly 4 options
- correct_index is 0-based (0=A, 1=B, 2=C, 3=D)
- Focus on clinically relevant concepts
- Vary difficulty from basic recall to application"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content.strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise HTTPException(status_code=500, detail="Failed to parse quiz from AI response")


def save_quiz(db: Session, title: str, topic: str, questions: List[Dict], created_by: int, pdf_id: int = None) -> Quiz:
    quiz = Quiz(
        title=title,
        topic=topic,
        questions=questions,
        created_by=created_by,
        source_pdf_id=pdf_id,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def submit_quiz_attempt(
    db: Session,
    quiz_id: int,
    user_id: int,
    answers: Dict[str, int],
    time_taken_sec: int,
) -> QuizAttempt:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = quiz.questions
    correct = sum(
        1 for i, q in enumerate(questions)
        if answers.get(str(i)) == q["correct_index"]
    )
    score = round((correct / len(questions)) * 100, 1) if questions else 0

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id,
        score=score,
        total_questions=len(questions),
        answers=answers,
        time_taken_sec=time_taken_sec,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt
