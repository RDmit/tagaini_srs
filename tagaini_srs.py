#!/usr/bin/env python3

import sqlite3
import zlib
import random
import os
import sys
import json
from datetime import timedelta, datetime


class colors:
    GRAY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'


class SrsItem:
    """Represents an SRS item. Is mapped to a row of the DB."""
    def __init__(self, item_id, external_id, text, reading,
                 meaning, grade, failures, successes, is_kanji):
        self.item_id = item_id
        self.external_id = external_id
        self.grade = grade
        self.failures = failures
        self.successes = successes
        self.is_kanji = is_kanji
        self.text = text
        self.reading = reading
        self.meaning = meaning


all_srs_query = '''
SELECT TagainiId, AssociatedKanji FROM srsentryset'''

tagaini_user_items_query = '''
SELECT id, type FROM training'''

tagaini_user_item_update_command = '''
UPDATE training SET score='{1}', nbTrained='{2}', nbSuccess='{3}'
WHERE Id='{0}'
'''

tagaini_kanji_reading_query = '''
SELECT group_concat(rc.c0reading)
FROM reading
LEFT JOIN readingText_content rc ON rc.docid = reading.docid
WHERE entry = {0}
'''

tagaini_kanji_meaning_query = '''
SELECT meanings FROM meaning WHERE entry = {0}'''

tagaini_vocab_query = '''
SELECT kanjic.c0reading, kanac.c0reading
FROM kanji
LEFT JOIN kanjiText_content kanjic ON kanjic.docid = kanji.docid
LEFT JOIN kana ON kana.id = kanji.id
LEFT JOIN kanaText_content kanac ON kanac.docid = kana.docid
WHERE kanji.id = {0} and kanji.priority = 0 and kana.priority = 0
'''

tagaini_vocab_kana_only_query = '''
SELECT kanac.c0reading, kanac.c0reading
FROM kana
LEFT JOIN kanaText_content kanac ON kanac.docid = kana.docid
WHERE kana.id = {0} and kana.priority = 0
'''

tagaini_vocab_meaning_query = '''
SELECT glosses FROM glosses WHERE id = {0}'''

due_items_query = '''
SELECT Id, CurrentGrade, FailureCount, SuccessCount,
    Meanings, Readings, AssociatedVocab, AssociatedKanji, TagainiId
FROM srsentryset
WHERE NextAnswerDate < {0}
'''

till_review_query = '''
SELECT NextAnswerDate
FROM srsentryset
WHERE NextAnswerDate > 0
ORDER BY NextAnswerDate ASC
LIMIT 1
'''

worst_items_query = '''
SELECT AssociatedVocab, AssociatedKanji, FailureCount
FROM srsentryset
ORDER BY FailureCount DESC
LIMIT {0}
'''

reviews_after_time_query = '''
SELECT COUNT(*) FROM srsentryset WHERE NextAnswerDate < {0}'''

create_srs_table_command = '''
CREATE TABLE IF NOT EXISTS srsentryset (
Id INTEGER PRIMARY KEY,
TagainiId INTEGER,
CurrentGrade INTEGER,
FailureCount INTEGER,
SuccessCount INTEGER,
Meanings INTEGER,
Readings INTEGER,
AssociatedVocab TEXT,
AssociatedKanji TEXT,
NextAnswerDate INTEGER,
LastUpdateDate INTEGER );
'''

insert_command = '''
INSERT INTO srsentryset (
TagainiId,
CurrentGrade,
FailureCount,
SuccessCount,
Meanings,
Readings,
AssociatedVocab,
AssociatedKanji,
NextAnswerDate,
LastUpdateDate )
VALUES ( {0}, 0, 0, 0, "{1}", "{2}", {3}, {4}, {5}, {6} );
'''

update_command = '''
UPDATE srsentryset SET CurrentGrade='{1}', FailureCount='{2}',
    SuccessCount='{3}', NextAnswerDate='{4}', LastUpdateDate='{5}'
WHERE Id='{0}'
'''

stats_query = '''
select count(*) from srsentryset union all
select count(*) from srsentryset where AssociatedVocab not NULL union all
select count(*) from srsentryset where AssociatedKanji not NULL union all
select count(*) from srsentryset where CurrentGrade = 0 union all
select count(*) from srsentryset where CurrentGrade = 1 union all
select count(*) from srsentryset where CurrentGrade = 2 union all
select count(*) from srsentryset where CurrentGrade = 3 union all
select count(*) from srsentryset where CurrentGrade = 4 union all
select count(*) from srsentryset where CurrentGrade = 5 union all
select count(*) from srsentryset where CurrentGrade = 6 union all
select count(*) from srsentryset where CurrentGrade = 7 union all
select count(*) from srsentryset where CurrentGrade = 8
'''


intervals = (4, 8, 24, 72, 168, 336, 720, 2880)
pause_before_exit = False
no_color = False


def add_srs_kanji(cursor, kanji_id):
    print('add kanji', chr(kanji_id))
    # Get reading
    con = sqlite3.connect(kanji_db)
    reading = con.cursor().execute(tagaini_kanji_reading_query.format(kanji_id)).fetchone()[0]
    con.close()
    # Get meaning
    con = sqlite3.connect(kanji_meaning_db)
    meaning = ','.join([get_tagaini_meaning(x[0]) for x in con.cursor().execute(tagaini_kanji_meaning_query.format(kanji_id))])
    con.close()
    cursor.execute(insert_command.format(kanji_id, meaning, reading, 'NULL', f'"{chr(kanji_id)}"', get_next_review_time(0), get_ticks()))
    cursor.connection.commit()


def add_srs_vocab(cursor, vocab_id):
    # Get reading
    con = sqlite3.connect(vocab_db)
    vocab = con.cursor().execute(tagaini_vocab_query.format(vocab_id)).fetchone()
    if vocab == None:
        vocab = con.cursor().execute(tagaini_vocab_kana_only_query.format(vocab_id)).fetchone()
    con.close()
    print('add vocab', vocab[0])
    # Get meaning
    con = sqlite3.connect(vocab_meaning_db)
    meaning = get_tagaini_meaning(con.cursor().execute(tagaini_vocab_meaning_query.format(vocab_id)).fetchone()[0])
    con.close()
    cursor.execute(insert_command.format(vocab_id, meaning, vocab[1], f'"{vocab[0]}"', 'NULL', get_next_review_time(0), get_ticks()))
    cursor.connection.commit()


def import_from_tagaini(cursor):
    srs_kanji = set()
    srs_vocab = set()
    for row in cursor.execute(all_srs_query):
        if row[1] is None:
            srs_vocab.add(row[0])
        else:
            srs_kanji.add(row[0])
    con = sqlite3.connect(tagaini_user_db)
    user_db_cursor = con.cursor()
    for row in user_db_cursor.execute(tagaini_user_items_query):
        if row[1] == 2 and row[0] not in srs_kanji:
            add_srs_kanji(cursor, row[0])
        elif row[1] == 1 and row[0] not in srs_vocab:
            add_srs_vocab(cursor, row[0])
    con.close()


def export_to_tagaini(item):
    con = sqlite3.connect(tagaini_user_db)
    con.cursor().execute(tagaini_user_item_update_command.format(item.external_id, grade_to_score(item.grade), item.failures + item.successes, item.successes))
    con.commit()
    con.close()


def create_db():
    con = sqlite3.connect(srs_db)
    cursor = con.cursor()
    cursor.execute(create_srs_table_command)
    con.commit()
    con.close()


def get_tagaini_meaning(text):
    return zlib.decompress(text[4:]).decode('utf-8').strip('\n').replace('\n', ',').replace(',,', ',').replace('"','\'')


def grade_to_score(grade):
    return (0, 10, 20, 30, 40, 55, 70, 85, 100)[grade]


def get_ticks(time_from_now = 0):
    start_date = datetime(1, 1, 1)
    date = datetime.utcnow()
    date += timedelta(hours = time_from_now)
    timediff = date - start_date
    sec = int(timediff.total_seconds())
    return sec * 10000000


def get_next_review_time(grade):
    if grade == 8:
        return None
    return get_ticks(intervals[grade])


def open_db():
    if not os.path.isfile(srs_db):
        create_db()
    con = sqlite3.connect(srs_db)
    return con.cursor()


def get_due_items(cursor):
    items = list()
    for row in cursor.execute(due_items_query.format(get_ticks())):
        is_kanji = row[7] is not None
        text = row[7] if is_kanji else row[6]
        items.append(SrsItem(row[0], row[8], text, row[5], row[4], row[1], row[2], row[3], is_kanji))
    return items


def store_item(cursor, item):
    cursor.execute(update_command.format(item.item_id, item.grade, item.failures, item.successes, get_next_review_time(item.grade), get_ticks()))
    cursor.connection.commit()
    export_to_tagaini(item)


def get_time_till_review(cursor):
    first_review_time = cursor.execute(till_review_query).fetchone()
    if first_review_time is None:
        return '∞ min'
    tick_diff = first_review_time[0] - get_ticks()
    minutes = tick_diff / 10000000 / 60
    if minutes < 60:
        return f'{round(minutes, 1)} min'
    else:
        return f'{round(minutes/60, 1)} hours'


def review_success(item):
    print(f'Grade {colors.GREEN}{item.grade} ↗ ', end='')
    if item.grade < 8:
        item.grade += 1
    print(f'{item.grade}{colors.END}')
    item.successes += 1


def review_fail(item):
    print(f'Grade {colors.RED}{item.grade} ↘ ', end='')
    if item.grade > 0:
        item.grade -= 1
    print(f'{item.grade}{colors.END}')
    item.failures += 1


def review_item(item):
    print('----------------------')
    if item.is_kanji:
        print(f'{colors.BLUE}Kanji{colors.END}')
    else:
        print(f'{colors.MAGENTA}Vocab{colors.END}')
    print(item.text)
    continue_input = input(f'{colors.GRAY}Press ENTER when ready (q to quit){colors.END}\n')
    if len(continue_input) > 0 and continue_input[0].lower() == 'q':
        quit()
    print(colors.CYAN + item.reading + '\n' + colors.YELLOW + item.meaning + colors.END)
    while True:
        reply = input(f'{colors.GRAY}Good? (y/n){colors.END} ')
        if len(reply) > 0:
            break
    return reply[0].lower() == 'y'


def main():
    cursor = open_db()
    import_from_tagaini(cursor)
    items = get_due_items(cursor)
    if len(items) == 0:
        print(f'Next review in {get_time_till_review(cursor)}')
        cursor.connection.close()
        quit()
    print(f'Items to review: {len(items)}')
    reply = input(f'{colors.GRAY}Start review? (y/n){colors.END} ')
    print(reply)
    if len(reply) > 0 and reply[0].lower() != 'y':
        cursor.connection.close()
        quit()
    while len(items) > 0:
        print(f'\n\nReviews left: {len(items)}')
        item = random.choice(items)
        result = review_item(item)
        if result:
            review_success(item)
        else:
            review_fail(item)
        store_item(cursor, item)
        items.remove(item)
    print('Done.')
    print(f'Next review in {get_time_till_review(cursor)}')
    cursor.connection.close()
    quit()


def get_db_stats():
    cursor = open_db()
    stats = cursor.execute(stats_query).fetchall()
    cursor.connection.close()
    return [x[0] for x in stats]


def show_db_stats():
    stats = get_db_stats()
    print('SRS statistics')
    print(f'Total: {stats[0]}    {colors.MAGENTA}Vocab: {stats[1]}    {colors.BLUE}Kanji: {stats[2]}{colors.END}')
    print(colors.RED, stats[3], stats[4],
          colors.YELLOW, stats[5], stats[6],
          colors.BLUE, stats[7], stats[8],
          colors.CYAN, stats[9], stats[10],
          colors.GREEN, stats[11], colors.END)


def show_worst_items():
    cursor = open_db()
    print('Worst items:')
    for row in cursor.execute(worst_items_query.format(10)):
        print(row)


def show_review_count(hours):
    cursor = open_db()
    reviews = cursor.execute(reviews_after_time_query.format(get_ticks(hours))).fetchone()[0]
    print(f'Reviews in {hours}h: {reviews}')

def colors_off():
    colors.GRAY = ''
    colors.RED = ''
    colors.GREEN = ''
    colors.YELLOW = ''
    colors.BLUE = ''
    colors.MAGENTA = ''
    colors.CYAN = ''
    colors.END = ''

def parse_cmd_line():
    for i, arg in enumerate(sys.argv):
        if arg == '--pause' or arg == '-p':
            global pause_before_exit
            pause_before_exit = True
        if arg == '--no-color' or arg == '-nc':
            colors_off()
        if arg == '--worst' or arg == '-w':
            show_worst_items()
            quit()
        if arg == '--stats' or arg == '-s':
            show_db_stats()
            quit()
        if arg == '--hours' or arg == '-h':
            try:
                hours = int(sys.argv[i + 1])
            except:
                hours = 24
            show_review_count(hours)
            quit()


def quit():
    if pause_before_exit:
        input(f'{colors.GRAY}Press ENTER{colors.END}\n')
    exit(0)


config = json.load(open('config.json'))
srs_db = config['srs_db']
tagaini_user_db =  config['tagaini_user_db']
kanji_db = config['kanji_db']
vocab_db = config['vocab_db']
kanji_meaning_db = config['kanji_meaning_db']
vocab_meaning_db = config['vocab_meaning_db']
if __name__ == '__main__':
    if sys.platform == 'win32':
        colors_off()
    parse_cmd_line()
    main()

