import curses
import random
import signal
import time


def build_exercise():
    return f'type this: {random.randint(0, 1000)}'


def do_exercise(win, exercise_builder):
    exercise_txt = exercise_builder()
    exercise_txt_len = len(exercise_txt)

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    COLOR_PENDING_TEXT = curses.color_pair(1)
    COLOR_CORRECT_TEXT = curses.color_pair(2)
    COLOR_WRONG_TEXT = curses.color_pair(3)

    win.clear()
    win_height, win_width = win.getmaxyx()

    # TODO: wrap text
    win.addstr(exercise_txt, COLOR_PENDING_TEXT)
    win.move(0,0)

    user_input = ''
    start_time = None

    while True:
        char = win.get_wch()
        if type(char) == int: # keypress not mapped to a character
            continue
        if char == '\n':
            break

        if start_time is None:
            start_time = time.time()

        if char == '\x7f': # backspace
            if len(user_input) == 0:
                continue
            current_position = list(win.getyx())
            last_position = current_position
            last_position[1] -= 1
            user_input = user_input[:-1]
            win.addstr(*last_position, exercise_txt[len(user_input)], COLOR_PENDING_TEXT)
            win.move(*current_position)
        else:
            if char == exercise_txt[len(user_input)]:
                win.addstr(char, COLOR_CORRECT_TEXT)
            else:
                win.addstr(char, COLOR_WRONG_TEXT)
            user_input += char

        if exercise_txt_len == len(user_input):
            break

    end_time = time.time()
    total_time = end_time - start_time if start_time else 0

    # win.addstr('\n')
    # win.addstr(user_input)
    # win.addstr(f'\n{len(user_input)}')

    if (user_input == exercise_txt):
        win.addstr('\nCorrect!')
    else:
        win.addstr('\nIncorrect!')

    win.addstr(f'\nTime: {total_time:.2f} seconds')
    win.refresh()
    win.addstr('\nPress <ENTER> to continue...')
    win.refresh()
    win.getstr()
   

def main(win):
    while True:
        do_exercise(win, build_exercise)


signal.signal(signal.SIGINT, lambda signum, frame: exit(0))
curses.wrapper(main)
