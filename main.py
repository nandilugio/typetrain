import argparse
import curses

from paragraph_state import ParagraphState
from plugins import get_plugins


def update_stats_heading(win, stats):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    HEADER_COLORS = curses.color_pair(1)
    
    current_position = list(win.getyx())
    _, win_width = win.getmaxyx()

    # Labels, values and minimum spacing takes 5+9 + 10+11 + 10+4 = 49 characters
    spacing_between_fields = (win_width - 49) // 2
    wpm_val_ljustify_len = 9 + spacing_between_fields
    accuracy_val_ljustify_len = 11 + spacing_between_fields
    progress_val_ljustify_len = 4

    win.addstr(0, 0, 'WPM:'.ljust(5 + wpm_val_ljustify_len) + \
        'Accuracy:'.ljust(10 + accuracy_val_ljustify_len) + \
        'Progress:', HEADER_COLORS)

    wpm_start_x = 5
    accuracy_starts_x = wpm_start_x + wpm_val_ljustify_len + 10
    progress_starts_x = accuracy_starts_x + accuracy_val_ljustify_len + 10

    win.move(0, 0)
    win.addstr(0, wpm_start_x, f'{stats["net_wpm"]:.0f} ({stats["gross_wpm"]:.0f})'.ljust(wpm_val_ljustify_len))
    win.addstr(0, accuracy_starts_x, f'{stats["result_accuracy"]:.0f}% ({stats["real_accuracy"]:.0f}%)'.ljust(accuracy_val_ljustify_len))
    win.addstr(0, progress_starts_x, f'{stats["progress_pct"]:.0f}%'.ljust(progress_val_ljustify_len))
    win.move(*current_position)


def render_stats_as_list(stats):
    return (
        f'WPM: {stats["net_wpm"]:.2f}, {stats["gross_wpm"]:.2f} gross\n'
        f'Accuracy: {stats["result_accuracy"]:.2f}%, {stats["real_accuracy"]:.2f}% real\n'
        f'Errors: {stats["error_count"]}, {stats["uncorrected_error_count"]} not corrected\n'
        f'Excercise Length: {stats["length_txt"]} chars, {stats["length_std_words"]:.2f} "standard" words\n'
        f'Time: {stats["time_s"]:.2f} s\n'
    )


def render_aggregate_stats_as_list(agg_stats):
    return (
        f'Average WPM: {agg_stats["net_wpm"]:.2f} ({agg_stats["gross_wpm"]:.2f} gross)\n'
        f'Average accuracy: {agg_stats["result_accuracy"]:.2f}% ({agg_stats["real_accuracy"]:.2f}% real)\n'
        f'Errors: {agg_stats["error_count"]} ({agg_stats["uncorrected_error_count"]} not corrected)\n'
        f'Total exercises length: {agg_stats["total_length_txt"]} chars, {agg_stats["total_length_std_words"]:.2f} "standard" words\n'
        f'Total paragraphs: {agg_stats["total_paragraphs"]}\n'
        f'Correct paragraphs: {agg_stats["correct_paragraphs"]} ({agg_stats["correct_paragraphs_pct"]:.2f}%)\n'
        f'Total typing time: {agg_stats["time_m"]:.2f} minutes\n'
    )


def run_paragraph_exercise(win, exercise_txt):
    curses.init_pair(10, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_RED)

    COLORS_BY_STATE = {
        ParagraphState.CHAR_PENDING: curses.color_pair(10),
        ParagraphState.CHAR_CORRECT: curses.color_pair(11),
        ParagraphState.CHAR_AMENDED: curses.color_pair(12),
        ParagraphState.CHAR_WRONG: curses.color_pair(13),
    }

    # Draw the initial state of the screen
    # TODO: Wrap text by words (not by characters)
    win.clear()
    state = ParagraphState(exercise_txt)
    update_stats_heading(win, state.stats())  # Will be all zeroes
    win.addstr(2,0, exercise_txt, COLORS_BY_STATE[ParagraphState.CHAR_PENDING])
    win.move(2,0)

    # Loop to handle keypresses
    while True:
        char = win.get_wch()

        # Bail out if needed
        if type(char) == int: # Keypress not mapped to a character
            continue
        if char == '\n':
            continue

        # Handle keypress
        if char in ('\x7f', '\b', 'KEY_BACKSPACE'): # Backspace TODO: are the last two needed? maybe for other OSes?
            try:
                deleted_char = state.register_backspace()
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

        # TODO: How do we make inverted question/exclamation marks, euro signs and other chars work? is it my keyboard layout?

        else: # Characters
            char_state = state.register_char(char)
            win.addstr(char, COLORS_BY_STATE[char_state]) 

        # TODO: Handle arrow keys or other special keys

        update_stats_heading(win, state.stats())

        if state.is_exercise_done():
            break

    # Exercise done. Move below text to display stats
    current_position = list(win.getyx())
    win.move(current_position[0] + 2, 0)

    stats = state.stats()
    if (stats['all_correct'] ):
        win.addstr('All correct!')
    else:
        win.addstr('Errors have been made...')
    win.addstr(f'\n\n{render_stats_as_list(stats)}\n')
    win.addstr('Press <ENTER> to continue...')
    win.refresh()
    win.getstr()

    return stats


def curses_app(win, selected_plugin):
    stats_per_paragraph = []
    try:
        for paragraph in selected_plugin.paragraph_generator():
            if len(paragraph) == 0:
                continue
            stats = run_paragraph_exercise(win, paragraph)
            stats_per_paragraph.append(stats)
    except KeyboardInterrupt:
        curses.flushinp()

    win.clear()
    win.addstr('Congratulations! Your exercise is done.\n\n')

    aggregate_stats = ParagraphState.aggregate_multiple_stats(stats_per_paragraph)
    win.addstr(render_aggregate_stats_as_list(aggregate_stats))

    win.addstr('\nPress <ENTER> to continue...')
    win.refresh()
    win.getstr()

    
def main():
    parser = argparse.ArgumentParser(prog='typetrain', description='Practice some typing with the TypeTrain!')
    subparsers = parser.add_subparsers(required=True, title='exercise types', dest='exercise_type') # TODO restrict, using `choices`?
    for plugin in get_plugins():
        plugin_parser = subparsers.add_parser(plugin.one_word_name, help=plugin.description)
        plugin.configure_argparse_subparser(plugin_parser)
        plugin_parser.set_defaults(plugin=plugin)
    args = parser.parse_args()

    selected_plugin = args.plugin(args)

    curses.wrapper(curses_app, selected_plugin)


if __name__ == '__main__':
    main()
