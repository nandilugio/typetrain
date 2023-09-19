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

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    COLOR_PENDING_TEXT = curses.color_pair(1)
    COLOR_CORRECT_TEXT = curses.color_pair(2)
    COLOR_WRONG_TEXT = curses.color_pair(3)

    win.clear()
    win.addstr(exercise_txt, COLOR_PENDING_TEXT)
    win.move(0,0)

    user_input = ''
    start_time = None
    error_count = 0

    while True:
        char = win.get_wch()
        if type(char) == int: # keypress not mapped to a character
            continue
        if char == '\n':
            continue

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
                error_count += 1
            user_input += char

        if exercise_txt_len == len(user_input):
            break

    end_time = time.time()
    
    total_time_s = end_time - start_time if start_time else 0
    total_time_m = total_time_s / 60

    uncorrected_error_count = sum(1 for a, b in zip(user_input, exercise_txt) if a != b)

    std_words = exercise_txt_len / 5

    gross_wpm = std_words / total_time_m
    net_wpm = gross_wpm - (uncorrected_error_count / total_time_m)

    result_accuracy = (exercise_txt_len - uncorrected_error_count) * 100 / exercise_txt_len
    real_accuracy = (exercise_txt_len - error_count) * 100 / exercise_txt_len

    # For debugging
    # win.addstr('\n')
    # win.addstr(user_input)
    # win.addstr(f'\n{len(user_input)}')

    current_position = list(win.getyx())
    win.move(current_position[0] + 2, 0)

    if (user_input == exercise_txt):
        win.addstr('All correct!')
    else:
        win.addstr(f'Some errors have been made.')

    win.addstr('\n')
    win.addstr(f'\nWPM: {net_wpm:.2f}, {gross_wpm:.2f} gross')
    win.addstr(f'\nAccuracy: {result_accuracy:.2f}%, {real_accuracy:.2f}% real')
    win.addstr(f'\nErrors: {error_count}, {uncorrected_error_count} not corrected')
    win.addstr(f'\nExcercise Length: {exercise_txt_len} chars, {std_words:.2f} "standard" words')
    win.addstr(f'\nTime: {total_time_s:.2f} s')
    win.addstr('\n')
    
    win.refresh()
    win.addstr('\nPress <ENTER> to continue...')
    win.refresh()
    win.getstr()
   