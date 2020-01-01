import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Text, Integer, String
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
        tbl = Table(self.tablename, meta, Column("id", Integer, primary_key=True, autoincrement=True),
                    Column("word_id", Integer),
                    Column("weight", Integer)
                    )
        meta.create_all(self.engine)
        logging.info(f"Finished creating {self.tablename} table")
        return

    def get_word_weights(self):
        query = f"select * from {self.tablename}"
        df = pd.read_sql(query, self.engine)
        df.sort_values('weight', inplace=True)
        return df

    def update_weight(self, id):
        query = f"select * from {self.tablename} where id={id}"
        df = pd.read_sql(query, self.engine)
        con = self.engine.connect()
        if len(df) == 0:
            stmt = self.tbl.insert().values({"word_id": id, "weight": 1})
            con.execute(stmt)
            logging.info(f"inserted word weight for {id}")
        else:
            df.loc[0, 'weight'] += 1
            stmt = self.tbl.update().where(self.tbl.c.id == id).values({'weight': df.loc[0, 'weight']})
            con.execute(stmt)
            logging.info(f"update weight of {id} to {df.loc[0, 'weight']}")
