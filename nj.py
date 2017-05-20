import argparse
import colorama
import datetime
import dateutil
import os
import re
from trello import TrelloClient
from exceptions import JerseyError

COLOR_MAPPING = {
    'green': colorama.Fore.GREEN,
    'yellow': colorama.Fore.YELLOW,
    'orange': colorama.Fore.LIGHTRED_EX,
    'red': colorama.Fore.RED,
    'purple': colorama.Fore.MAGENTA,
    'blue': colorama.Fore.BLUE,
    'sky': colorama.Fore.CYAN,
    'lime': colorama.Fore.LIGHTGREEN_EX,
    'pink': colorama.Fore.LIGHTMAGENTA_EX,
    'black': colorama.Fore.WHITE
}

def trello_creds():
    return TrelloClient(
        api_key=os.environ['TRELLO_API_KEY'],
        api_secret=os.environ['TRELLO_API_SECRET'],
        token=os.environ['TRELLO_TOKEN'],
        token_secret=os.environ['TRELLO_TOKEN_SECRET']
    )

def trello_board_name():
    return os.getenv('TRELLO_BACKLOG_BOARD') or 'Backlog'

def backlog_board():
    """Retrieve the backlog board"""

    client = trello_creds()

    backlog_boards = [_ for _ in client.list_boards() if _.name == trello_board_name()]
    if len(backlog_boards) != 1:
        raise ValueError(f'Unexpected count of boards found: {len(backlog_boards)}')

    return backlog_boards[0]

def format_due_date(card):
    """Format the due date for output"""

    local_timezone = dateutil.tz.tzlocal()
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)

    due_output = f'{colorama.Fore.BLUE}Unscheduled'
    if card.due_date:
        due_datetime = card.due_date.astimezone(local_timezone)
        hour = due_datetime.hour if due_datetime.hour <= 12 else due_datetime.hour - 12
        minute = ('0' + str(due_datetime.minute))[-2:]
        am_or_pm = 'am' if due_datetime.hour < 12 else 'pm'
        if due_datetime.date() == today.date():
            due_output = f'{colorama.Style.BRIGHT}Today {hour}:{minute} {am_or_pm}{colorama.Style.NORMAL}'
        elif due_datetime.date() < today.date():
            due_output = f'{colorama.Style.BRIGHT}{colorama.Fore.RED}Past Due{colorama.Style.NORMAL}'
        elif due_datetime.date() == tomorrow.date():
            due_output = f'Tomorrow {hour}:{minute} {am_or_pm}'
        else:
            due_output = due_datetime.strftime(f'%Y-%m-%d {hour}:{minute} {am_or_pm}')
        due_output = f'{colorama.Fore.CYAN}{due_output}'
    return due_output

def parse_new_due_date(due_date):
    if not due_date:
        return

    new_due_date_hour = 17
    new_due_date_minute = 0
    new_due_date_second = 0
    new_due_date_ms = 0

    today = datetime.datetime.today()

    if due_date == 'today':
        new_due_date = today.replace(
            hour=new_due_date_hour,
            minute=new_due_date_minute,
            second=new_due_date_second,
            microsecond=new_due_date_ms
        )
        return new_due_date

    if due_date == 'tomorrow':
        new_due_date = today.replace(
            day=today.day + 1,
            hour=new_due_date_hour,
            minute=new_due_date_minute,
            second=new_due_date_second,
            microsecond=new_due_date_ms
        )
        return new_due_date

    regex_match = re.search(r'^(\d+)\s*days?$', due_date)
    if regex_match:
        new_due_date = today + datetime.timedelta(days=int(regex_match.group(1)))
        new_due_date = new_due_date.replace(
            hour=new_due_date_hour,
            minute=new_due_date_minute,
            second=new_due_date_second,
            microsecond = new_due_date_ms
        )
        return new_due_date

    regex_match = re.search(r'^(\d+)[/-](\d+)$', due_date)
    if regex_match:
        new_due_date = datetime.datetime(today.year, int(regex_match.group(1)), int(regex_match.group(2)), new_due_date_hour, new_due_date_minute)
        return new_due_date

    regex_match = re.search(r'^(\d+)[/-](\d+)[/-](\d+)$', due_date)
    if regex_match:
        new_due_date = datetime.datetime(int(regex_match.group(1)), int(regex_match.group(2)), int(regex_match.group(3)), new_due_date_hour, new_due_date_minute)
        return new_due_date

def arg_list(cli_args):
    """List a board card summary"""

    board = backlog_board()

    lists = board.list_lists()
    input_list = [_ for _ in lists if _.name == cli_args.list_name][0]

    for card in sorted(input_list.list_cards(), key=lambda card: str(card.due_date) if card.due_date else 'zzz'):
        due_output = format_due_date(card)
        comments_count = len(card.get_comments())
        comments_output = f' {colorama.Fore.GREEN}({comments_count})' if comments_count > 0 else ''
        print(f'{colorama.Fore.YELLOW}{card.id[-3:]} {due_output} {colorama.Fore.RESET}{card.name}{comments_output}')

def card_by_id(card_id_postfix, board):
    """Retrieve a card by the last 3 digits of its id"""

    found_cards = [
        _ for _ in board.get_cards()
        if _.id[-3:] == card_id_postfix
    ]

    if len(found_cards) == 0:
        return
    elif len(found_cards) > 1:
        print(f'{colorama.Fore.RED}More than one card unexpectedly found{colorama.Fore.RESET}')
        return

    return found_cards[0]

def arg_show(cli_args):
    """Show a card summary"""

    board = backlog_board()

    card = card_by_id(cli_args.card_id, board)

    if not card:
        return

    print(f'{colorama.Fore.YELLOW}{colorama.Style.BRIGHT}{card.name}{colorama.Fore.RESET}')
    print(f'Due: {format_due_date(card)}{colorama.Fore.RESET}')

    for comment in sorted(card.get_comments(), key=lambda c: c['date'], reverse=True):
        comment_datetime = str(dateutil.parser.parse(comment['date']))
        print(f'{colorama.Fore.BLUE}{comment_datetime}', end=' ')
        print(f'{colorama.Fore.GREEN}{comment["data"]["text"]}')
        print(colorama.Fore.RESET, end='')

def arg_move(cli_args):
    """Move a card to a new list"""

    board = backlog_board()

    try:
        destination_list = [_ for _ in board.list_lists() if _.name == cli_args.list_name][0]
    except IndexError:
        print(f'{colorama.Fore.RED}Destination list not found')
        return

    card = card_by_id(cli_args.card_id, board)
    if not card:
        print(f'{colorama.Fore.RED}Card not found')
        return

    card.change_list(destination_list.id)

def parse_labels(labels_raw):
    """Parse label objects from a raw string"""

    board = backlog_board()
    labels = [_.strip() for _ in labels_raw.split(',')]
    return [_ for _ in board.get_labels() if _.name in labels]

def arg_add(cli_args):
    """Add a new card to a given list"""

    try:
        destination_list = [
            _ for _ in backlog_board().list_lists()
            if _.name == cli_args.list_name
        ][0]
    except IndexError:
        print(f'{colorama.Fore.RED}Error searching for list')
        return

    new_due = str(parse_new_due_date(cli_args.due))

    add_labels = None
    if cli_args.labels:
        add_labels = parse_labels(cli_args.labels)
    
    destination_list.add_card(
        name=cli_args.card_name,
        due=new_due if cli_args.due else "null",
        labels=add_labels
    )

def arg_list_labels(cli_args):
    """List the current labels on the board"""

    board = backlog_board()

    for label in board.get_labels():
        print(f'{COLOR_MAPPING[label.color] if label.color else colorama.Fore.WHITE}{label.name}{colorama.Fore.RESET}')

def arg_comment(cli_args):
    """Add a comment to a card"""

    board = backlog_board()

    card = card_by_id(cli_args.card_id, board)

    card.comment(cli_args.comment)

def arg_sort(cli_args):
    """Sort all cards in board"""
    board = backlog_board()

    for trello_list in board.list_lists():
        for card in sorted(trello_list.list_cards(), key=lambda card: card.due):
            print(f'{card.pos} {card.due}')

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # list a list of card summaries
    list_parser = subparsers.add_parser('list', help='list things')
    list_parser.add_argument('list_name', help='name of the list to show')
    list_parser.set_defaults(func=arg_list)

    # show card detail by id
    show_parser = subparsers.add_parser('show', help='display a card and contents')
    show_parser.add_argument('card_id', help='show card details')
    show_parser.set_defaults(func=arg_show)

    # move a card
    move_parser = subparsers.add_parser('move', help='move a card to a different list')
    move_parser.add_argument('card_id', help='card to move')
    move_parser.add_argument('list_name', help='list to move card to')
    move_parser.set_defaults(func=arg_move)

    # add a card
    add_parser = subparsers.add_parser('add', help='add a new card')
    add_parser.add_argument('card_name', help='card name and content')
    add_parser.add_argument('list_name', help='the destination list to add the card to')
    add_parser.add_argument('-d', '--due', help='(optional) due date for the card')
    add_parser.add_argument(
        '-l',
        '--labels',
        help='(optional) comma-separated list of labels for the new card'
    )
    add_parser.set_defaults(func=arg_add)

    # list labels
    label_parser = subparsers.add_parser('labels', help='list labels')
    label_parser.set_defaults(func=arg_list_labels)

    # add a comment to a card
    comment_parser = subparsers.add_parser('comment', help='add a comment to a card')
    comment_parser.add_argument('card_id', help='card to comment on')
    comment_parser.add_argument('comment', help='commend to add to card')
    comment_parser.set_defaults(func=arg_comment)

    # sort all cards in the board
    sort_parser = subparsers.add_parser('sort', help='sort all cards in the bard')
    sort_parser.set_defaults(func=arg_sort)

    cli_args = parser.parse_args()
    cli_args.func(cli_args)

if __name__ == '__main__':
    main()

# list all non-done lists ::  $ nj
#   - order (doing, blocked, need_to_do)
# list particular list ::     $ nj list <list_name>
# show info about card ::     $ nj show <card_id>
# move card ::                $ nj move <card_id> <list_name>
# add card ::                 $ nj add 'card name' <list_name> -d <due_date> -l <labels>
#   - due_date can be 'today', 'tomorrow', '4 days', 'next wednesday', '5/31', '2017/5/31'
#   - due_date is optional
#   - labels is a comma-delimited list of existing labels
# list labels ::              $ nj labels
# sort all cards ::           $ nj sort
#   - sorts all cards by date in all lists
#   - cards with no dates appear last on the respective list
# add comment to card:        $ nj comment <card_id> <comment>

# label -> colorama mapping
# ========================= 
# green -> GREEN
# yellow -> YELLOW
# orange -> LIGHTRED_EX
# red -> RED
# purple -> MAGENTA
# blue -> BLUE
# sky -> CYAN
# lime -> LIGHTGREEN_EX
# pink -> LIGHTMAGENTA_EX
# black -> None
# None -> None
