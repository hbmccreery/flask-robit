import pandas as pd
# import seaborn as sns
from typing import Tuple
import json

from ootp_helper.constants import old_to_new, TABLE_PROPERTIES


def create_player_data(months: list) -> dict:
    dfs = {}

    # read in month-by-month
    for month in months:
        df = pd.read_pickle('pickles/' + month + '.pickle')
        df['HELPER'] = df['HELPER'].str.replace(' ', '').str.replace('/', '-')

        df = df.fillna(0)
        dfs[month] = df

    return dfs


def render_standing_tables(divs: list, standings: pd.DataFrame, cm, league: bool) -> dict:
    div_dict = {}

    if league:
        subset = standings.loc[standings['division'].isin(divs)]
        lg_name = divs[0][:2]

        div_dict[lg_name] = subset.style.set_properties(
            **TABLE_PROPERTIES
        ).set_table_styles(
            [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
        ).background_gradient(
            subset=['pct', 'r_pct', 'diff'],
            cmap=cm,
        ).set_table_attributes(
            "class='sortable'"
        ).hide_index().render()

    else:
        for division in divs:
            # subset div, drop cols we don't want
            subset = standings.loc[standings['division']==division]
            subset.drop('division', axis=1, inplace=True)

            # render table
            div_dict[division] = subset.style.set_properties(
                **TABLE_PROPERTIES
            ).set_table_styles(
                [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
            ).background_gradient(
                subset=['Division', 'WC', 'Playoffs'],
                cmap=cm,
                low=0,
                high=1
            ).hide_index().render()

    return div_dict


def create_benchmarks() -> Tuple[pd.DataFrame, pd.DataFrame]:
    batting_benchmarks = pd.read_csv('csv_data/batting_benchmarks.csv')
    pitching_benchmarks = pd.read_csv('csv_data/pitching_benchmarks.csv')

    return batting_benchmarks, pitching_benchmarks


def read_dist_data() -> pd.DataFrame:
    with open('csv_data/player_dists.json', 'r') as f:
        return pd.DataFrame(json.load(f))