from ai.chat import ask_groq
from utils.markdown import clean_markdown


def generate_test(topic_name):
    prompt = f'''
Создай реалистичный тест ЕНТ по предмету "{topic_name}".

- 10 вопросов
- 4 варианта ответа
- Только русский язык

В конце напиши:

ANSWERS:
1-A
2-B
'''

    reply = ask_groq([
        {
            "role": "system",
            "content": f"Ты создаешь тесты ЕНТ по предмету {topic_name}."
        },
        {
            "role": "user", "content": prompt
        }
    ])

    return clean_markdown(reply)