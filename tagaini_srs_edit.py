#!/usr/bin/env python3

import tagaini_srs

all_query = '''
SELECT Id, CurrentGrade, FailureCount, SuccessCount,
    Meanings, Readings, AssociatedVocab, AssociatedKanji, TagainiId
FROM srsentryset
'''
find_kanji_query = all_query + 'WHERE AssociatedKanji="{0}"'
find_vocab_by_text_query = all_query + 'WHERE AssociatedVocab="{0}"'
find_vocab_by_reading_query = all_query + 'WHERE Readings="{0}"'

update_kanji_command = '''
UPDATE srsentryset SET Meanings='{1}', Readings='{2}'
WHERE Id='{0}'
'''

update_vocab_command = '''
UPDATE srsentryset SET AssociatedVocab='{1}', Meanings='{2}', Readings='{3}'
WHERE Id='{0}'
'''


def find_kanji(cursor, text):
    row = cursor.execute(find_kanji_query.format(text)).fetchone()
    return tagaini_srs.SrsItem(row[0], row[8], row[7], row[5], row[4], row[1], row[2], row[3], True)

def find_vocab_by_text(cursor, text):
    row = cursor.execute(find_vocab_by_text_query.format(text)).fetchone()
    return tagaini_srs.SrsItem(row[0], row[8], row[6], row[5], row[4], row[1], row[2], row[3], False)

def find_vocab_by_reading(cursor, text):
    row = cursor.execute(find_vocab_by_reading_query.format(text)).fetchone()
    return tagaini_srs.SrsItem(row[0], row[8], row[6], row[5], row[4], row[1], row[2], row[3], False)

def store_kanji(cursor, item):
    cursor.execute(update_kanji_command.format(item.item_id, item.meaning, item.reading))
    cursor.connection.commit()

def store_vocab(cursor, item):
    cursor.execute(update_vocab_command.format(item.item_id, item.text, item.meaning, item.reading))
    cursor.connection.commit()

def store_item(cursor, text):
    if item.is_kanji:
        store_kanji(cursor, item)
    else:
        store_vocab(cursor, item)

cursor = tagaini_srs.open_db()
search_type = input('Search by:\n1 - Kanji\n2 - Vocab\n3 - Vocab by reading\n')
query = input('Search: ')
if search_type == '1':
    item = find_kanji(cursor, query)
elif search_type == '2':
    item = find_vocab_by_text(cursor, query)
else:
    item = find_vocab_by_reading(cursor, query)
print('----------------------')
print(item.text)
print(item.reading)
print(item.meaning)
edit_type = input('Edit:\n1 - Text\n2 - Reading\n3 - Meaning\n')
if edit_type == '1':
    prompt = 'New text:\n'
elif edit_type == '2':
    prompt = 'New reading:\n'
else:
    prompt = 'New meaning:\n'
new_value = input(prompt)
if edit_type == '1':
    item.text = new_value
elif edit_type == '2':
    item.reading = new_value
else:
    item.meaning = new_value
print('----------------------')
print(item.text)
print(item.reading)
print(item.meaning)
confirm_save = input('Save? (y/n): ')
if confirm_save.lower() == 'y':
    store_item(cursor, item)
cursor.connection.close()
