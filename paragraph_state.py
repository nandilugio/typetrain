from functools import reduce
import time


class ParagraphState:

    class AlreadyAtBeggining(RuntimeError): pass

    CHAR_PENDING = 'p'
    CHAR_CORRECT = 'c'
    CHAR_AMENDED = 'a'
    CHAR_WRONG = 'w'


    def __init__(self, exercise_txt):
        self.exercise_txt = exercise_txt

        self.length_txt = len(self.exercise_txt)

        self.char_state_map = list(self.CHAR_PENDING * self.length_txt)
        self.current_char_idx = 0
        self.chars_touched = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None


    def register_char(self, char):
        # Start the timer if it's the first character
        if self.start_time is None:
            self.start_time = time.time()

        # Derive the new state of the character (and count errors)
        resulting_char_state = self.CHAR_CORRECT
        if char == self.exercise_txt[self.current_char_idx]:
            if self.char_state_map[self.current_char_idx] not in (self.CHAR_PENDING, self.CHAR_CORRECT):
                resulting_char_state = self.CHAR_AMENDED
        else:
            resulting_char_state = self.CHAR_WRONG
            self.error_count += 1

        # Update the state of the character
        self.char_state_map[self.current_char_idx] = resulting_char_state
        self.current_char_idx += 1
        self.chars_touched = max(self.chars_touched, self.current_char_idx)

        # Stop the timer if it's the last character
        if self.current_char_idx == self.length_txt:
            self.end_time = time.time()

        return resulting_char_state


    def register_backspace(self):
        if self.current_char_idx == 0:
            raise self.AlreadyAtBeggining()

        self.current_char_idx -= 1
        deleted_char = self.exercise_txt[self.current_char_idx]

        return deleted_char


    def is_exercise_done(self):
        return self.end_time is not None


    # TODO: Decouple stats from ParagraphState? it'd make sense to leave this
    #   module only dealing with the character states and leave any timing
    #   for a separate stats module. It can use the ParagraphState to ask
    #   for length, error count, etc.


    # Formulas from https://www.speedtypingonline.com/typing-equations
    def stats(self):
        end_time = self.end_time or time.time()
        length_std_words = self.chars_touched / 5
        time_s = end_time - self.start_time if self.start_time else 0
        total_time_m = time_s / 60
        uncorrected_error_count = len([x for x in self.char_state_map if x == self.CHAR_WRONG])

        # HACK: 0.2 is the word-length of a character. This fixes the issue of a single character being counted as infinite WPM
        gross_wpm = (length_std_words - 0.2) / total_time_m if total_time_m > 0 else 0
        # Net WPM could be negative since an error is penalized as one whole wrong word. Constrained since it wouldn't make much sense
        net_wpm = max(0, gross_wpm - (uncorrected_error_count / total_time_m)) if total_time_m > 0 else 0
        result_accuracy = (self.chars_touched - uncorrected_error_count) * 100 / self.chars_touched if self.chars_touched > 0 else 0
        # Real accuracy could be negative if there are many errors on the same characters. Constrained since it wouldn't make much sense
        real_accuracy = max(0, (self.chars_touched - self.error_count) * 100 / self.chars_touched) if self.chars_touched > 0 else 0

        return {
            'all_correct': uncorrected_error_count == 0,
            'progress_pct': self.chars_touched * 100 / self.length_txt,
            'length_txt': self.length_txt,
            'length_std_words': length_std_words,
            'time_s': time_s,
            'error_count': self.error_count,
            'uncorrected_error_count': uncorrected_error_count,
            'gross_wpm': gross_wpm,
            'net_wpm': net_wpm,
            'result_accuracy': result_accuracy,
            'real_accuracy': real_accuracy,
        }


    # Formulas from https://www.speedtypingonline.com/typing-equations
    @staticmethod
    def aggregate_multiple_stats(stats_list):
        def aggregate(acc, stats):
            acc['total_paragraphs'] += 1
            if stats['all_correct']:
                acc['correct_paragraphs'] += 1
            acc['correct_paragraphs_pct'] = acc['correct_paragraphs'] * 100 / acc['total_paragraphs']

            acc['total_length_txt'] += stats['length_txt']
            acc['total_length_std_words'] = acc['total_length_txt'] / 5
            acc['time_s'] += stats['time_s']
            acc['time_m'] = acc['time_s'] / 60
            acc['error_count'] += stats['error_count']
            acc['uncorrected_error_count'] += stats['uncorrected_error_count']

            # HACK: 0.2 is the word-length of a character. This fixes the issue of a single character being counted as infinite WPM
            acc['gross_wpm'] = (acc['total_length_std_words'] - 0.2) / acc['time_m'] if acc['time_m'] > 0 else 0
            # Net WPM could be negative since an error is penalized as one whole wrong word. Constrained since it wouldn't make much sense
            acc['net_wpm'] = max(0, acc['gross_wpm'] - (acc['uncorrected_error_count'] / acc['time_m'])) if acc['time_m'] > 0 else 0
            acc['result_accuracy'] = (acc['total_length_txt'] - acc['uncorrected_error_count']) * 100 / acc['total_length_txt'] if acc['total_length_txt'] > 0 else 0
            # Real accuracy could be negative if there are many errors on the same characters. Constrained since it wouldn't make much sense
            acc['real_accuracy'] = max(0, (acc['total_length_txt'] - acc['error_count']) * 100 / acc['total_length_txt']) if acc['total_length_txt'] > 0 else 0

            return acc

        return reduce(aggregate, stats_list, {
            'total_paragraphs': 0,
            'correct_paragraphs': 0,
            'correct_paragraphs_pct': 0,
            'total_length_txt': 0,
            'total_length_std_words': 0,
            'time_s': 0,
            'time_m': 0,
            'error_count': 0,
            'uncorrected_error_count': 0,
            'gross_wpm': 0,
            'net_wpm': 0,
            'result_accuracy': 0,
            'real_accuracy': 0,
        })
