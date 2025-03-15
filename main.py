import argparse
import curses
import textwrap
import time
import unicodedata

from paragraph_state import ParagraphState
from plugins import get_plugins


# From https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def update_stats_heading(win, stats):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    HEADER_COLORS = curses.color_pair(1)
    
    initial_position = list(win.getyx())
    _, win_width = win.getmaxyx()

    # Calculate spacing according to the win size
    # Labels, values and minimum spacing takes 5+9 + 10+11 + 10+4 = 49 characters
    spacing_between_fields = (win_width - 49) // 2
    wpm_val_ljustify_len = 9 + spacing_between_fields
    accuracy_val_ljustify_len = 11 + spacing_between_fields
    progress_val_ljustify_len = 4

    # Add labels to the top
    win.addstr(0, 0, 'WPM:'.ljust(5 + wpm_val_ljustify_len) + \
        'Accuracy:'.ljust(10 + accuracy_val_ljustify_len) + \
        'Progress:', HEADER_COLORS)

    # More spacing calculation, specific for values
    wpm_start_x = 5
    accuracy_starts_x = wpm_start_x + wpm_val_ljustify_len + 10
    progress_starts_x = accuracy_starts_x + accuracy_val_ljustify_len + 10

    # Add values to the side of the labels
    win.move(0, 0)
    win.addstr(0, wpm_start_x, f'{stats["net_wpm"]:.0f} ({stats["gross_wpm"]:.0f})'.ljust(wpm_val_ljustify_len))
    win.addstr(0, accuracy_starts_x, f'{stats["result_accuracy"]:.0f}% ({stats["real_accuracy"]:.0f}%)'.ljust(accuracy_val_ljustify_len))
    win.addstr(0, progress_starts_x, f'{stats["progress_pct"]:.0f}%'.ljust(progress_val_ljustify_len))

    win.move(*initial_position)


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


def sanitize_text(user_text):
    # Unicode combining characters take space on the string, but not on the
    # screen, messing up UI calculations. The line is then normalized to NFKC.
    # This way we have no combining characters, and have the resulting combined
    # characters be the canonical equivalent form, most probably the one the
    # keyboard/terminal/OS will deliver (untested assumption but makes sense :p).
    # EDIT: Already used the app with different text pulled from different
    # places of the internet and has not given any problems so far :)
    normalized_text = unicodedata.normalize('NFKC', user_text)

    # Replace characters that are not easily typeable
    # TODO: Make this an option? There are weird ways to type these...
    return normalized_text.translate(str.maketrans("–‘’“”", "-''\"\"")).replace("…", "...")


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

    exercise_txt = sanitize_text(exercise_txt)

    # Draw the initial state of the screen
    win.clear()
    state = ParagraphState(exercise_txt)
    update_stats_heading(win, state.stats())  # Will be all zeroes

    # Get window dimensions
    max_y, max_x = win.getmaxyx()
    max_x -= 1  # Adjust for border

    # Split text into lines and wrap by words
    lines = exercise_txt.split('\n')
    wrapped_lines = []
    for line in lines:
        wrapped_lines.extend(textwrap.wrap(line, width=max_x))

    # Display the wrapped text
    for i, line in enumerate(wrapped_lines):
        win.addstr(i + 2, 0, line, COLORS_BY_STATE[ParagraphState.CHAR_PENDING])
    win.move(2, 0)

    # Loop to handle key-presses
    while not state.is_exercise_done():
        key = win.get_wch()

        # Handle backspace (POSIX, Windows)
        if key in ('\x7f', '\x08'):
            try:
                deleted_char = state.register_backspace()
            except ParagraphState.AlreadyAtBeggining:
                continue

            last_position = list(win.getyx())

            # Handle line wrapping going backwards
            if last_position[1] == 0:
                last_position[0] -= 1
                last_position[1] = len(lines[last_position[0] - 2])
            else:
                last_position[1] -= 1

            win.addstr(*last_position, deleted_char, COLORS_BY_STATE[ParagraphState.CHAR_PENDING])
            win.move(*last_position)

        # Handle regular printable characters and newlines (enter key)
        elif (type(key) == str and key.isprintable()) or key == '\n':
            char_state = state.register_char(key)
            if key == '\n' and char_state == ParagraphState.CHAR_WRONG:
                key = '↵'
            win.addstr(key, COLORS_BY_STATE[char_state])

        # Other key-presses produce ints or non-printable strings
        else:
            continue

        update_stats_heading(win, state.stats())

    # Exercise done. Move below text to display stats
    current_position = list(win.getyx())
    win.move(current_position[0] + 2, 0)

    # Display stats
    stats = state.stats()
    if stats['all_correct']:
        win.addstr('All correct!')
    else:
        win.addstr('Errors have been made...')
    win.addstr(f'\n\n{render_stats_as_list(stats)}\n')

    return stats


def curses_app(win, selected_plugin, skip):
    stats_per_paragraph = []
    try:

        # Pull paragraphs (exercises content) from the selected plugin. Then
        # for each of them run the exercise and store the resulting stats
        try:
            for paragraph in selected_plugin.paragraph_generator():
                paragraph = paragraph.strip()
                if len(paragraph) == 0:
                    continue
                if skip > 0:
                    skip -= 1
                    continue
                stats = run_paragraph_exercise(win, paragraph)
                stats_per_paragraph.append(stats)
                win.addstr('Press <ENTER> to continue...')
                win.refresh()
                win.getstr()
        except KeyboardInterrupt:
            curses.flushinp()

        # After finishing or hitting Ctrl+C, show the aggregate stats and exit

        win.clear()
        win.addstr('Congratulations! Your exercise is done.\n\n')

        aggregate_stats = ParagraphState.aggregate_multiple_stats(stats_per_paragraph)
        win.addstr(render_aggregate_stats_as_list(aggregate_stats))
        win.refresh()

        time.sleep(1)
        curses.flushinp()
        win.addstr('\nPress <ENTER> to continue...')
        win.getstr()

    except KeyboardInterrupt:
        pass
    finally:
        return aggregate_stats

    
def main():

    # Main CLI argument parser setup
    parser = argparse.ArgumentParser(prog='typetrain', description='Practice some typing with the TypeTrain!')
    parser.add_argument('--skip', type=int, default=0, help='skip the first N paragraphs')

    # CLI argument sub-parsers setup for plugins
    subparsers = parser.add_subparsers(required=True, title='exercise types', dest='exercise_type') # TODO restrict, using `choices`?
    for plugin in get_plugins():
        plugin_parser = subparsers.add_parser(plugin.one_word_name, help=plugin.description)
        plugin.configure_argparse_subparser(plugin_parser)
        plugin_parser.set_defaults(plugin=plugin)

    # Run argument parser
    args = parser.parse_args()
    selected_plugin = args.plugin(args)

    # Run the app
    aggregate_stats = curses.wrapper(curses_app, selected_plugin, skip=args.skip)

    # Report last paragraph written before exit (outside curses) to easily
    # continue the exercise in a future run
    if aggregate_stats and aggregate_stats["total_paragraphs"] > 0:
        last_written_paragraph_index = aggregate_stats["total_paragraphs"] + args.skip
        print(f'Last paragraph written was the {ordinal(last_written_paragraph_index)}.\n')
    else:
        print('No paragraphs written.\n')


if __name__ == '__main__':
    main()
