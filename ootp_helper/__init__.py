from flask import Flask, render_template, request, redirect, session
import numpy as np
import random
from pymongo import MongoClient

# import matplotlib
# matplotlib.use('Agg')

from ootp_helper.constants import *
from ootp_helper.data_reading import create_player_data, create_benchmarks, read_dist_data, create_standings
from ootp_helper.player.header_text import generate_player_name, generate_player_header, generate_player_stat_string, generate_ratings_header
from ootp_helper.player.run_calculators import *
from ootp_helper.player.table_generators import *
from ootp_helper.position.position_utils import create_position_tables
from ootp_helper.color_maps import *
from ootp_helper.utils import clean_tables, create_table_json, get_front_page_data
from ootp_helper.team.team_utils import add_splits_data, generate_lineup_card

(al_standing_tables, nl_standing_tables, finances) = create_standings()
(batting_benchmarks, pitching_benchmarks) = create_benchmarks()

# stop rounding my buttons
pd.set_option('display.max_colwidth', -1)

# database connection
read_user = 'read_connection'
read_pass = 'password123'
client = MongoClient(
    'mongodb://{0}:{1}@ds253368.mlab.com:53368/flask_robit?retryWrites=false'.format(read_user, read_pass)
)
db = client['flask_robit']

# the data for columns on the front page
all_rise = get_front_page_data(db, {'og-1': {'$gte': 0.5}, 'POS': {'$nin': ['RP', 'CL']}})
all_fall = get_front_page_data(db, {'og-1': {'$lte': -0.5}})
partial_rise = get_front_page_data(db, {'og-1': {'$gte': 0.5}, 'TM': {'$in': ['COL', 'CIN', 'WAS']}})
partial_fall = get_front_page_data(db, {'og-1': {'$lte': -0.5}, 'TM': {'$in': ['COL', 'CIN', 'WAS']}})


def generate_error_message(message: str):
    return render_template(
        'landing.html',
        col_names=json.dumps([''] + FRONT_PAGE_COLS[1:]),
        all_rise=json.dumps(all_rise),
        all_fall=json.dumps(all_fall),
        partial_rise=json.dumps(partial_rise),
        partial_fall=json.dumps(partial_fall),
        error=message,
        phrase=random.choice(phrases),
    )


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'supes_secrit_key'


@app.route('/')
def landing_page():
    return render_template(
        'landing.html',
        col_names=json.dumps([''] + FRONT_PAGE_COLS[1:]),
        all_rise=json.dumps(all_rise),
        all_fall=json.dumps(all_fall),
        partial_rise=json.dumps(partial_rise),
        partial_fall=json.dumps(partial_fall),
        phrase=random.choice(phrases),
    )


@app.route('/', methods=['POST'])
@app.route('/rising-prospects', methods=['POST'])
@app.route('/team/<team>', methods=['POST'])
@app.route('/pos/<pos>', methods=['POST'])
@app.route('/player/<player>', methods=['POST'])
@app.route('/compare', methods=['POST'])
@app.route('/compare/<helper1>', methods=['POST'])
@app.route('/compare/<helper1>/<helper2>', methods=['POST'])
def landing_page_team_request(team=None, pos=None, player=None, helper1=None, helper2=None, year=None):
    
    if 'player' in request.form.keys():
        # grab text, get table of players w/ that name
        text = request.form['player']

        if len(text) < 3:
            return generate_error_message('Search too short; may give too many results')

        processed_text = text.lower()

        potential_players = db[months[0]].find({'Name': {'$regex': processed_text, '$options': 'i'}}).distinct('_id')
        
        if len(potential_players) == 0:
            return generate_error_message('{} not found'.format(text))

        if len(potential_players) == 1:
            return redirect('/player/{}'.format(potential_players[0]))

        session['search_results'] = potential_players
        return redirect('/search')

    if 'comparison' in request.form.keys():
        # grab text, get table of players w/ that name
        text = request.form['comparison']

        if len(text) < 3:
            return generate_error_message('Search too short; may give too many results')

        processed_text = text.lower()
        potential_players = db[months[0]].find({'Name': {'$regex': processed_text, '$options': 'i'}}).distinct('_id')

        if len(potential_players) == 0:
            return generate_error_message('{} not found'.format(text))

        if len(potential_players) == 1:
            if helper1 is not None:
                return redirect('/compare/{0}/{1}'.format(helper1, potential_players[0]))
            
            return redirect('/compare/{}'.format(potential_players[0]))

        session['search_results'] = potential_players

        if helper1 is not None:
            return redirect('/compsearch/{}'.format(helper1))
        else:
            return redirect('/compsearch')

    elif 'team' in request.form.keys():
        text = request.form['team']
        processed_text = text.upper()

        # would throw error if team was blank
        if processed_text == '':
            return generate_error_message('Please enter a team.')

        # check to see if this is a position
        if processed_text in POS:
            return redirect('/pos/{}'.format(processed_text))

        if processed_text in ['RISING', 'RIS', 'R']:
            return redirect('rising-prospects')

        if len([x for x in db[months[0]].find({'TM': processed_text})]) > 0:
            return redirect('/team/{}'.format(processed_text))

        return generate_error_message('Invalid team choice.')

    else:
        return generate_error_message('An error has occurred. Please berate Hugh at your convenience.')



@app.route('/search')
def search_results():
    # get the search results
    potential_results = session.get('search_results', None)

    player_records = db[months[0]].find({'_id': {'$in': potential_results}})
    player_df = pd.DataFrame.from_records([record for record in player_records])
    player_df.rename({'_id': 'HELPER'}, axis=1, inplace=True)
    player_df = player_df[PLAYER_DISP]
    player_df['HELPER'] = player_df['HELPER'].apply(lambda x: BUTTON_STRING.format(x.replace("'", "%27")))

    table = player_df.to_html(index=False, classes=["table-bordered", "table-striped", "table-hover"])
    table = table[0:7] + 'id="players" ' + table[7:]

    # find and replace right tags the pandas to_html fucked
    table = table.replace('&lt;', '<').replace('&gt;', '>').replace('HELPER', 'Player Page')

    return render_template('player_select.html', table=table, phrase=random.choice(phrases))


@app.route('/search')
def player_search_results_request():
    form_id = request.form['submit_button']
    return redirect('/player/{}'.format(form_id))


@app.route('/compsearch')
@app.route('/compsearch/<helper1>')
def comp_search_results(helper1=None):
    # get the search results
    potential_results = session.get('search_results', None)

    player_records = db[months[0]].find({'_id': {'$in': potential_results}})
    player_df = pd.DataFrame.from_records([record for record in player_records])
    player_df.rename({'_id': 'HELPER'}, axis=1, inplace=True)
    player_df = player_df[PLAYER_DISP]

    if helper1:
        player_df['HELPER'] = player_df['HELPER'].apply(lambda x: COMPARISON_PAGE_STRING.format(helper1, x))
    else:
        player_df['HELPER'] = player_df['HELPER'].apply(lambda x: COMPARISON_SEARCH_STRING.format(x))

    table = player_df.to_html(index=False, classes=["table-bordered", "table-striped", "table-hover"])
    table = table[0:7] + 'id="players" ' + table[7:]

    # find and replace right tags the pandas to_html fucked
    table = table.replace('&lt;', '<').replace('&gt;', '>').replace('HELPER', 'Player Page')

    return render_template('player_select.html', table=table, phrase=random.choice(phrases))


@app.route('/compsearch')
@app.route('/compsearch/<helper1>')
def comp_search_results_request(helper1=None):
    form_id = request.form['submit_button']

    if helper1 is not None:
        return redirect('/compare/{0}/{1}'.format(helper1, form_id))

    return redirect('/compare/{}'.format(form_id))


@app.route('/rising-prospects')
@app.route('/rising-prospects/<position>')
def rising_prospect_page(position=None):

    if position is None:
        rising_records = db[months[0]].find({
            'Lev': {'$ne': 'MLB'},
            '$and': [{'old grade': {'$gte': 8}}, {'Age': {'$lte': 26}}],
        }).sort('mwar-1', -1).limit(20)

        rising_players = pd.DataFrame.from_records(
            [record for record in rising_records]
        ).rename(
            {'_id': 'HELPER'},
            axis=1,
        )

        rising_players['rank'] = rising_players['mwar-1'].rank(ascending=False)

        falling_records = db[months[0]].find({
            'Lev': {'$ne': 'MLB'},
            '$and': [{'old grade': {'$gte': 8}}, {'Age': {'$lte': 26}}],
        }).sort('mwar-1', 1).limit(20)

        falling_players = pd.DataFrame.from_records(
            [record for record in falling_records]
        ).rename(
            {'_id': 'HELPER'},
            axis=1,
        )

        falling_players['rank'] = falling_players['mwar-1'].rank()

        rising = clean_tables(rising_players, 'farm-system', include_team=True)
        falling = clean_tables(falling_players, 'farm-system', include_team=True)

        return render_template(
            'team.html',
            name='Rising',
            team_logo=None,
            prospects=falling,
            roster=rising,
            batting_table=None,
            pitching_table=None,
            phrase=random.choice(phrases),
        )


@app.route('/team/<team>')
def team(team: str):

    minors_query = db[months[0]].find({'TM': team, 'Lev': {'$ne': 'MLB'}}).sort('old grade', -1)
    minors_records = [record for record in minors_query]
    minors_records = add_splits_data(minors_records)

    if team != 'FA':
        majors_query = db[months[0]].find({'TM': team, 'Lev': 'MLB'}).sort('old grade', -1)
        majors_records = [record for record in majors_query]
        majors_records = add_splits_data(majors_records)

        # check if there's a team
        if len(majors_records) == 0 and team != 'DRAFT':
            generate_error_message('Team not found.')

        majors_df = pd.DataFrame.from_records(majors_records).rename({'_id': 'HELPER'}, axis=1).fillna(0)

    minors_df = pd.DataFrame.from_records(minors_records).rename({'_id': 'HELPER'}, axis=1).fillna(0)
    prosects_columns, prospects_data = create_table_json(minors_df)

    if team not in ['DRAFT', 'FA']:
        majors_columns, majors_data = create_table_json(majors_df)
        total_df = pd.concat([minors_df, majors_df], ignore_index=True)

        pitching_table, batting_table = generate_lineup_card(majors_df)

        team_finances = finances.loc[finances['Name'] == team].iloc[0]
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

        dead_money = total_df.loc[
            (total_df['POT'] < 50) &
            (total_df['old grade'] < 8) &
            (total_df['SLR'] != '-')
        ]

        dead_money['SLR'] = dead_money['SLR'].apply(lambda x: float(x[1:].replace(',', '')))
        dead_money = dead_money.sort_values('SLR', ascending=False)
        dead_money = dead_money.loc[dead_money['SLR'] > 1000000]
        dead_amt = dead_money['SLR'].sum()

        if dead_money.shape[0] > 0:
            salary_strings = dead_money.apply(
                lambda x: '{} {} ({:.1f} ${:,.0f})'.format(x['POS'], x['Name'], x['old grade'], x['SLR']),
                axis=1
            )
            dead_names = '<br>'.join(list(salary_strings))
        else:
            dead_names = ''

        header_rec = header_str_rec.format(
            team_finances['W'],
            team_finances['L'],
            py_str,
            r_str,
        )

        header_fin = header_str_fin.format(
            team_finances['Budget'],
            team_finances['Cash'], 
            team_finances['Payroll'],
        )

        header_ded = header_str_ded.format(dead_amt, dead_names)

    else:
        total_df = minors_df
        majors_columns = []
        majors_data = []
        pitching_table = ''
        batting_table = ''
        header_rec = ''
        header_fin = ''
        header_ded = ''

    # other scouts takes
    with_bio = [record for record in db['scout_takes'].find({'TM': team})]
    with_bio = pd.DataFrame.from_records(with_bio)
    with_bio.rename({'_id': 'HELPER'}, axis=1, inplace=True)

    scout_bio_cols = ['HELPER', 'POS', 'Lev', 'Age', 'old grade', 'mwar_mean']

    with_bio = pd.merge(total_df[scout_bio_cols], with_bio, on='HELPER')
    with_bio['HELPER'] = with_bio['HELPER'].apply(lambda x: BUTTON_STRING.format(x.replace("'", "%27")))

    with_bio['old grade'] = with_bio['old grade'].round(1)
    with_bio['mwar_mean'] = with_bio['mwar_mean'].round(1)
    with_bio.drop('TM', axis=1, inplace=True)

    # reorder columns
    scout_takes_cols = list(set(with_bio.columns) - set(OTHER_SCOUT_COLUMN_ORDER))
    with_bio = with_bio[OTHER_SCOUT_COLUMN_ORDER + scout_takes_cols]

    other_scouts_columns = list(with_bio.columns)
    other_scouts_columns = ['' if col == 'HELPER' else col for col in other_scouts_columns]
    other_scouts_data = with_bio.values.tolist()

    non_team_cols = scout_bio_cols + ['', 'Name']
    other_scouts_indexes = [idx for idx, val in enumerate(other_scouts_columns) if val not in non_team_cols]

    return render_template(
        'team.html',
        name=full_team_name[team],
        header_rec=header_rec,
        header_fin=header_fin,
        header_ded=header_ded,
        team_logo='../static/team_logos/{}.png'.format(team),
        prospects_columns=prosects_columns,
        prospects_data=prospects_data,
        majors_columns=majors_columns,
        majors_data=majors_data,
        batting_table=batting_table,
        pitching_table=pitching_table,
        other_scouts_columns=other_scouts_columns,
        other_scouts_data=other_scouts_data,
        other_scout_indexes=other_scouts_indexes,
        phrase=random.choice(phrases),
    )


@app.route('/pos/<pos>')
def pos(pos: str):
    pos = pos.upper()

    if pos in ['SP', 'RP']:
        if pos == 'SP':
            position_filter = {'ip_mean': {'$gte': 150}}
            sort_column = 'pwar_mean'
            sort_order = -1

        else:
            position_filter = {'ip_mean': {'$lte': 150}}
            sort_column = 'fip_mean'
            sort_order = 1

    else:
        if pos == 'OF':
            position_filter = {
                '$or': [
                    {'LF_runs': {'$gte': SCRATCH_LEVELS['LF']}},
                    {'CF_runs': {'$gte': SCRATCH_LEVELS['CF']}},
                    {'CF_runs': {'$gte': SCRATCH_LEVELS['CF']}},
                ],
            }

        elif pos == 'IF':
            position_filter = {
                '$or': [
                    {'2B_runs': {'$gte': SCRATCH_LEVELS['2B']}},
                    {'3B_runs': {'$gte': SCRATCH_LEVELS['3B']}},
                    {'SS_runs': {'$gte': SCRATCH_LEVELS['SS']}},
                ],
            }
        else:
            position_filter = {pos + '_runs': {'$gte': SCRATCH_LEVELS[pos]}}

        sort_column = 'woba_mean'
        sort_order = -1

    prospects, roster = create_position_tables(db, position_filter, sort_column, sort_order)

    return render_template('team.html', name=pos, prospects=prospects, roster=roster, phrase=random.choice(phrases))


@app.route('/player/<helper>')
def player(helper):
    player_records = [db[month].find_one({'_id': helper}) for month in months]
    player_records = [record for record in player_records if record is not None]

    war_dist_data = db['dist_data'].find_one({'_id': helper})

    subset = pd.DataFrame.from_records(player_records)[PLAYER_SUBSET]
    subset.insert(loc=5, column='og80', value=(subset['mwar_mean'] * 0.8 + subset['POT'] / 50))

    round_three = ['woba', 'woba_mean']
    round_two = ['og80', 'fip', 'fip_mean']
    round_one = ['old grade', 'POT', 'bwar', 'bwar_mean', 'ip', 'pwar', 'pwar_mean']

    subset[round_three] = subset[round_three].round(3)
    subset[round_two] = subset[round_two].round(2)
    subset[round_one] = subset[round_one].round(1)

    # getting unique index errors b/c players will occasionally fall in the same spot
    subset = subset.reset_index().drop(columns='index')
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

    # get the numbers to build tables with
    current_record = db[months[0]].find_one({'_id': helper})
    current_df = pd.DataFrame.from_records([current_record])

    def_stats = current_df[DEF_STAT_COLUMNS]
    def_ratings = current_df[DEF_RAT_COLUMNS]
    bat_ratings = current_df[BAT_RAT_COLUMNS]
    pit_ratings = current_df[PIT_RAT_COLUMNS]
    other_ratings = current_df[OTHER_RAT_COLUMNS]
    pitch_ratings = current_df[IND_PIT_COLUMNS + IND_PIT_POT_COLUMNS]

    # then build table
    bat_splits = generate_splits_table(current_record, BAT_RAT_COLUMNS)
    pit_splits = generate_splits_table(current_record, PIT_RAT_COLUMNS)

    name = generate_player_name(player_records[0])
    rating_header = generate_ratings_header(subset, bat_splits, pit_splits, war_dist_data)
    bio = generate_player_header(player_records[0])
    def_rats, def_stats, best_pos = generate_defense_table(def_stats, def_ratings)
    bat_rats = generate_rating_table(bat_ratings, True)
    pit_rats = generate_rating_table(pit_ratings, False)
    other_rats = generate_other_table(other_ratings)
    ind_pit_rats = generate_ind_pitch_table(pitch_ratings)

    # and a little text snippet of recent ratings changes
    changes = []

    for i in range(len(months)-1):

        if i + 1 >= len(player_records):
            break

        total_rats = BAT_RAT_COLUMNS + PIT_RAT_COLUMNS
        current_records = player_records[i]
        last_month_records = player_records[i+1]

        for rating in total_rats:
            change_str = None

            if current_records[rating] - last_month_records[rating] > 2:
                change_str = '<font color="green"> {0}: {1} improves from {2:.3} to {3:.3} / 80.</font>'

            elif current_records[rating] - last_month_records[rating] < -2:
                change_str = '<font color="red"> {0}: {1} drops from {2:.3} to {3:.3} / 80.</font>'\

            if change_str:
                changes.append(change_str.format(
                    months[i], rating, last_month_records[rating], current_records[rating]
                ))

    total_change_str = '<br/>'.join(changes)

    # put the player subset -> json to use in d3
    # keep index as x-axis
    subset = subset.reset_index()
    
    subset['mwar'] = subset[['bwar', 'pwar']].apply(np.max, axis=1)
    columns_used = ['index', 'Month', 'old grade', 'woba', 'woba_mean', 'fip', 'fip_mean', 'mwar_mean', 'mwar']
    subset = subset[columns_used].to_json(orient='records')

    bat_levels = batting_benchmarks[[best_pos, 'lev']].rename({best_pos: 'pos'}, axis=1)
    bat_levels = bat_levels.to_json(orient='records')

    pit_levels = pitching_benchmarks[['SP', 'lev']].to_json(orient='records')

    other_teams = [record for record in db['scout_takes'].find({'_id': helper})]
    other_teams = pd.DataFrame.from_records(other_teams)

    other_team_table = other_teams.drop(['_id', 'TM', 'Name'], axis=1).style.applymap(
        rating_colors,
    ).set_properties(
        **{
            'text-align': 'left',
            'padding': '15px',
            'margin-bottom': '40px',
            'font-size': '1.4em'
        } 
    ).set_table_styles(
        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
    ).hide_index().render()

    return render_template(
        'player.html',
        name=name,
        rating_header=rating_header,
        bio=bio,
        table=table,
        def_rats=def_rats,
        def_stats=def_stats,
        bat_rats=bat_rats,
        pit_rats=pit_rats,
        other_rats=other_rats,
        ind_pit_rats=ind_pit_rats,
        bat_splits=json.dumps(bat_splits),
        pit_splits=json.dumps(pit_splits),
        subset=subset,
        bat_levs=bat_levels,
        pit_levs=pit_levels,
        other_team_table=other_team_table,
        months={'months': reversed_months},
        total_change_str=total_change_str,
        war_dists=war_dist_data,
        phrase=random.choice(phrases),
    )


@app.route('/compare')
@app.route('/compare/<helper1>')
def comparison_search(helper1=None):
    if helper1:
        return render_template('comparisonSearch.html', name=helper1, phrase=random.choice(phrases))
    
    return render_template('comparisonSearch.html', phrase=random.choice(phrases))


@app.route('/compare/<helper1>/<helper2>')
def comparison(helper1, helper2):
    player_records = db[months[0]].find({'_id': {'$in': [helper1, helper2]}})
    players = pd.DataFrame.from_records([x for x in player_records]).rename({'_id': 'HELPER'}, axis=1)

    players['HELPER'] = players['HELPER'].apply(lambda x: BUTTON_STRING.format(x.replace("'", "%27")))
    players['Name'] = players['Name'].apply(lambda x: '<b> {} </b>'.format(x))
                        
    players = players[ALL_STAT_COLS]

    players[THREE_DEC] = players[THREE_DEC].round(3)
    players[TWO_DEC] = players[TWO_DEC].round(2)
    players[ONE_DEC] = players[ONE_DEC].round(1)
    
    players = players.transpose()

    table = players.to_html(classes=["table-bordered", "table-striped", "table-hover"], header=False)
    table = table[0:7] + 'id="players" ' + table[7:]

    # find and replace right tags the pandas to_html fucked
    table = table.replace('&lt;', '<')
    table = table.replace('&gt;', '>')
    table = table.replace('HELPER', 'Player Page')

    return render_template('comparisons.html', table=table, phrase = random.choice(phrases))
