import pandas as pd
import numpy as np
from ootp_helper.color_maps import stat_color, pitch_color

def generate_player_name(subset: pd.Series) -> str:
    if subset['ON40'] == 'Yes':
        fourty = ' - On 40'
    else:
        fourty = ''

    name_str = (subset['POS'] + ' ' + 
                subset['Name'] + 
                ' <a href="../team/' + subset['TM'] + '"> ' + subset['TM'] + '</a>' +
                ' (' + subset['Lev'] + fourty + ')')

    return name_str


def generate_player_header(player: pd.Series) -> str:
    line_one = ('<b> Age: </b> ' + str(player['Age']) + 
                ' | <b> Inj: </b>' + player['INJ'] + 
                ' | <b> Personality: </b> ' + player['Type'])

    if player['ETY'] == 0:
        extension = 'N/A'
    else:
        extension = str(player['ECV']) + '/' + str(player['ETY'])

    line_two = ('<b> Contract: </b> ' + str(player['SLR']) + '/' + str(player['YL']) + 
                ' | <b> Extension: </b> ' + extension)

    line_three = ('<b> ML Yr: </b> ' + str(player['MLY']) + 
                  ' | <b> Pro Yr: </b> ' + str(player['PROY']) + 
                  ' | <b> Options: </b> ' + str(player['OPTU']))

    return line_one + '<br/>' + line_two + '<br/>' + line_three


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
        bat_stats = ('<font color="black">' + 
                     pa + ' | ' + 
                     ops + ' | ' + 
                     ks + ' | ' + 
                     bbs + ' | ' + 
                     iso + ' | ' +
                     sb + '</font>')

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
        pit_stats = (ip + ' | ' + 
                     era + ' | ' + 
                     ks + ' | ' + 
                     bbs + ' | ' + 
                     hrs + ' | ' +
                     grd + ' | ' +
                     pit)
    
    to_return = ('<b> Current bat performance: </b> ' + bat_stats + '<br/>' + 
                 '<b> Current pit performance: </b> ' + pit_stats)

    return to_return
