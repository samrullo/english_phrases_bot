import logging
from telegram import ParseMode
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
        self.GUESSWORD, self.GUESS_FROM_PHRASE, self.NOTHING = range(3)

    def get_option_list(self):
        return f"/showanswer for meaning\n/show_phrase for an associated phrase\n/show_uzbek for uzbek translation\n/show_russian for russian translation.\n/everything for the whole word\n/end to end"

    def get_random_word(self):
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
        logging.info(f"chosen word is {chosen_word}")
        return chosen_word

    def start(self, update, context):
        self.chosen_word = self.get_random_word()
        logging.info(f"chosen word is {self.chosen_word}")
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.chosen_word['meaning'])
        return self.GUESSWORD

    def guess_word(self, update, context):
        guessed_word = update.message.text
        logging.info(f"user guessed word {guessed_word}")
        if guessed_word.lower() == self.chosen_word['word'].lower():
            update.message.reply_text(f"You guessed right, congrats!\n" + self.get_option_list())
            return self.NOTHING
        else:
            update.message.reply_text(f"Oops! That's not quite right. You can try again or \n" + self.get_option_list())
            return self.GUESSWORD

    def start_guess_from_phrase(self, update, context):
        self.chosen_word = self.get_random_word()
        the_chosen_word = self.chosen_word['word']
        lowercase_word = the_chosen_word.lower()
        uppercase_word = the_chosen_word[0].upper() + the_chosen_word[1:]
        logging.info(f"chosen word is {self.chosen_word}")
        update.message.reply_text(self.chosen_word['phrase'].replace(lowercase_word, "-------").replace(uppercase_word, "-------"))
        return self.GUESS_FROM_PHRASE

    def guess_from_phrase(self, update, context):
        guessed_word = update.message.text
        logging.info(f"user guessed word {guessed_word}")
        if guessed_word.lower() == self.chosen_word['word'].lower():
            update.message.reply_text(f"You guessed right, congrats!\n" + self.get_option_list())
            return self.NOTHING
        else:
            update.message.reply_text(f"Oops! That's not quite right. You can try again or \n" + self.get_option_list())
            return self.GUESS_FROM_PHRASE

    def show_answer(self, update, context):
        update.message.reply_text(self.chosen_word['word'])
        return self.NOTHING

    def show_phrase(self, update, context):
        update.message.reply_text(self.chosen_word['phrase'])
        return self.NOTHING

    def show_uzbek(self, update, context):
        update.message.reply_text(self.chosen_word['uzbek_meaning'])
        return self.NOTHING

    def show_russian(self, update, context):
        update.message.reply_text(self.chosen_word['russian_meaning'])
        return self.NOTHING

    def show_everything(self, update, context):
        word_obj = Word(self.chosen_word['word'], self.engine)
        word_obj.update_word()
        msg = f"*{word_obj.word}*\n"
        msg += f"Meaning : {word_obj.meaning}\n"
        msg += f"Uzbek meaning : {word_obj.uzbek_meaning}\n"
        msg += f"Russian meaning : {word_obj.russian_meaning}\n"
        msg += f"Phrase : {word_obj.phrase}\n"
        msg += f"Source : {word_obj.source}\n"
        msg += f"Writer : {word_obj.writer}"
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        return self.NOTHING

    def any_state_handler(self, update, context):
        update.message.reply_text(self.get_option_list())

    def end(self, update, context):
        update.message.reply_text("have a nice day, bye...")
        return ConversationHandler.END
