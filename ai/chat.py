from config.settings import client, MODEL_NAME


def ask_groq(messages):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )

    return response.choices[0].message.content