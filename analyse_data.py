# Imports
from prep_data import col_dict
from datetime import datetime, timedelta
import numpy as np


def filter_year(data,
                 year_condition,
                 year_col = "Start Date"):
    """
    Function for filtering data to a certain year, range of years 
    or list of years.
    It returns a list of lists, the filtered data for the selected years.
    ---------------------------------------------------------------------
    
    data           = list, list of lists (rows of data) returned by e.g. read_data_all
    year_condition = list or range of years that you want to filter to
    year_col       = string, the date column you want to select with col_dict to filter on
    """

    # Return all data where the chosen date column falls within the given year selection
    return [row for row in data if row[col_dict[year_col]].year in year_condition]



def filter_condition(data,
                col1, condition1,
                col2 = None, condition2 = None,
                logical_and = True,
                logical_or = False):

    """
    Function for filtering data by up to two conditions. If only one condition
    is passed, it only filters by that one condition. If two are passed,
    you can choose which operator to apply to the two conditions (e.g AND or OR)
    Columns can be selected by their string names using the col_dict from prep_data.
    If you want to filter on a tournament stage, see the tournament_dict from
    prep_data for the naming conventions of rounds.

    It returns a list of lists, the filtered data for the selected conditions.
    ---------------------------------------------------------------------
    
    data        = list, list of lists (rows of data) returned by e.g. read_data_all
    col1        = string, column that you want to filter on
    condition1  = string, the condition that you want to filter column 1 on
    col2        = string, 2nd column that you want to filter on
    condition2  = string, the condition that you want to filter column 2 on
    logical_and = bool, make true if you want to filter with AND on both conditions
    logical_or = bool, make true if you want to filter with OR on both conditions.
    Remember to make logical_and = False if you use this.
    """
    # Return data if filtered on condition 1 AND condition 2
    if logical_and and condition1 and condition2:
        return [row for row in data if row[col_dict[col1]] == condition1 and row[col_dict[col2]] == condition2]

    # Return data if filtered on condition 1 OR condition 2
    elif logical_or and condition1 and condition2:
        return [row for row in data if row[col_dict[col1]] == condition1 or row[col_dict[col2]] == condition2]

    # Return data if filtered on ONLY one condition, default is condition 1
    elif condition1:
        return [row for row in data if row[col_dict[col1]] == condition1]

    # Let the user know their conditions need to be corrected 
    else:
        print("Conditions not properly specified")



def selector(data,
            value1 = "Winner",
            value2 = None):
    """
    Helper function to return the required value or two values from "data".
    If only one value is passed it returns a list of those values.
    If two values are passed it returns a list of lists, where each sublist
    is those two values.
    ---------------------------------------------------------------------

    data   = list, list of lists (rows of data) returned by e.g. read_data_all
    value1 = string, column that you want to return
    value2 = string, the 2nd column that you want to return
    """
    # Return data if only one value is needed
    if not value2:
        return [x[col_dict[value1]] for x in data]

    # Return data if two values are needed
    else:
        return [[x[col_dict[value1]], x[col_dict[value2]]] for x in data]


def get_unique_players(data):
    """
    Helper function to return a list of the unique players in "data".
    ---------------------------------------------------------------------

    data   = list, list of lists (rows of data) returned by e.g. read_data_all
    """
    # Get all player 1s
    players = [x[4] for x in data]
    # Get all player 2s
    players2 = [x[5] for x in data]
    # Add the two together
    players.extend(players2)
    # Remove duplicates
    unique_players = list(set(players))

    return unique_players


def calc_ww(data):
    """
    Function to rank the players in "data" according to the Winners Win algorithm.
    It returns a list of tuples where each tuple contains the player's name
    and the amount of matches they won.
    The list has been sorted in descending order of matches won.
    ---------------------------------------------------------------------

    data   = list, list of lists (rows of data) returned by e.g. read_data_all
    """

    # Get list of unique players from data
    unique_players = get_unique_players(data)
    # Make dictionary with unique players as keys, match counts as values
    match_counter = {x:0 for x in unique_players}

    # Iterate through data
    for row in data:
        # Exception is rare, so try except is faster than if statement
        try: 
            match_counter[row[11]] += 1
        except KeyError:
            pass
    # Order the dictionary descending by number of matches won
    matches_won = sorted(match_counter.items(), 
                        # More wins is best
                        reverse = True,
                        # Make the sort key the dict value, not dict key
                        key = lambda item: item[1])
    
    return matches_won


def calc_wdl(data):
    """
    Function to rank the players in "data" according to the Winners Don't Lose algorithm.
    It returns a list of tuples where each tuple contains the player's name
    and the score generated by this algorithm for them.
    The list has been sorted in descending order of the algorithm score,
    so best ranked players are at the start of the list.
    ---------------------------------------------------------------------

    data   = list, list of lists (rows of data) returned by e.g. read_data_all
    """
    # Get list of unique players from data
    unique_players = get_unique_players(data)
    # Make dictionary with unique players as keys, match counts as values
    wdl_dict = {x:0 for x in unique_players}

    # Iterate through data
    for row in data:
        # Update winners with r
        try:
            wdl_dict[row[11]] += row[14]
        except KeyError:
            pass
        # Update losers with -1/r
        try:
            wdl_dict[row[12]] -= (1 / row[14])
        except KeyError:
            pass

    # Order the dictionary descending by algorithm score
    wdl_dict_sorted = sorted(wdl_dict.items(), 
                        # Higher score is best
                        reverse = True,
                        # Make the sort key the dict value, not dict key
                        key = lambda item: item[1])
    
    return wdl_dict_sorted


def calc_wbw(data,
             display_convergence = True, 
             stopping_threshold = 0.00000000001):
    """
    Function to rank the players in "data" according to the Winners Beat Winners algorithm.
    It returns a list of tuples where each tuple contains the player's name
    and the score generated by this algorithm for them.
    The list has been sorted in descending order of the algorithm score,
    so best ranked players are at the start of the list.
    ---------------------------------------------------------------------

    data = list, list of lists (rows of data) returned by e.g. read_data_all

    display_convergence = bool, set true if you want to see which loop
    the algorithm converged on

    stopping_threshold = float, the absolute minimum difference between
    smallest and largest wbw_scores from one iteration to the next that is
    used to determine if the algorithm has converged
    """
    # Get the unique list of tennis players in the data
    unique_players = get_unique_players(data)
    n = len(unique_players)
    # Make dictionary with unique players as keys, 1 / number unique players as values
    wbw_dict = {x : (1 / n) for x in unique_players}

    # Get dict of players that each player lost to
    beaten_by_dict = dict()
    for k in unique_players:
        beaten_by = [x[11] for x in data if x[12] == k]
        beaten_by_dict[k] = beaten_by

    # Run algorithm until convergence / stopping criteria reached
    for i in range(1000):
        
        # Get separate dict for shares of scores to be added to
        shares_dict = {x : 0 for x in beaten_by_dict.keys()}
        
        # Get max and min values for stopping condition
        max_score_pre = max([v for v in wbw_dict.values()])
        min_score_pre = min([v for v in wbw_dict.values()])
        
        # Iterate through player and the players who beat them
        for k, victors in beaten_by_dict.items():
            # If they lost at some point (likely)
            if not len(victors) == 0: 
                # Calculate share of score
                share_of_score = (wbw_dict[k] / len(victors))
                
                # Pass this share of score to everyone who beat them
                # Giving multiple shares to those who beat them multiple times
                for victor in victors:
                    shares_dict[victor] += share_of_score
                    
            # Handle case where player never lost
            else:
                # Pass current score to themselves
                wbw_dict[k] += wbw_dict[k]  

        # Updates scores to be sum of shares received and rescale
        wbw_dict = {k : ((v * 0.85) + (0.15 / n)) for k, v in shares_dict.items()}

        # Stopping criteria- have the max and min values changed much?
        max_score_post = max([v for v in wbw_dict.values()])
        min_score_post = min([v for v in wbw_dict.values()])
        
        # Enforce stopping criteria
        if abs(max_score_post - max_score_pre) < stopping_threshold and abs(min_score_post - min_score_pre) < stopping_threshold:
            if display_convergence:
                print(f"Converged on loop {i}")
            break
        
    # Order the dictionary descending by algorithm score
    wbw_dict_sorted = sorted(wbw_dict.items(), 
                        # Higher score is best
                        reverse = True,
                        # Make the sort key the dict value, not dict key
                        key = lambda item: item[1])
    
    return wbw_dict_sorted


def compare_wbw_wta(data, all_data, stopping_threshold = 0.00000000001):
    """
    Function to compare a player's WTA ranking at the start of each tournament in "data" with the
    WBW score that is generated for that tournament (based on the player's performance
    in the previous 52 weeks.)

    It returns an array of 3 columns: The player's WBW score for that tournament,
    their WTA rank for that tournament, and the rank form of their WBW score for
    that tournament (e.g. The player with highest WBW score gets rank 1).
    This is included to help make visualisation more intuitive later on.

    Note: Not all players have WTA rankings, so can't be included.
    ---------------------------------------------------------------------

    data = list, list of lists (rows of data) that have been filtered 
    in some way, e.g. To only include data from 2008 onwards

    all_data = list, list of lists (rows of data) returned by e.g. read_data_all

    stopping_threshold = float, the absolute minimum difference between
    smallest and largest wbw_scores from one iteration to the next that is
    used to determine if the algorithm has converged
    """
    all_ranks = list()
    all_ranks_alt = list()

    # Get list of tournaments in particular years to iterate through
    tourn_list = set([x[10] for x in data])

    # Iterate through tournament-years
    for tourn in tourn_list:
        # Select data for that tournament in that year to get WTA ranks
        tourn_data = [x for x in data if x[10] == tourn]
        
        start_date = datetime.strptime(tourn.split()[-1], "%Y-%m-%d")
        weeks_52_prior = start_date - timedelta(weeks = 52)
        # Select data for 52 weeks before and up to that tournament in that year
        # This includes the 2007 data that we use to initialise our 2008 estimates with
        tourn_wbw_data = [x for x in all_data if x[1] >= weeks_52_prior and x[1] <= start_date]
        tourn_wbw_scores = calc_wbw(tourn_wbw_data, 
                                    display_convergence = False,
                                    stopping_threshold = stopping_threshold)

        # Create dict of players as keys with WBW scores as values in a list
        # It's stored as a list so that the WTA rank can be appended to it
        ranks_data = {k : [v] for k,v in tourn_wbw_scores}
        # An alternative way of storing the WBW scores, puts them into rank format
        # for more intuitive comparison with WTA ranks.
        ranks_data_alt = {k : [rank] for rank, k in enumerate(sorted(ranks_data, key = ranks_data.get, reverse = True), 1)}
        
        # Append the WTA ranks to ranks_data dict
        # Taking their first recorded rank as the rank if they changed mid tournament
        for row in tourn_data:
            # Add player 1's WTA rank, if it's not already been added (e.g. take their first rank)
            # Doesn't add players who lacked a WTA rank (coded as 0 currently)
            if len(ranks_data[row[4]]) == 1 and row[6] != 0:
                ranks_data[row[4]].append(row[6])
                # Also add it to the alternative ranks data
                ranks_data_alt[row[4]].append(row[6])
            
            # Add player 2's WTA rank, if it's not already been added (e.g. take their first rank)
            # Doesn't add players who lacked a WTA rank (coded as 0 currently)
            if len(ranks_data[row[5]]) == 1 and row[7] != 0:
                ranks_data[row[5]].append(row[7])
                # Also add it to the alternative ranks data
                ranks_data_alt[row[5]].append(row[7])

        # Select only the ranks for players in the previous 52 weeks, but also
        # who actually played in the current tournament-year
        tourn_ranks = [v for v in ranks_data.values() if len(v) == 2]
        tourn_ranks_alt = [v for v in ranks_data_alt.values() if len(v) == 2]
        # Add tournament specific data to overall data
        all_ranks.extend(tourn_ranks)
        all_ranks_alt.extend(tourn_ranks_alt)
    # Make into arrays and combine to get WBW data in both score and rank format
    all_ranks = np.array(all_ranks)
    all_ranks_alt = np.array([x[0] for x in all_ranks_alt])

    # return the combined data
    return np.column_stack((all_ranks, all_ranks_alt))