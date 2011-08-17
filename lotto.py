#!/usr/bin/python

import random, ConfigParser, ast, copy
from optparse import OptionParser
from time import time
#import gc   # XXX: Debug memory leaks.

# Global variables.
g_config = {}               # Stores GameType config options.
g_prizes = {}               # Stores prizes from config file.
g_prize_amounts = {}        # Stores prize amounts from config file.
g_ticket_quick_picks = []   # Store an array of QuickPicks to use for tickets.
g_total_money_won = 0
g_total_tickets_won = 0
g_prizes_won = {}           # Format: {'3':3, '3+1':2, '4':2 ...}
g_quick_pick_file = ''
g_how_many_tickets_played = 0
g_how_many_tickets_won = 0


#gc.set_debug( gc.DEBUG_STATS | gc.DEBUG_LEAK )   # XXX: Debug memory leaks
#gc.set_debug( gc.DEBUG_LEAK )   # XXX: Debug memory leaks


class TicketNumbers( object ):
    '''Represents the numbers of a ticket (or the 7 winning numbers).
    @var numbers: A sorted array of 7 unique numbers from 1-49.'''

    def __init__( self, numbers ):
        '''Constructor.
        @param numbers: The numbers for this ticket.'''

        self.numbers = numbers
        self._set_numbers( numbers )

    def name( self ):
        '''Return the name of this class type.'''
        return "TicketNumbers"

    def __str__( self ):
        '''Returns a string of the number list.'''
        str_nums = []
        for i in range( len( self.numbers ) ):
            str_nums.append( str( self.numbers[i] ) )

        return ', '.join( str_nums )

    def _set_numbers( self, numbers ):
        '''Sets the numbers member variable and validates the numbers.
        @param numbers: The numbers to assign.'''

        global g_config
        self.numbers = sorted( numbers )

        if len( self.numbers ) != int(g_config['how_many_numbers']):
            raise Exception( "You must have %d numbers, but found %d numbers: %s" % (g_config['how_many_numbers'], len( self.numbers ), str(self.numbers)) )
        tmp = []

        for num in self.numbers:
            # Check if numbers are in range.
            if ( num < int(g_config['min_number']) ) or ( num > int(g_config['max_number']) ):
                raise Exception( "The numbers must be between %d & %d!" % (int(g_config['min_number']), int(g_config['max_number'])) )
            # Check for duplicate numbers.
            if num in tmp:
                raise Exception( "You cannot have duplicate numbers!  %d in %s" % (num, str( self.numbers )) )
            tmp.append( num )


class PlayedTicket( TicketNumbers ):
    '''Represents a ticket that was played.
    @var amount_won: How much $$ this ticket won.'''

    def __init__( self, numbers ):
        '''Constructor.
        @param numbers: The numbers for this ticket.'''

        super( PlayedTicket, self ).__init__( numbers )
        self.amount_won = {}    # Map of Game Index to $$ won each play.
        self.tickets_won = {}   # Map of Game Index to Free Tickets won each play.

    def name( self ):
        '''Return the name of this class type.'''
        return "PlayedTicket"

    def compare_with( self, winning_numbers, game_index=None ):
        '''Compares this ticket with the specified winning numbers and sets the amount_won & tickets_won members accordingly.
        @param winning_numbers: The winning numbers to compare against.
        @param game_index: (optional) The game index for this game.  Defaults to 1 + the number of games recorded.
        @return: A tuple of ($$ won, # free tickets won).'''

        global g_config, g_prizes, g_prize_amounts, g_prizes_won, g_how_many_tickets_won
        nums_correct = 0
        bonus_correct = 0
        amount_won = 0
        tickets_won = 0

        if game_index == None:
            game_index = len( self.amount_won )

        # Check each individual number of the ticket against the winning numbers.
        for num in self.numbers:
            if num in winning_numbers.numbers:
                nums_correct = nums_correct + 1
            elif num in winning_numbers.bonus_numbers:
                bonus_correct = bonus_correct + 1

        # Now see if we won anything.
        for (key, value) in g_prizes.items():
            main_nums = key[0]
            bonus_nums = key[1]

            if (main_nums == nums_correct) and ((bonus_nums == bonus_correct) or (bonus_nums == 0)):
                if not g_prizes_won.has_key( value ):
                    g_prizes_won[value] = 0

                g_how_many_tickets_won = g_how_many_tickets_won + 1
                g_prizes_won[value] = g_prizes_won[value] + 1  # Increment map of how many times each prize won. 

                # We won.   Now figure out what we won.
                if g_prize_amounts[value] > amount_won:
                    amount_won = g_prize_amounts[value]
                    tickets_won = 0
                elif g_prize_amounts[value] == -1:
                    amount_won = 0
                    tickets_won = 1

        if amount_won or tickets_won:
            if g_config['verbose']:
                print( "Ticket %s won: $%d & %d Free tickets." % (str(self.numbers), amount_won, tickets_won) )

        # Set and return the amount won.
        self.amount_won[game_index] = amount_won
        self.tickets_won[game_index] = tickets_won
        return (amount_won, tickets_won)


class QuickPick( PlayedTicket ):
    '''Represents a Quick Pick ticket.'''

    def __init__( self, numbers ):
        '''Constructor.
        @param numbers: The numbers for this ticket.'''

        super( QuickPick, self ).__init__( numbers )
        self.amount_won = {}    # Map of Game Index to $$ won each play.
        self.tickets_won = {}   # Map of Game Index to Free Tickets won each play.

    def name( self ):
        '''Return the name of this class type.'''
        return "QuickPick"


class WinningNumbers( TicketNumbers ):
    '''Represents the winning numbers + bonus number.
    @var bonus_numbers: The bonus numbers.'''

    def __init__( self, numbers, bonus_numbers=None ):
        '''Constructor.
        @param numbers: The winning numbers.
        @param bonus_numbers: (optional) The bonus number(s).  Defaults to empty list.'''

        global g_config
        bonus_numbers = bonus_numbers or []
        super( WinningNumbers, self ).__init__( numbers )
        self.bonus_numbers = []
        if bonus_numbers:
            self.bonus_numbers = sorted( bonus_numbers )
        tmp = []

        if len( bonus_numbers ) != int(g_config['how_many_bonus']):
            raise Exception( "You must have %d bonus numbers!" % int(g_config['how_many_bonus']) )

        for num in bonus_numbers:
            if (num in tmp) or (num in self.numbers):
                raise Exception( "You cannot have duplicate numbers!" )
            tmp.append( num )

    def __str__( self ):
        '''Converts this class into a string.'''
        ret = super( WinningNumbers, self ).__str__()

        str_bnums = []

        if len( self.bonus_numbers ):
            for i in range( len( self.bonus_numbers ) ):
                str_bnums.append( str( self.bonus_numbers[i] ) )

            ret = ret + ' + ' + ', '.join( str_bnums )

        return ret
            

    def name( self ):
        '''Return the name of this class type.'''
        return "WinningNumbers"


def load_config( filename ):
    '''Reads the config file to load program defaults.
    @param filename: The filename of the config file.
    @return: A ConfigParser object containing the parsed config file.'''

    # Read the config file into the parser.
    global g_config, g_prizes, g_prize_amounts
    conf = ConfigParser.SafeConfigParser()
    conf.read( filename )

    if (not conf.has_section( 'GameType' )) or (not conf.has_section( 'Prizes' )):
        raise Exception( "Invalid config file!  [GameType] and/or [Prizes] sections are missing!" )

    options = ['min_number', 'max_number', 'how_many_numbers', 'how_many_bonus', 'how_many_hand_picked_lines', 'how_many_quick_pick_lines', 'cost_per_ticket', 'quick_pick_pool_size', 'how_many_tickets_bought']

    for option in options:
        if not conf.has_option( 'GameType', option ):
            raise Exception( "Invalid config file!  '%s' option is missing!" % option )

        g_config[option] = int( conf.get( 'GameType', option ) )

    # Prizes section contains maps.
    g_prizes = ast.literal_eval( conf.get( 'Prizes', 'prizes' ) )
    g_prize_amounts = ast.literal_eval( conf.get( 'Prizes', 'prize_amounts' ) )
#    print( "*** prizes = %s  type = %s" % (str(g_prizes), type(g_prizes)) )                         # DEBUG
#    print( "*** prize_amounts = %s  type = %s" % (str(g_prize_amounts), type(g_prize_amounts)) )    # DEBUG


def load_tickets_conf( filename ):
    '''Loads tickets from a config file.
    @param filename: The filename to load the tickets from.
    @return: A map of # of tickets to an array of Tickets.'''

    # Read the config file into the parser.
    conf = ConfigParser.SafeConfigParser()
    conf.read( filename )
    ticket_map = {}

    # First read the 'all_groups' option that contains a list of all ticket groups.
    if not conf.has_section( 'AllTicketGroups' ):
        raise Exception( "Invalid config file!  [AllTicketGroups] section is missing!" )

    all_groups = parse_number_line( conf.get( 'AllTicketGroups', 'all_groups' ) )

    # Then read each ticket group and add the tickets to the map.
    for group in all_groups:
        if not conf.has_section( str( group ) ):
            raise Exception( "Invalid config file!  [%d] section is missing!" % group )

        tickets = []

        for i in range( 1, group + 1 ):
            if not conf.has_option( str( group ), str( i ) ):
                raise Exception( "Invalid config file!  There is no '%d' option under the [%d] section!" % (i, group) )

            numbers = parse_number_line( conf.get( str( group ), str( i ) ) )
            ticket = PlayedTicket( numbers )
            tickets.append( ticket )

        ticket_map[group] = tickets

    return ticket_map


def load_tickets_txt( filename, ticket_class = PlayedTicket ):
    '''Loads tickets from a text file.
    @param filename: The filename to load the tickets from.
    @param ticket_class: (optional) The class name for the type of tickets you want returned.
    @return: A map of # of tickets to an array of Tickets.'''

    global g_config

    # Read the file into an array of lines.
    fd = open( filename, 'r' )
    lines = fd.readlines()
    fd.close()

    # Create the hand picked list of tickets.
    ticket_list = parse_number_lines( lines, ticket_class )
    number_of_tickets = len( ticket_list )

    if ticket_class != QuickPick:
        # Add the appropriate number of quick picks.
        num_quick_picks = number_of_tickets * g_config['how_many_quick_pick_lines']
        ticket_list.extend( quick_picks( num_quick_picks ) )

    tickets = {number_of_tickets : ticket_list}

    return tickets


def load_winning_numbers( lines ):
    '''Loads the winning numbers from a CSV file and returns an array of WinningNumbers.
    @param lines: The lines of the CSV containing the winning numbers.
    @return: An array of WinningNumbers objects.'''

    global g_config

    numbers = []
    winning_tickets = []

    # Parse the string lines into arrays of numbers.
    for line in lines:
        numbers.append( parse_number_line( line ) )

    how_many_numbers = g_config['how_many_numbers']
    how_many_bonus = g_config['how_many_bonus']

    # Create an array of WinningTickets.
    for line in numbers:
        if len( line ) != (how_many_numbers + how_many_bonus):
            raise Exception( "Invalid winning numbers CSV file!  There should be %d numbers, but we found %d!" % (how_many_numbers + how_many_bonus, len( line ) ) )
        else:
            nums = line[0:how_many_numbers]
            bonus = line[-how_many_bonus:]
            ticket = WinningNumbers( nums, bonus )
            winning_tickets.append( ticket )

    return winning_tickets


def parse_number_lines( lines, ticket_class = PlayedTicket ):
    '''Parses an array of strings (comma delimited number lines).
    @param lines: An array of strings (comma delimited number lines).
    @param ticket_class: (optional) The class name for the type of tickets you want returned.
    @return: An array of tickets of the type specified by ticket_class.'''

    tickets = []

    for line in lines:
        numbers = parse_number_line( line )
        tickets.append( ticket_class( numbers ) )

    return tickets


def parse_number_line( line ):
    '''Parses a string (comma delimited number line).
    @param line: A string (comma delimited number line).
    @return: An array of sorted numbers.'''

    nums = line.split( ',' )
    numbers = []

    for num in nums:
        numbers.append( int( num.strip() ) )

    return sorted( numbers )


def quick_pick():
    '''Returns a QuickPick ticket.
    @return: A QuickPick ticket.'''

    global g_config, g_quick_pick_file
    random.seed()
    numbers = []

    while len( numbers ) < g_config['how_many_numbers']:
        num = random.randrange( g_config['min_number'], g_config['max_number'], 1 )  # From 1 to 49, step by 1.

        if not num in numbers:
            numbers.append( num )

    # If we're using a quick pick file, this function should never be called, so print this to let us know.
    if g_config['verbose'] and g_quick_pick_file:
        print( "Warning: You specified a quick pick file, but quick_pick() was called and returned: %s" % str(numbers) )

    return QuickPick( numbers )


def quick_picks( number_of_tickets, quick_pick_list=None ):
    '''Returns a list of QuickPick tickets.
    @param number_of_tickets: The number of QuickPick tickets to generate.
    @param quick_pick_list: (optional) Get as many quick picks from this list instead of generating new ones.
    @return: A list of QuickPick tickets.'''

    tickets = []

    if quick_pick_list:
#        print( "*** len( quick_pick_list ) = %d" % len( quick_pick_list ) ) # DEBUG
        if len( quick_pick_list ) >= number_of_tickets:
#            print( "*** quick_pick_list is big enough." )   # DEBUG
            tickets.extend( quick_pick_list[0:number_of_tickets] )
        else:
            print( "*** quick_pick_list is too small." )    # DEBUG
            tickets.extend( quick_pick_list )

            for i in range( number_of_tickets - len( quick_pick_list ) ):
                tickets.append( quick_pick() )
    else:
        print( "*** quick_pick_list is None." ) # DEBUG
        for i in range( number_of_tickets ):
            tickets.append( quick_pick() )

#    print( "*** quick_picks( %d )" % number_of_tickets )    # DEBUG
    return tickets


def single_play( played_tickets, winning_numbers ):
    '''Compares tickets to winning numbers and calculates what each ticket won.
    The 'amount_won' member will be set for any tickets that won.
    @param played_tickets: An array of PlayedTickets.
    @param winning_numbers: A WinningNumbers object.
    @return: A tuple of ($$ won, # free tickets won).'''

    global g_total_money_won, g_total_tickets_won, g_config, g_how_many_tickets_played
    total_money = 0
    total_tickets = 0
    num_tickets = len( played_tickets )

    # Compare each ticket against the winning numbers.
    for i in range( 0, num_tickets - 1 ):
        ticket = played_tickets[i]
        g_how_many_tickets_played = g_how_many_tickets_played + 1

        if g_config['verbose']:
            print( "[%s] = %s" % (played_tickets[i].name(), str(played_tickets[i])) )

        (money_won, tickets_won) = ticket.compare_with( winning_numbers )
        total_money = total_money + money_won
        total_tickets = total_tickets + tickets_won

    # Keep track of the totals won over all.
    g_total_money_won = g_total_money_won + total_money
    g_total_tickets_won = g_total_tickets_won + total_tickets

    return (total_money, total_tickets)


def get_tickets( played_ticket_map, how_many_tickets, keys ):
    '''Returns an array of tickets of the specified size, with as many hand_picked tickets as possible.
    @param played_ticket_map: A map of # of tickets to array of PlayedTickets to choose from.
    @param how_many_tickets: The number of tickets to be returned.
    @param keys: The sorted list of keys in played_ticket_map.
    @return: An array of tickets of the specified size, with as many hand_picked tickets as possible.'''

    global g_ticket_quick_picks
    tickets = []

    # If any of the ticket pools have the exact number of tickets we need, use it; otherwise add quick picks
    # to a ticket pool that's smaller than we need until we have the right number of tickets.
    if how_many_tickets in keys:
        tickets = copy.deepcopy(played_ticket_map[how_many_tickets] )
    else:
        # Find next ticket pool lower than how_many_tickets and add quick picks to fill up the rest.
        last_key_index = -1

        for i in keys:
            if i > how_many_tickets:
                break

            last_key_index = i

        if last_key_index == -1:
            # Looks like we're using all quick picks.
            print( "*** get_tickets() is adding all %d quick picks" % how_many_tickets )                   # DEBUG
            tickets = quick_picks( how_many_tickets, g_ticket_quick_picks )
        else:
            if (how_many_tickets - last_key_index) > 50:
                print( "*** get_tickets() is adding %d quick picks" % (how_many_tickets - last_key_index) )    # DEBUG
            tickets = copy.deepcopy( played_ticket_map[last_key_index] )
            tickets.extend( quick_picks( how_many_tickets - last_key_index, g_ticket_quick_picks ) )

    return tickets


def multiple_plays( played_ticket_map, quick_pick_list_const, winning_numbers, number_of_tickets ):
    '''Compares tickets to an array of winning numbers and calculates what each ticket won over x number of games played.
    The 'amount_won' member will be set for any tickets that won.
    @param played_ticket_map: A map of # of tickets to array of PlayedTickets to choose from.
    @param quick_pick_list_const: A list of QuickPick tickets to choose from.
    @param winning_numbers: An array of WinningNumbers objects.
    @param number_of_tickets: The usual number of tickets bought (assuming no extra or free tickets).
    @return: A tuple of: (extra_tickets, extra_quick_picks, money_left_over)'''

    global g_ticket_quick_picks, g_config

    extra_tickets = 0
    extra_quick_picks = 0
    money_left_over = 0

    amount_won = 0
    tickets_won = 0
    game_num = 0
    keys = sorted( played_ticket_map.keys() )
#    print( "*** played_ticket_map size = %d" % len(played_ticket_map) )   # XXX: Debug memory leaks.
#    print( "*** quick_pick_list_const size = %d" % len(quick_pick_list_const) )   # XXX: Debug memory leaks.
#    print( "*** winning_numbers size = %d" % len(winning_numbers) )   # XXX: Debug memory leaks.

    # For each winning ticket, check if any of our tickets won.
    for winning_ticket in winning_numbers:
        total_tickets_won = 0
        total_amount_won = 0
        game_num += 1

        if g_config['verbose']:
            print( "Winning numbers are: %s" % winning_ticket )

        # Check the hand picked tickets.
        how_many_tickets = number_of_tickets + extra_tickets
        tickets = get_tickets( played_ticket_map, how_many_tickets, keys )
#        print( "*** get_tickets() returned %d tickets" % len(tickets) )    # DEBUG

        # Play the numbers we picked.
        (amount_won, tickets_won) = single_play( tickets, winning_ticket )
        for ticket in tickets:
            del ticket
        del tickets
        total_amount_won = total_amount_won + amount_won
        total_tickets_won = total_tickets_won + tickets_won

        # Check the quick picks.
        how_many_quick_picks = (g_config['how_many_quick_pick_lines'] * number_of_tickets) + extra_quick_picks
#        print( "*** how_many_quick_picks = %d" % how_many_quick_picks )    # DEBUG

        # Make a copy of quick_pick_list_const.
        quick_pick_list = quick_pick_list_const[0:len(quick_pick_list_const)]

        # If the quick_pick pool isn't big enough, increase the pool size.
        if len( quick_pick_list ) < how_many_quick_picks:
#            print( "***** len( quick_pick_list ) = %d" % len( quick_pick_list ) )   # DEBUG
            quick_pick_list.extend( quick_picks( how_many_quick_picks - len(quick_pick_list), g_ticket_quick_picks ) )

        # Now play the quick picks.
        (amount_won, tickets_won) = single_play( quick_pick_list[0:how_many_quick_picks], winning_ticket )
        total_amount_won = total_amount_won + amount_won
        total_tickets_won = total_tickets_won + tickets_won

        # Now change the number of quick picks and extra money to reflect what we just won.
        if g_config['verbose']:
            print( "[Game %d]: We won: $%d, and %d Free Tickets.\n\n" % (game_num, total_amount_won, total_tickets_won) )

        extra_tickets = int( (total_amount_won + money_left_over) / g_config['cost_per_ticket'] )
        money_left_over = total_amount_won + money_left_over - (extra_tickets * g_config['cost_per_ticket'])
        extra_quick_picks = total_tickets_won

    return (extra_tickets, extra_quick_picks, money_left_over)


def main():
    '''The start of the program.'''

    global g_ticket_quick_picks, g_quick_pick_file, g_config, g_total_money_won, g_total_tickets_won, g_prizes_won, \
        g_how_many_tickets_played, g_how_many_tickets_won

    # Create the arg parser.
    usage = """\
usage: %prog -c <config_file> -t <tickets_file> -w <winning_numbers_file> [-q <quick_pick_file>] [-o <quick_pick_output_file>] [-T] [-v]
   or: %prog -c <config_file> -o <quick_pick_output_file> [-v]
    -c, --config             The main config file.
    -t, --tickets            The tickets config file.
    -o, --output             Will dump some quick pick numbers into this file.
    -w, --winning-numbers    The winning numbers csv file.
    -d, --debug              Debug mode.
    -T, --text               Read tickets_file as a text file instead of a config file.
    -v, --verbose            Enable verbose mode."""
    parser = OptionParser( usage=usage )
    parser.add_option( '-c', '--config', dest='config_file' )
    parser.add_option( '-t', '--tickets', dest='tickets_file' )
    parser.add_option( '-o', '--output', dest='output_file' )
    parser.add_option( '-q', '--quick-pick', dest='quick_pick_file' )
    parser.add_option( '-w', '--winning-numbers', dest='winning_numbers' )
    parser.add_option( '-d', '--debug', action='store_true', dest='debug_mode' )
    parser.add_option( '-T', '--text', action='store_true', dest='text_mode' )
    parser.add_option( '-v', '--verbose', action='store_true', dest='verbose' )
    (options, args) = parser.parse_args()

    if len( args ):
        parser.error( "The following arguments are unrecognized: %s" % str( args ) )

    if (not options.config_file):
        parser.error( "--config is a required parameter!" )

    # Load the main config file.
    load_config( options.config_file )
    ticket_map = None
    g_config['debug_mode'] = False
    g_config['verbose'] = False

    if options.debug_mode:
        g_config['debug_mode'] = True

    if options.verbose:
        g_config['verbose'] = True

    if g_config['verbose']:
        # Print out current configuration.
        print( "min_number = %s" % g_config['min_number'] )
        print( "max_number = %s" % g_config['max_number'] )
        print( "how_many_numbers = %s" % g_config['how_many_numbers'] )
        print( "how_many_bonus = %s" % g_config['how_many_bonus'] )
        print( "how_many_hand_picked_lines = %s" % g_config['how_many_hand_picked_lines'] )
        print( "how_many_quick_pick_lines = %s" % g_config['how_many_quick_pick_lines'] )
        print( "cost_per_ticket = %s" % g_config['cost_per_ticket'] )
        print( "quick_pick_pool_size = %s" % g_config['quick_pick_pool_size'] )
        print( "how_many_tickets_bought = %s" % g_config['how_many_tickets_bought'] )
        print( "verbose mode = %s\n" % str(g_config['verbose']) )


    # Load the quick pick pool from a file or generate the numbers.
    quick_pick_pool = []
    if options.quick_pick_file:
        g_quick_pick_file = options.quick_pick_file
        quick_pick_map = load_tickets_txt( options.quick_pick_file, QuickPick )
        for key, val in quick_pick_map.items():
            quick_pick_pool = val
    else:
        quick_pick_pool = quick_picks( g_config['quick_pick_pool_size'] )


    if (options.output_file):   # Just output some quick picks.
        if ((options.tickets_file) or (options.winning_numbers) or (options.text_mode)):
            parser.error( "--output cannot be used with --tickets or --winning-numbers or --text!" )
        else:
            # Just output some quick picks to a file.
            fd = open( options.output_file, 'w' )
            for quick_pick in quick_pick_pool:
                fd.write( str( quick_pick ) + '\n' )
            fd.close()
    else:   # Play the games.
        # Move half the quick pick pool to g_ticket_quick_picks for use with normal tickets.
        for i in range( (len(quick_pick_pool) / 2) ):
            g_ticket_quick_picks.append( quick_pick_pool.pop(0) )

        if (not options.tickets_file) or (not options.winning_numbers):
            parser.error( "Incorrect number of arguments!" )
        else:
            # Load the tickets & winning numbers.
            if options.text_mode:
                ticket_map = load_tickets_txt( options.tickets_file )
            else:
                ticket_map = load_tickets_conf( options.tickets_file )

            # Read the file into an array of lines.
            fd = open( options.winning_numbers, 'r' )
            lines = []
            extra_tickets     = 0
            extra_quick_picks = 0
            money_left_over   = 0

            iter = 0   # XXX: Debug memory leak.
            while True:
                seconds = time()
                iter = iter + 1   # XXX: Debug memory leak
                print( "====== Iteration %d" % iter )   # XXX: Debug memory leak

                for i in range( 1000 ):
                    line = fd.readline()
                    if not line:
                        break
                    lines.append( line )
                if not lines:
                    break

                winning_numbers = load_winning_numbers( lines )

                # Start the simulation.
                (extra_tickets, extra_quick_picks, money_left_over) = multiple_plays( ticket_map, quick_pick_pool, winning_numbers, g_config['how_many_tickets_bought'] )
                del lines
                lines = []

                print( "*** The iteration took %f seconds." % float(time() - seconds) )   # XXX: Debug memory leaks.
#                print( "*** GC.get_objects() returned %d objects." % len( gc.get_objects() ) )   # XXX: Debug memory leaks.
#                print( "*** GC.get_count()   returned %s." % str(gc.get_count()) )  # XXX: Debug memory leaks.
#                print( "*** GC.garbage       returned %d objects." % len( gc.garbage ) )   # XXX: Debug memory leaks.
#                print( "***** gc.get_referents() returned %d" % len(gc.get_referents(winning_numbers)) )   # XXX: Debug memory leaks.
#                gc.collect()

            print( "After %d games, we won a total of $%d and %d Free Tickets ($%d)." % (len( winning_numbers ), g_total_money_won, g_total_tickets_won, (g_total_tickets_won * 5 + g_total_money_won)) )
            print( "We played %d ticket lines and %d lines won." % (g_how_many_tickets_played, g_how_many_tickets_won) )
            fd.close()

            # Now display the results of all the games.
            for (key, value) in sorted( g_prizes.items() ):
                if g_prizes_won.has_key( value ):
                    print( "    '%s' won, %d times." % (value, g_prizes_won[value]) ) 


if __name__ == "__main__":
    main()
    
