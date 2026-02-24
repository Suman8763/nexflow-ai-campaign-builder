import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


# -----------------------------------------
# Helper: Safe Proof Formatter
# -----------------------------------------

def format_proof_points(strategy: dict, max_points: int = None):
    proofs = strategy.get("supporting_proof_points", [])

    if not proofs:
        return "- Strong strategic foundation\n"

    if max_points:
        proofs = proofs[:max_points]

    formatted = ""
    for p in proofs:
        formatted += f"- {p}\n"

    return formatted


# -----------------------------------------
# LinkedIn Post Generator
# -----------------------------------------

def generate_linkedin_post(strategy: dict):

    key_insight = strategy.get("key_insight", "")
    value_prop = strategy.get("value_proposition", "")
    strategic_angle = strategy.get("strategic_campaign_angle", "")

    proof_text = format_proof_points(strategy)

    return f"""
{key_insight}

{value_prop}

Why this matters:
{proof_text}

Strategic Focus:
{strategic_angle}

#B2BMarketing #SaaS #Growth
""".strip()


# -----------------------------------------
# Cold Email Generator
# -----------------------------------------

def generate_cold_email(strategy: dict):

    key_insight = strategy.get("key_insight", "")
    value_prop = strategy.get("value_proposition", "")

    # Limit to 2 proofs for email brevity
    proof_text = format_proof_points(strategy, max_points=2)

    return f"""
Subject: Strategic Growth Opportunity

Hi [Name],

{key_insight}

{value_prop}

Here’s what makes this powerful:
{proof_text}

Let’s connect and explore how this can drive measurable results.

Best,
[Your Name]
""".strip()

def generate_landing_hero(strategy: dict):
    key_insight = strategy.get("key_insight", "")
    value_prop = strategy.get("value_proposition", "")
    return f"""
Headline: {key_insight[:60]}... – Unlock Growth with NexFlow
Subheadline: {value_prop}. Join 150+ companies seeing 38% better leads.
CTA: Get Started Free
"""

def generate_paid_ad(strategy: dict):
    strategic_angle = strategy.get("strategic_campaign_angle", "")
    proof_text = format_proof_points(strategy, max_points=1)  # Use 1 proof for short ad
    return f"""
Headline: {strategic_angle[:50]}... – AI-Powered Marketing
Description: {proof_text} Reduce costs by 19%. Target high-quality leads now!
CTA: Learn More
"""
def generate_landing_hero(strategy: dict):
    key_insight = strategy.get("key_insight", "Unlock Your Growth Potential")
    value_prop = strategy.get("value_proposition", "AI-powered marketing automation")
    return f"""
Headline: {key_insight[:70].rstrip(' .,!?')} – Powered by NexFlow
Subheadline: {value_prop}. Join 150+ companies with 38% better leads.
CTA: Start Free Trial Today
"""

def generate_paid_ad(strategy: dict):
    angle = strategy.get("strategic_campaign_angle", "AI-Driven Growth")
    proof_text = format_proof_points(strategy, max_points=1).strip('- \n')
    return f"""
Headline: {angle[:50]}... – Scale Smarter
Description: {proof_text} 38% more qualified leads. Proven in DACH region.
CTA: Get Started – Free Trial
"""