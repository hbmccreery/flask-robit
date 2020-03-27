import pandas as pd
from pymongo import MongoClient
from typing import Tuple

from ootp_helper.constants import months
from ootp_helper.utils import clean_tables


def create_position_tables(db: MongoClient, player_filter: dict, sort_column: str, sort_order: int) -> Tuple[str, str]:
    ascending = False if sort_order == -1 else True

    records = db[months[0]].find(player_filter).sort(sort_column, sort_order)
    pos_df = pd.DataFrame.from_records([x for x in records]).rename({'_id': 'HELPER'}, axis=1)

    minors_subset = pos_df.loc[pos_df['Lev'] != 'MLB'].iloc[0:50]
    minors_subset.insert(loc=4, column='rank', value=minors_subset[sort_column].rank(ascending=ascending))
    prospects = clean_tables(minors_subset, 'farm-system', include_team=True)

    majors_subset = pos_df.loc[pos_df['Lev'] == 'MLB'].iloc[0:50]
    majors_subset.insert(loc=4, column='rank', value=majors_subset[sort_column].rank(ascending=ascending))
    roster = clean_tables(majors_subset, 'ml-roster', include_team=True)

    return prospects, roster
