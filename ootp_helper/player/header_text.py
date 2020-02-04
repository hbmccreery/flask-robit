import pandas as pd
import numpy as np
from ootp_helper.color_maps import *


def generate_player_name(subset: pd.Series) -> str:

    return '{0} {1} (<a href="../team/{2}">{2}</a> {3}{4})'.format(
        subset['POS'],
        subset['Name'],
        subset['TM'],
        subset['Lev'],
        ' - On 40' if subset['ON40'] == 'Yes' else '',
    )


def generate_player_header(player: pd.Series) -> str:

    line_one = '<b> Age: </b> {0} | <b> Inj: </b> {1} | <b> Personality: </b> {2}'.format(
        player['Age'],
        player['INJ'],
        player['Type'],
    )

    line_two = '<b> Contract: </b> {0}/{1}'.format(player['SLR'], player['YL'])

    if player['ETY'] > 0:
        line_two = line_two + ' | <b> Extension: </b> {0}/{1}'.format(player['ECV'], player['ETY'])

    line_three = '<b> ML Yr: </b> {0} | <b> Pro Yr: </b> {1} | <b> Options: </b> {2}'.format(
        player['MLY'],
        player['PROY'],
        player['OPTU']
    )

    return '<br/>'.join([line_one, line_two, line_three])


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


def generate_ratings_header(df: pd.DataFrame) -> str:
    df = df.iloc[0:4]

    current_month = df.iloc[0]
    overall_og_trend = sum(df['og-1'])
    overall_war_trend = sum(df['mwar-1'])
    num_positive_og = sum(df['og-1'] > 0)
    num_negative_og = sum(df['og-1'] < 0)
    num_positive_war = sum(df['mwar-1'] > 0)
    num_negative_war = sum(df['mwar-1'] < 0)
    current_war = max(current_month['bwar'], current_month['pwar'])
    mark = highlight_mwar_change(overall_war_trend/2).replace('background-color', 'background')

    if mark == '':
        mark = 'background: #FFFFFF'

    if current_month['bwar_mean'] > current_month['pwar_mean']:
        adv_stat_type = 'wOBA'
        adv_stat_now = round(current_month['woba'], 3)
        adv_stat = round(current_month['woba_mean'], 3)
        adv_stat_trend = round(sum(df['pwoba-1']), 3)
        adv_stat_positive = sum(df['pwoba-1'] > 0)
        adv_stat_negative = sum(df['pwoba-1'] < 0)

    else:
        adv_stat_type = 'FIP'
        adv_stat_now = round(current_month['fip'], 3)
        adv_stat = round(current_month['fip_mean'], 3)
        adv_stat_trend = round(sum(df['pfip-1']), 3)
        adv_stat_positive = sum(df['pfip-1'] > 0)
        adv_stat_negative = sum(df['pfip-1'] < 0)

    ratings_header = (
        '<h2> <mark style="{0};"> Grade {1} ({2}: +{3}, -{4}) |'
        ' WAR {14}/{5} ({6}: +{7}, -{8}) | '
        '{9} {15}/{10} ({11}: +{12} -{13}) </mark> </h2>'
    ).format(
        mark,
        current_month['old grade'],
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
        current_war,
        adv_stat_now, 
    )

    return ratings_header
