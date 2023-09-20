import os
import random

class RandomFile:
    one_word_name = 'random-file'
    description = 'practice typing random paragraphs in a file'

    def __init__(self, args):
        self.path = args.path

    @staticmethod
    def configure_argparse_subparser(parser):
        parser.add_argument('path', help='path to the file to practice typing')

    def paragraph_generator(self):
        if not os.path.exists(self.path):
            exit(f'File {self.path} does not exist')
            
        with open(self.path, 'r') as f:
            paragraphs = f.read().split('\n')
            random.shuffle(paragraphs)
            for paragraph in paragraphs:
                yield paragraph.strip()
            