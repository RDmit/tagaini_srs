#!/usr/bin/env python3

import tagaini_srs
import sqlite3

all_query = '''
SELECT Id, CurrentGrade, FailureCount, SuccessCount,
    Meanings, Readings, AssociatedVocab, AssociatedKanji, TagainiId
FROM srsentryset
'''


def get_all_items(cursor):
    items = list()
    for row in cursor.execute(all_query):
        is_kanji = row[7] is not None
        text = row[7] if is_kanji else row[6]
        items.append(tagaini_srs.SrsItem(row[0], row[8], text, row[5], row[4], row[1], row[2], row[3], is_kanji))
    return items

def get_all_tagaini_ids():
    con = sqlite3.connect(tagaini_srs.tagaini_user_db)
    cursor = con.cursor()
    items = list()
    for row in cursor.execute(tagaini_srs.tagaini_user_items_query):
        items.append(row[0])
    con.close()
    return items


cursor = tagaini_srs.open_db()
srs_items = get_all_items(cursor)
cursor.connection.close()
tagaini_ids = get_all_tagaini_ids()
missing = filter(lambda item: item.external_id not in tagaini_ids, srs_items) 
for item in missing:
    print(item.text, item.reading, item.is_kanji, item.meaning)

