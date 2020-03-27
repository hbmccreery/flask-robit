from ootp_helper.constants import CLEAN_TABLES_COLS, POT_COLS, BUTTON_STRING, TABLE_PROPERTIES
from ootp_helper.color_maps import rating_colors, highlight_woba, highlight_fip, highlight_mwar, highlight_og_change, \
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
    round_zero = POT_COLS + ['POT']

    subset[round_three] = subset[round_three].round(3)
    subset[round_two] = subset[round_two].round(2)
    subset[round_one] = subset[round_one].round(1)
    subset[round_zero] = subset[round_zero].applymap(int)

    # create button to player page
    subset['HELPER'] = subset['HELPER'].apply(lambda x: BUTTON_STRING.format(x.replace("'", "%27")))

    table = subset.style.applymap(
        rating_colors,
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
