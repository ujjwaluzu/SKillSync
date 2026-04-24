def extract_features(text):
    text = text.lower()

    return {
        "ecommerce": int("ecommerce" in text),
        "payment": int("payment" in text),
        "auth": int("login" in text or "auth" in text),
    }


def estimate_price(features):
    base = 5000

    if features["ecommerce"]:
        base += 20000
    if features["payment"]:
        base += 10000
    if features["auth"]:
        base += 5000

    return base, int(base * 1.5)