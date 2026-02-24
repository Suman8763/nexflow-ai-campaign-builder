def score_campaign(strategy: dict, config: dict):
    """
    Scores campaign quality based on multiple factors.
    Returns total score + breakdown for UI.
    """
    score = 0
    breakdown = {
        "persona": 0,
        "key_insight": 0,
        "value_proposition": 0,
        "proof_points": 0,
        "strategic_angle": 0,
        "sources": 0,
        "total": 0
    }

    # 1. Persona alignment (20 points)
    if config.get("persona") and config["persona"].lower() in str(strategy).lower():
        score += 20
        breakdown["persona"] = 20
    else:
        breakdown["persona"] = 0

    # 2. Key Insight quality (15 points)
    insight = strategy.get("key_insight", "")
    if len(insight) > 60 and "opportunity" in insight.lower() or "growth" in insight.lower():
        score += 15
        breakdown["key_insight"] = 15
    else:
        breakdown["key_insight"] = 5 if len(insight) > 30 else 0

    # 3. Value Proposition strength (15 points)
    prop = strategy.get("value_proposition", "")
    if len(prop) > 60 and ("increase" in prop.lower() or "improve" in prop.lower()):
        score += 15
        breakdown["value_proposition"] = 15
    else:
        breakdown["value_proposition"] = 5 if len(prop) > 30 else 0

    # 4. Supporting proof points (20 points)
    proofs = strategy.get("supporting_proof_points", [])
    if len(proofs) >= 3:
        score += 20
        breakdown["proof_points"] = 20
    elif len(proofs) >= 1:
        score += 10
        breakdown["proof_points"] = 10
    else:
        breakdown["proof_points"] = 0

    # 5. Strategic angle quality (15 points)
    angle = strategy.get("strategic_campaign_angle", "")
    if len(angle) > 50 and ("campaign" in angle.lower() or "focus" in angle.lower()):
        score += 15
        breakdown["strategic_angle"] = 15
    else:
        breakdown["strategic_angle"] = 5 if len(angle) > 20 else 0

    # 6. Sources present (15 points)
    sources = strategy.get("sources", [])
    if len(sources) > 0:
        score += 15
        breakdown["sources"] = 15
    else:
        breakdown["sources"] = 0

    breakdown["total"] = min(score, 100)

    return {
        "total_score": breakdown["total"],
        "breakdown": breakdown
    }