from .services.ai_engine import analyze_project, estimate_time_label


def predict_price(text):
    analysis = analyze_project(text)
    return analysis.min_price, analysis.max_price, analysis.estimated_price


def estimate_time(avg_price):
    if avg_price < 20000:
        return estimate_time_label(6)
    if avg_price < 50000:
        return estimate_time_label(16)
    return estimate_time_label(35)
