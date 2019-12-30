import logging
from english_words.word import Word
from telegram.ext import ConversationHandler
import pandas as pd
import numpy as np


class GuessWordHandler:
    def __init__(self, engine):
        self.name = "guess word handler"
        self.chosen_word = None
        self.engine = engine
        self.GUESSWORD = 1

    def start(self, update, context):
        all_words_query = "select * from words"
        all_words_df = pd.read_sql(all_words_query, self.engine)
        chosen_inx = np.random.choice(all_words_df.index)
        chosen_word = all_words_df.loc[chosen_inx]
        self.chosen_word = chosen_word
        logging.info(f"chosen word is {chosen_word}")
        update.message.reply_text(chosen_word['meaning'])
        return self.GUESSWORD

    def guess_word(self, update, context):
        guessed_word = update.message.text
        logging.info(f"user guessed word {guessed_word}")
        if guessed_word.lower() == self.chosen_word['word'].lower():
            update.message.reply_text(f"You guessed right, congrats!")
            return ConversationHandler.END
        else:
            update.message.reply_text(f"You can try again or press /showanswer for the answer")
            return self.GUESSWORD

    def show_answer(self, update, context):
        update.message.reply_text(self.chosen_word['word'])
        return ConversationHandler.END
