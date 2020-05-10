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


def create_standings() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # read standings from csv, create team link
    standings = pd.read_csv('csv_data/finances.csv')

    standings['Name'] = standings['Team']
    standings['Team'] = standings['Team'].apply(
        lambda x: "<a  href='./team/{}'><img height='50px' src=../static/team_logos/{}.png></a>".format(x, x)
    )

    standings['pct'] = standings['W'] / (standings['W'] + standings['L'])
    standings['pct'] = standings['pct'].round(3)
    standings['r_pct'] = standings['rW'] / (standings['rW'] + standings['rL'])
    standings['r_pct'] = standings['r_pct'].round(3)
    standings['diff'] = standings['W'] - standings['rW']
    standings = standings.sort_values('pct', ascending=False)

    money_cols = ['Payroll', 'Budget', 'TotalRevenue', 'GateRevenue', 'SeasonTickets', 'PlayoffRevenue',
                  'MerchRevenue', 'MediaRevenue', 'RevenueSharing', 'Cash']

    for col in money_cols:
        standings[col] = standings[col].map('${:,.0f}'.format)

    standings_subset = standings[['Team', 'division', 'Name', 'Payroll', 'W', 'L', 'pct', 'rW', 'rL', 'r_pct', 'diff']]

    # color map for rendered tables
    # cm = sns.diverging_palette(240, 10, as_cmap=True)

    # switch for leauge/division tables
    # lg = True

    # al_standing_tables = render_standing_tables(['ALE', 'ALC', 'ALW'], standings_subset, cm, lg)
    # nl_standing_tables = render_standing_tables(['NLE', 'NLC', 'NLW'], standings_subset, cm, lg)

    al_standing_tables = pd.DataFrame()
    nl_standing_tables = pd.DataFrame()

    return al_standing_tables, nl_standing_tables, standings


def create_benchmarks() -> Tuple[pd.DataFrame, pd.DataFrame]:
    batting_benchmarks = pd.read_csv('csv_data/batting_benchmarks.csv')
    pitching_benchmarks = pd.read_csv('csv_data/pitching_benchmarks.csv')

    return batting_benchmarks, pitching_benchmarks


def read_dist_data() -> pd.DataFrame:
    with open('csv_data/player_dists.json', 'r') as f:
        return pd.DataFrame(json.load(f))