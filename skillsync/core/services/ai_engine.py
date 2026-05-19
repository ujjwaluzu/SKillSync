from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import math
import re


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "core" / "data" / "dataset.csv"
MODEL_VERSION = "rf-tfidf-v2"


SKILL_KEYWORDS = {
    "Django": ["django"],
    "Python": ["python"],
    "REST API": ["rest api", "api", "backend api"],
    "GraphQL": ["graphql"],
    "Frontend": ["frontend", "html", "css", "bootstrap", "tailwind", "responsive"],
    "JavaScript": ["javascript", "js", "ajax"],
    "UI/UX Design": ["ui", "ux", "modern ui", "figma", "wireframe", "animations"],
    "Authentication": ["auth", "authentication", "login", "signup", "user roles", "2fa"],
    "Payments": ["payment", "stripe", "razorpay", "subscription", "checkout"],
    "Ecommerce": ["ecommerce", "e-commerce", "store", "cart", "checkout"],
    "Admin Dashboard": ["admin", "dashboard", "analytics", "reporting"],
    "Real-time Chat": ["chat", "real-time", "socket", "websocket", "messaging"],
    "Notifications": ["notification", "notifications", "alerts"],
    "Search": ["search", "filter", "filters", "recommendation"],
    "AI/ML": ["ai", "machine learning", "prediction", "recommendation system", "chatbot"],
    "Maps": ["map", "maps", "location"],
    "Cloud Deployment": ["deploy", "deployment", "cloud", "ci/cd", "hosting"],
    "Database Design": ["database", "sqlite", "postgres", "mysql", "schema"],
}

FEATURE_WEIGHTS = {
    "Payments": 5,
    "AI/ML": 5,
    "Real-time Chat": 4,
    "Ecommerce": 4,
    "Authentication": 3,
    "Admin Dashboard": 3,
    "REST API": 3,
    "Search": 2,
    "Notifications": 2,
    "Cloud Deployment": 3,
}

TAG_KEYWORDS = {
    "web-app": ["website", "platform", "app", "portal"],
    "marketplace": ["marketplace", "freelance", "freelancing", "bid"],
    "payments": ["payment", "stripe", "razorpay", "subscription"],
    "dashboard": ["dashboard", "analytics", "admin", "reporting"],
    "realtime": ["chat", "real-time", "websocket", "notification"],
    "ai": ["ai", "machine learning", "prediction", "recommendation"],
    "mobile-ready": ["mobile", "responsive"],
    "commerce": ["ecommerce", "store", "cart", "checkout"],
}


@dataclass
class FreelancerRecommendation:
    user_id: int
    username: str
    display_name: str
    match_percentage: int
    skill_overlap: list[str] = field(default_factory=list)
    experience_score: int = 0
    rating: float = 0
    headline: str = ""


@dataclass
class ProjectAnalysis:
    min_price: int
    max_price: int
    estimated_price: int
    estimated_days: int
    time_label: str
    complexity: str
    confidence_score: int
    skills: list[str]
    tags: list[str]
    budget_justification: str
    feature_summary: dict
    similar_projects: list[dict] = field(default_factory=list)
    recommended_freelancers: list[dict] = field(default_factory=list)


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def infer_title(description):
    text = re.sub(r"\s+", " ", (description or "").strip())
    if not text:
        return "Untitled project"
    words = text.split()[:9]
    title = " ".join(words)
    return title[:1].upper() + title[1:]


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def money_round(value):
    return int(round(value / 500.0) * 500)


def extract_skills(text):
    normalized = normalize_text(text)
    skills = []
    for skill, keywords in SKILL_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            skills.append(skill)
    if not skills:
        skills.extend(["Frontend", "Database Design"])
    return skills[:8]


def generate_tags(text, skills, complexity):
    normalized = normalize_text(text)
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            tags.append(tag)
    for skill in skills:
        tag = skill.lower().replace("/", "-").replace(" ", "-")
        if tag not in tags:
            tags.append(tag)
    if complexity not in tags:
        tags.append(complexity)
    return tags[:10]


def classify_complexity(text, skills):
    normalized = normalize_text(text)
    score = len(skills)
    score += min(len(normalized.split()) // 18, 4)
    score += sum(FEATURE_WEIGHTS.get(skill, 1) for skill in skills)

    if any(word in normalized for word in ("enterprise", "scalable", "multi-vendor", "advanced")):
        score += 5
    if any(word in normalized for word in ("basic", "simple", "landing page", "portfolio")):
        score -= 3

    if score >= 18:
        return "expert"
    if score >= 12:
        return "advanced"
    if score >= 7:
        return "intermediate"
    return "basic"


def extract_extra_features(text):
    normalized = normalize_text(text)
    skills = extract_skills(normalized)
    feature_count = normalized.count(" with ") + normalized.count(",") + normalized.count(" and ")
    return [
        len(normalized.split()),
        feature_count,
        len(skills),
        int("ecommerce" in normalized or "store" in normalized),
        int("ai" in normalized or "machine learning" in normalized),
        int("chat" in normalized or "real-time" in normalized),
        int("dashboard" in normalized or "admin" in normalized),
        int("payment" in normalized or "stripe" in normalized or "razorpay" in normalized),
        int("authentication" in normalized or "login" in normalized),
        int("advanced" in normalized or "enterprise" in normalized),
        int("basic" in normalized or "simple" in normalized),
    ]


def derive_training_days(description, price):
    normalized = normalize_text(description)
    days = max(3, int(price / 3500))
    if "basic" in normalized or "portfolio" in normalized:
        days -= 2
    if "advanced" in normalized or "enterprise" in normalized:
        days += 8
    if "payment" in normalized:
        days += 4
    if "ai" in normalized or "machine learning" in normalized:
        days += 8
    if "real-time" in normalized or "chat" in normalized:
        days += 5
    return clamp(days, 3, 90)


@lru_cache(maxsize=1)
def get_models():
    try:
        import numpy as np
        import pandas as pd
        from scipy.sparse import hstack
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        return None

    df = pd.read_csv(DATASET_PATH)
    descriptions = df["description"].fillna("")
    extra_features = np.array([extract_extra_features(text) for text in descriptions])

    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words="english")
    text_matrix = vectorizer.fit_transform(descriptions)
    combined = hstack([text_matrix, extra_features])

    price_model = RandomForestRegressor(
        n_estimators=260,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
    )
    price_model.fit(combined, df["price"])

    derived_days = [
        derive_training_days(description, price)
        for description, price in zip(descriptions, df["price"])
    ]
    time_model = RandomForestRegressor(
        n_estimators=180,
        max_depth=12,
        min_samples_leaf=2,
        random_state=99,
    )
    time_model.fit(combined, derived_days)

    return {
        "vectorizer": vectorizer,
        "price_model": price_model,
        "time_model": time_model,
        "np": np,
        "hstack": hstack,
    }


def heuristic_price_and_time(text):
    skills = extract_skills(text)
    complexity = classify_complexity(text, skills)
    base = 7000 + len(normalize_text(text).split()) * 450
    for skill in skills:
        base += FEATURE_WEIGHTS.get(skill, 1) * 2200

    complexity_multiplier = {
        "basic": 0.85,
        "intermediate": 1.1,
        "advanced": 1.45,
        "expert": 1.85,
    }[complexity]
    estimated_price = money_round(base * complexity_multiplier)
    min_price = money_round(max(3000, estimated_price * 0.78))
    max_price = money_round(max(min_price + 2500, estimated_price * 1.34))
    estimated_days = int(clamp(round(estimated_price / 3200), 3, 70))
    confidence = clamp(62 + len(skills) * 3, 62, 82)
    return min_price, max_price, estimated_price, estimated_days, confidence


def predict_price_and_time(text):
    model_bundle = get_models()
    if model_bundle is None:
        return heuristic_price_and_time(text)

    vectorizer = model_bundle["vectorizer"]
    price_model = model_bundle["price_model"]
    time_model = model_bundle["time_model"]
    np = model_bundle["np"]
    hstack = model_bundle["hstack"]

    text_vector = vectorizer.transform([text])
    extra = np.array([extract_extra_features(text)])
    combined = hstack([text_vector, extra])

    price_predictions = np.array([tree.predict(combined)[0] for tree in price_model.estimators_])
    time_predictions = np.array([tree.predict(combined)[0] for tree in time_model.estimators_])

    estimated_price = money_round(float(price_predictions.mean()))
    spread = float(price_predictions.std())
    min_price = money_round(max(3000, estimated_price - spread * 0.85))
    max_price = money_round(max(min_price + 2500, estimated_price + spread * 1.15))
    estimated_days = int(clamp(round(float(time_predictions.mean())), 3, 90))

    confidence = 92 - int((spread / max(estimated_price, 1)) * 110)
    confidence = clamp(confidence, 56, 96)
    return min_price, max_price, estimated_price, estimated_days, confidence


def estimate_time_label(days):
    if days <= 7:
        return f"{days} days"
    if days <= 21:
        weeks = math.ceil(days / 7)
        return f"{weeks} weeks"
    return f"{math.ceil(days / 7)} weeks"


def explain_budget(text, skills, complexity):
    drivers = []
    normalized = normalize_text(text)
    driver_map = {
        "payment": "payment integration",
        "auth": "authentication and user access",
        "authentication": "authentication and user access",
        "admin": "admin dashboard functionality",
        "dashboard": "dashboard and analytics work",
        "chat": "real-time communication",
        "ai": "AI or recommendation logic",
        "machine learning": "AI or recommendation logic",
        "ecommerce": "ecommerce workflow",
        "api": "backend API integration",
        "deployment": "deployment and infrastructure work",
    }
    for keyword, label in driver_map.items():
        if keyword in normalized and label not in drivers:
            drivers.append(label)

    if not drivers and skills:
        drivers = [skills[0].lower(), "implementation scope"]

    driver_text = ", ".join(drivers[:4])
    complexity_text = complexity.replace("_", " ")
    return (
        f"Predicted budget is {complexity_text} because the project includes "
        f"{driver_text}. The model also considers description length, detected skills, "
        "feature count, and similar synthetic training projects."
    )


def find_similar_projects(description, queryset, limit=4):
    projects = list(queryset)
    if not projects:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = [description] + [project.description for project in projects]
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=700)
        matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    except ImportError:
        target_terms = set(normalize_text(description).split())
        scores = []
        for project in projects:
            terms = set(normalize_text(project.description).split())
            score = len(target_terms.intersection(terms)) / max(len(target_terms.union(terms)), 1)
            scores.append(score)

    ranked = sorted(zip(projects, scores), key=lambda item: item[1], reverse=True)[:limit]
    return [
        {
            "id": project.id,
            "title": project.title_or_summary,
            "score": int(score * 100),
            "budget": project.budget_range,
        }
        for project, score in ranked
        if score > 0.08
    ]


def _profile_skill_set(profile):
    return {skill.lower() for skill in profile.skill_list()}


def score_freelancer(profile, project_skills, project_description="", budget=0):
    freelancer_skills = _profile_skill_set(profile)
    target_skills = {skill.lower() for skill in project_skills}
    overlap = sorted(target_skills.intersection(freelancer_skills))
    skill_score = int((len(overlap) / max(len(target_skills), 1)) * 58)

    experience_score = clamp(profile.completed_projects * 4, 0, 22)
    rating_score = int((float(profile.rating or 0) / 5) * 15)
    availability_score = 5 if profile.availability == "available" else 0
    budget_score = 0
    if budget and profile.hourly_rate:
        estimated_hours = max(10, budget / max(profile.hourly_rate, 1))
        budget_score = 5 if estimated_hours >= 15 else 2

    match = clamp(skill_score + experience_score + rating_score + availability_score + budget_score, 8, 98)
    return {
        "match_percentage": match,
        "skill_overlap": [skill.title() for skill in overlap],
        "experience_score": experience_score,
        "rating_score": rating_score,
    }


def recommend_freelancers(project_skills, freelancer_profiles, budget=0, limit=3):
    recommendations = []
    for profile in freelancer_profiles:
        score = score_freelancer(profile, project_skills, budget=budget)
        recommendations.append(
            FreelancerRecommendation(
                user_id=profile.user_id,
                username=profile.user.username,
                display_name=profile.display_name,
                match_percentage=score["match_percentage"],
                skill_overlap=score["skill_overlap"],
                experience_score=score["experience_score"],
                rating=float(profile.rating or 0),
                headline=profile.headline,
            )
        )

    recommendations.sort(key=lambda item: item.match_percentage, reverse=True)
    return [item.__dict__ for item in recommendations[:limit]]


def recommendation_badges(match_percentage, project):
    badges = []
    if match_percentage >= 75:
        badges.append("Best match")
    if project.max_price >= 60000 or project.estimated_price >= 50000:
        badges.append("High budget")
    if project.estimated_days and project.estimated_days <= 7:
        badges.append("Urgent")
    if not badges:
        badges.append("Open project")
    return badges


def analyze_project(description, freelancer_profiles=None, similar_queryset=None):
    skills = extract_skills(description)
    complexity = classify_complexity(description, skills)
    min_price, max_price, estimated_price, estimated_days, confidence = predict_price_and_time(description)
    tags = generate_tags(description, skills, complexity)

    recommendations = []
    if freelancer_profiles is not None:
        recommendations = recommend_freelancers(skills, freelancer_profiles, estimated_price)

    similar = []
    if similar_queryset is not None:
        similar = find_similar_projects(description, similar_queryset)

    feature_summary = {
        "detected_skill_count": len(skills),
        "description_words": len(normalize_text(description).split()),
        "complexity": complexity,
        "model_version": MODEL_VERSION,
    }

    return ProjectAnalysis(
        min_price=min_price,
        max_price=max_price,
        estimated_price=estimated_price,
        estimated_days=estimated_days,
        time_label=estimate_time_label(estimated_days),
        complexity=complexity,
        confidence_score=confidence,
        skills=skills,
        tags=tags,
        budget_justification=explain_budget(description, skills, complexity),
        feature_summary=feature_summary,
        similar_projects=similar,
        recommended_freelancers=recommendations,
    )
