This directory contains utilities that help instructors teach
with the book _Problem Solving with Python: Using Computational
Thinking in Everyday Life_ by Michael D. Smith (MIT Press).

`grab32.py`: Makes it easy for students to grab repo files. It
handles the chapter code and programming problem sets. It permits
the re-grabbing of a clean copy of a repo files without overwriting
the current working copy. It also handles the reconfiguration of
the CS50 codespace for CS32. This program exists because cs50.dev
doesn't allow students to run `git clone`. It should be put at
the top-level directory in a student's Github Codespace.

`strip_notes.py`: The classnotes available to instructors that adopt
the textbook come with instructor notes embedded in them (i.e., they
exist as a "notes" `slide_type` in the `slideshow` dictionary in a
cell's `metadata`). Given an `ipynb` file with classnotes, this script
creates a new `ipynb` file stripped of any "notes" cells, which you
can distribute to your students.
