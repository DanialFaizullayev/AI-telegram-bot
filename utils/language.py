def detect_language(text):

    text = text.lower()

    kazakh_letters = "әіңғүұқөһ"

    if any(letter in text for letter in kazakh_letters):
        return "Kazakh"

    elif any("а" <= c <= "я" for c in text):
        return "Russian"

    else:
        return "English"