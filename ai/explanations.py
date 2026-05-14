EXPLAIN_WORDS = [
    "объяс",
    "түсіндір",
    "explain",
    "разбор",
    "why",
    "почему"
]

def explain_test(test_data):

    return f"""
Ты преподаватель ЕНТ.

Вот прошлый тест:

{test_data["questions"]}

Правильные ответы:
{test_data["answers"]}

Ответы ученика:
{test_data["user_answers"]}

Объясни КАЖДЫЙ вопрос пошагово.
Объясни почему правильный ответ правильный.
Пиши только на русском языке.
"""