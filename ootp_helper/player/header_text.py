import requests

import pandas as pd
import numpy as np

from typing import Optional, Tuple, List
from bs4 import BeautifulSoup

from ootp_helper.color_maps import *
from ootp_helper.player.run_calculators import calculate_batting_runs, calculate_pitching_runs
from ootp_helper.constants import STATSPLUS_PLAYER_FORMAT, DB_STATSPLUS_TABLE, DB_TRANSACTIONS_TABLE, TXN_TYPE_MAP, \
    INJ_TYPE_MAP


def generate_player_name(player_record: dict, best_pos: str, statsplus: Optional[dict]) -> str:
    name_string = '<h1 style="display: inline"> {0} {1} (<a href="../team/{2}">{2}</a> {3}) {4} {5} </h1>'.format(
        best_pos,
        player_record['Name'],
        player_record['TM'],
        player_record['Lev'],
        '<i>"{}"</i>'.format(player_record['Nickname']) if player_record['Nickname'] != '' else '',
        ' - On 40' if player_record['ON40'] == 'Yes' else '',
    )

    if not statsplus:
        return name_string

    player_url = STATSPLUS_PLAYER_FORMAT.format(id=statsplus['statsplus_id'], page='dash')
    statsplus_string = '<i><a href={} style="font-size: 150%"> OBL StatsPlus </a></i>'.format(player_url)

    return name_string + statsplus_string


def generate_war_probabilities_styled(war_dists: dict) -> str:
    results = {}
    thresholds = [0, 3, 4, 5, 7]

    for dist in ['bat_dist', 'pit_dist']:
        results[dist] = []
        for threshold in thresholds:
            results[dist] = results[dist] + [sum([item['p'] for item in war_dists[dist] if item['WAR'] > threshold])]

    bat_str = None
    pit_str = None
    color_list = ['#dd0000', '#dd8033', '#eac117', '#117722', '#44bbdd']

    if results['bat_dist'][0] == 0 and results['pit_dist'][0] == 0:
        return '<h2> <font color="{}"> Abandon hope all ye who enter </font> </h2>'.format(color_list[0])

    for war, prob, color in zip(thresholds, results['bat_dist'], color_list):
        if prob == 0:
            continue

        formatted_str = '<font color="{0}"> {1:.1f}% {2} WAR </font>'.format(color, prob * 100, war)

        if bat_str:
            bat_str = bat_str + ' | ' + formatted_str
        else:
            bat_str = formatted_str

    for war, prob, color in zip(thresholds, results['pit_dist'], color_list):
        if prob == 0:
            continue

        formatted_str = '<font color="{0}"> {1:.1f}% {2} WAR </font>'.format(color, prob * 100, war)

        if pit_str:
            pit_str = pit_str + ' | ' + formatted_str
        else:
            pit_str = formatted_str

    if bat_str and pit_str:
        return '<h2> Batter: {} <br/> Pitcher: {} </h2>'.format(bat_str, pit_str)

    return '<h2> {} </h2>'.format(bat_str if bat_str else pit_str)


def format_injury_string(inj: str) -> str:
    if inj == 'Wrecked':
        return f'<b> <font color="#dd0000"> {inj.upper()} </font> </b>'

    if inj == 'Fragile':
        return f'<b> <font color="##dd8033"> {inj} </font> </b>'

    return inj


def format_personality_string(personality: str) -> str:
    if personality in ['Captain', 'Fan Fav', 'Prankster', 'Sparkplug']:
        return f'<b> <font color="#117722"> {personality} </font> </b>'

    if personality in ['Disruptive', 'Outspoken', 'Unmotivated', 'Selfish']:
        return f'<b> <font color="#dd0000"> {personality} </font> </b>'

    return personality


def generate_player_header(player: dict) -> str:
    line_zero = '<b> HT/WT </b> {0}, {1} | <b> B/T</b> {2}/{3}'.format(
        player['HT'],
        player['WT'],
        player['B'],
        player['T']
    )

    line_one = '<b> Age: </b> {0} | <b> Inj: </b> {1} | <b> Personality: </b> {2}'.format(
        player['Age'],
        format_injury_string(player['Prone'].strip()),
        format_personality_string(player['Type'].strip()),
    )

    line_two = '<b> Leadership: </b> {0} | <b> Loyalty: </b> {1} | <b> Adaptability: </b> {2} | ' \
               '<b> Greed: </b> {3} | <b> Work Ethic: </b> {4}'.format(
        player['LEA'], player['LOY'], player['AD'], player['GRE'], player['WE'],
    )

    line_three = '<b> Contract: </b> {0}/{1}'.format(player['SLR'], player['YL'])

    if player['ETY'] != 0:
        line_three = line_three + ' | <b> Extension: </b> {0}/{1}'.format(player['ECV'], player['ETY'])

    line_four = '<b> ML Yr: </b> {0} | <b> Pro Yr: </b> {1} | <b> Options: </b> {2}'.format(
        -1, # player['MLY'],
        player['PROY'],
        player['OPT']
    )

    return '<br/>'.join([line_zero, line_one, line_two, line_three, line_four])


def generate_player_stat_string(player: pd.Series) -> str:
    # account for players w/ no experience at level
    if np.isnan(player['PA']):
        return '<i> No statistics available for this player. </i>'

    if player['PA'] < 15:
        bat_stats = 'Not enough PA to qualify.'
    else:
        pa = '{:.0f} PA'.format(player['PA'])
        ops = stat_color(player['OPS+'], 'OPS+')
        ks = stat_color(player['SO+'], 'SO+')
        bbs = stat_color(player['BB+'], 'BB+')
        iso = stat_color(player['ISO+'], 'ISO+')
        sb = '{:.0f} SB'.format(player['SB'])
        bat_stats = ' | '.join([pa, ops, ks, bbs, iso, sb])
        bat_stats = '<font color="black"> {} </font>'.format(bat_stats)

    if player['IP'] < 5:
        pit_stats = 'Not enough IP to qualify.'
    else:
        ip = '{:.0f} IP'.format(player['IP'])
        era = stat_color(player['ERA+'], 'ERA+')
        ks = stat_color(player['K9+'], 'SO+')
        bbs = stat_color(player['BB9+'], 'BB+')
        hrs = stat_color(player['HR9+'], 'HR9+')
        grd = stat_color(player['GO+'], 'GO+')
        pit = pitch_color(player['PPG'])
        pit_stats = ' | '.join([ip, era, ks, bbs, hrs, grd, pit])
        pit_stats = '<font color="black"> {} </font>'.format(pit_stats)

    return '<b> Current bat performance: </b> {0} <br/> <b> Current pit performance: </b> {1} '.format(
        bat_stats,
        pit_stats,
    )


def generate_ratings_header(
        records: List[dict],
        bat_splits: dict,
        pit_splits: dict,
        war_dists: dict,
) -> str:
    woba_rhp, runs_rhp = calculate_batting_runs(bat_splits['r'])
    woba_lhp, runs_lhp = calculate_batting_runs(bat_splits['l'])
    fip_rhb, runs_rhb = calculate_pitching_runs(pit_splits['r'])
    fip_lhb, runs_lhb = calculate_pitching_runs(pit_splits['l'])

    current_month = records[0]
    overall_og_trend = sum([x['og-1'] for x in records])
    overall_war_trend = sum([x['mwar-1'] for x in records])
    num_positive_og = sum([x['og-1'] > 0 for x in records])
    num_negative_og = sum([x['og-1'] < 0 for x in records])
    num_positive_war = sum([x['mwar-1'] > 0 for x in records])
    num_negative_war = sum([x['mwar-1'] < 0 for x in records])
    current_war = max(current_month['bwar'], current_month['pwar'])
    mark = highlight_mwar_change(overall_war_trend / 2).replace('background-color', 'background')

    if mark == '':
        mark = 'background: #FFFFFF'

    if current_month['bwar_mean'] > current_month['pwar_mean']:
        adv_stat_type = 'wOBA'
        adv_stat_now = round(current_month['woba'], 3)
        adv_stat_vl = round(woba_lhp, 3)
        adv_stat_vr = round(woba_rhp, 3)
        adv_stat = round(current_month['woba_mean'], 3)
        adv_stat_trend = round(sum([x['pwoba-1'] for x in records]), 3)
        adv_stat_positive = sum([x['pwoba-1'] > 0 for x in records])
        adv_stat_negative = sum([x['pwoba-1'] < 0 for x in records])

    else:
        adv_stat_type = 'FIP'
        adv_stat_now = round(current_month['fip'], 2)
        adv_stat_vl = round(fip_lhb, 2)
        adv_stat_vr = round(fip_rhb, 2)
        adv_stat = round(current_month['fip_mean'], 2)
        adv_stat_trend = round(sum([x['pfip-1'] for x in records]), 2)
        adv_stat_positive = sum([x['pfip-1'] > 0 for x in records])
        adv_stat_negative = sum([x['pfip-1'] < 0 for x in records])

    ratings_header = (
        '<h2> <mark style="{0};"> Grade {1} ({2}: +{3}, -{4}) |'
        ' WAR {14}/{5} ({6}: +{7}, -{8}) | '
        '{9} {15}/{10} ({11}: +{12} -{13}) {16} vL / {17} vR </mark> </h2>'
    ).format(
        mark,
        round(current_month['old grade'], 1),
        round(overall_og_trend, 1),
        num_positive_og,
        num_negative_og,
        round(current_month['mwar_mean'], 1),
        round(overall_war_trend, 2),
        num_positive_war,
        num_negative_war,
        adv_stat_type,
        adv_stat,
        adv_stat_trend,
        adv_stat_positive,
        adv_stat_negative,
        round(current_war, 1),
        adv_stat_now,
        adv_stat_vl,
        adv_stat_vr,
    )

    return ratings_header + ' <br/> ' + generate_war_probabilities_styled(war_dists)


def format_pitching_row(item: dict) -> dict:
    top_level_keys = ['Year', 'Team', 'G', 'IP', 'K%', 'BB%', 'HR%', 'ERA', 'FIP', 'xFIP', 'WAR']

    return {
        key: item.get(key, None)
        for key
        in top_level_keys
    }


def format_hitting_row(item: dict) -> dict:
    top_level_keys = ['Year', 'Team', 'G', 'PA', 'K%', 'BB%', 'AVG', 'OBP', 'SLG', 'BABIP', 'wRC+', 'WAR']

    item['K%'] = '{:.0f}%'.format(100 * int(item['K']) / int(item['PA'])) if item['PA'] != '0' else None
    item['BB%'] = '{:.0f}%'.format(100 * int(item['BB']) / int(item['PA'])) if item['PA'] != '0' else None

    return {
        key: item.get(key, None)
        for key
        in top_level_keys
    }


def format_statsplus_table(statsplus_table) -> Optional[list]:
    if statsplus_table is None:
        return None

    headers = [item.text for item in statsplus_table.findAll('th')]
    total_headers = [headers[0]] + headers[3:]

    data = [
        [x.text for x in row.findAll('td')]
        for row
        in statsplus_table.findAll('tr')[1:]
    ]

    nontotal_with_headers = [dict(zip(headers, row)) for row in data if len(headers) == len(row)]
    total_with_headers = [
        {**dict(zip(total_headers, row)), **{'Year': 'Total'}} for row in data if len(total_headers) == len(row)
    ]

    data_with_headers = nontotal_with_headers + total_with_headers

    for item in data_with_headers:
        item['Team'] = item['Team'].split('\n')[2]

    return data_with_headers


def build_statsplus_data(soup, table_class: str, format_fxn) -> Tuple[Optional[list], Optional[list]]:
    pitch_tables = soup.select('table[class*={}]'.format(table_class))

    if len(pitch_tables) == 2:
        majors = [format_fxn(item) for item in format_statsplus_table(pitch_tables[0])]
        minors = [format_fxn(item) for item in format_statsplus_table(pitch_tables[1])]

        return majors, minors

    elif len(pitch_tables) == 1:
        minors = [format_fxn(item) for item in format_statsplus_table(pitch_tables[0])]

        return [], minors

    return [], []


def parse_draft_info(line_body: str) -> str:
    draft_round = line_body[line_body.find('Round')+5:line_body.find(',')].strip()
    draft_pick = line_body[line_body.find('Pick')+4:].strip()
    draft_pick = draft_pick[:draft_pick.find(',')]

    return 'Round {} Pick {}'.format(draft_round, draft_pick)


def format_transaction_row(item: dict) -> dict:
    return {
        'date': item['date'],
        'type': TXN_TYPE_MAP.get(item['txn_type'], item['txn_type']),
        'to': item['to'],
        'from': item['from'] if item['txn_type'] != 'drafted' else parse_draft_info(item['line_body']),
        'amount': '${:,.0f}'.format(item['amount']) if item['amount'] else None,
        'years': item['contract_length'],
        'detail': item['line_body'][item['line_body'].find('[G]')+3:],
    }


def format_injury_row(item: dict) -> dict:
    return{
        'date': item['date'],
        'info': INJ_TYPE_MAP.get(item['injury_detail'], item['injury_detail']),
        'type': item.get('injury_name', '').lower(),
        'length': item.get('injury_length', '').replace('one', '1').replace('.', ''),
        'detail': item['line_body'][item['line_body'].find('[I]') + 3:].strip(),
    }


def generate_statsplus_info(statsplus: dict, db) -> Tuple[str, list, list, tuple, tuple]:
    r = requests.get(STATSPLUS_PLAYER_FORMAT.format(id=statsplus['statsplus_id'], page='pitch'))
    soup = BeautifulSoup(r.text)
    pitching_data = build_statsplus_data(soup, 'player-pitch-table', format_pitching_row)

    r = requests.get(STATSPLUS_PLAYER_FORMAT.format(id=statsplus['statsplus_id'], page='hit'))
    soup = BeautifulSoup(r.text)
    hitting_data = build_statsplus_data(soup, 'player-bat-table', format_hitting_row)

    team = soup.find('div', {'class': 'playertopright'}).find('a')

    if team is not None:
        team_name = team.text
        team_id = team['href'].replace('/oblootp/team/', '')
        team_info = db[DB_STATSPLUS_TABLE].find_one({'team_id': int(team_id)})

        team_string = '<h3>Statsplus - Org: {org} | Lev: {lev} | Team: {tm}</h3>'.format(
            org=team_info['TM'],
            lev=team_info['Lev'],
            tm=team_name
        )

    else:
        team_string = ''

    transaction_info_db = db[DB_TRANSACTIONS_TABLE].find({'player': statsplus['statsplus_id']}, {'_id': 0})
    transaction_records = [item for item in transaction_info_db]

    injuries = [
        format_injury_row(item)
        for item
        in transaction_records
        if item['line_type'] == 'injury'
    ]

    transactions = [
        format_transaction_row(item)
        for item
        in transaction_records
        if item['line_type'] == 'transaction'
    ]

    return (
        team_string,
        injuries,
        transactions,
        pitching_data,
        hitting_data,
    )
