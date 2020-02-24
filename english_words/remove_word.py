import logging
from telegram import ParseMode
from english_words.word import Word
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd


class RemoveWordConversationHandler:
    def __init__(self, engine):
        self.name = "remove word conversation handler"
        self.engine = engine
        self.START, self.REMOVE = range(2)

    def send_list_of_words(self, update, context):
        words_df = pd.read_sql("SELECT * FROM `words`", self.engine)
        keyboard = [[InlineKeyboardButton(row['word'], callback_data=row['word'])] for i, row in words_df.iterrows()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Choose the word to edit", reply_markup=reply_markup)
        return self.REMOVE

    def remove_word(self, update, context):
        word_to_remove = update.callback_query.data
        word_df = pd.read_sql(f"SELECT * FROM `words` WHERE `word`='{word_to_remove}'", self.engine)
        word_id = int(word_df.loc[0, 'id'])
        con = self.engine.connect()
        stmt = f"DELETE FROM `word_weights` WHERE `word_id`={int(word_id)}"
        con.execute(stmt)
        stmt = f"DELETE FROM `words` WHERE `word`='{word_to_remove}'"
        con.execute(stmt)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Removed {word_to_remove}")
        return ConversationHandler.END

    def cancel(self):
        return ConversationHandler.END
