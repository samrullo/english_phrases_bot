import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Text, Integer, String
import pandas as pd


class Word:
    def __init__(self, word, engine):
        self.word = word
        self.meaning = "new meaning"
        self.uzbek_meaning = "new uzbek meaning"
        self.russian_meaning = "new russian meaning"
        self.phrase = "new phrase"
        self.source = "source book"
        self.writer = "the writer"
        self.word_dict = {}
        self.engine = engine
        self.tablename = "words"
        if self.tablename not in engine.table_names():
            self.create_table()
        self.meta = MetaData()
        self.tbl = Table(self.tablename, self.meta, autoload=True, autoload_with=self.engine)

    def get_word(self):
        new_word_df = pd.read_sql(f"SELECT * FROM `words` WHERE word='{self.word}'", self.engine)
        return new_word_df.loc[0]

    def update_word(self):
        new_word = self.get_word()
        self.meaning = new_word['meaning']
        self.uzbek_meaning = new_word['uzbek_meaning']
        self.russian_meaning = new_word['russian_meaning']
        self.phrase = new_word['phrase']
        self.source = new_word['source']
        self.writer = new_word['writer']
        self.word_dict = {"word": self.word, "uzbek_meaning": self.uzbek_meaning, "russian_meaning": self.russian_meaning, "phrase": self.phrase, "source": self.source, "writer": self.writer}
        return

    def save_word(self):
        insert_values = {"word": self.word, "meaning": self.meaning, "uzbek_meaning": self.uzbek_meaning, "russian_meaning": self.russian_meaning, "phrase": self.phrase, "source": self.source, "writer": self.writer}
        stmt = self.tbl.insert().values(insert_values)
        con = self.engine.connect()
        con.execute(stmt)
        logging.info(f"Successfully saved {insert_values}")
        return True

    def update_column_value(self, col_name, new_col_value):
        stmt = self.tbl.update().where(self.tbl.c.word == self.word).values({col_name: new_col_value})
        con = self.engine.connect()
        con.execute(stmt)
        logging.info(f"Successfully updated {self.word} {col_name} to {new_col_value}")
        self.update_word()
        return

    def get_col_value_based_on_col_name(self, col_name):
        if col_name in self.word_dict.keys():
            return self.word_dict[col_name]
        else:
            return f"{col_name} is invalid column name"

    def create_table(self):
        meta = MetaData()
        tbl = Table(self.tablename, meta, Column("id", Integer, primary_key=True, autoincrement=True),
                    Column("word", String),
                    Column("meaning", Text),
                    Column("uzbek_meaning", Text),
                    Column("russian_meaning", Text),
                    Column("phrase", Text),
                    Column("source", String),
                    Column("writer", String))
        meta.create_all(self.engine)
        logging.info(f"Finished creating {self.tablename} table")
        return

    def __str__(self):
        return f"word : {self.word}, meaning : {self.meaning}, uzbek_meaning : {self.uzbek_meaning}, russian_meaning : {self.russian_meaning}, phrase : {self.phrase}, source : {self.source}, writer : {self.writer}"
