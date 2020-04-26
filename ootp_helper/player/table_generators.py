from typing import Tuple, List

import pandas as pd
import json

from ootp_helper.player.run_calculators import runs_to_ratings, ratings_to_runs
from ootp_helper.color_maps import defense_stat_colors
from ootp_helper.constants import DEF_RAT_COLUMNS, TABLE_PROPERTIES, IND_PIT_COLUMNS, IND_PIT_POT_COLUMNS


def generate_defense_table(stats: pd.DataFrame, ratings: pd.DataFrame) -> Tuple[str, str, str]:
    # make a row of col names
    stats = stats.append(pd.DataFrame([runs_to_ratings(stats.iloc[0])], columns=stats.columns.values))

    stats.columns = [col.replace('_runs', '') for col in stats.columns]

    # engine ratings -> in game
    stats = pd.concat([stats, ratings.apply(lambda x: x, axis=0)])
    stats = stats.append(ratings_to_runs(stats.iloc[2]), ignore_index=True)
    stats = stats.applymap(int)

    # get their best position
    best_position = stats.iloc[0].idxmax()

    # mess around with the table
    stats.insert(0, 'Type', ['POT ZR', 'potential', 'current', 'CUR ZR'])
    stats = stats.reindex([3, 0, 2, 1])

    # put them into a JSON
    rendered_ratings = stats.iloc[[2, 3]].set_index('Type').T.reset_index().to_json(orient='records')

    # make the table
    rendered_stats = stats.iloc[[0, 1]].style.applymap(
        defense_stat_colors,
        subset=DEF_RAT_COLUMNS
    ).set_properties(
        **TABLE_PROPERTIES
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).hide_index().render()

    return rendered_ratings, rendered_stats, best_position


def generate_rating_table(ratings: pd.DataFrame, is_batter: bool) -> str:

    # get cur, pot
    if is_batter:
        cur_rats = ratings[ratings.columns[0:5]]
        pot_rats = ratings[ratings.columns[5:]]

    else:
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


def generate_other_table(ratings: pd.DataFrame) -> str:
    # minor reshaping
    reshaped_rats = ratings.reset_index()
    reshaped_rats = reshaped_rats.applymap(int)
    reshaped_rats = reshaped_rats.append(reshaped_rats)

    # get rid of index
    reshaped_rats = reshaped_rats[reshaped_rats.columns[1:]]

    reshaped_rats.insert(0, 'Type', ['current', 'potential'])

    # put them into a JSON
    rendered_ratings = reshaped_rats.set_index('Type').T.reset_index().to_json(orient='records')

    return rendered_ratings


def generate_ind_pitch_table(ratings: pd.DataFrame) -> str:
    ratings = ratings.iloc[0]
    pitch_cur = ratings[IND_PIT_COLUMNS]
    pitch_pots = ratings[IND_PIT_POT_COLUMNS]

    valid_ind = list(pitch_pots.values > 20)

    pitch_cur = pitch_cur[valid_ind]
    pitch_pots = pitch_pots[valid_ind]
    pitch_pots.index = pitch_cur.index

    pitch_df = pd.concat([pitch_cur, pitch_pots], axis=1).reset_index()
    pitch_df.columns = ['index', 'current', 'potential']
    pitch_df[['current', 'potential']] = pitch_df[['current', 'potential']].applymap(int)

    return pitch_df.to_json(orient='records')


def generate_splits_table(ratings: dict, column_names: List) -> dict:
    return {
        'r': [
            {'index': key, 'current': int(ratings[key])}
            for key
            in [col + ' vR' for col in column_names if ' ' not in col]
        ],
        'l': [
            {'index': key, 'current': int(ratings[key])}
            for key
            in [col + ' vL' for col in column_names if ' ' not in col]
        ],
    }