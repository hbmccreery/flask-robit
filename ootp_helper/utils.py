import pymongo
import json
import random

import pandas as pd

from typing import List, Tuple, Optional
from flask import render_template

from ootp_helper.constants import CLEAN_TABLES_COLS, POT_COLS, BUTTON_STRING, TABLE_PROPERTIES, months, FRONT_PAGE_COLS, \
    DB_CONNECTION_STRING, DB_NAME_STRING, PHRASES
from ootp_helper.color_maps import background_rating_colors, highlight_woba, highlight_fip, highlight_mwar, highlight_og_change, \
    highlight_mwar_change


def clean_tables(subset, table_name, include_team=False, team_pot=''):
    # cleaning
    if include_team:
        insert_cols = CLEAN_TABLES_COLS[:1] + ['TM', 'rank'] + CLEAN_TABLES_COLS[1:]
    else:
        insert_cols = CLEAN_TABLES_COLS

    if team_pot != '':
        pot_ind = insert_cols.index('POT')
        insert_cols = insert_cols[:pot_ind + 1] + [team_pot] + insert_cols[pot_ind + 1:]

    subset = subset[insert_cols]

    round_three = ['woba', 'woba_mean']
    round_two = ['og-1', 'mwar-1', 'fip', 'fip_mean']
    round_one = ['old grade', 'mwar_mean']
    round_zero = ['POT']

    subset[round_three] = subset[round_three].round(3)
    subset[round_two] = subset[round_two].round(2)
    subset[round_one] = subset[round_one].round(1)
    subset[round_zero] = subset[round_zero].applymap(int)

    # create button to player page
    subset['HELPER'] = subset['HELPER'].apply(lambda x: BUTTON_STRING.format(x.replace("'", "%27")))

    table = subset.style.applymap(
        background_rating_colors,
        subset=POT_COLS + ['POT', team_pot]
    ).applymap(
        highlight_mwar_change,
        subset='mwar-1'
    ).applymap(
        highlight_og_change,
        subset='og-1'
    ).applymap(
        highlight_mwar,
        subset='mwar_mean'
    ).applymap(
        highlight_woba,
        subset=['woba', 'woba_mean']
    ).applymap(
        highlight_fip,
        subset=['fip', 'fip_mean']
    ).set_properties(
        **(dict(TABLE_PROPERTIES, **{'font-size': '1.3em'}))
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).set_table_attributes(
        "class='sortable'"
    ).hide_index().render()

    return table


def create_aggregated_dist_data(record: dict) -> dict:
    return {
        'HELPER': record['_id'],
        'bat3': round(sum([x['p'] for x in record['bat_dist'] if x['WAR'] >= 3]), 2),
        'bat5': round(sum([x['p'] for x in record['bat_dist'] if x['WAR'] >= 5]), 2),
        'bat7': round(sum([x['p'] for x in record['bat_dist'] if x['WAR'] >= 7]), 2),
        'pit3': round(sum([x['p'] for x in record['pit_dist'] if x['WAR'] >= 3]), 2),
        'pit5': round(sum([x['p'] for x in record['pit_dist'] if x['WAR'] >= 5]), 2),
        'pit7': round(sum([x['p'] for x in record['pit_dist'] if x['WAR'] >= 7]), 2),
    }


def create_table_json(subset, db, include_team=False) -> Tuple[List, List[List]]:
    insert_cols = CLEAN_TABLES_COLS[:1] + ['TM', 'rank'] + CLEAN_TABLES_COLS[1:] if include_team else CLEAN_TABLES_COLS

    dist_data = [create_aggregated_dist_data(x) for x in db['dist_data'].find({'_id': {'$in': list(subset['HELPER'])}})]

    subset = subset[insert_cols]
    subset = pd.merge(subset, pd.DataFrame(dist_data), how='left')

    round_three = ['woba', 'woba_rhp', 'woba_lhp', 'woba_mean']
    round_two = ['og-1', 'mwar-1', 'fip', 'fip_rhb', 'fip_lhb', 'fip_mean']
    round_one = ['old grade', 'mwar_mean']
    round_zero = ['POT', 'ip']

    subset[round_three] = subset[round_three].round(3)
    subset[round_two] = subset[round_two].round(2)
    subset[round_one] = subset[round_one].round(1)
    subset[round_zero] = subset[round_zero].applymap(int)

    subset['HELPER'] = subset['HELPER'].apply(lambda x: BUTTON_STRING.format(x.replace("'", "%27")))

    return_cols = ['' if col == 'HELPER' else col for col in subset.columns]
    return_data = subset.values.tolist()

    return return_cols, return_data


def get_front_page_data(db, data_filter: dict) -> List[list]:
    # add in skill floor, get data from db
    data_filter['old grade'] = {'$gte': 5}
    db_cursor = db[months[0]].find(data_filter)
    records = [[record[key] for key in FRONT_PAGE_COLS] for record in db_cursor]

    # reformat
    helper_idx = FRONT_PAGE_COLS.index('_id')
    round_indexes = [FRONT_PAGE_COLS.index(item) for item in ['old grade', 'og-1', 'mwar_mean', 'mwar-1']]
    round_two_indexes = [FRONT_PAGE_COLS.index(item) for item in ['fip_mean']]
    round_three_indexes = [FRONT_PAGE_COLS.index(item) for item in ['woba_mean']]

    records = [
        [
            BUTTON_STRING.format(item.replace("'", "%27")) if idx == helper_idx
            else round(item, 1) if idx in round_indexes
            else round(item, 2) if idx in round_two_indexes
            else round(item, 3) if idx in round_three_indexes
            else item
            for idx, item
            in enumerate(record)
        ]
        for record in records
    ]

    return records


def init_db() -> pymongo.mongo_client:
    client = pymongo.MongoClient(DB_CONNECTION_STRING)
    return client[DB_NAME_STRING]


def generate_error_message(
        message: str,
        all_rise: Optional[List[dict]] = None,
        all_fall: Optional[List[dict]] = None,
        team_rise: Optional[List[dict]] = None,
        team_fall: Optional[List[dict]] = None
):
    return render_template(
        'landing.html',
        col_names=json.dumps([''] + FRONT_PAGE_COLS[1:]),
        all_rise=json.dumps(all_rise) if all_rise else '',
        all_fall=json.dumps(all_fall) if all_rise else '',
        partial_rise=json.dumps(team_rise) if all_rise else '',
        partial_fall=json.dumps(team_fall) if all_rise else '',
        error=message,
        phrase=random.choice(PHRASES),
    )
