from __future__ import print_function
from lib.can_actions import CanActions, int_from_str_base, msg_to_candump_format
from modules.send import FILE_LINE_COMMENT_PREFIX
from sys import argv, stdout
import argparse
import datetime


def initiate_dump(handler, args):
    """
    Adds a CAN message handler which should add found data to found_arb_ids.
    Prints all of these afterwards, sorted by the number of hits.

    :param handler: Message handler function
    :param args: Argument namespace (reversed sorting applied if args.reverse)
    """
    whitelist = [int_from_str_base(x) for x in args.whitelist]
    if args.candump_format:
        format_func = msg_to_candump_format
    else:
        format_func = str

    def whitelist_handling(msg):
        if len(whitelist) == 0 or msg.arbitration_id in whitelist:
            handler(format_func(msg))

    print("Dumping CAN traffic (press Ctrl+C to exit)".format(whitelist))
    with CanActions() as can_wrap:
        can_wrap.add_listener(whitelist_handling)
        while True:
            pass


def parse_args(args):
    """
    Argument parser for the dump module.

    :param args: List of arguments
    :return: Argument namespace
    """
    parser = argparse.ArgumentParser(prog="cc.py dump",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="CAN traffic dump module for CaringCaribou",
                                     epilog="""Example usage:
  cc.py dump
  cc.py dump -f output.txt
  cc.py dump -c -f output.txt 0x733 0x734""")
    parser.add_argument("-f", "--file",
                        metavar="F",
                        help="Write output to file F (default: stdout)")
    parser.add_argument("whitelist",
                        metavar="W",
                        nargs="*",
                        help="Arbitration ID to whitelist")
    parser.add_argument("-c",
                        action="store_true",
                        dest="candump_format",
                        help="Output on candump format")
    args = parser.parse_args(args)
    return args


def file_header():
    """
    Returns an output file header string, consisting of a number of comment lines.

    :return: str header
    """
    argument_str = " ".join(argv)
    lines = ["Caring Caribou dump file",
             datetime.datetime.now(),
             argument_str]
    header = "".join(["{0} {1}\n".format(FILE_LINE_COMMENT_PREFIX, line) for line in lines])
    return header


def module_main(args):
    """
    Dump module main wrapper.

    :param args: List of module arguments
    """
    args = parse_args(args)
    # Print to stdout
    if args.file is None:
        initiate_dump(print, args)
    # Print to file
    else:
        try:
            with open(args.file, "w") as output_file:
                global count
                count = 0

                # Write file header
                header = file_header()
                output_file.write(header)

                def write_line_to_file(line):
                    global count
                    count += 1
                    print("\rMessages printed to file: {0}".format(count), end="")
                    output_file.write("{0}\n".format(line))
                    stdout.flush()

                initiate_dump(write_line_to_file, args)
        except IOError as e:
            print("IOError: {0}".format(e))
