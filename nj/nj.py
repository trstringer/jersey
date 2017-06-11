"""Main module for Jersey CLI"""
import argparse
import sys
from card import arg_comment, arg_move, arg_show, arg_add
from label import arg_list_labels
from worklist import arg_list, arg_sort, display_active_lists

def main():
    """Main module execution function"""

    parser = argparse.ArgumentParser(
        prog='nj'
    )
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

    # if the user calls nj with no args then show
    # all active lists
    if len(sys.argv) == 1:
        display_active_lists()
        sys.exit(0)

    cli_args = parser.parse_args()
    cli_args.func(cli_args)

if __name__ == '__main__':
    main()
