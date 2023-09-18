import curses
import time


def _last_position(win):
    current_position = list(win.getyx())
    last_position = current_position.copy()
    last_position[1] -= 1
    return last_position


def _revert_last_char(win, original_char, color_pair):
    last_position = _last_position(win)
    win.addstr(*last_position, original_char, color_pair)
    win.move(*last_position)


def run_paragraph_exercise(win, exercise_txt):
    exercise_txt_len = len(exercise_txt)

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    COLOR_PENDING_TEXT = curses.color_pair(1)
    COLOR_CORRECT_TEXT = curses.color_pair(2)
    COLOR_WRONG_TEXT = curses.color_pair(3)

    win.clear()
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
            user_input = user_input[:-1]
            _revert_last_char(win, exercise_txt[len(user_input)], COLOR_PENDING_TEXT)
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

    # For debugging
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
   