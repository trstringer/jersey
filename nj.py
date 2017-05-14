import datetime
import dateutil
import pdb
import os
import colorama
from trello import TrelloClient

client = TrelloClient(
    api_key='',
    api_secret='',
    token='',
    token_secret=''
)

backlog_boards = [_ for _ in client.list_boards() if _.name == 'Backlog']
if len(backlog_boards) != 1:
    raise ValueError(f'Unexpected count of boards found: {len(backlog_boards)}')

board = backlog_boards[0]
lists = board.list_lists()
need_to_do_list = [_ for _ in lists if _.name == 'need_to_do'][0]
doing_list = [_ for _ in lists if _.name == 'doing'][0]
blocked_list = [_ for _ in lists if _.name == 'blocked'][0]
done_list = [_ for _ in lists if _.name == 'done'][0]

local_timezone = dateutil.tz.tzlocal()
today = datetime.datetime.today()
tomorrow = today + datetime.timedelta(days=1)
for card in sorted(need_to_do_list.list_cards(), key=lambda card: str(card.due_date) if card.due_date else 'zzz'):
    due_output = f'{colorama.Fore.BLUE}Unscheduled'
    if card.due_date:
        due_datetime = card.due_date.astimezone(local_timezone)
        hour = due_datetime.hour if due_datetime.hour <= 12 else due_datetime.hour - 12
        minute = ('0' + str(due_datetime.minute))[-2:]
        am_or_pm = 'am' if due_datetime.hour < 12 else 'pm'
        if due_datetime.date() <= today.date():
            due_output = f'{colorama.Style.BRIGHT}Today {hour}:{minute} {am_or_pm}{colorama.Style.NORMAL}'
        elif due_datetime.date() == tomorrow.date():
            due_output = f'Tomorrow {hour}:{minute} {am_or_pm}'
        else:
            due_output = due_datetime.strftime(f'%Y-%m-%d {hour}:{minute} %P')
        due_output = f'{colorama.Fore.CYAN}{due_output}'
    comments_count = len(card.get_comments())
    comments_output = f' {colorama.Fore.GREEN}({comments_count})' if comments_count > 0 else ''
    print(f'{colorama.Fore.YELLOW}{card.id[-3:]} {due_output} {colorama.Fore.RESET}{card.name}{comments_output}')

# list all non-done lists ::  $ nj
#   - order (doing, blocked, need_to_do)
# list particular list ::     $ nj <list_name>
# show info about card ::     $ nj show <card_id>
# move card ::                $ nj move <card_id> <list_name>
# add card ::                 $ nj add 'card name' -d <due_date> -l <labels>
#   - due_date can be 'today', 'tomorrow', '4 days', 'next wednesday', '5/31', '2017/5/31'
#   - due_date is optional
#   - labels is a comma-delimited list of existing labels
# list labels ::              $ nj labels
# sort all cards ::           $ nj sort
#   - sorts all cards by date in all lists
#   - cards with no dates appear last on the respective list

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
