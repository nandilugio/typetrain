import time


class ParagraphState:
    
    class CannotGoBack(RuntimeError): pass

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


    def char_typed(self, char):
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


    def backspace_pressed(self):
        if self.current_char_idx == 0:
            raise self.CannotGoBack()

        self.current_char_idx -= 1
        deleted_char = self.exercise_txt[self.current_char_idx]

        return deleted_char
    

    def is_exercise_done(self):
        return self.end_time is not None
    

    def get_stats(self):
        end_time = self.end_time or time.time()
        length_std_words = self.chars_touched / 5
        total_time_s = end_time - self.start_time if self.start_time else 0
        total_time_m = total_time_s / 60
        uncorrected_error_count = len([x for x in self.char_state_map if x == self.CHAR_WRONG])
        gross_wpm = length_std_words / total_time_m if total_time_m > 0 else 0
        net_wpm = max(0, gross_wpm - (uncorrected_error_count / total_time_m)) if total_time_m > 0 else 0
        result_accuracy = (self.chars_touched - uncorrected_error_count) * 100 / self.chars_touched if self.chars_touched > 0 else 0
        real_accuracy = (self.chars_touched - self.error_count) * 100 / self.chars_touched if self.chars_touched > 0 else 0

        return {
            'all_correct': uncorrected_error_count == 0,
            'progress_pct': self.chars_touched * 100 / self.length_txt,
            'length_txt': self.length_txt,
            'length_std_words': length_std_words,
            'total_time_s': total_time_s,
            'error_count': self.error_count,
            'uncorrected_error_count': uncorrected_error_count,
            'gross_wpm': gross_wpm,
            'net_wpm': net_wpm,
            'result_accuracy': result_accuracy,
            'real_accuracy': real_accuracy,
        }