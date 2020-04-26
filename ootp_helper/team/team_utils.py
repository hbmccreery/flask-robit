from typing import List

from ootp_helper.player.run_calculators import calculate_batting_runs, calculate_pitching_runs
from ootp_helper.player.table_generators import generate_splits_table
from ootp_helper.constants import BAT_RAT_COLUMNS, PIT_RAT_COLUMNS


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