from typing import List, Dict
from app.config import settings

SYSTEM_PROMPT = """You are DentAI, an expert educational assistant specializing in Odontogenic Oral Pathology and dental education. You help dental students and faculty with:

- Oral pathology concepts (dental caries, periodontitis, oral lesions, abscesses, etc.)
- Dental anatomy and histology
- Diagnosis and treatment planning concepts
- Study tips and quiz preparation
- Explaining complex dental conditions in simple terms

Guidelines:
- Be educational, accurate, and supportive
- Use clinical terminology but explain it clearly
- Provide evidence-based information
- Encourage further study and clinical application
- Keep responses concise but comprehensive
- If asked about non-dental topics, gently redirect to dental education"""

FALLBACK_RESPONSES = {
    "caries": "Dental caries is caused by acid-producing bacteria (primarily Streptococcus mutans) that demineralize tooth enamel. Prevention includes fluoride, oral hygiene, and reducing sugar intake.",
    "periodontitis": "Periodontitis is a severe gum infection causing irreversible alveolar bone loss. Key bacteria include P. gingivalis and A. actinomycetemcomitans. Treatment involves scaling, root planing, and sometimes surgery.",
    "abscess": "A dental abscess is a pocket of pus from bacterial infection. Periapical abscesses originate from pulp necrosis; periodontal abscesses from deep pockets. Treatment: drainage, antibiotics, and addressing the source.",
    "default": "I'm DentAI, your dental education assistant. I can help with oral pathology, dental anatomy, quiz preparation, and more. What would you like to learn about today?",
}


def get_fallback_response(message: str) -> str:
    msg_lower = message.lower()
    for key, response in FALLBACK_RESPONSES.items():
        if key in msg_lower:
            return response
    return FALLBACK_RESPONSES["default"]


async def chat_with_ai(
    message: str,
    history: List[Dict[str, str]],
    user_role: str = "student",
) -> str:
    if not settings.GROQ_API_KEY:
        return get_fallback_response(message)

    from openai import OpenAI

    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    role_context = f"\nThe user is a {user_role} in dental education." if user_role else ""
    system = SYSTEM_PROMPT + role_context

    messages = [{"role": "system", "content": system}]
    for turn in history[-10:]:  # keep last 10 turns for context
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=messages,
    )
    return response.choices[0].message.content
