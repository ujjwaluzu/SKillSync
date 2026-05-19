from .services.ai_engine import analyze_project, extract_skills


def extract_features(text):
    skills = extract_skills(text)
    normalized = (text or "").lower()
    return {
        "skills": skills,
        "ecommerce": int("ecommerce" in normalized or "store" in normalized),
        "payment": int("payment" in normalized or "stripe" in normalized or "razorpay" in normalized),
        "auth": int("login" in normalized or "auth" in normalized),
    }


def estimate_price(features):
    description = " ".join(features.get("skills", [])) if isinstance(features, dict) else str(features)
    analysis = analyze_project(description)
    return analysis.min_price, analysis.max_price
