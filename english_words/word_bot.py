from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
import logging
from english_words.new_word_conversation_handler import NewWordConversationHandler
from sqlalchemy import create_engine

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    TOKEN = "365379007:AAFN0M2gifkBuVlLPQbSdl_DqrSsazqY8Qc"
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    engine = create_engine("sqlite:///english_words.sqlite")
    new_word_handler_obj = NewWordConversationHandler(engine)

    new_word_handler = ConversationHandler(entry_points=[CommandHandler("newword", new_word_handler_obj.start)],
                                           states={
                                               new_word_handler_obj.WORD: [MessageHandler(Filters.text, new_word_handler_obj.new_word_handler)],
                                               new_word_handler_obj.PHRASE: [MessageHandler(Filters.text, new_word_handler_obj.new_phrase_handler)],
                                               new_word_handler_obj.SOURCE: [MessageHandler(Filters.text, new_word_handler_obj.new_source_handler)],
                                               new_word_handler_obj.WRITER: [MessageHandler(Filters.text, new_word_handler_obj.new_writer_handler)]
                                           },
                                           fallbacks=[CommandHandler("cancel", new_word_handler_obj.cancel)])
    dispatcher.add_handler(new_word_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
