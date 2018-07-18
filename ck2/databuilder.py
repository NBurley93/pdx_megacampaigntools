import sqlite3
import os
from common import loggy


class SaveDatabase(object):
    def __init__(self, outputName: str):
        if os.path.exists(outputName):
            os.remove(outputName)
        self.db = sqlite3.connect('{0}'.format(outputName))
        self.cursor = self.db.cursor()


    def addTable(self, tableName: str, fields: list):
        # Expect fields to be a list of tuples containing fieldname and fieldtype
        cmd = 'CREATE TABLE "{0}" ("_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE )'.format(tableName)
        self.cursor.execute(cmd)
        for field in fields:
            fname = field[0]
            ftype = field[1]

            self.cursor.execute("ALTER TABLE {0} ADD COLUMN {1} {2}".format(tableName, fname, ftype))


    def addRow(self, tableName: str, item: tuple):
        itemStr = '( NULL, '
        for t in item:
            itemStr += '\'' + str(t) + '\'' + ', '
        itemStr = itemStr[:-2] + ' )'
        cmd = 'INSERT INTO "{0}" VALUES {1}'.format(tableName, itemStr)
        self.cursor.execute(cmd)


    def export(self):
        self.db.commit()
        self.db.close()
