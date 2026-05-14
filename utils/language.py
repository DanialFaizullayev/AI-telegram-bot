def detect_language(text):
    text = text.lower()

    if any(c in text for c in "әіңғүұқөһ"):
        return "Kazakh"

    if any("а" <= c <= "я" for c in text):
        return "Russian"

    return "English"