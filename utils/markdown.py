import re

def clean_markdown(text):

    math_symbols = {
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\gamma': 'γ',
        r'\\delta': 'δ',
        r'\\theta': 'θ',
        r'\\lambda': 'λ',
        r'\\pi': 'π',
        r'\\sqrt': '√',
        r'\\times': '×',
        r'\\cdot': '•',
        r'\\pm': '±',
    }

    for pattern, replacement in math_symbols.items():
        text = re.sub(pattern, replacement, text)

    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'\$+', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    return text.strip()