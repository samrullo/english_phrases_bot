import logging
from telegram import ParseMode
from english_words.word import Word
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd


class EditWordConversationHandler:
    def __init__(self, engine):
        self.name = "edit word conversation handler"
        self.engine = engine
        self.word_obj = None
        self.chosen_word = None
        self.chosen_item = None
        self.START, self.CHOOSE_EDIT_ITEM, self.EDIT, self.SAVE = range(4)

    def send_list_of_words(self, update, context):
        words_df = pd.read_sql("SELECT * FROM `words`", self.engine)
        keyboard = [[InlineKeyboardButton(row['word'], callback_data=row['word'])] for i, row in words_df.iterrows()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Choose the word to edit", reply_markup=reply_markup)
        return self.CHOOSE_EDIT_ITEM

    def choose_item_for_edit(self, update, context):
        self.chosen_word = update.callback_query.data
        self.word_obj = Word(self.chosen_word, self.engine)
        self.word_obj.update_word()
        keyboard = [[InlineKeyboardButton(item, callback_data=item)] for item in ('meaning', 'uzbek_meaning', 'russian_meaning', 'phrase', 'source', 'writer')]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You chose the word *{self.chosen_word}* for editing. Next choose what you want to edit", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        return self.EDIT

    def edit_item(self, update, context):
        chosen_item = update.callback_query.data
        self.chosen_item = chosen_item
        chosen_item_current_value = self.word_obj.get_col_value_based_on_col_name(self.chosen_item)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have chosen {chosen_item} of the word {self.chosen_word} for editing. Current value of {chosen_item} is *{chosen_item_current_value}* .\nNext enter new value for the chosen item", parse_mode=ParseMode.MARKDOWN)
        return self.SAVE

    def save_item(self, update, context):
        new_col_val = update.message.text
        logging.info(f"will update {self.chosen_item} to {new_col_val}")
        self.word_obj.update_column_value(self.chosen_item, new_col_val)
        self.word_obj.update_word()
        update.message.reply_text(f"Updated word as {str(self.word_obj)}")
        return ConversationHandler.END

    def cancel(self, update, context):
        update.message.reply_text("Canceled edit word conversation. See you next time...")
        return ConversationHandler.END
