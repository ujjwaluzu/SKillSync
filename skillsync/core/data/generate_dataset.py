import pandas as pd
import random

# 🔹 Expanded project types
project_types = [
    "portfolio website", "blog website", "ecommerce website",
    "chat application", "dashboard", "booking system",
    "social media app", "LMS platform", "CMS website",
    "job portal", "freelancing platform", "crypto dashboard",
    "finance tracking app", "note taking app", "task manager",
    "project management tool", "real estate platform",
    "food delivery app", "video streaming platform",
    "music streaming app", "news aggregator",
    "forum website", "event management system",
    "inventory management system", "healthcare system",
    "education platform", "online exam system"
]

# 🔹 Expanded features (grouped logically)
features = [
    # Auth & users
    "with login", "with authentication", "with user roles",
    "with two-factor authentication",

    # Payments
    "with payment integration", "with subscription system",

    # UI/UX
    "mobile responsive", "with modern UI", "with animations",

    # Backend
    "with REST API", "with GraphQL API", "with backend integration",

    # Advanced functionality
    "with real-time chat", "with notifications",
    "with search functionality", "with advanced filters",
    "with recommendation system",

    # Admin & analytics
    "with admin panel", "with analytics dashboard",
    "with reporting system",

    # Integrations
    "with third-party API", "with map integration",
    "with payment gateway (Stripe)", "with Razorpay",

    # AI/ML features
    "with AI chatbot", "with machine learning model",
    "with prediction system",

    # DevOps & infra
    "with cloud deployment", "with CI/CD pipeline"
]

# 🔹 Complexity
complexity_levels = ["basic", "intermediate", "advanced"]

# 🔹 Better pricing logic
def calculate_price(base, feature_count, complexity, project_type):
    multiplier = {
        "basic": 1,
        "intermediate": 1.5,
        "advanced": 2.2
    }

    # Project-specific weight
    project_weight = 1

    if "ecommerce" in project_type:
        project_weight = 1.5
    elif "streaming" in project_type:
        project_weight = 1.8
    elif "AI" in project_type or "machine learning" in project_type:
        project_weight = 1.7
    elif "management" in project_type:
        project_weight = 1.3

    return int((base + feature_count * 6000) * multiplier[complexity] * project_weight)


data = []

# 🔥 Generate 1000 rows (bigger dataset)
for _ in range(1000):
    project = random.choice(project_types)

    selected_features = random.sample(features, random.randint(2, 6))
    complexity = random.choice(complexity_levels)

    description = f"{complexity} {project} " + " ".join(selected_features)

    base_price = random.randint(5000, 20000)

    price = calculate_price(base_price, len(selected_features), complexity, project)

    data.append({
        "description": description,
        "price": price
    })

# Save dataset
df = pd.DataFrame(data)
df.to_csv("core/data/dataset.csv", index=False)

print("🔥 Improved dataset generated successfully!")