import curses
import random
import signal

from paragraph_exercise import run_paragraph_exercise


def build_numeric_exercise(num_lines=3, num_words_per_line=4, num_digits=4):
    exercise_txt = ''
    for _ in range(num_lines):
        for _ in range(num_words_per_line):
            exercise_txt += f'{random.randint(0, 10**num_digits):0{num_digits}} '
        exercise_txt = exercise_txt[:-1]
        exercise_txt += '\n'
    return exercise_txt


def build_file_exercise():
    with open('exercise.txt', 'r') as f:
        return f.read()


def main(win):
    while True:
        # exercise_txt = build_numeric_exercise()
        exercise_txt = build_file_exercise()
        for paragraph in exercise_txt.split('\n'):
            if len(paragraph) == 0:
                continue
            run_paragraph_exercise(win, paragraph)
        win.clear()
        win.addstr('Congratulations! Your exercise is done.\nPress any key to restart...')
        win.get_wch()



signal.signal(signal.SIGINT, lambda signum, frame: exit(0))
curses.wrapper(main)
