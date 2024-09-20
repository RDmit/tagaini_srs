#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from tkinter import font
import tagaini_srs
import tagaini_srs_histogram
import random
import locale

def show_answer(item):
    readingLabel["text"] = item.reading
    meaingLabel["text"] = item.meaning
    answer_button.grid_remove()
    bad_button.grid()
    good_button.grid()
    root.bind('<KeyPress-1>', lambda x: review_bad(item))
    root.bind('<KeyPress-2>', lambda x: review_good(item))

def update_item(item):
    global review_counter
    tagaini_srs.store_item(cursor, item)
    items.remove(item)
    review_counter += 1
    new_review()

def review_good(item):
    tagaini_srs.review_success(item)
    last_review_text_label["text"] = item.text + ' ↑' + str(item.grade)
    last_review_text_label["foreground"] = '#080'
    update_item(item)

def review_bad(item):
    tagaini_srs.review_fail(item)
    last_review_text_label["text"] = item.text + ' ↓' + str(item.grade)
    last_review_text_label["foreground"] = '#800'
    update_item(item)

def new_review():
    root.focus_set() # to avoid pressing 'bad'/'good' button on spacebar press
    root.unbind('<KeyPress-1>')
    root.unbind('<KeyPress-2>')
    if len(items) == 0:
        end_review()
        return
    global item
    review_counter_label["text"] = '    ' + str(review_counter) + '/' + str(len(items) + review_counter)
    item = random.choice(items)
    item_descr_label["text"] = 'Kanji:' if item.is_kanji else 'Vocab:'
    text_label["text"] = item.text
    text_label["foreground"] = '#05f' if item.is_kanji else '#80f'
    readingLabel["text"] = ""
    meaingLabel["text"] = ""
    bad_button.grid_remove()
    good_button.grid_remove()
    answer_button.grid()

def start_review():
    new_review()
    start_frame.grid_remove()
    review_frame.grid()

def end_review():
    update_db_stats()
    start_frame.grid()
    review_frame.grid_remove()

def open_histogram():
    tagaini_srs_histogram.main()

def update_db_stats():
    stats = tagaini_srs.get_db_stats()
    db_items_label["text"] = f"Total: {stats[0]}    Vocab: {stats[1]}    Kanji: {stats[2]}"
    level0_label["text"] = str(stats[3])
    level1_label["text"] = str(stats[4])
    level2_label["text"] = str(stats[5])
    level3_label["text"] = str(stats[6])
    level4_label["text"] = str(stats[7])
    level5_label["text"] = str(stats[8])
    level6_label["text"] = str(stats[9])
    level7_label["text"] = str(stats[10])
    level8_label["text"] = str(stats[11])
    level9_label["text"] = str(stats[12])
    global items
    items = tagaini_srs.get_due_items(cursor)
    if len(items) > 0:
        reviews_status_label["text"] = f"Ready for review: {len(items)}"
        start_review_button["state"] = "normal"
    else:
        reviews_status_label["text"] = f"Next review in {tagaini_srs.get_time_till_review(cursor)}"
        start_review_button["state"] = "disabled"

if __name__ == '__main__':
    try:
        locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
    except:
        pass
    cursor = tagaini_srs.open_db()
    tagaini_srs.import_from_tagaini(cursor)
    items = tagaini_srs.get_due_items(cursor)
    item = None
    review_counter = 0
    root = Tk()
    root.title('Tagaini SRS')
    start_frame = ttk.Frame(root, padding=10)
    start_frame.grid()
    db_items_label = ttk.Label(start_frame, text="", font=font.Font(size=15))
    db_items_label.grid(column=0, row=0, columnspan=10)
    level0_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#a00')
    level0_label.grid(column=0, row=1)
    level1_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#a00')
    level1_label.grid(column=1, row=1)
    level2_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#aa0')
    level2_label.grid(column=2, row=1)
    level3_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#aa0')
    level3_label.grid(column=3, row=1)
    level4_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#00a')
    level4_label.grid(column=4, row=1)
    level5_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#00a')
    level5_label.grid(column=5, row=1)
    level6_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#0aa')
    level6_label.grid(column=6, row=1)
    level7_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#0aa')
    level7_label.grid(column=7, row=1)
    level8_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#0a0')
    level8_label.grid(column=8, row=1)
    level9_label = ttk.Label(start_frame, text="", font=font.Font(size=15), foreground='#0a0')
    level9_label.grid(column=9, row=1)
    reviews_status_label = ttk.Label(start_frame, text="", font=font.Font(size=15))
    reviews_status_label.grid(column=0, row=2, columnspan=10)
    start_review_button = ttk.Button(start_frame, text="Start review", command=start_review)
    start_review_button.grid(column=0, row=3, columnspan=10)
    histogram_button = ttk.Button(start_frame, text="Histogram", command=open_histogram)
    histogram_button.grid(column=8, row=3, columnspan=2)
    update_db_stats()
    review_frame = ttk.Frame(root, padding=10)
    last_review_text_label = ttk.Label(review_frame, text="", font=font.Font(size=12))
    last_review_grade_label = ttk.Label(review_frame, text="", font=font.Font(size=12))
    review_counter_label = ttk.Label(review_frame, text="", font=font.Font(size=12))
    last_review_text_label.grid(column=0, row=0, columnspan=1)
    review_counter_label.grid(column=1, row=0, columnspan=1)
    item_descr_label = ttk.Label(review_frame, text="", font=font.Font(size=15))
    item_descr_label.grid(column=0, row=2, columnspan=2)
    text_label = ttk.Label(review_frame, text="", font=font.Font(size=25))
    text_label.grid(column=0, row=3, columnspan=2)
    readingLabel = ttk.Label(review_frame, text="", font=font.Font(size=20), wraplength=500, foreground='#00f')
    readingLabel.grid(column=0, row=4, columnspan=2)
    meaingLabel = ttk.Label(review_frame, text="", font=font.Font(size=15), wraplength=500, foreground='#f80')
    meaingLabel.grid(column=0, row=5, columnspan=2)
    bad_button = ttk.Button(review_frame, text="Bad (1)", command=lambda: review_bad(item))
    good_button = ttk.Button(review_frame, text="Good (2)", command=lambda: review_good(item))
    bad_button.grid(column=0, row=1)
    good_button.grid(column=1, row=1)
    answer_button = ttk.Button(review_frame, text="Answer", command=lambda: show_answer(item))
    answer_button.grid(column=0, row=1, columnspan=2)
    root.bind('<space>', lambda x: show_answer(item))
    root.bind('<Return>', lambda x: show_answer(item))
    review_frame.grid_remove()
    root.mainloop()
