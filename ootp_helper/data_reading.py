import pandas as pd
import seaborn as sns
from typing import Tuple

from ootp_helper.constants import old_to_new, TABLE_PROPERTIES

def create_player_data(months: list) -> dict:
	dfs = {}

	# read in month-by-month
	for month in months:
	    df = pd.read_pickle('pickles/' + month + '.pickle')
	    df['HELPER'] = df['HELPER'].str.replace(' ', '').str.replace('/', '-')

	    df = df.fillna(0)
	    dfs[month] = df

	return dfs


def render_standing_tables(divs: list, standings: pd.DataFrame, cm) -> dict:
	div_dict = {}

	for division in divs:
		# subset div, drop cols we don't want
	    subset = standings.loc[standings['division']==division]
	    subset = subset.drop(['rotation', 'pen', 'lineup', 'bench', 'division'], axis=1)

	    # render table
	    div_dict[division] = subset.style.background_gradient(
	        subset=['Division', 'WC', 'Playoffs'],
	        cmap=cm,
	        low=0,
	        high=1
	    ).set_properties(
	        **TABLE_PROPERTIES
	    ).set_table_styles(
	        [{'selector': 'th', 'props': [('font-size', '1.2em')]}]
	    ).hide_index().render()

	return div_dict


def create_standings() -> Tuple[dict, dict]:
	# read standings from csv, create team link
	standings = pd.read_csv('current_projections.csv')
	standings['Team'] = standings['Team'].apply(
		lambda x: "<a  href='./team/{}'><img height='50px' src=../static/team_logos/{}.png></a>".format(x, x)
	)

	# empty dicts to store rendered tables
	al_standing_tables = {}
	nl_standing_tables = {}

	# color map for rendered tables
	cm = sns.light_palette("seagreen", as_cmap=True)

	al_standing_tables = render_standing_tables(['ALE', 'ALC', 'ALW'], standings, cm)
	nl_standing_tables = render_standing_tables(['NLE', 'NLC', 'NLW'], standings, cm)

	return al_standing_tables, nl_standing_tables