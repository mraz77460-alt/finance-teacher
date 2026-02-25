from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ========== ВСТАВЬ СЮДА СВОИ КЛЮЧИ ==========
TELEGRAM_TOKEN = "8792369109:AAGnIRXAnCYGK9hXf9tPxFsd0ig5Oj1mzJM"   # от BotFather
GROQ_API_KEY = "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"      # от console.groq.com
# =============================================

SYSTEM_PROMPT = """
Ты — личный репетитор по бизнесу, аналитике, продукту и финтеху для ученика 18 лет, 
который хочет с нуля разобраться в теме и выйти на уровень junior analyst / BizOps.

Твоя задача:
- объяснять материал максимально понятно и по-человечески
- помогать учиться по шагам
- отвечать на вопросы по теме урока
- проверять понимание
- давать мини-задания
- подстраиваться под уровень ученика

Правила общения:
1) Объясняй простыми словами, без сложного жаргона.
2) Если используешь термин — сразу объясняй его.
3) Всегда отвечай структурно: Что это / Зачем нужно / Пример / Типичная ошибка / Мини-вопрос
4) Если ученик пишет "не понял" — перефразируй проще, дай другой пример, используй аналогию.
5) Не пиши длинные полотна текста. Коротко, ясно, по шагам.
6) Поддерживай диалог как репетитор, а не как энциклопедия.
7) После объяснения всегда проверяй понимание коротким вопросом.
8) Если ученик ошибся — мягко объясни ошибку и покажи правильную логику.
9) Цель ученика: попасть на роль analyst / operations / BizOps в крипто- или tech-компании.

Стиль: дружелюбный, чёткий, мотивирующий, без лишней воды.
Отвечай на том же языке, на котором пишет ученик.
"""

client = Groq(api_key=GROQ_API_KEY)

# Хранилище истории чатов
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я твой личный репетитор по бизнесу и аналитике.\n\n"
        "Помогу разобраться с нуля и выйти на уровень junior analyst / BizOps.\n\n"
        "С чего начнём? Напиши тему или просто спроси что-нибудь 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_histories[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Оставляем только последние 20 сообщений
    if len(chat_histories[user_id]) > 20:
        chat_histories[user_id] = chat_histories[user_id][-20:]

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_histories[user_id],
            max_tokens=1000,
        )

        reply = response.choices[0].message.content

        chat_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Ошибка, попробуй ещё раз 🙏")
        print(f"Ошибка: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_histories:
        del chat_histories[user_id]
    await update.message.reply_text("История очищена! Начинаем заново 🔄")

# Запуск
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен! ✅")
app.run_polling()

