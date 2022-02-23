# Imports
import matplotlib.pyplot as plt

# Change font size for all plots to be larger
plt.rcParams["font.size"] = 20

def plot_wta_wbw(
    comp_data, 
    wta_rank_filter = 9999,
    plot_wbw_scores = True,
    make_axes_1_to_1 = False):

    """
    Plotting function that returns a scatter plot of either WTA ranks against
    WBW scores or WTA ranks against WBW ranks. It uses the array/data returned
    by analyse_data.compare_wbw_wta() for the plot.
    ---------------------------------------------------------------------

    comp_data        = np.array, the data returned by analyse_data.compare_wbw_wta()
    wta_rank_filter  = int, filter data to only include rows with WTA ranks
    less than or equal to this value. 9999 includes all data.
    plot_wbw_scores  = bool, if True will plot WTA ranks against WBW scores, 
    otherwise will plot WTA ranks against WBW ranks.
    make_axes_1_to_1 = bool, if True will rescale axes to be one-to-one.
    """
    # Select all rows where WTA rank is less or equal to the filter
    # Default of 9999 ensures all rows are selected
    plot_data = comp_data[comp_data[:, 1] <= wta_rank_filter]

    # Create plot fig
    fig, ax = plt.subplots(figsize = (24,12))

    # Choose which graph to plot, the WBW scores or the WBW ranks
    # Plot WBW in score format
    if plot_wbw_scores:
        # Plot WTA rank against WBW scores
        ax.scatter(plot_data[:, 1], plot_data[:, 0], alpha = 0.1)
        ax.set_ylabel("WBW Scores",
                        labelpad = 10, 
                        fontdict = {"weight" : "bold",
                                        "size" : 30})

        ax.set_title("Comparison of WTA Ranks with WBW Scores", 
                    fontdict = {"weight" : "bold",
                                "size" : 35},
                                pad = 20)

    # Plot WBW in rank format
    else:
        ax.scatter(plot_data[:, 1], plot_data[:, 2], alpha = 0.1)
        ax.set_ylabel("WBW Ranks", 
                        labelpad = 10, 
                        fontdict = {"weight" : "bold",
                                    "size" : 30})
        ax.set_title("Comparison of WTA Ranks with WBW Ranks", 
        fontdict = {"weight" : "bold",
                    "size" : 35},
                    pad = 20)

    # Add titles and labels
    ax.set_xlabel("WTA Ranks", labelpad = 10, fontdict = {"weight" : "bold",
                                                        "size" : 30})

    # Hide spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Adjust x and y lims if required
    if make_axes_1_to_1:
        ax.set_xlim(0, wta_rank_filter)
        ax.set_ylim(0, wta_rank_filter)