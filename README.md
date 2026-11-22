# AI ENT Assistant

Telegram bot that helps with ENT prep (the university entrance exam in Kazakhstan). You pick a subject, send a question or a photo of a problem, and it explains the solution step by step. It can also make a 10 question test and check your answers.

## How it works

- `/start` shows a keyboard with the subjects (math, physics, chemistry, biology, informatics, geography, history of Kazakhstan, world history, reading literacy, general)
- picking a subject loads a system prompt for that subject
- every message goes to the Groq API with the subject prompt and the last 10 messages as history
- the language is detected from your message (Kazakh / Russian / English) and the bot answers in the same one
- photos are sent to the same model (it's multimodal) and it solves the task from the image
- the "Тест" button asks the model for a 10 question multiple choice test with an answer key at the end. The bot cuts the key out, shows you the questions, and when you send `A C D B ...` it checks them and gives a score
- after a test you can write "Объясни тест" and it explains every question
- answers go through a small cleanup function because Telegram doesn't render markdown/LaTeX from the model

There's also `/stats` and a small Flask dashboard (`dashboard.py`) that read users from `data/users.json`.

## Tech stack

- Python
- python-telegram-bot 20.7
- Groq API, model `meta-llama/llama-4-scout-17b-16e-instruct`
- python-dotenv
- Flask (dashboard only)

## Project structure

```
bot.py              entry point, registers handlers
dashboard.py        flask dashboard
ai/
  chat.py           groq request wrapper
  prompts.py        system prompt for each subject
  test_generator.py prompt for generating tests
  explanations.py   prompt for explaining tests
config/
  settings.py       env vars, model name, groq client, in-memory state
handlers/
  start_handler.py
  message_handler.py  subjects, chat, tests, answer checking
  photo_handler.py
  stats_handler.py
  test_handler.py
templates/
  index.html        dashboard page
  topic_intros.py   intro text for each subject
utils/
  keyboards.py
  language.py       language detection
  markdown.py       cleans markdown/latex
  storage.py        read/write users.json
```
