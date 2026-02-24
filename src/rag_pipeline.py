from pydantic import BaseModel, ValidationError
from typing import List
import json
import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq


# -----------------------------------------
# Persona Strategy Mapping
# -----------------------------------------

PERSONA_STRATEGY = {
    "Enterprise CMO": {
        "filters": ["case_studies", "company_info"],
        "focus": "ROI, scalability, compliance, enterprise impact",
        "tone": "strategic, executive-level, data-driven"
    },
    "Startup Founder": {
        "filters": ["pricing_plans", "product_features"],
        "focus": "affordability, flexibility, fast deployment",
        "tone": "practical, growth-focused, concise"
    },
    "Marketing Manager": {
        "filters": ["product_features", "case_studies"],
        "focus": "execution efficiency, automation, measurable results",
        "tone": "operational, performance-driven"
    }
}


# -----------------------------------------
# Structured Campaign Response Schema
# -----------------------------------------

class CampaignResponse(BaseModel):
    persona: str
    key_insight: str
    value_proposition: str
    supporting_proof_points: List[str]
    strategic_campaign_angle: str
    sources: List[dict]


# -----------------------------------------
# Load environment variables
# -----------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)


# -----------------------------------------
# Initialize Embeddings & Vectorstore
# -----------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory="../chroma_db",
    embedding_function=embeddings
)


# -----------------------------------------
# Greeting Detection
# -----------------------------------------

def is_greeting(query: str) -> bool:
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    return query.lower().strip() in greetings


# -----------------------------------------
# Build Retriever
# -----------------------------------------

def get_retriever(metadata_filter: dict = None):

    search_kwargs = {
        "k": 5,
        "fetch_k": 15
    }

    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs=search_kwargs
    )


# -----------------------------------------
# Main Function
# -----------------------------------------

def ask_question(user_query: str, persona: str = None):

    # Greeting
    if is_greeting(user_query):
        return {
            "message": "Hello 👋 I'm NexFlow’s AI assistant. How can I help you today?"
        }

    # Persona logic
    metadata_filter = None
    persona_context = ""
    tone_instruction = ""

    if persona and persona in PERSONA_STRATEGY:
        strategy = PERSONA_STRATEGY[persona]

        metadata_filter = {
            "category": {"$in": strategy["filters"]}
        }

        persona_context = strategy["focus"]
        tone_instruction = strategy["tone"]

    # Retrieval
    retriever = get_retriever(metadata_filter)
    retrieved_docs = retriever.invoke(user_query)

    if not retrieved_docs:
        return {"error": "No relevant documents found."}

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # Persona-aware JSON prompt
    prompt = f"""
You are NexFlow’s AI Marketing Strategist.

Persona: {persona}
Communication Tone: {tone_instruction}
Strategic Focus: {persona_context}

You MUST answer only using the provided company context.
If information is missing, return an empty JSON object {{}}.

Context:
{context}

User Question:
{user_query}

Return ONLY valid JSON in this exact format:

{{
  "persona": "{persona}",
  "key_insight": "...",
  "value_proposition": "...",
  "supporting_proof_points": ["...", "..."],
  "strategic_campaign_angle": "..."
}}

No markdown.
No explanations.
Only raw JSON.
"""

    # Call LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    raw_output = response.choices[0].message.content.strip()

    # Validate JSON
    try:
        parsed_json = json.loads(raw_output)

        validated = CampaignResponse(
            persona=parsed_json.get("persona", persona),
            key_insight=parsed_json.get("key_insight", ""),
            value_proposition=parsed_json.get("value_proposition", ""),
            supporting_proof_points=parsed_json.get("supporting_proof_points", []),
            strategic_campaign_angle=parsed_json.get("strategic_campaign_angle", ""),
            sources=[doc.metadata for doc in retrieved_docs]
        )

        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError):
        return {
            "error": "Model output validation failed",
            "raw_output": raw_output
        }


# -----------------------------------------
# Local Test
# -----------------------------------------



if __name__ == "__main__":

    from campaign_generator import generate_linkedin_post, generate_cold_email

    strategy = ask_question(
        user_query="What pricing plans are available?",
        persona="Startup Founder"
    )

    print("\n=== STRATEGY JSON ===\n")
    print(json.dumps(strategy, indent=2))

    linkedin_post = generate_linkedin_post(strategy)
    email = generate_cold_email(strategy)

    print("\n=== LINKEDIN POST ===\n")
    print(linkedin_post)

    print("\n=== COLD EMAIL ===\n")
    print(email)
