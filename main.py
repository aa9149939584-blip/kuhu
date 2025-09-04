import os
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Bot token (inserted directly as requested)
TOKEN = "8458713216:AAEm5R9N0vGR4p9vOq--1-MDbqPcMwho6zY"

# Welcome message for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'سلام! من یک ربات خلاصه‌ساز متن هستم.\n'
        'فقط کافیه متن مورد نظرت رو برام بفرستی تا خلاصه‌اش رو تحویل بدم.'
    )

# Main function to summarize the text
async def summarize_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if not text:
        return

    try:
        # Using Sumy for summarization with a Persian tokenizer
        parser = PlaintextParser.from_string(text, Tokenizer("persian"))
        summarizer = LexRankSummarizer()
        
        # You can change the number of summary sentences here
        summary_sentences = summarizer(parser.document, sentences_count=3)
        
        summary = " ".join([str(sentence) for sentence in summary_sentences])

        if not summary:
            await update.message.reply_text('متن ارسالی شما برای خلاصه‌سازی خیلی کوتاهه.')
        else:
            await update.message.reply_text(f'**خلاصه متن شما:**\n\n{summary}')

    except Exception as e:
        await update.message.reply_text('متاسفم، مشکلی در پردازش متن شما پیش آمد.')
        print(f"Error: {e}")

# Create the Flask application and Telegram bot application
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, summarize_text))

# This is the webhook endpoint that Telegram sends updates to
@app.route("/", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        application.process_update(update)
    return jsonify({"status": "ok"})

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
