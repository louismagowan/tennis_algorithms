# Imports
from datetime import datetime
import numpy as np
import math

def pre_process(line):
    """
    Pre-processing function to handle some errors that were identified in the data.
    This used to contain a lot more code, but much was removed when the data was updated.
    Only the incorrect naming for Sharapova is left in.
    It takes a line read from the opened csv in the read_data function (below), fixes these errors and returns the fixed line.
    ---------------------------------------------------------------------

    line = str, line from opened csv in read_data
    """
    # There were several pieces of dodgy/incorrect data, much of which was corrected in the data update
    # Sharapova's name at times didn't follow the naming convention for all other players
    line = line.replace('"Sharapova, M."', 'Sharapova M.')

    return line

def handle_dodgy_dates(split_line):
    """
    Helper function for processing the dates of the split lines in process_line (below).
    Many tournaments in this dataset were incorrectly broken up over two years.
    The tournaments that ran from the end of the year (29th, 30th or 31st December) were broken up and given different start dates.
    For example, the 2014 Brisbane Internaional or many of the ASB Classics have different start dates for the same tournament- which is incorrect.
    These rows were just given the 1st of Jan of the next year as the start date for the matches that took place in the following year.

    To rectify this, all the dates 29th-31st Dec are modified in place as 1st Jan for the following year.

    The data was checked to ensure this didn't change tournaments that shouldn't have had their dates changed.
    The end dates were left unchanged as they aren't used later, and serve as a flag for this dodgy data.
    ---------------------------------------------------------------------
    
    split_line = list of dates and strings, from process_line()
    """
    # Handle the dodgy dates. 
    if split_line[1].month == 12 and split_line[1].day in [29, 30, 31]:
        split_line[1] = datetime(split_line[1].year + 1, 1, 1)


def process_line(line):
    """
    Key function for processing lines of data read in from opened csv in read_data(). 
    It returns a list of variables that have been parsed from the line. 
    It also appends a concatenation of tournament and start date to the line
    to help avoid nested looping later on.
    ---------------------------------------------------------------------
    
    line = str, line from opened csv in read_data
    """
    # Remove whitespace and make into list
    clean_line = line.strip().split(",")
    # Parse dates as datetimes
    clean_line[1] = datetime.strptime(clean_line[1], "%Y-%m-%d")
    clean_line[2] = datetime.strptime(clean_line[2], "%Y-%m-%d")
    
    # Handle dodgy dates
    handle_dodgy_dates(clean_line)

    # Parse best of and ranks as ints, making missing ranks zeroes
    clean_line[3] = int(clean_line[3])
    # int float combo is needed as the data is stored in text as string floats
    clean_line[6] = int(float(clean_line[6] or 0))
    clean_line[7] = int(float(clean_line[7] or 0))

    # Change set results in line to help make them into numpy array later
    for set_result in [8,9,10]:
        # Deal with empty sets
        if not clean_line[set_result]:
            clean_line[set_result] = "0-0"
        clean_line[set_result] = clean_line[set_result].split("-")

    # Make set results into numpy array
    results_array = np.array([clean_line[8], clean_line[9], clean_line[10]], dtype=int)
    # Replace results with array and remove now unnecessary columns
    clean_line[8] = results_array
    final_line = clean_line[:9]
    # Re-add the comment
    final_line.append(clean_line[-1])
    # Append a merge of start and tournament name as well,
    # so we can avoid nested loops later on
    final_line.append(final_line[0] + " " + str(final_line[1].date()))

    return final_line


def find_winner_loser(clean_line):
    """
    Takes a processed line of data and determines who the winner and loser were. 
    Modifies the line in place, appending the winner and then the loser.
    It has three procedures to handle: 2 set, 3 set and retirement matches.
    ---------------------------------------------------------------------
    
    clean_line = list, the processed line of text from process_line()
    """
    
    # Handle matches with a retirement
    if clean_line[-2] != 'Completed':
        retiree = clean_line[-2].replace(" Retired", "")
        # If player 1 is the retiree
        if clean_line[4] == retiree:
            # Player 2 is the winner
            clean_line.append(clean_line[5])
            # Player 1 is the loser
            clean_line.append(clean_line[4])
        else:
            # Player 1 is the winner
            clean_line.append(clean_line[4])
            # Player 2 is the loser
            clean_line.append(clean_line[5])
            
    # Handle two set matches
    # Check if third set is [0,0], the recoding of "" / no set played
    elif np.all(clean_line[8][2] == 0):
        # If player 1's result is higher than player 2's
        if clean_line[8][0, 0] > clean_line[8][0, 1]:
            # player 1 is the winner
            clean_line.append(clean_line[4])
            # Player 2 is the loser
            clean_line.append(clean_line[5])
        else:
            # Player 2 is the winner
            clean_line.append(clean_line[5])
            # Player 1 is the loser
            clean_line.append(clean_line[4])
        
    # Handle 3 set matches
    else:
        # Check number of sets where player 1's score minus player 2's is positive
        if ( (clean_line[8][:, 0] - clean_line[8][:, 1] > 0).sum() ) > 1:
            # If this happens more than once, player 1 is the winner
            clean_line.append(clean_line[4])
            # Player 2 is the loser
            clean_line.append(clean_line[5])
        else:
            # Player 2 is the winner
            clean_line.append(clean_line[5])
            # Player 1 is the loser
            clean_line.append(clean_line[4])


def read_data(file_path):
    """
    Reads in a csv at the given file-path. Reads it in and processes it line by line.
    Returns a list of lists, each sublist corresponds to a row in the csv- a list of parsed
    variables. The header row is skipped too.
    Each line has 0 appended to it twice as well, to make bracket reconstruction easier later on
    and to help with algorithms later too.
    ---------------------------------------------------------------------
    
    file_path = Path to csv of tennis data to read in.
    """
    
    clean_data = list()
    # Open connection to file
    raw_data = open(file_path, 'r')
    # Skip header row
    next(raw_data)

    # Read in actual data, clean and append to list
    for line in raw_data:
        # Remove data errors
        line = pre_process(line)
        # Parse data and split into list
        clean_line = process_line(line)
        # Find winner and loser
        find_winner_loser(clean_line)
        # Append 0 to help with bracket reconstruction later
        clean_line.append(0)
        # Append 0 to help with algorithms later too
        clean_line.append(0)

        # Append line to overall data
        clean_data.append(clean_line)

    return clean_data


def read_data_all(list_of_files):
    """
    A wrapper function for read_data that works with a list of file-paths.
    Runs read_data on each of the file-paths.
    Returns a list of lists similar to read_data, except it's all the rows
    (excluding headers) for all the csvs in list_of_files.

    ---------------------------------------------------------------------
    
    list_of_files = list, all the file-paths for the csvs that need to be read in.
    """
    all_data = list()
    # Iterate through files, reading in data for each and appending to overall data
    for file in list_of_files:
        data = read_data(file)
        all_data.extend(data)
        
    return all_data


def find_exceptions(tournaments, years, data):
    """
    Takes the names of round robin tournaments and their corresponding round robin years, builds a dict
    and uses this to find the indexes of data that are or aren't round robin matches.
    Returns the rr_dict used to find these indexes, as well as the indexes themselves.
    ---------------------------------------------------------------------
    
    tournaments = list, the names of the tournaments that had round robins.
    years       = list, the years that correspond to round robins in the previous tournaments,
    contains a list within years for multi-year round robin tournaments.
    data        = list of lists, the csv rows returned from read_data_all.
    """

    # Construct a dict to identify round robin matches with.
    rr_dict = {j:years[i] for i, j in enumerate(tournaments)}
    
    # Iterate through lines, getting the indexes of round robin matches
    rr_indices = list()
    for k,v in rr_dict.items():
        rr_lines = [i for i, val in enumerate(data) 
                    # Check tournament in key
                    if val[0] in k 
                    # and year in values
                    and val[1].year in v]
        # Add round robin indexes to list
        rr_indices.extend(rr_lines)
    
    return rr_dict, rr_indices



def filter_round_robin(tournaments, years, data):
    """
    A wrapper function that works with find_exceptions to split data between round robin and normal matches.
    Takes tournaments and years of round robin matches, uses them
    to filter data to either normal or round robin rows/matches.
    Returns the dict first from find_exceptions() so you can check your round robin years/tournaments are correct.
    It then returns normal match data and round robin match data- in that order.
    ---------------------------------------------------------------------
    
    tournaments = list, the names of the tournaments that had round robins.
    years       = list or range, the years that correspond to round robins in the previous tournaments,
    multi-year consecutive tournaments can be passed as a range, otherwise multi-years should be a list.
    data        = list of lists, the csv rows returned from read_data_all.
    """
    # Get round robin dict and respective indexes of normal/round robin tournaments and years
    rr_dict,  rr_indices = find_exceptions(tournaments, years, data)

    # Filter to normal match data
    normal_data = [data[i] for i in range(len(data)) if i not in rr_indices]
    # Filter to round robin match data
    rr_data = [data[i] for i in range(len(data)) if i in rr_indices]
    
    return rr_dict, normal_data, rr_data



# Useful dictionary to map more meaningful round/stage names to
# in bracket reconstruction
tournament_dict = {1: "Final",
                   2: "Semi-final",
                   3: "Quarter-final",
                   "x": "Third-place Playoff",
                   "group": "Group Stage"
                  }

def reconstruct_brackets(data):
    """"
    Quite an involved function as we can't assume that the order of lines in the data 
    reflect the order in which the matches were played.
    It utilises shallow copying (that inner lists in lists point to the same space in memory / 
    aren't copied recursively) to modify the rows of "data" in place, reconstructing the brackets for each tournament.
    The round and round number of the tournament in each row become/overwrite the last two elements 
    of each row, which were 0 previously. e.g. The 2nd last element might become "Round 1" and the last element
    would be 1. See tournament_dict for the mapping of special case round names like final/semi-final.
    *** Deep-copying could have been used to make the code more intuitive, but this would have
    been at the cost of memory.
    ---------------------------------------------------------------------
    
    data = list, list of lists (rows of data) returned by read_data_all
    """
    # Get unique tournament-years
    tourn_list = set([x[10] for x in data])
    # Iterate through each tournament-year
    for tourn in tourn_list:
        # Select the data for the given tournament-year
        tourn_data = [x for x in data if x[10] == tourn]

        # Calculate the number of stages, log2 of the number of matches + 1
        num_stages = math.log(len(tourn_data)+1, 2)
        # Create a reversed range of this number of stages
        # to iterate through. Reversed to help with neater round naming.
        stage_iterable = list(range(round(num_stages), 0, -1))

        # Iterate through each stage of tournament
        for stage in stage_iterable:

            # Get neat name for round
            if stage in tournament_dict.keys():
                round_name = tournament_dict[stage]
            else:
                round_name = f"Round {stage_iterable.index(stage) + 1}"  
            
            # Get unique losers and winners
            losers = [x[12] for x in tourn_data if x[13] == 0]
            winners = [x[11] for x in tourn_data if x[13] == 0]
            # Set operation to determine the players who've only ever lost
            # for the current stage. e.g. Round 1 losers would only ever have lost
            # and so would only appear in the losers.
            current_stage_losers = set(losers) - set(winners)
            
            # Iterate through tourn_data, updating brackets as needed
            for row in tourn_data:
                # Ignore rows that have already been reconstructed
                if row[13] != 0:
                    continue
                
                # If loser is in the losers of the current stage
                if row[12] in current_stage_losers:
                    # Update with the stage/round name
                    row[13] = round_name
                    # Also update with stage/round number (to help with algorithms later)
                    row[14] = stage_iterable.index(stage) + 1
                
                # Check for 3rd place playoff
                if stage == 2 and row[11] in current_stage_losers and row[12] in current_stage_losers:
                    row[13] = tournament_dict["x"]
                    # Also update with stage/round number (to help with algorithms later)
                    row[14] = stage_iterable.index(stage) + 2


def reconstruct_brackets_rr(rr_data):
    """"
    Similar function to reconstruct_brackets() except it is built to work with round robin data.
    It utilises shallow copying (that inner lists in lists point to the same space in memory / 
    aren't copied recursively) to modify the rows of "rr_data" in place.
    The round and round number of the tournament in each row become/overwrite the last two elements of each row.
    Group stage matches are given a round number of 1, similar to "Round 1" matches in normal data.

    ---------------------------------------------------------------------
    
    data = list, list of lists (rows of data) returned by read_data_all
    """

    # Get unique tournament-years
    tourn_list = set([x[10] for x in rr_data])
    # Iterate through each tournament-year
    for tourn in tourn_list:
        # Select the data for the given tournament-year
        tourn_data = [x for x in rr_data if x[10] == tourn]

        # Get unique list of all players
        all_players = [x[4] for x in tourn_data]
        all_players.extend([x[5] for x in tourn_data])
        # Drop duplicates
        all_players = list(set(all_players))
        # Create a dict to count the number of matches each player played
        match_counter = {x:0 for x in all_players}

        # Update the match_counter each time the player played
        for row in tourn_data:
            # Check if they were player 1
            try:
                # Increment matches played by 1 if so
                match_counter[row[4]] += 1    
            except KeyError:
                pass
            # Check if they were player 2
            try:
                # Increment matches played by 1 if so
                match_counter[row[5]] += 1
            except KeyError:
                pass

        # Find min and max matches played
        # The if v > 2 statement is needed to account for
        # "alternates" where a player subs in for a retiree in the group stage
        min_matches = min([v for v in match_counter.values() if v > 2])
        max_matches = max(match_counter.values())

        # Find the players who lost in group stages/the group stage matches
        group_stage_losers = [k for k,v in match_counter.items() if v <= min_matches]
        # Find the finalists / final
        finalists = [k for k,v in match_counter.items() if v == max_matches]

        # Counters to prevent players who played in both group and knockouts
        # from being recorded as playing in duplicate knockouts
        final_counter = 1
        semi_final_counter = 2

        # Iterate through data and update the stage/round variable
        for row in tourn_data:
            # Identify group stage matches
            if row[4] in group_stage_losers or row[5] in group_stage_losers:
                # Update round variable
                row[13] = tournament_dict["group"]
                # Also update the round number variable
                row[14] = 1

            # Identify finals
            elif row[4] in finalists and row[5] in finalists:
                # Need this if statement to account for finalists who played each other in both
                # a group stage and the final. These rows are impossible to distinguish without making an
                # assumption about the order of the data so the later row that is encountered is assumed 
                # to be the final, as per Patrick's response on Moodle
                if final_counter == 1:
                    # Update round variable
                    row[13] = tournament_dict[1]
                    # Also update the round number variable
                    row[14] = 3
                    final_counter -= 1
                    # Shallow copy of first-encountered row where finalists played 
                    final_lineup_repeated = row
                else:
                    # If finalists played more than once, update the later game/row encountered
                    # as the final and re-update the earlier row encountered to be a group match
                    row[13] = tournament_dict[1]
                    row[14] = 3
                    # Reupdate the earlier row
                    final_lineup_repeated[13] = tournament_dict["group"]
                    final_lineup_repeated[14] = 1
                
            # Identify semi-finals, matches containing finalists and not containing group stage losers
            elif (row[4] in finalists or row[5] in finalists) and row[13] == 0:
                # Same logic as if statement for finalists
                if semi_final_counter == 2:
                    row[13] = tournament_dict[2]
                    row[14] = 2
                    semi_final_counter -= 1
                    # Shallow copy of first-encountered row where semi-finalists played 
                    semi_final_lineup_repeated = row

                # Need to add an extra increment for semi-finals
                elif semi_final_counter == 1:
                    row[13] = tournament_dict[2]
                    row[14] = 2
                    semi_final_counter -= 1

                # If semi-finalists played more than once, update the later game/row encountered
                # as the semi-final and re-update the earlier row encountered to be a group match   
                else:
                    row[13] = tournament_dict[2]
                    row[14] = 2
                    # Reupdate the first row
                    semi_final_lineup_repeated[13] = tournament_dict["group"]
                    semi_final_lineup_repeated[14] = 1

            # This bit is added in as certain semi-finalists who played in the group stage but not finals
            #  weren't being counted as group stage losers and so were having their round and round number be left as zero
            else:
                row[13] = tournament_dict["group"]
                row[14] = 1

def reconstruct_all_brackets(normal_data, rr_data):
    """"
    Wrapper function for reconstruct_brackets() and reconstruct_brackets_rr().
    It modifies normal_data and rr_data in place, overwriting the last two elemenents of each row
    with the round of that match in the tournament in the 2nd last element and the round number in the last element.
    It returns a combined list (list of lists/rows) of normal_data and rr_data with all brackets reconstructed.
    The naming convention for rounds is "Final", "Semi-final", "Quarter-final" and then "Round {n}", where n is the round number
    e.g. "Round 1". Group stage matches in round robin data are "Group Stage."
    ---------------------------------------------------------------------
    
    normal_data = list, list of lists (rows of normal data) returned by filter_round_robin
    rr_data     = list, list of lists (rows of round robin data) returned by filter_round_robin
    """

    all_data = list()
    # Reonstruct the brackets for both normal and round robin data
    reconstruct_brackets(normal_data)
    reconstruct_brackets_rr(rr_data)

    # Add the newly added data to the overall data list
    all_data.extend(normal_data)
    all_data.extend(rr_data)

    return all_data


# Useful dictionary to help select particular variables in a row
# More intuitive than using indexes
col_dict_cols = ["Tournament", 'Start Date', 'End Date', 'Best Of',
                'Player 1', 'Player 2', 'Rank 1', 'Rank 2',
                'Results', 'Comment', 'Tournament-Start', 'Winner',
                'Loser', 'Round', 'r']
# Zip the cols into a dictionary to map with
col_dict = dict(zip(col_dict_cols, range(len(col_dict_cols))))