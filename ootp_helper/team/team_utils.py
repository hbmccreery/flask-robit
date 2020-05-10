import pandas as pd
import numpy as np
from itertools import product, groupby
from typing import List, Tuple

from ootp_helper.player.run_calculators import calculate_batting_runs, calculate_pitching_runs
from ootp_helper.player.table_generators import generate_splits_table
from ootp_helper.constants import BAT_RAT_COLUMNS, PIT_RAT_COLUMNS, TABLE_PROPERTIES


def add_splits_data(records: List[dict]) -> List[dict]:
    [
        record.update({
            'woba_rhp': calculate_batting_runs(generate_splits_table(record, BAT_RAT_COLUMNS)['r'])[0],
            'woba_lhp': calculate_batting_runs(generate_splits_table(record, BAT_RAT_COLUMNS)['l'])[0],
            'fip_rhb': calculate_pitching_runs(generate_splits_table(record, PIT_RAT_COLUMNS)['r'])[0],
            'fip_lhb': calculate_pitching_runs(generate_splits_table(record, PIT_RAT_COLUMNS)['l'])[0],
        })
        for record
        in records
    ]

    return records


def generate_pitcher_lineup(team_df: pd.DataFrame) -> str:
    lineup_pit_cols = ['HELPER', 'Name', 'ip', 'fip', 'pwar']

    sp = team_df.nlargest(5, 'pwar')[lineup_pit_cols]
    rp = team_df.loc[~team_df['HELPER'].isin(sp['HELPER'])].nsmallest(8, 'fip', keep='last')[lineup_pit_cols]

    sp['POS'] = 'SP'
    rp['POS'] = 'RP'

    pitching = sp.append(rp, ignore_index=True)
    pitching.drop('HELPER', axis=1, inplace=True)

    pitching = pitching[['POS', 'Name', 'fip', 'ip']].round(2)

    return pitching.style.set_properties(
        **(dict(TABLE_PROPERTIES, **{'font-size': '1.5em'}))
    ).hide_index().render()


def create_split_lineup(team_df: pd.DataFrame, split_name: str) -> pd.DataFrame:
    # get all possible lineups sets of player/woba/WAR (w/ duplicates)
    # boy that is badly formatted
    potential_pairs = team_df.sort_values('woba', ascending=False).head(15).apply(
        lambda x: [
            (
                y,
                x['HELPER'],
                x['Name'],
                x['woba'],
                x['woba_lhp'],
                x['woba_rhp'],
                x['bwar']
            )
            for y
            in x['pot_pos']
        ], axis=1
    ).tolist()

    potential_pairs = list(filter(lambda x: x != [], potential_pairs))

    ungrouped_items = [item for sublist in potential_pairs for item in sublist]
    ungrouped_items.sort(key=lambda x: x[0])

    groups = []
    unique_keys = []

    for key, group in groupby(ungrouped_items, lambda x: x[0]):
        groups.append(list(group))  # Store group iterator as a list
        unique_keys.append(key)

    potential_lineups = [x for x in product(*groups)]

    lineup_woba = []

    for lineup in potential_lineups:
        if len(set([x[1] for x in lineup])) != 8:
            lineup_woba.append(0)
        else:
            lineup_woba.append(sum([x[3] for x in lineup]))

    # noinspection PyTypeChecker
    optimal_lineup = pd.DataFrame(list(potential_lineups[np.argmax(lineup_woba)]))
    optimal_lineup.columns = ['lineup_pos', 'HELPER', 'Name', 'woba', 'woba_lhp', 'woba_rhp', 'bwar']
    optimal_lineup = optimal_lineup.sort_values('woba', ascending=False)

    bench = team_df.loc[~team_df['HELPER'].isin(optimal_lineup['HELPER'])].nlargest(5, 'woba', keep='last')
    bench = bench[['HELPER', 'Name', 'bwar', 'woba', 'woba_lhp', 'woba_rhp']]
    bench['lineup_pos'] = 'PH'

    return optimal_lineup.append(bench, ignore_index=True)


def generate_batting_lineup(team_df: pd.DataFrame) -> str:
    team_df['optim_pos'] = '-'
    team_df['pot_pos'] = ''
    team_df['pot_pos'] = team_df['pot_pos'].apply(list)

    # mark off which positions they currently play
    for position in ['C', 'SS', 'CF', '2B', '3B', 'RF', 'LF', '1B']:
        if position not in ['C', '1B', 'LF']:
            cutoff = 45
        elif position in ['C', 'LF']:
            cutoff = 40
        else:
            cutoff = 25

        player_df = team_df.loc[(team_df[position] > cutoff) & (team_df['optim_pos'] == '-')]

        for player_name in player_df['HELPER']:
            team_df.loc[team_df['HELPER'] == player_name, 'pot_pos'].iloc[0].extend([position])

    batting = create_split_lineup(team_df, 'woba')

    batting = batting[['lineup_pos', 'Name', 'woba', 'woba_lhp', 'woba_rhp', 'bwar']].round(3)

    return batting.style.set_properties(
        **(dict(TABLE_PROPERTIES, **{'font-size': '1.5em'}))
    ).hide_index().render()


def generate_lineup_card(team_df: pd.DataFrame) -> Tuple[str, str]:
    return generate_pitcher_lineup(team_df), generate_batting_lineup(team_df)
