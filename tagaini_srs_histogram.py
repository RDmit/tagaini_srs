#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk
from tkinter import font
import tagaini_srs

size_x = 1000
bar_count = 100
bar_max_height = 200
offset_x = 30

def get_bars(cursor):
    bars = []
    total = 0
    query = 'SELECT count(*) FROM srsentryset WHERE NextAnswerDate < {0}'
    for time in range(bar_count + 1):
        query_result = cursor.execute(query.format(tagaini_srs.get_ticks(time))).fetchone()[0]
        new_items = int(query_result) - total
        bars.append(new_items)
        total += new_items
    return bars

def get_bars_additive(cursor):
    bars = []
    total = 0
    query = 'SELECT count(*) FROM srsentryset WHERE NextAnswerDate < {0}'
    for time in range(bar_count + 1):
        query_result = cursor.execute(query.format(tagaini_srs.get_ticks(time))).fetchone()[0]
        bars.append(int(query_result))
    return bars
        

if __name__ == '__main__':
    cursor = tagaini_srs.open_db()
    bars = get_bars(cursor)
    bar_width = size_x / bar_count
    root = Tk()
    root.title('Tagaini SRS')
    root.geometry(f"{size_x+offset_x*2}x{bar_max_height+40}" )
    canvas = Canvas(root)
    canvas.pack(fill=BOTH, expand=1)
    maximum_value = max(bars)
    scaling = bar_max_height / maximum_value
    canvas.create_text(offset_x + 9*bar_width, 30 + bar_max_height, anchor=S, text="8h")
    canvas.create_text(offset_x + 25*bar_width, 30 + bar_max_height, anchor=S, text="1d")
    canvas.create_text(offset_x + (24*2+1)*bar_width, 30 + bar_max_height, anchor=S, text="2d")
    canvas.create_text(offset_x + (24*3+1)*bar_width, 30 + bar_max_height, anchor=S, text="3d")
    canvas.create_text(offset_x + (24*4+1)*bar_width, 30 + bar_max_height, anchor=S, text="4d")
    canvas.create_text(offset_x - 5, 10, anchor=E, text=f"{maximum_value}")
    canvas.create_text(offset_x + bar_count*bar_width + 5, 10, anchor=W, text=f"{maximum_value}")    
    canvas.create_text(offset_x - 5, 10 + bar_max_height - maximum_value*3//4*scaling, anchor=E, text=f"{maximum_value*3//4}")
    canvas.create_text(offset_x + bar_count*bar_width + 5, 10 + bar_max_height - maximum_value*3//4*scaling, anchor=W, text=f"{maximum_value*3//4}")
    canvas.create_text(offset_x - 5, 10 + bar_max_height - maximum_value//2*scaling, anchor=E, text=f"{maximum_value//2}")
    canvas.create_text(offset_x + bar_count*bar_width + 5, 10 + bar_max_height - maximum_value//2*scaling, anchor=W, text=f"{maximum_value//2}")
    canvas.create_text(offset_x - 5, 10 + bar_max_height - maximum_value//4*scaling, anchor=E, text=f"{maximum_value//4}")
    canvas.create_text(offset_x + bar_count*bar_width + 5, 10 + bar_max_height - maximum_value//4*scaling, anchor=W, text=f"{maximum_value//4}")
    canvas.create_line(offset_x, 10,
                       offset_x + bar_count*bar_width, 10, dash=(4, 2))
    canvas.create_line(offset_x, 10 + bar_max_height - maximum_value*3//4*scaling,
                       offset_x + bar_count*bar_width, 10 + bar_max_height - maximum_value*3//4*scaling, dash=(4, 2))
    canvas.create_line(offset_x, 10 + bar_max_height - maximum_value//2*scaling,
                       offset_x + bar_count*bar_width, 10 + bar_max_height - maximum_value//2*scaling, dash=(4, 2))
    canvas.create_line(offset_x, 10 + bar_max_height - maximum_value//4*scaling,
                       offset_x + bar_count*bar_width, 10 + bar_max_height - maximum_value//4*scaling, dash=(4, 2))
    for i in range(bar_count):
        canvas.create_rectangle(offset_x + i * bar_width, 10 + bar_max_height,
                                offset_x + (i+1) * bar_width, 10 + bar_max_height - bars[i]*scaling, fill='red')
    
    root.mainloop()
