#!/usr/bin/python

from copy import deepcopy
from optparse import OptionParser
import ConfigParser, re

g_line = []

def load_template_conf( filename ):
    '''Loads template from a config file.
    @param filename: The filename to load the template from.
    @return: A map of letters to numbers.'''

    # Read the config file into the parser.
    template = ConfigParser.SafeConfigParser()
    template.optionxform = str  # This is needed to make ConfigParser case-sensitive.
    template.read( filename )
    number_map = {}

    # First read the 'all_letters' option that contains a list of all letters to be mapped with numbers.
    if not template.has_section( 'template' ):
        raise Exception( "Invalid config file!  [template] section is missing!" )

    if not template.has_section( 'map' ):
        raise Exception( "Invalid config file!  [map] section is missing!" )

    all_letters = parse_line( template.get( 'template', 'all_letters' ) )

    # Then read each letter and add the numbers to the map.
    for letter in all_letters:
        tickets = []

        number = template.get( 'map', letter ).strip()
        number_map[letter] = number

    return number_map


def parse_line( line ):
    '''Parses a string (comma delimited line).
    @param line: A string (comma delimited line).
    @return: An array of sorted letters.'''

    letters = line.split( ',' )
    letter_list = []

    for letter in letters:
        letter_list.append( letter.strip() )

    return sorted( letter_list )


def convert_template( filename, template_map ):
    '''Converts the template into a set of ticket numbers.
    @param filename: The template filename.
    @param template_map: A map of letters to numbers.
    @return: An array of string lines for the converted file.'''
    fd = open( filename )
    lines = fd.readlines()
    fd.close()
    new_lines = []

    for line in lines:
        new_line = ''
        if re.match( '[0-9]+ *=', line.strip() ):
            for i in range( len(line) ):
                if line[i] in template_map:
                    new_line = new_line + template_map[line[i]]
                else:
                    new_line = new_line + line[i]
            new_lines.append( new_line )
        else:
            new_lines.append( line )

    return new_lines


def main():
    usage = """\
usage: %prog -c <config_file> -t <template_file>
  Ex. %prog -c template-numbers.conf -t wheel-template.conf > wheel.conf
"""

    parser = OptionParser( usage=usage )
    parser.add_option( '-c', '--config', dest='config' )
    parser.add_option( '-t', '--template', dest='template' )
    (options, args) = parser.parse_args()

    if len( args ):
        parser.error( "The following arguments are unrecognized: %s" % str( args ) )

    if (not options.config) or (not options.template):
        parser.error( "Missing required parameters!" )

    template_map = load_template_conf( options.config )
    output = convert_template( options.template, template_map )
    for line in output:
        print( line.strip( '\n' ) )


if __name__ == "__main__":
    main()
