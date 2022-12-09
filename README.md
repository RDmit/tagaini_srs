# Tagaini SRS
Flashcard training app based on Spaced Repetition System for Tagaini Jisho (www.tagaini.net).

# About
Tagaini SRS is intended for people who use Tagaini Jisho but prefer to train words and kanji using Spaced Repetition System (like Anki). Tagaini SRS automatically takes your study list from Tagaini Jisho and exports your progress back to Tagaini Jisho as entry's score so you can see your progress there.

# Usage
Tagaini SRS is written in Python. It requires at least Python 3.8.
You will need to put the correct paths to databases into config.json.

### On Windows:
Install Python at least 3.8.
Run tagaini_srs_gui.py

### On Linux:
Install Python at least 3.8. Install TkInter if you want to use the GUI version.
Run tagaini_srs.py for the console interface version. 
Run tagaini_srs_gui.py for the GUI version.

Console version takes the following arguments:

--pause, -p to pause before exiting

--no-color, -nc to turn off colors for output

--worst, -w to display your worst entries

--stats, -s to show SRS statistics

--hours, -h [X] to show how many reviews will be ready in X hours

# Tools
tagaini_srs.py - command line version

tagaini_srs_gui.py - GUI version

tagaini_srs_edit.py is a command line tool for editing your entries.

tagaini_srs_histogram.py shows how many reviews will be due in a form of a histogram.

tagaini_srs_missing.py shows which entries from the SRS database are missing from your Tagaini Jisho database.
