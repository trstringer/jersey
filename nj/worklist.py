"""List handling"""
import datetime
import pytz
import colorama
from .trelloutil import backlog_board, format_due_date

def arg_list(cli_args):
    """List a board card summary"""

    board = backlog_board()

    lists = board.list_lists()
    input_list = [_ for _ in lists if _.name == cli_args.list_name][0]

    for card in sorted(
            input_list.list_cards(),
            key=lambda card: str(card.due_date) if card.due_date else 'zzz'):
        due_output = format_due_date(card)
        comments_count = len(card.get_comments())
        comments_output = f' {colorama.Fore.GREEN}({comments_count})' if comments_count > 0 else ''
        # pylint: disable=line-too-long
        print(f'{colorama.Fore.YELLOW}{card.id[-3:]} {due_output} {colorama.Fore.RESET}{card.name}{comments_output}')

def arg_sort(cli_args):
    """Sort all cards in board"""
    board = backlog_board()

    for trello_list in board.list_lists():
        cards = trello_list.list_cards()
        if not cards or trello_list.name == 'done':
            continue
        min_pos = min(cards, key=lambda card: card.pos).pos
        max_pos = max(cards, key=lambda card: card.pos).pos
        len_cards = len(cards)
        # pylint: disable=line-too-long
        for idx, card in enumerate(sorted(
                trello_list.list_cards(),
                key=lambda card: card.due_date if card.due_date else datetime.datetime.max.replace(tzinfo=pytz.UTC))):
            target_pos = min_pos + (idx * (max_pos - min_pos) / (len_cards - 1))
            if card.pos != target_pos:
                card.set_pos(target_pos)
