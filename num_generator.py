#!/usr/bin/python

from copy import deepcopy
from optparse import OptionParser

g_line = []

def print_line( line, min_num, max_num, r_index ):
    global g_line
#    print( "line = %s, min = %d, max = %d, r_index = %d" % (line, min_num, max_num, r_index) )
    num = deepcopy( min_num )

    while num <= (max_num - r_index):
        num = num + 1
        line_copy = deepcopy( line )
        line_copy.append( num )

        if r_index == 0:
            if line != g_line:
                print line
                g_line = line
        else:
            print_line( line_copy, num, max_num, (r_index - 1) )


def main():
    usage = """\
usage: %prog --min <min_num> --max <max_num> --num <num>"""

    parser = OptionParser( usage=usage )
    parser.add_option( '-m', '--min', dest='min_num' )
    parser.add_option( '-M', '--max', dest='max_num' )
    parser.add_option( '-n', '--num', dest='how_many' )
    (options, args) = parser.parse_args()

    if len( args ):
        parser.error( "The following arguments are unrecognized: %s" % str( args ) )

    if (not options.min_num) or (not options.max_num) or (not options.how_many):
        parser.error( "Missing required parameters!" )

    line = []
    print_line( line, int(options.min_num) - 1, int(options.max_num), int(options.how_many) )
            


if __name__ == "__main__":
    main()
