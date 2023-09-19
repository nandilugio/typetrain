import curses
import random
import signal

from paragraph_state import ParagraphState


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


def run_paragraph_exercise(win, exercise_txt):
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)

    COLORS_BY_STATE = {
        ParagraphState.CHAR_PENDING: curses.color_pair(1),
        ParagraphState.CHAR_CORRECT: curses.color_pair(2),
        ParagraphState.CHAR_AMENDED: curses.color_pair(3),
        ParagraphState.CHAR_WRONG: curses.color_pair(4),
    }

    # Draw the initial state of the screen
    # TODO: Wrap text by words (not by characters)
    win.clear()
    win.addstr(exercise_txt, COLORS_BY_STATE[ParagraphState.CHAR_PENDING])
    win.move(0,0)

    state = ParagraphState(exercise_txt)

    # Loop to handle keypresses
    while True:
        char = win.get_wch()

        # Bail out if needed
        if type(char) == int: # Keypress not mapped to a character
            continue
        if char == '\n':
            continue

        # Handle keypress
        if char == '\x7f': # Backspace
            try:
                deleted_char = state.backspace_pressed()
            except ParagraphState.CannotGoBack:
                continue

            # Handle the case where the cursor is at the beginning of a line
            last_position = list(win.getyx())
            if last_position[1] == 0:
                last_position[0] -= 1
                last_position[1] = win.getmaxyx()[1] - 1
            else:
                last_position[1] -= 1

            win.addstr(*last_position, deleted_char, COLORS_BY_STATE[ParagraphState.CHAR_PENDING])
            win.move(*last_position)

        else: # Characters
            char_state = state.char_typed(char)
            win.addstr(char, COLORS_BY_STATE[char_state]) 

        # TODO: Handle arrow keys or other special keys

        if state.is_exercise_done():
            break

    # Exercise done. Move below text to display stats
    current_position = list(win.getyx())
    win.move(current_position[0] + 2, 0)

    stats = state.get_stats()

    if (stats['all_correct'] ):
        win.addstr('All correct!')
    else:
        win.addstr('Errors have been made...')

    win.addstr('\n')
    win.addstr(f'\nWPM: {stats["net_wpm"]:.2f}, {stats["gross_wpm"]:.2f} gross')
    win.addstr(f'\nAccuracy: {stats["result_accuracy"]:.2f}%, {stats["real_accuracy"]:.2f}% real')
    win.addstr(f'\nErrors: {stats["error_count"]}, {stats["uncorrected_error_count"]} not corrected')
    win.addstr(f'\nExcercise Length: {stats["length_txt"]} chars, {stats["length_std_words"]:.2f} "standard" words')
    win.addstr(f'\nTime: {stats["total_time_s"]:.2f} s')
    win.addstr('\n')
    
    win.refresh()
    win.addstr('\nPress <ENTER> to continue...')
    win.refresh()
    win.getstr()


# TODO: Wrap in catch-all exception handler
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
