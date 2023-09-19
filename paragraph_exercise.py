import curses
import time


def _last_position(win):
    last_position = list(win.getyx())
    if last_position[1] == 0:
        last_position[0] -= 1
        last_position[1] = win.getmaxyx()[1] - 1
    else:
        last_position[1] -= 1
    return tuple(last_position)


def run_paragraph_exercise(win, exercise_txt):
    CHAR_PENDING = 'p'
    CHAR_CORRECT = 'c'
    CHAR_AMENDED = 'a'
    CHAR_WRONG = 'w'

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)
    COLOR_PENDING_TEXT = curses.color_pair(1)
    COLOR_CORRECT_TEXT = curses.color_pair(2)
    COLOR_AMENDED_TEXT = curses.color_pair(3)
    COLOR_WRONG_TEXT = curses.color_pair(4)

    win.clear()
    win.addstr(exercise_txt, COLOR_PENDING_TEXT)
    win.move(0,0)

    exercise_txt_len = len(exercise_txt)
    char_state_map = list(CHAR_PENDING * exercise_txt_len)
    current_char_idx = 0
    error_count = 0
    start_time = None

    while True:
        char = win.get_wch()
        if type(char) == int: # keypress not mapped to a character
            continue
        if char == '\n':
            continue

        if start_time is None:
            start_time = time.time()

        if char == '\x7f': # backspace
            if current_char_idx == 0:
                continue
            current_char_idx -= 1
            last_position = _last_position(win)
            win.addstr(*last_position, exercise_txt[current_char_idx], COLOR_PENDING_TEXT)
            win.move(*last_position)
        else:
            if char == exercise_txt[current_char_idx]:
                if char_state_map[current_char_idx] in (CHAR_PENDING, CHAR_CORRECT):
                    char_state_map[current_char_idx] = CHAR_CORRECT
                    win.addstr(char, COLOR_CORRECT_TEXT)
                else:
                    char_state_map[current_char_idx] = CHAR_AMENDED
                    win.addstr(char, COLOR_AMENDED_TEXT)
            else:
                error_count += 1
                char_state_map[current_char_idx] = CHAR_WRONG
                win.addstr(char, COLOR_WRONG_TEXT)
            current_char_idx += 1

        if exercise_txt_len == current_char_idx:
            break

    end_time = time.time()
    
    std_words = exercise_txt_len / 5

    total_time_s = end_time - start_time if start_time else 0
    total_time_m = total_time_s / 60

    uncorrected_error_count = len([x for x in char_state_map if x == CHAR_WRONG])

    gross_wpm = std_words / total_time_m
    net_wpm = gross_wpm - (uncorrected_error_count / total_time_m)

    result_accuracy = (exercise_txt_len - uncorrected_error_count) * 100 / exercise_txt_len
    real_accuracy = (exercise_txt_len - error_count) * 100 / exercise_txt_len

    current_position = list(win.getyx())
    win.move(current_position[0] + 2, 0)

    if (uncorrected_error_count == 0):
        win.addstr('All correct!')
    else:
        win.addstr('Errors have been made...')

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
   