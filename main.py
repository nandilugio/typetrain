import curses
import random
import signal

from paragraph_exercise import run_paragraph_exercise


def build_exercise():
    return f'type this: {random.randint(0, 1000)}'


def main(win):
    while True:
        exercise_txt = build_exercise()
        run_paragraph_exercise(win, exercise_txt)


signal.signal(signal.SIGINT, lambda signum, frame: exit(0))
curses.wrapper(main)
