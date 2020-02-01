from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import random
import json
from itertools import product, groupby, chain

from ootp_helper.constants import *
from ootp_helper.data_reading import create_player_data, create_standings, create_benchmarks
from ootp_helper.player.header_text import generate_player_name, generate_player_header, generate_player_stat_string, generate_ratings_header
from ootp_helper.player.run_calculators import *
from ootp_helper.player.table_generators import *
from ootp_helper.player.image_progression import *
from ootp_helper.color_maps import *

dfs = create_player_data(months)

currentMonth = dfs[currMonth]

(al_standing_tables, nl_standing_tables, finances) = create_standings()
(batting_benchmarks, pitching_benchmarks) = create_benchmarks()

# draft results
draft_results = pd.read_csv('csv_data/draft_classes.csv')
draft_results['HELPER'] = draft_results['HELPER'].str.replace(' ', '').str.replace('/', '-')

# and other teams' takes
pot_grid = pd.read_pickle('pickles/scout_takes.pickle')
pot_grid['HELPER'] = pot_grid['HELPER'].str.replace(' ', '').str.replace('/', '-')

# stop rounding my buttons
pd.set_option('display.max_colwidth', -1)


def generate_lineup_card(team_df: pd.DataFrame):
    lineup_pit_cols = ['HELPER', 'Name', 'ip', 'fip', 'pwar']

    sp = team_df.nlargest(5, 'pwar')[lineup_pit_cols]
    rp = team_df.loc[~team_df['HELPER'].isin(sp['HELPER'])].nsmallest(8, 'fip', keep='last')[lineup_pit_cols]

    sp['POS'] = 'SP'
    rp['POS'] = 'RP'

    pitching = sp.append(rp, ignore_index=True)
    pitching.drop('HELPER', axis=1, inplace=True)

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
            cutoff = 30

        player_df = team_df.loc[(team_df[position]>cutoff) & (team_df['optim_pos']=='-')]

        for player in player_df['HELPER']:
            team_df.loc[team_df['HELPER']==player, 'pot_pos'].iloc[0].extend([position])
    
    # get all possible lineups sets of player/woba/WAR (w/ duplicates)
    # boy that is badly formatted
    potential_pairs = team_df.apply(
                        lambda x: [
                            (y, 
                             x['HELPER'], 
                             x['Name'], 
                             x['woba'], 
                             x['bwar']
                            ) for y in x['pot_pos']
                        ], axis=1
                      ).tolist()

    potential_pairs = list(filter(lambda x: x != [], potential_pairs))
    
    ungrouped_items = [item for sublist in potential_pairs for item in sublist]
    ungrouped_items.sort(key=lambda x: x[0])

    groups = []
    uniquekeys = []
    for key, group in groupby(ungrouped_items, lambda x: x[0]):
        groups.append(list(group))      # Store group iterator as a list
        uniquekeys.append(key)
        
    potential_lineups = [x for x in product(*groups)]
    
    lineup_woba = []

    for lineup in potential_lineups:
        if len(set([x[1] for x in lineup])) != 8:
            lineup_woba.append(0)
        else:
            lineup_woba.append(sum([x[3] for x in lineup]))

    optim_lineup = pd.DataFrame(list(potential_lineups[np.argmax(lineup_woba)]))
    optim_lineup.columns = ['lineup_pos', 'HELPER', 'Name', 'woba', 'bwar']
    optim_lineup = optim_lineup.sort_values('woba', ascending=False)
    
    bench = team_df.loc[~team_df['HELPER'].isin(optim_lineup['HELPER'])].nlargest(5, 'woba', keep='last')
    bench = bench[['HELPER', 'Name', 'bwar', 'woba']]
    bench['lineup_pos'] = 'PH'
    
    batting = optim_lineup.append(bench, ignore_index=True)

    optim_lineup.drop('HELPER', axis=1, inplace=True)

    pitching = pitching[['POS', 'Name', 'fip', 'ip']].round(2)
    batting = batting[['lineup_pos', 'Name', 'woba', 'bwar']].round(3)
    
    pitching_html = pitching.style.set_properties(
        **(dict(TABLE_PROPERTIES, **{'font-size':'1.5em'}))
    ).hide_index().render()
    
    batting_html = batting.style.set_properties(
        **(dict(TABLE_PROPERTIES, **{'font-size':'1.5em'}))
    ).hide_index().render()

    return [pitching_html, batting_html]
    

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'lookIgetthatIneedonebutwhosgonnastealthis'

@app.route('/')
def landing_page():
    return render_template('landing.html',
                            al_standings = al_standing_tables,
                            nl_standings = nl_standing_tables,
                            phrase = random.choice(phrases))

@app.route('/', methods=['POST'])
@app.route('/rising-prospects', methods=['POST'])
@app.route('/draft-class/<year>', methods=['POST'])
@app.route('/draft-class/<year>/<team>', methods=['POST'])
@app.route('/team/<team>', methods=['POST'])
@app.route('/pos/<pos>', methods=['POST'])
@app.route('/player/<player>', methods=['POST'])
@app.route('/compare', methods=['POST'])
@app.route('/compare/<helper1>', methods=['POST'])
@app.route('/compare/<helper1>/<helper2>', methods=['POST'])
def landing_page_team_request(team = None, pos = None, player = None, helper1 = None, helper2 = None):
    
    if 'player' in request.form.keys():
        # grab text, get table of players w/ that name
        text = request.form['player']

        if len(text) < 3:
            return render_template('landing.html', error='Search too short; may give too many results', phrase = random.choice(phrases))
        
        processed_text = text.lower()
        potential_players = currentMonth.loc[currentMonth['Name'].str.lower() == processed_text]
        #potential_players = currentColl.find({"name_lower":processed_text})

        subset = potential_players[PLAYER_DISP]
        
        if len(subset['HELPER']) == 0:

            potential_players = currentMonth.loc[currentMonth['Name'].str.lower().str.find(processed_text) != -1]
            subset = potential_players[PLAYER_DISP]

            if len(subset['HELPER']) == 0:
                return render_template('landing.html', error=text+' not found', phrase = random.choice(phrases))

        if len(subset['HELPER']) == 1:
            return redirect('/player/'+ subset['HELPER'].iloc[0])

        # create button to player page
        buttonStart = '<input type="button" value="Player Page" onclick="window.location.href=\'/player/'
        buttonEnd = '\'" />'
        subset['HELPER'] = buttonStart + subset['HELPER'] + buttonEnd

        # get HTML from table, then make table sortable
        table = subset.to_html(index=False, classes=["table-bordered", "table-striped", "table-hover"])
        table = table[0:7] + 'id="players" ' + table[7:]

        # find and replace right tags the pandas to_html fucked
        table = table.replace('&lt;', '<')
        table = table.replace('&gt;', '>')
        table = table.replace('HELPER', 'Player Page')

        session['search_results'] = table
            
        return redirect('/search')

    if 'comparison' in request.form.keys():
        # grab text, get table of players w/ that name
        text = request.form['comparison']

        if len(text) < 3:
            return render_template('landing.html', error='Search too short; may give too many results', phrase = random.choice(phrases))
        
        processed_text = text.lower()
        potential_players = currentMonth.loc[currentMonth['Name'].str.lower() == processed_text]
        #potential_players = currentColl.find({"name_lower":processed_text})

        subset = potential_players[PLAYER_DISP]
        
        if len(subset['HELPER']) == 0:

            potential_players = currentMonth.loc[currentMonth['Name'].str.lower().str.find(processed_text) != -1]
            subset = potential_players[PLAYER_DISP]

            if len(subset['HELPER']) == 0:
                return render_template('landing.html', error=text+' not found', phrase = random.choice(phrases))

        if len(subset['HELPER']) == 1:
            if helper1 != None:
                return redirect('/compare/'  + helper1 + '/' + subset['HELPER'].iloc[0])
            
            return redirect('/compare/' + subset['HELPER'].iloc[0])
        
        # create button to player page
        if helper1 != None:
            buttonStart = '<input type="button" value="Compare" onclick="window.location.href=\'/compare/' + helper1 + '/'
        else:
            buttonStart = '<input type="button" value="Compare" onclick="window.location.href=\'/compare/'
            
        buttonEnd = '\'" />'
        subset['HELPER'] = buttonStart + subset['HELPER'] + buttonEnd

        # get HTML from table, then make table sortable
        table = subset.to_html(index=False, classes=["table-bordered", "table-striped", "table-hover"])
        table = table[0:7] + 'id="players" ' + table[7:]

        # find and replace right tags the pandas to_html fucked
        table = table.replace('&lt;', '<')
        table = table.replace('&gt;', '>')
        table = table.replace('HELPER', 'Player Page')

        session['search_results'] = table

        if helper1 != None:
            return redirect('/compsearch/' + helper1)
        else:
            return redirect('/compsearch')

    elif 'team' in request.form.keys():
        text = request.form['team']
        processed_text = text.upper()

        # would throw error if team was blank
        if processed_text == '':
            return render_template('landing.html',
                                   al_standings = al_standing_tables,
                                   nl_standings = nl_standing_tables, 
                                   error = 'Please enter a team.', 
                                   phrase = random.choice(phrases))

        # check to see if this is a position
        if processed_text in POS:
            return redirect('/pos/' + processed_text)

        # or a draft year
        if processed_text in DRAFT_YEARS:
            return redirect('/draft-class/' + processed_text)

        if processed_text in ['RISING', 'RIS', 'R']:
            return redirect('rising-prospects')

        if any(currentMonth['TM'].str.contains(processed_text)):
            return redirect('/team/' + processed_text)

        return render_template('landing.html',
                               al_standings = al_standing_tables,
                               nl_standings = nl_standing_tables, 
                               error = 'Invalid team choice.', 
                               phrase = random.choice(phrases))

    elif 'ogp' in request.form.keys():
        OG_PERCENT = int(request.form['ogp'])
        return render_template('landing.html', phrase = random.choice(phrases))

    else:
        return render_template('landing.html', 
                               error='An error has occured. Please berate Hugh at your nearest convenience.',
                               phrase = random.choice(phrases))


@app.route('/search')
def search_results():
    # get the search results
    table = session.get('search_results', None)
    return render_template('player_select.html', table = table, phrase = random.choice(phrases))


@app.route('/search')
def player_search_results_request():
    form_id = request.form['submit_button']
    return redirect('/player/' + form_id)


@app.route('/compsearch')
@app.route('/compsearch/<helper1>')
def comp_search_results(helper1 = None):
    # get the search results
    table = session.get('search_results', None)
    return render_template('player_select.html', table = table, phrase = random.choice(phrases))


@app.route('/compsearch')
@app.route('/compsearch/<helper1>')
def comp_search_results_request(helper1 = None):
    form_id = request.form['submit_button']
    if helper1 != None:
        return redirect('/compare/' + helper1 + '/' + form_id)
    return redirect('/compare/' + form_id)


# routine to clean tables
def clean_tables(subset, table_name, include_team=False):
    # cleaning
    if include_team:
        insert_cols = CLEAN_TABLES_COLS[:1] + ['TM', 'rank'] + CLEAN_TABLES_COLS[1:]
        subset = subset[insert_cols]
    else:
        subset = subset[CLEAN_TABLES_COLS]

    round_three = ['woba', 'woba_mean']
    round_two = ['og-1', 'mwar-1', 'fip', 'fip_mean']
    round_one = ['old grade', 'mwar_mean']
    round_zero = POT_COLS + ['POT']

    subset[round_three] = subset[round_three].round(3)
    subset[round_two] = subset[round_two].round(2)
    subset[round_one] = subset[round_one].round(1)
    subset[round_zero] = subset[round_zero].applymap(int)

    # create button to player page
    buttonStart = '<input type="button" value="Player Page" onclick="window.location.href=\'/player/'
    buttonEnd = '\'" />'
    subset['HELPER'] = buttonStart + subset['HELPER'] + buttonEnd

    table = subset.style.applymap(
        rating_colors,
        subset=POT_COLS + ['POT']
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
        **(dict(TABLE_PROPERTIES, **{'font-size':'1.3em'}))
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).set_table_attributes(
        "class='sortable'"
    ).hide_index().render()
    
    return table


@app.route('/rising-prospects')
@app.route('/rising-prospects/<position>')
def rising_prospect_page(position = None):
    if position is None:
        rising_players = currentMonth.loc[
            (currentMonth['Lev'] != 'MLB') & ~((currentMonth['old grade'] < 8) | (currentMonth['Age'] >= 26))
        ].sort_values('mwar-1', ascending=False).head(20)
        rising_players['rank'] = rising_players['mwar-1'].rank(ascending=False)

        falling_players = currentMonth.loc[
            (currentMonth['Lev'] != 'MLB') & ~((currentMonth['old grade'] < 8) | (currentMonth['Age'] >= 26))
        ].sort_values('mwar-1', ascending=True).head(20)
        falling_players['rank'] = falling_players['mwar-1'].rank()

        rising = clean_tables(rising_players, 'farm-system', include_team=True)
        falling = clean_tables(falling_players, 'farm-system', include_team=True)

        return render_template('team.html',
                               name='Rising',
                               team_logo=None,
                               prospects=falling,
                               roster=rising,
                               batting_table=None,
                               pitching_table=None,
                               phrase=random.choice(phrases))


@app.route('/draft-class/<year>')
@app.route('/draft-class/<year>/<team>')
def draft_class(year: str, team: str = None):
    year = int(year)
    # set up the info for non-team results
    year_info = draft_results.loc[draft_results['class'] == year]
    grade_min = 8

    if team is not None:
        year_info = year_info.loc[year_info['team']==team.upper()]
        grade_min = 0

    # print(year)
    year_info = pd.concat([year_info.set_index('HELPER'), 
                           currentMonth.set_index('HELPER')],
                          axis=1, join='inner').reset_index()

    best_players = year_info.loc[year_info['old grade'] > grade_min].sort_values('mwar_mean', ascending=False)

    while best_players.shape[0] < 50:
        grade_min = grade_min - 1
        best_players = year_info.loc[year_info['old grade'] > grade_min].sort_values('mwar_mean', ascending=False)
        
    best_players['rank'] = best_players['mwar_mean'].rank(ascending=False)
    best_players['TM'] = best_players['team']

    player_tbl = clean_tables(best_players, 'farm-system', include_team=True)


    if team is None:
        pivot = pd.pivot_table(year_info,
                               values=['old grade', 'mwar_mean'],
                               index='team')
        pivot = pivot.sort_values('mwar_mean', ascending=False).reset_index()

        team_tbl = pivot.style.render()
    else:
        team_tbl = None

    return render_template('team.html',
                           name=year,
                           team_logo=None,
                           prospects=team_tbl,
                           roster=player_tbl,
                           batting_table=year,
                           pitching_table=None,
                           phrase=random.choice(phrases))


@app.route('/team/<team>')
def team(team):
    # get players w/ OG > 5
    subset = currentMonth.loc[(currentMonth['TM'] == team) & (currentMonth['Lev'] != 'MLB') & (currentMonth['old grade'] > 5)].sort_values('old grade', ascending=False)
    # also drop old dudes w/ OG < 8 (non-propsects that have topped out)
    subset = subset.loc[~((subset['old grade'] < 8) & (subset['Age'] >= 26))]
    prospects = clean_tables(subset, 'farm-system')

    # check if there's a team
    if subset.shape[0]==0:
        return render_template('landing.html', error='Team not found.', phrase = random.choice(phrases))

    # then pull ML roster
    subset = currentMonth.loc[(currentMonth['TM'] == team) & (currentMonth['Lev'] == 'MLB')].sort_values('old grade', ascending=False)
    roster = clean_tables(subset, 'ml-roster')

    # avoid generating line-ups, team header for FA
    if team != 'FA':
        pitching_table, batting_table = generate_lineup_card(subset)

        team_finances = finances.loc[finances['Name']==team].iloc[0]
        header_str_rec = '{0} - {1} ({2} Pythagorean, {3} Robit)' 
        header_str_fin = 'Budget: {0} | Cash: {1} | Payroll: {2}'
        header_str_ded = '${:,.0f} in dead money - <br> {}'

        py_diff = team_finances['W'] - team_finances['pW']
        r_diff = team_finances['W'] - team_finances['rW']

        if py_diff > 0:
            py_str = '<font color="green"> {} </font>'.format(py_diff)
        else:
            py_str = '<font color="red"> {} </font>'.format(py_diff)

        if r_diff > 0:
            r_str = '<font color="green"> {} </font>'.format(r_diff)
        else:
            r_str = '<font color="red"> {} </font>'.format(r_diff)

        dead_money = currentMonth.loc[
            (currentMonth['TM'] == team) & 
            (currentMonth['POT'] < 50) & 
            (currentMonth['old grade'] < 8) &
            (currentMonth['SLR'] != '-')
        ]

        dead_money['SLR'] = dead_money['SLR'].apply(lambda x: float(x[1:].replace(',', '')))
        dead_money = dead_money.sort_values('SLR', ascending=False)
        dead_money = dead_money.loc[ dead_money['SLR'] > 1000000]
        dead_amt =  dead_money['SLR'].sum()

        if dead_money.shape[0] > 0:
            dead_names = '<br>'.join(list(dead_money.apply(lambda x: '{} {} ({:.1f} ${:,.0f})'.format(x['POS'], x['Name'], x['old grade'], x['SLR']), axis=1)))
        else:
            dead_names = ''


        header_rec = header_str_rec.format(
            team_finances['W'],
            team_finances['L'],
            py_str,
            r_str
        )

        header_fin = header_str_fin.format(
            team_finances['Budget'],
            team_finances['Cash'], 
            team_finances['Payroll']
        )

        header_ded = header_str_ded.format(dead_amt, dead_names)

    else:
        pitching_table = ''
        batting_table = ''
        header_rec='',
        header_fin='',
        header_ded='',
        
    return render_template('team.html',
                            name=full_team_name[team],
                            header_rec=header_rec,
                            header_fin=header_fin,
                            header_ded=header_ded,
                            team_logo='../static/team_logos/{}.png'.format(team),
                            prospects=prospects,
                            roster=roster, 
                            batting_table=batting_table,
                            pitching_table=pitching_table,
                            phrase=random.choice(phrases))


@app.route('/pos/<pos>')
def pos(pos):
    if pos == 'SP':
        subset = currentMonth.loc[(currentMonth['ip_mean'] > 150) & (currentMonth['Lev'] != 'MLB')].sort_values('pwar_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['pwar_mean'].rank(ascending=False))
        prospects = clean_tables(subset, 'farm-system', include_team=True)

        subset = currentMonth.loc[(currentMonth['ip_mean'] > 150) & (currentMonth['Lev'] == 'MLB')].sort_values('pwar_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['pwar_mean'].rank(ascending=False))
        roster = clean_tables(subset, 'ml-roster', include_team=True)

    elif pos == 'RP':
        subset = currentMonth.loc[(currentMonth['ip_mean'] < 150) & (currentMonth['Lev'] != 'MLB')].sort_values('fip_mean')
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['fip_mean'].rank())
        prospects = clean_tables(subset, 'farm-system', include_team=True)

        subset = currentMonth.loc[(currentMonth['ip_mean'] < 150) & (currentMonth['Lev'] == 'MLB')].sort_values('pwar_mean')
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['fip_mean'].rank())
        roster = clean_tables(subset, 'ml-roster', include_team=True)

    elif pos == 'OF':
        qual = (currentMonth['LF_runs'] > SCRATCH_LEVELS['LF']) |  (currentMonth['CF_runs'] > SCRATCH_LEVELS['CF']) |  (currentMonth['RF_runs'] > SCRATCH_LEVELS['RF'])
        subset = currentMonth.loc[qual & (currentMonth['Lev'] != 'MLB')].sort_values('woba_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['woba_mean'].rank(ascending=False))
        prospects = clean_tables(subset, 'farm-system', include_team=True)

        subset = currentMonth.loc[qual & (currentMonth['Lev'] == 'MLB')].sort_values('woba_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['woba_mean'].rank(ascending=False))
        roster = clean_tables(subset, 'ml-roster', include_team=True)

    elif pos == 'IF':
        qual = (currentMonth['2B_runs'] > SCRATCH_LEVELS['2B']) |  (currentMonth['3B_runs'] > SCRATCH_LEVELS['3B']) |  (currentMonth['SS_runs'] > SCRATCH_LEVELS['SS'])
        subset = currentMonth.loc[qual & (currentMonth['Lev'] != 'MLB')].sort_values('woba_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['woba_mean'].rank(ascending=False))
        prospects = clean_tables(subset, 'farm-system', include_team=True)

        subset = currentMonth.loc[qual & (currentMonth['Lev'] == 'MLB')].sort_values('woba_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['woba_mean'].rank(ascending=False))
        roster = clean_tables(subset, 'ml-roster', include_team=True)

    else:
        subset = currentMonth.loc[(currentMonth[pos + '_runs'] > SCRATCH_LEVELS[pos]) & (currentMonth['Lev'] != 'MLB')].sort_values('woba_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['woba_mean'].rank(ascending=False))
        prospects = clean_tables(subset, 'farm-system', include_team=True)

        subset = currentMonth.loc[(currentMonth[pos + '_runs'] > SCRATCH_LEVELS[pos]) & (currentMonth['Lev'] == 'MLB')].sort_values('woba_mean', ascending=False)
        subset = subset.iloc[0:50]
        subset.insert(loc=4, column='rank', value=subset['woba_mean'].rank(ascending=False))
        roster = clean_tables(subset, 'ml-roster', include_team=True)

    return render_template('team.html', name = pos, prospects = prospects, roster=roster, phrase = random.choice(phrases))


@app.route('/player/<helper>')
def player(helper):
    subset = currentMonth.loc[currentMonth['HELPER'] == helper]
    subset['Month'] = currMonth

    subset = subset[PLAYER_SUBSET]

    # store the first month to make decisions on position/age later
    curr_mo_subset = subset.iloc[0] 

    for month in months[1:]:
        newLine = dfs[month]
        newLine = newLine.loc[newLine['HELPER'] == helper]
        newLine['Month'] = month
        newLine = newLine[PLAYER_SUBSET]
        subset = subset.append(newLine)

    subset.insert(loc=5, column='og80', value=(subset['mwar_mean']*0.8 + subset['POT'] / 50))

    round_three = ['woba', 'woba_mean']
    round_two = ['og80', 'fip', 'fip_mean']
    round_one = ['old grade', 'POT', 'bwar', 'bwar_mean', 'ip', 'pwar', 'pwar_mean']

    subset[round_three] = subset[round_three].round(3)
    subset[round_two] = subset[round_two].round(2)
    subset[round_one] = subset[round_one].round(1)


    # get HTML from table, then make table sortable
    # table = subset.to_html(index=False, classes=["table-bordered", "table-striped", "table-hover"])
    # table = table[0:7] + 'id="players" ' + table[7:]
    
    # i = 0
    # while table.find('<th>') != -1:
    #     table = table.replace('<th>', '<th onclick="sortTable(' + str(i) + ', )">', 1)
    #     i = i + 1

    src = 'images\\' + helper + '.png'

    # gettting unique index errors b/c players will occasionally fall in the same spot
    subset = subset.reset_index().drop(columns='index')
    # subset = subset
    subset_drop_cols = ['mwar_mean', 'mwar-1', 'og-1', 'pwoba-1', 'pfip-1']

    table = subset.drop(subset_drop_cols, axis=1).style.applymap(
        rating_colors,
        subset=['POT']
    ).applymap(
        highlight_mwar,
        subset=['bwar', 'bwar_mean', 'pwar', 'pwar_mean']
    ).set_properties(
        **(dict(**TABLE_PROPERTIES, **{'font-size': '1.5em'}))
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.5em')]}]
    ).hide_index().render()

    # things to print
    bio_series = currentMonth.loc[currentMonth['HELPER'] == helper].iloc[0][BIO_COLS]

    # get the numbers to build tables with
    def_stats = currentMonth.loc[currentMonth['HELPER'] == helper][DEF_STAT_COLUMNS]
    def_ratings = currentMonth.loc[currentMonth['HELPER'] == helper][DEF_RAT_COLUMNS]
    bat_ratings = currentMonth.loc[currentMonth['HELPER'] == helper][BAT_RAT_COLUMNS]
    pit_ratings = currentMonth.loc[currentMonth['HELPER'] == helper][PIT_RAT_COLUMNS]
    other_ratings = currentMonth.loc[currentMonth['HELPER'] == helper][OTHER_RAT_COLUMNS]

    # then build table
    name = generate_player_name(bio_series)
    rating_header = generate_ratings_header(subset)
    bio = generate_player_header(bio_series)
    #stats = generate_player_stat_string(bio_series)
    def_rats, def_stats, best_pos = generate_defense_table(def_stats, def_ratings)
    bat_rats = generate_bat_table(bat_ratings, helper)
    pit_rats = generate_pit_table(pit_ratings, helper)
    other_rats = generate_other_table(other_ratings, helper)

    # and a little text snippet of recent ratings changes
    changes = []

    for i in range(len(months)-2):
        cur_mo = months[i]
        last_mo = months[i+1]

        total_rats = BAT_RAT_COLUMNS + PIT_RAT_COLUMNS
        cur_df = dfs[cur_mo]
        last_df = dfs[last_mo]

        cur_ratings = cur_df.loc[cur_df['HELPER'] == helper][total_rats]
        last_ratings = last_df.loc[last_df['HELPER'] == helper][total_rats]

        if last_ratings.empty:
            break

        for rating in (BAT_RAT_COLUMNS + PIT_RAT_COLUMNS):
            if cur_ratings.iloc[0][rating] - last_ratings.iloc[0][rating] > 2:
                change_str = '<font color="green"> {0}: {1} improves from {2:.3} to {3:.3} / 80.</font>'.format(
                    cur_mo, rating, last_ratings.iloc[0][rating], cur_ratings.iloc[0][rating]
                )
                changes.append(change_str)
            elif cur_ratings.iloc[0][rating] - last_ratings.iloc[0][rating] < -2:
                change_str = '<font color="red"> {0}: {1} drops from {2:.3} to {3:.3} / 80.</font>'.format(
                    cur_mo, rating, last_ratings.iloc[0][rating], cur_ratings.iloc[0][rating]
                )
                changes.append(change_str)

    total_change_str = '<br/>'.join(changes)

    # put the player subset -> json to use in d3
    # keep index as x-axis
    subset = subset.reset_index()
    
    subset['mwar'] = subset[['bwar', 'pwar']].apply(np.max, axis=1)
    subset = subset[['index', 'Month', 'old grade', 'woba', 'woba_mean', 'fip', 'fip_mean', 'mwar_mean', 'mwar']].to_json(orient='records')

    bat_levs = batting_benchmarks[[best_pos, 'lev']].rename({best_pos: 'pos'}, axis=1)
    bat_levs = bat_levs.to_json(orient='records')

    pit_levs = pitching_benchmarks[['SP', 'lev']].to_json(orient='records')

    other_teams = pot_grid.loc[pot_grid['HELPER']==helper]
    other_team_table = other_teams.drop('HELPER', axis=1).style.applymap(
        rating_colors,
    ).set_properties(**{
            'text-align': 'left',
            'padding': '15px',
            'margin-bottom': '40px',
            'font-size': '1.4em'
        } 
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).hide_index().render()

    return render_template('player.html', 
                            name = name, 
                            rating_header=rating_header,    
                            bio = bio, 
                            # stats = stats, 
                            table = table, 
                            def_rats = def_rats, 
                            def_stats = def_stats, 
                            bat_rats = bat_rats,
                            pit_rats = pit_rats,
                            other_rats = other_rats,
                            subset = subset,
                            bat_levs = bat_levs,
                            pit_levs = pit_levs,
                            other_team_table=other_team_table,
                            months = {'months': reversed_months},
                            total_change_str = total_change_str,
                            phrase = random.choice(phrases))


@app.route('/compare')
@app.route('/compare/<helper1>')
def comparisonSearch(helper1 = None):
    if helper1 != None:
        return render_template('comparisonSearch.html', name=helper1, phrase = random.choice(phrases))
    
    return render_template('comparisonSearch.html', phrase = random.choice(phrases))


@app.route('/compare/<helper1>/<helper2>')
def comparison(helper1, helper2):
    players = currentMonth.loc[(currentMonth['HELPER'] == helper1) | (currentMonth['HELPER'] == helper2)]

    buttonStart = '<input type="button" value="Player Page" onclick="window.location.href=\'/player/'
    buttonEnd = '\'" />'
    players['HELPER'] = buttonStart + players['HELPER'] + buttonEnd

    players['Name'] = '<b>' + players['Name'] + '</b>'
                        
    players = players[ALL_STAT_COLS]

    players[THREE_DEC] = players[THREE_DEC].round(3)
    players[TWO_DEC] = players[TWO_DEC].round(2)
    players[ONE_DEC] = players[ONE_DEC].round(1)
    
    players = players.transpose()
    #players = players[]
    
    table = players.to_html(classes=["table-bordered", "table-striped", "table-hover"], header=False)
    table = table[0:7] + 'id="players" ' + table[7:]

    # find and replace right tags the pandas to_html fucked
    table = table.replace('&lt;', '<')
    table = table.replace('&gt;', '>')
    table = table.replace('HELPER', 'Player Page')

    return render_template('comparisons.html', table=table, phrase = random.choice(phrases))
