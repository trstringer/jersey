"""Handle Trello labels"""
import colorama
from colormapping import COLOR_MAPPING
from trelloutil import backlog_board

def parse_labels(labels_raw):
    """Parse label objects from a raw string"""

    board = backlog_board()
    labels = [_.strip() for _ in labels_raw.split(',')]
    return [_ for _ in board.get_labels() if _.name in labels]

def label_name_with_color(label):
    return f'{COLOR_MAPPING[label.color] if label.color else colorama.Fore.WHITE}{label.name}{colorama.Fore.RESET}'

def arg_list_labels(cli_args):
    """List the current labels on the board"""

    board = backlog_board()

    for label in board.get_labels():
        # pylint: disable=line-too-long
        print(label_name_with_color(label))
