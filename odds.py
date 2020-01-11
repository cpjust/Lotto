#!/usr/bin/python

from optparse import OptionParser
import math
from mpmath import mpf, mp      # Install with:  apt-get install python-mpmath


def choose( x, n ):
    """Calculates x choose n."""
    # ( x )      x!
    # ( n ) = --------
    #         n!(x-n)!
    x_fac = mpf( math.factorial( x ) )
    n_fac = mpf( math.factorial( n ) )
    xn_fac = mpf( math.factorial( x - n ) )
    ret = (x_fac / (n_fac * xn_fac))
    return ret


def main():
    usage = """\
usage: %prog --max <max_num> --num <num> --prize <num>
  where: <max_num> is the max numbers you can pick in the game
         <num> is how many numbers you pick in the game.
         <prize> is how many numbers you need to get right for a certain prize (ex. 2 numbers = free ticket)
Example: %prog -m 49 -n 6 -p 2
Will return the odds of getting 2 numbers right for lotto 6/49."""

    parser = OptionParser( usage=usage )
    parser.add_option( '-m', '--max', dest='max_num' )
    parser.add_option( '-n', '--num', dest='how_many' )
    parser.add_option( '-p', '--prize', dest='prize' )
    (options, args) = parser.parse_args()

    if len( args ):
        parser.error( "The following arguments are unrecognized: %s" % str( args ) )

    if (not options.max_num) or (not options.how_many) or (not options.prize):
        parser.error( "Missing required parameters!" )

    max = int( options.max_num )
    num = int( options.how_many )
    prize = int( options.prize )

    if (max < 1) or (num < 1) or (prize < 1):
        parser.error( "num, max & prize must be greater than 0!" )

    if prize > num:
        parser.error( "prize cannot be greater than num!" )

    if num > max:
        parser.error( "num canot be greater than max!" )

    # The formula to calculate odds of getting x numbers in lotto 6/49 is:
    # ( 6 )( 49 - 6 )
    # ( x )(  6 - x )
    # ---------------
    #    ( 49 )
    #    (  6 )
    left = choose( num, prize )
    right = choose( max - num, num - prize )
    bottom = choose( max, num )
    odds = bottom / (left * right)
    print( "The odds of getting %d numbers right in lotto %d/%d is: 1/%s" % (prize, num, max, str(odds)) )


if __name__ == "__main__":
    main()
