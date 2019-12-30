import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Text, Integer, String


class Word:
    def __init__(self, word, engine):
        self.word = word
        self.meaning = "new meaning"
        self.uzbek_meaning = "new uzbek meaning"
        self.russian_meaning = "new russian meaning"
        self.phrase = "new phrase"
        self.source = "source book"
        self.writer = "the writer"
        self.engine = engine
        self.tablename = "words"
        if self.tablename not in engine.table_names():
            self.create_table()
        self.meta = MetaData()
        self.tbl = Table(self.tablename, self.meta, autoload=True, autoload_with=self.engine)

    def save_word(self):
        insert_values = {"word": self.word, "meaning": self.meaning, "uzbek_meaning": self.uzbek_meaning, "russian_meaning": self.russian_meaning, "phrase": self.phrase, "source": self.source, "writer": self.writer}
        stmt = self.tbl.insert().values(insert_values)
        con = self.engine.connect()
        con.execute(stmt)
        logging.info(f"Successfully saved {insert_values}")
        return True

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
