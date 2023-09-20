import os

class File:
    one_word_name = 'file'
    description = 'practice typing the contents of a file'

    def __init__(self, args):
        self.path = args.path

    @staticmethod
    def configure_argparse_subparser(parser):
        parser.add_argument('path', help='path to the file to practice typing')

    def paragraph_generator(self):
        if not os.path.exists(self.path):
            exit(f'File {self.path} does not exist')

        with open(self.path, 'r') as f:
            while line := f.readline():
                yield line.strip()
