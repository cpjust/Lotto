What's in this repo:

# lotto.py
This is the main program that simulates playing many lottery games, taking the winnings from one game and using the money to buy extra tickets for the next game...  After iterating through all the games it prints a grand total of how much you won over all the games...

usage: ./lotto.py -c <config_file> -t <tickets_file> -w <winning_numbers_file> [-q <quick_pick_file>] [-o <quick_pick_output_file>] [-T] [-v]

   or: ./lotto.py -c <config_file> -o <quick_pick_output_file> [-v]

    -c, --config             The main config file.
    -t, --tickets            The tickets config file.
    -o, --output             Will dump some quick pick numbers into this file.
    -w, --winning-numbers    The winning numbers csv file.
    -d, --debug              Debug mode.
    -T, --text               Read tickets_file as a text file instead of a config file.
    -v, --verbose            Enable verbose mode.
    
    Ex.  ./lotto.py -c lotto.conf -t wheel-15.conf -w winning_numbers.csv

# make-wheel.py
Currently it's an exact copy of template-to-numbers.py.  I haven't touched this code in 9 years, so I forgot what I was going to do with this script.

usage: ./make-wheel.py -c <config_file> -t <template_file>

    Ex. ./make-wheel.py -c template-numbers.conf -t wheel-template.conf > wheel.conf

# template-to-numbers.py
This program takes a number template and wheel template and converts it into a wheel.conf file that you pass to the lotto.py script.

usage: ./template-to-numbers.py -c <config_file> -t <template_file>

    Ex. ./template-to-numbers.py -c template-numbers.conf -t wheel-template.conf > wheel.conf

# num_generator.py
This generates all possible combinations of ticket numbers for a given lotto game (ex. 49 possible numbers with 6 numbers per ticket).

usage: ./num_generator.py --min <min_num> --max <max_num> --num <num>

    Ex. ./num_generator.py -m 1 -M 49 -n 6

# odds.py
This program can calculate the odds of winning a certain prize (3 numbers, 4 numbers...) for a lottery with a certain number of numbers to choose from and certain number of numbers per ticket.

usage: %prog --max <max_num> --num <num> --prize <num>

  where:
  
    <max_num> is the max numbers you can pick in the game
    <num> is how many numbers you pick in the game.
    <prize> is how many numbers you need to get right for a certain prize (ex. 2 numbers = free ticket)

Example: %prog -m 49 -n 6 -p 2
Will return the odds of getting 2 numbers right for lotto 6/49.

### lotto.conf
Contains config values for lotto.py.  Currently setup to play Lotto MAX.

### quick-picks-*.txt
These files contain pre-calculated quick-pick numbers.

### wheel-#.conf
These files contain lotto wheels that you can pass to the lotto.py program.
They are the output of the make-wheel.py or template-to-numbers.py programs.

### wheel-template*.conf
These files contain templates for generating the wheel-#.conf files.

### winning_numbers.csv
This contains all the Lotto MAX winning numbers, which you pass to lotto.py.