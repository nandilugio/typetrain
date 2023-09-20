import random

class Numbers:
    one_word_name = 'numbers'
    description = 'practice typing random numbers'

    def __init__(self, args):
        self.num_words_per_paragraph = args.words
        self.num_digits_per_word = args.digits

    @staticmethod
    def configure_argparse_subparser(parser):
        parser.add_argument('--words', type=int, default=4, help='number of words per paragraph')
        parser.add_argument('--digits', type=int, default=4, help='number of digits per word')

    def paragraph_generator(self):
        while True:
            paragraph = ''
            for _ in range(self.num_words_per_paragraph):
                paragraph += f'{random.randint(0, 10 ** self.num_digits_per_word):0{self.num_digits_per_word}} '
            paragraph = paragraph[:-1]
            yield paragraph