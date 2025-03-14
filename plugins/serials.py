import random
import string


class Serials:
    one_word_name = 'serials'
    description = 'practice typing random serial numbers'

    def __init__(self, args):
        self.num_words_per_paragraph = args.num
        self.num_chars_per_gen_word = args.chars
        self.words_file_path = args.words_file
        self.words_from_file = None

    @staticmethod
    def configure_argparse_subparser(parser):
        parser.add_argument('--num', type=int, default=6, help='number of words per paragraph')
        parser.add_argument('--chars', type=int, default=9, help='number of characters per generated serial word')
        parser.add_argument('--words-file', type=str, help='path to a file containing words to intercalate between numbers')

    def paragraph_generator(self):
        while True:
            paragraph = ''
            for i in range(self.num_words_per_paragraph):
                if i % 2 == 1 and self.words_file_path:
                    paragraph += self._word_from_file()
                else:
                    paragraph += self._generate_serial_number()
                paragraph += ' '
            paragraph = paragraph[:-1]
            yield paragraph

    def _word_from_file(self):
        if not self.words_from_file:
            with open(self.words_file_path, 'r') as f:
                self.words_from_file = [w.strip() for w in f.read().splitlines() if len(w.strip()) > 0]
        return random.choice(self.words_from_file)

    def _generate_serial_number(self):
        serial_number = ''
        for i in range(self.num_chars_per_gen_word):
            if i == int(self.num_chars_per_gen_word / 2):
                serial_number += '-'
                continue
            r = random.randint(0, 9)
            if r < 2:
                serial_number += random.choice(string.ascii_uppercase + '.')
            else:
                serial_number += str(random.randint(0, 9))
        return serial_number
