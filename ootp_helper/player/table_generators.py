from typing import Tuple, List, Any

import pandas as pd
import json

from datetime import datetime

from ootp_helper.player.run_calculators import runs_to_ratings, ratings_to_runs
from ootp_helper.color_maps import defense_stat_colors, rating_colors
from ootp_helper.constants import DEF_RAT_COLUMNS, TABLE_PROPERTIES, IND_PIT_COLUMNS, IND_PIT_POT_COLUMNS


def create_rating_item_list(record: dict, keys: list) -> list:
    return [
        '<font color={}> {} </font>'.format(rating_colors(record[key]), str(int(record[key])))
        if key in record.keys() else ''
        for key
        in keys
    ]


def create_rating_table_row(record: dict, label: str, keys: list) -> str:
    return '<tr> <td>' + '</td><td>'.join([label] + create_rating_item_list(record, keys)) + '</td> </tr>'


def create_rating_table(record: dict, build_dict: dict, header: str) -> str:
    table_rows = [header] + [
        create_rating_table_row(record, key, build_dict[key])
        for key
        in build_dict.keys()
    ]

    return f'<table class="ratings-player-inner">{"".join(table_rows)}</table>'


def format_player_record(idx: int, record: dict) -> dict:
    record['mwar'] = max(record['bwar'], record['pwar'])
    record['index'] = idx

    pitch_names = [
        col
        for col
        in IND_PIT_COLUMNS
        if record.get(col + 'P', 0) > 20
    ]

    fielding_ratings = [col for col in DEF_RAT_COLUMNS if record.get(col, 0) > 20]

    bat_table_head = (
        "<tr> <th> Batting </th> <th> CON </th> <th> GAP </th> <th> POW </th> <th> EYE </th> <th> Ks </th> </tr>"
    )
    ind_pit_head = "<tr> <th> Ind Pitch </th> <th>" + "</th><th>".join(pitch_names) + "</th> </tr>"
    pit_table_head = "<tr> <th> Pitching </th> <th> STU </th> <th> MOV </th> <th> CTL </th> <th> STM </th> </tr>"
    other_rat_head = "<tr> <th> Name </th> <th> Rating </th> </tr>"

    bat_table_build_dict = {
        'Current': ['CON', 'GAP', 'POW', 'EYE', 'K'],
        'Potential': ['CON P', 'GAP P', 'POW P', 'EYE P', 'K P'],
        'vR': ['CON vR', 'GAP vR', 'POW vR', 'EYE vR', 'K vR'],
        'vL': ['CON vL', 'GAP vL', 'POW vL', 'EYE vL', 'K vL']
    }

    pit_table_build_dict = {
        'Current': ['STU', 'MOV', 'CTL', 'STM'],
        'Potential': ['STU P', 'MOV P', 'CTL P'],
        'vR': ['STU vR', 'MOV vR', 'CTL vR'],
        'vL': ['STU vL', 'MOV vL', 'CTL vL'],
    }

    ind_pit_table_build_dict = {
        'Current': pitch_names,
        'Potential': [name + 'P' for name in pitch_names],
    }

    def_table_build_dict = {item: [item] for item in fielding_ratings}
    other_table_build_dict = {item: [item] for item in ['SPE', 'RUN', 'STE']}

    bat_table = create_rating_table(record, bat_table_build_dict, bat_table_head)
    pit_table = create_rating_table(record, pit_table_build_dict, pit_table_head)
    ind_pit_table = create_rating_table(record, ind_pit_table_build_dict, ind_pit_head) if pitch_names else ''
    field_table = create_rating_table(record, def_table_build_dict, other_rat_head) if fielding_ratings else ''
    other_table = create_rating_table(record, other_table_build_dict, other_rat_head)

    table_list = [f"<td>{table}</td>" for table in [bat_table, pit_table, ind_pit_table, field_table, other_table]]
    record['detail'] = f'<table><tbody style="vertical-align: top;"><tr>{"".join(table_list)}</tr></tbody></table>'

    return record


def format_report_record(idx: int, record: dict) -> dict:
    record.pop('_id')
    record['Sct'] = record['Sct'].strftime('%m-%d-%y')

    return format_player_record(idx, record)


def generate_defensive_ratings_string(listed_pos: str, rendered_ratings: List[dict]) -> str:
    listed_potential = [item['potential'] for item in rendered_ratings if item['index'] == listed_pos]

    # pitchers
    if not listed_potential:
        return listed_pos
    else:
        listed_potential = listed_potential[0]

    reached_positions = [
        '<font color="{}">{}</font>'.format(rating_colors(item['potential']), item['index'])
        for item
        in rendered_ratings
        if item['index'] != listed_pos and item['potential'] > 40 and item['current'] > 40
    ]

    unreached_positions = [
        '<i><font color="{}">{}</font></i>'.format(rating_colors(item['potential']), item['index'])
        for item
        in rendered_ratings
        if item['index'] != listed_pos and item['potential'] > 40 and item['current'] < 40
    ]

    listed_pos_str = (
        '<font color="{}"> {} </font>'.format(rating_colors(listed_potential), listed_pos)
        if listed_potential >= 45
        else '<font color="{}"> {} ({}) </font>'.format(
            rating_colors(listed_potential),
            listed_pos,
            int(listed_potential),
        )
    )
    other_pos_str = (
        '({})'.format(', '.join(reached_positions + unreached_positions))
        if reached_positions or unreached_positions
        else ''
    )

    return listed_pos_str + other_pos_str


def generate_defense_table(stats: pd.DataFrame, ratings: pd.DataFrame, listed_pos: str) -> Tuple[Any, ...]:
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

    # string to display as position on player header
    pos_string = generate_defensive_ratings_string(listed_pos, json.loads(rendered_ratings))

    # make the table
    rendered_stats = stats.iloc[[0, 1]].style.applymap(
        defense_stat_colors,
        subset=DEF_RAT_COLUMNS
    ).set_properties(
        **TABLE_PROPERTIES
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).hide_index().render()

    return rendered_ratings, rendered_stats, best_position, pos_string


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