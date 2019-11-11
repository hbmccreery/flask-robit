import pandas as pd

from ootp_helper.player.run_calculators import runs_to_ratings, ratings_to_runs
from ootp_helper.color_maps import defense_stat_colors
from ootp_helper.constants import DEF_RAT_COLUMNS, TABLE_PROPERTIES

def generate_defense_table(stats: pd.DataFrame, ratings: pd.DataFrame) -> str:
    # make a row of col names
    stats = stats.append(pd.DataFrame([runs_to_ratings(stats.iloc[0])], columns=stats.columns.values))

    def_cols = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
    stats.columns = [col.replace('_runs', '') for col in stats.columns]

    # engine ratings -> in game
    stats = pd.concat([stats, ratings.apply(lambda x: ((x - 100)*.3) + 50)], axis=0)
    stats = stats.append(ratings_to_runs(stats.iloc[2]), ignore_index=True)
    stats = stats.applymap(int)

    # get their best position
    best_position = stats.iloc[0].idxmax()

    # mess around with the table
    stats.insert(0, 'Type', ['POT ZR', 'potential', 'current', 'CUR ZR'])
    stats = stats.reindex([3,0,2,1])

    # put them into a JSON
    rendered_ratings = stats.iloc[[2,3]].set_index('Type').T.reset_index().to_json(orient='records')

    # make the table
    rendered_stats = stats.iloc[[0,1]].style.applymap(
        defense_stat_colors,
        subset=DEF_RAT_COLUMNS
    ).set_properties(
        **TABLE_PROPERTIES
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).hide_index().render()

    return rendered_ratings, rendered_stats, best_position


def generate_bat_table(ratings: pd.DataFrame, helper: str) -> str:

    # get cur, pot
    cur_rats = ratings[ratings.columns[0:5]]
    pot_rats = ratings[ratings.columns[5:]]

    # change col names
    pot_rats.columns = [col[:-2] for col in pot_rats.columns]

    # put into one df
    reshaped_rats = cur_rats.append(pot_rats, ignore_index=True)
    reshaped_rats = reshaped_rats.reset_index()
    reshaped_rats = reshaped_rats.applymap(int)

    # get rid of index, add in names
    reshaped_rats = reshaped_rats[reshaped_rats.columns[1:]]
    reshaped_rats.insert(0, 'Type', ['current', 'potential'])

    # put them into a JSON
    rendered_ratings = reshaped_rats.set_index('Type').T.reset_index().to_json(orient='records')

    return rendered_ratings


def generate_pit_table(ratings: pd.DataFrame, helper: str) -> str:
    cur_rats = ratings[ratings.columns[0:3]]
    pot_rats = ratings[ratings.columns[3:]]

    # change col names
    pot_rats.columns = [col[:-2] for col in pot_rats.columns]

    # put into one df
    reshaped_rats = cur_rats.append(pot_rats, ignore_index=True)
    reshaped_rats = reshaped_rats.reset_index()
    reshaped_rats = reshaped_rats.applymap(int)

    # get rid of index, add in names
    reshaped_rats = reshaped_rats[reshaped_rats.columns[1:]]
    reshaped_rats.insert(0, 'Type', ['current', 'potential'])

    # put them into a JSON
    rendered_ratings = reshaped_rats.set_index('Type').T.reset_index().to_json(orient='records')

    return rendered_ratings


def generate_other_table(ratings: pd.DataFrame, helper: str) -> str:
    # minor reshaping
    reshaped_rats = ratings.reset_index()
    reshaped_rats = reshaped_rats.applymap(int)
    reshaped_rats = reshaped_rats.append(reshaped_rats) # cur = pot

    # get rid of index
    reshaped_rats = reshaped_rats[reshaped_rats.columns[1:]]

    # editor -> in game
    reshaped_rats = reshaped_rats.apply(lambda x: ((x - 100) * 3/10) + 50)
    reshaped_rats = reshaped_rats.apply(round)

    reshaped_rats.insert(0, 'Type', ['current', 'potential'])

    # put them into a JSON
    rendered_ratings = reshaped_rats.set_index('Type').T.reset_index().to_json(orient='records')

    return rendered_ratings
