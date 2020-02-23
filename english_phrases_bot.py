from config import Config
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from english_words.new_word_conversation_handler import NewWordConversationHandler
from english_words.guess_word import GuessWordHandler
from sqlalchemy import create_engine

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def start_old(update, context):
    keyboard = [[InlineKeyboardButton("New word", callback_data="/newword"), InlineKeyboardButton("Guess word", callback_data="/guessword")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hello, I am english phrase bot. Choose what you want to do.", reply_markup=reply_markup)


def start(update, context):
    keyboard = [[InlineKeyboardButton('Guess a word', callback_data="/guessword")], [InlineKeyboardButton("Guess from phrase", callback_data="/guessfromphrase")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose what you want", reply_markup=reply_markup)


def help(update, context):
    update.message.reply_text("Choose what you want?\n /newword \n /guessword\n /guessfromphrase\n")


def button(update, context):
    query = update.callback_query
    context.bot.send_message(chat_id=update.effective_chat.id, text=query.data)


def main():
    updater = Updater(token=Config.token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    # dispatcher.add_handler(CallbackQueryHandler(button))

    engine = create_engine("sqlite:///english_words.sqlite")
    new_word_handler_obj = NewWordConversationHandler(engine)

    new_word_handler = ConversationHandler(entry_points=[CommandHandler("newword", new_word_handler_obj.start)],
                                           states={
                                               new_word_handler_obj.WORD: [MessageHandler(Filters.text, new_word_handler_obj.new_word_handler)],
                                               new_word_handler_obj.MEANING: [MessageHandler(Filters.text, new_word_handler_obj.new_meaning_handler)],
                                               new_word_handler_obj.UZBEK_MEANING: [MessageHandler(Filters.text, new_word_handler_obj.new_uzbek_meaning_handler)],
                                               new_word_handler_obj.RUSSIAN_MEANING: [MessageHandler(Filters.text, new_word_handler_obj.new_russian_meaning_handler)],
                                               new_word_handler_obj.PHRASE: [MessageHandler(Filters.text, new_word_handler_obj.new_phrase_handler)],
                                               new_word_handler_obj.SOURCE: [MessageHandler(Filters.text, new_word_handler_obj.new_source_handler)],
                                               new_word_handler_obj.WRITER: [MessageHandler(Filters.text, new_word_handler_obj.new_writer_handler)]
                                           },
                                           fallbacks=[CommandHandler("cancel", new_word_handler_obj.cancel)])
    dispatcher.add_handler(new_word_handler)

    guess_word_obj = GuessWordHandler(engine)
    guess_word_handler = ConversationHandler(entry_points=[CommandHandler("guessword", guess_word_obj.start)],
                                             states={
                                                 guess_word_obj.GUESSWORD: [MessageHandler(Filters.text, guess_word_obj.guess_word)],
                                                 guess_word_obj.NOTHING: [MessageHandler(Filters.text, guess_word_obj.any_state_handler)]
                                             },
                                             fallbacks=[CommandHandler("showanswer", guess_word_obj.show_answer),
                                                        CommandHandler("show_phrase", guess_word_obj.show_phrase),
                                                        CommandHandler("show_uzbek", guess_word_obj.show_uzbek),
                                                        CommandHandler("show_russian", guess_word_obj.show_russian)])

    dispatcher.add_handler(guess_word_handler)

    guess_from_phrase_handler = ConversationHandler(entry_points=[CommandHandler("guessfromphrase", guess_word_obj.start_guess_from_phrase)],
                                                    states={guess_word_obj.GUESS_FROM_PHRASE: [MessageHandler(Filters.text, guess_word_obj.guess_from_phrase)],
                                                            guess_word_obj.NOTHING: [MessageHandler(Filters.text, guess_word_obj.any_state_handler)]},
                                                    fallbacks=[CommandHandler("showanswer", guess_word_obj.show_answer),
                                                               CommandHandler("show_phrase", guess_word_obj.show_phrase),
                                                               CommandHandler("show_uzbek", guess_word_obj.show_uzbek),
                                                               CommandHandler("show_russian", guess_word_obj.show_russian)])
    dispatcher.add_handler(guess_from_phrase_handler)

    dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.add_error_handler(error)
    updater.start_polling()
    logging.info("eng_phrases_bot started polling...")
    updater.idle()


if __name__ == '__main__':
    main()
