import logging
from english_words.word import Word
from english_words.word_weights import WordWeight
from telegram.ext import ConversationHandler
import pandas as pd
import numpy as np
from collections import defaultdict


class GuessWordHandler:
    def __init__(self, engine):
        self.name = "guess word handler"
        self.chosen_word = None
        self.engine = engine
        self.word_weight_obj = WordWeight(self.engine)
        self.GUESSWORD, self.GUESS_FROM_PHRASE = range(2)

    def start(self, update, context):
        all_words_query = "SELECT * FROM `words` WHERE `id` NOT IN (SELECT `word_id` FROM `word_weights`)"
        all_words_df = pd.read_sql(all_words_query, self.engine)
        if len(all_words_df) > 0:
            chosen_inx = np.random.choice(all_words_df.index)
            chosen_word = all_words_df.loc[chosen_inx]
            self.word_weight_obj.update_weight(chosen_word['id'])
        else:
            word_weights_df = self.word_weight_obj.get_word_weights()
            chosen_word_id = word_weights_df.loc[0, 'word_id']
            chosen_word_df = pd.read_sql(f"SELECT * FROM `words` WHERE `id`={chosen_word_id}", self.engine)
            chosen_word = chosen_word_df.loc[0]
            self.word_weight_obj.update_weight(chosen_word_id)
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

    def start_guess_from_phrase(self, update, context):
        all_words_query = "select * from words"
        all_words_df = pd.read_sql(all_words_query, self.engine)
        chosen_inx = np.random.choice(all_words_df.index)
        chosen_word = all_words_df.loc[chosen_inx]
        self.chosen_word = chosen_word
        the_chosen_word = chosen_word['word']
        lowercase_word = the_chosen_word.lower()
        uppercase_word = the_chosen_word[0].upper() + the_chosen_word[1:]
        logging.info(f"chosen word is {chosen_word}")
        update.message.reply_text(chosen_word['phrase'].replace(lowercase_word, "-------").replace(uppercase_word, "-------"))
        return self.GUESS_FROM_PHRASE

    def guess_from_phrase(self, update, context):
        guessed_word = update.message.text
        logging.info(f"user guessed word {guessed_word}")
        if guessed_word.lower() == self.chosen_word['word'].lower():
            update.message.reply_text(f"You guessed right, congrats!")
            return ConversationHandler.END
        else:
            update.message.reply_text(f"You can try again or press /showanswer for the answer")
            return self.GUESS_FROM_PHRASE

    def show_answer(self, update, context):
        update.message.reply_text(self.chosen_word['word'])
        return ConversationHandler.END
