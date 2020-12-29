import sys
import logging
import getopt
from .bezier2arc import convert_file, list_paths


logging.basicConfig(
    filename="test.log"
    )

def main(argv):
    opts, args = getopt.getopt(argv, "", ["list", "convert"])
    for opt, arg in opts:
        if opt == "--list":
            list_paths(args)
    if opt == "--convert":
        convert_file(args)


if __name__ == "__main__":
    main(sys.argv[1:])

