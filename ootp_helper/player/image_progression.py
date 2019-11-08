import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_progression(helper, subset, months):
    prog_months = months
    
    if subset['Age'].iloc[0] < 26:
        if(subset['bwar_mean'].iloc[0] >= subset['pwar_mean'].iloc[0]):
            secondary = 'woba_mean'
        else:
            secondary = 'fip_mean'
    else:
        if(subset['bwar'].iloc[0] >= subset['pwar'].iloc[0]):
            secondary = 'woba'
        else:
            secondary = 'fip'

    # initialize figure, set plot style
    plt.style.use('seaborn-bright')
    fig, ax1 = plt.subplots()

    # plotting things
    label = 'old grade'
    ratings = subset['old grade'].iloc[::-1]

    # subset the months if the player was generated before
    if len(ratings) != len(prog_months):
        prog_months = prog_months[:len(ratings)]
        
    ax1.plot(range(0,len(prog_months)), ratings, label = label, linewidth = 4, color = 'b')

    # add legends, axis labels
    ax1.legend(ncol = 3, borderaxespad=0., prop={'size': 12}, loc = 1)
    xlab_names = prog_months
    plt.xticks(range(0,len(prog_months)), reversed(xlab_names))
    plt.xlabel('Month')
    plt.ylabel('Old Grade')

    # create axis to plot secondary data on
    ax2 = ax1.twinx()

    label = secondary
    ratings = subset[secondary].iloc[::-1]
    ax2.plot(range(0,len(prog_months)), ratings, label = label, linewidth = 4, color = 'r')
    #ax2.plot(range(len(filenames)-1, len(filenames)+3), np.insert(stepwise_fit.predict(n_periods=3), 0, prog2[player][-1]), linewidth = 4, color='r', ls=':')

    # want lower FIP to go up
    if(secondary == 'fip_mean' or secondary == 'fip'):
        plt.gca().invert_yaxis()

    # legends, axis label
    ax2.legend(ncol = 3, borderaxespad=0., prop={'size': 12}, loc = 2)
    ax1.grid(True)
    ax1.set_facecolor('lightgray')
    plt.ylabel(secondary)

    # output
    fig.set_size_inches(10,7.5)
    resource_path = os.path.join(os.getcwd(), 'images\\' + helper + '.png')
    plt.savefig(resource_path)

    # make sure we're not holding onto too many images
    plt.clf()
    plt.close()

    return
