import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Text, Integer, String, ForeignKey
import pandas as pd


class WordWeight:
    def __init__(self, engine):
        self.tablename = "word_weights"
        self.engine = engine
        if self.tablename not in engine.table_names():
            self.create_table()
        self.meta = MetaData()
        self.tbl = Table(self.tablename, self.meta, autoload=True, autoload_with=self.engine)

    def create_table(self):
        meta = MetaData()
        words_tbl = Table("words", meta, autoload=True, autoload_with=self.engine)
        tbl = Table(self.tablename, meta, Column("id", Integer, primary_key=True, autoincrement=True),
                    Column("word_id", Integer, ForeignKey("words.id"), nullable=False),
                    Column("weight", Integer),

                    )
        meta.create_all(self.engine)
        logging.info(f"Finished creating {self.tablename} table")
        return

    def get_word_weights(self):
        query = f"select * from {self.tablename}"
        df = pd.read_sql(query, self.engine)
        df.sort_values('weight', inplace=True)
        df.index = range(len(df))
        return df

    def update_weight(self, word_id):
        word_id = int(word_id)
        query = f"select * from {self.tablename} where `word_id`={word_id}"
        df = pd.read_sql(query, self.engine)
        con = self.engine.connect()
        if len(df) == 0:
            stmt = self.tbl.insert().values({"word_id": word_id, "weight": 1})
            con.execute(stmt)
            logging.info(f"inserted word weight for {word_id}")
        else:
            df.loc[0, 'weight'] += 1
            stmt = self.tbl.update().where(self.tbl.c.word_id == word_id).values({'weight': int(df.loc[0, 'weight'])})
            con.execute(stmt)
            logging.info(f"update weight of {word_id} to {df.loc[0, 'weight']}")
