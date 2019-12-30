import logging
from english_words.word import Word
from telegram.ext import ConversationHandler


class NewWordConversationHandler:
    def __init__(self, engine):
        self.name = "new word conversation"
        self.engine = engine
        self.word = None
        self.WORD, self.MEANING, self.UZBEK_MEANING, self.RUSSIAN_MEANING, self.PHRASE, self.SOURCE, self.WRITER = range(7)

    def start(self, update, context):
        update.message.reply_text("Please enter the new word")
        return self.WORD

    def new_word_handler(self, update, context):
        user = update.message.from_user
        new_word = update.message.text
        self.word = Word(new_word, self.engine)
        logging.info(f"New word initiated by {user.first_name} is {new_word}")
        update.message.reply_text(f"Please enter a meaning for {new_word}")
        return self.MEANING

    def new_meaning_handler(self, update, context):
        user = update.message.from_user
        new_meaning = update.message.text
        self.word.meaning = new_meaning
        logging.info(f"New meaning specified by {user.first_name} is {new_meaning}")
        update.message.reply_text(f"Please enter uzbek meaning for {self.word.word}")
        return self.UZBEK_MEANING

    def new_uzbek_meaning_handler(self, update, context):
        new_uzbek_meaning = update.message.text
        self.word.uzbek_meaning = new_uzbek_meaning
        logging.info(f"uzbek meaning for {self.word.word} is {new_uzbek_meaning}")
        update.message.reply_text(f"Please enter russian meaning for {self.word.word}")
        return self.RUSSIAN_MEANING

    def new_russian_meaning_handler(self, update, context):
        new_russian_meaning = update.message.text
        self.word.russian_meaning = new_russian_meaning
        logging.info(f"russian meaning for {self.word.word} is {new_russian_meaning}")
        update.message.reply_text(f"Please enter a phrase for {self.word.word}")
        return self.PHRASE

    def new_phrase_handler(self, update, context):
        user = update.message.from_user
        new_phrase = update.message.text
        self.word.phrase = new_phrase
        logging.info(f"New phrase for {self.word.word} is {new_phrase} set by {user.first_name}")
        update.message.reply_text(f"Now enter the source for {self.word.word}")
        return self.SOURCE

    def new_source_handler(self, update, context):
        new_source = update.message.text
        self.word.source = new_source
        logging.info(f"New source for {self.word.word} is {new_source}")
        update.message.reply_text(f"Now enter the writer of {self.word.source}")
        return self.WRITER

    def new_writer_handler(self, update, context):
        new_writer = update.message.text
        self.word.writer = new_writer
        logging.info(f"New writer for {self.word.word}, {self.word.source} is {new_writer}")
        self.word.save_word()
        update.message.reply_text(f"Saved {str(self.word)} into database")
        return ConversationHandler.END

    def cancel(self, update, context):
        user = update.message.from_user
        logging.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text('All right you cancelled new word conversation.')
        return ConversationHandler.END
