import sys
import logging
from .bezier2arc import convert_file, list_paths, colorize, get_parser


logging.basicConfig(
    filename="/home/phn/dev/bezier2arc/data/test.log"
    )

def main(args):
    print(args)
    if args.list:
        list_paths(args)
    elif args.convert:
        convert_file(args)
    elif args.color:
        colorize(args)
    else:
        raise ValueError("Wrong arguments")


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)

