import os


class Song:
    one_word_name = 'song'
    description = 'practice typing songs from a file'

    def __init__(self, args):
        self.path = args.path

    @staticmethod
    def configure_argparse_subparser(parser):
        parser.add_argument('path', help='path to the file to practice typing')

    def paragraph_generator(self):
        if not os.path.exists(self.path):
            exit(f'File {self.path} does not exist')

        with open(self.path, 'r') as f:
            contiguous_lines = []
            while line := f.readline():
                if line.strip() == '': 
                    yield "\n".join(contiguous_lines)
                else:
                    contiguous_lines += line
            yield "\n".join(contiguous_lines)
