# mapping of column names used to support old code
old_to_new = {
    'pbWAR': 'bwar_mean',
    'ppWAR': 'pwar_mean',
    'pwOBA': 'woba_mean',
    'pFIP': 'fip_mean',
    'Old Grade': 'old grade',
    'Team': 'TM',
    'Level': 'Lev',
    'max WAR': 'mwar_mean',
    'OG-1': 'og-1',
    'cbWAR': 'bwar',
    'cpWAR': 'pwar',
    'wOBA': 'woba',
    'FIP': 'fip',
    'IP': 'ip',
    'C': 'C_runs',
    '1B': '1B_runs',
    '2B': '2B_runs',
    '3B': '3B_runs',
    'SS': 'SS_runs',
    'LF': 'LF_runs',
    'CF': 'CF_runs',
    'RF': 'RF_runs'
}

# subsets of atts used to display tables
PLAYER_DISP = ['HELPER', 'TM', 'POS', 'Name', 'Lev', 'Age']

FRONT_PAGE_COLS = PLAYER_DISP[1:] + ['old grade', 'og-1', 'POT', 'mwar_mean', 'mwar-1']

POT_COLS = ['CON P', 'GAP P', 'POW P', 'EYE P', 'K P', 'STU P', 'MOV P', 'CTL P']

CLEAN_TABLES_COLS = ['HELPER', 'POS', 'Name', 'Lev', 'Age', 'SLR', 'YL', 'old grade', 'og-1', 'POT',
                    'mwar_mean', 'mwar-1', 'woba', 'woba_mean', 'fip', 'fip_mean'] + POT_COLS

PLAYER_SUBSET = ['Month', 'POS', 'Lev', 'Age', 'old grade', 'POT', 'mwar_mean', 'woba', 'bwar', 'woba_mean',
                 'bwar_mean', 'ip', 'fip', 'pwar', 'fip_mean', 'pwar_mean']

DEF_STAT_COLUMNS = ['C_runs', '1B_runs', '2B_runs', '3B_runs', 'SS_runs', 'LF_runs', 'CF_runs', 'RF_runs']

DEF_RAT_COLUMNS = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']

BAT_RAT_COLUMNS = ['CON', 'GAP', 'POW', 'EYE', 'K', 'CON P', 'GAP P', 'POW P', 'EYE P', 'K P']

PIT_RAT_COLUMNS = ['STU', 'MOV', 'CTL', 'STU P', 'MOV P', 'CTL P']

OTHER_RAT_COLUMNS = ['SPE', 'STE', 'RUN', 'STM']

ALL_STAT_COLS = ['TM', 'Name'] + PLAYER_SUBSET[1:] + DEF_STAT_COLUMNS + ['og-1', 'og-2', 'POT-1', 'POT-2']

# rounding 
THREE_DEC = ['woba', 'woba_mean']

TWO_DEC = ['old grade', 'og-1', 'og-2', 'POT', 'POT-1', 'POT-2', 'fip', 'fip_mean']

ONE_DEC = ['bwar', 'bwar_mean', 'pwar', 'pwar_mean'] + DEF_STAT_COLUMNS

BIO_COLS = ['HELPER', 'POS', 'Name', 'TM', 'Lev', 'Age', 'INJ', 'Type', 
            'CV', 'YL', 'ECV', 'ETY', 'MLY', 'PROY', 'OPTU', 'ON40', 
            'PA', 'BB+', 'SO+', 'ISO+', 'OPS+', 'SB', 'BsR',
            'IP', 'HR9+', 'BB9+', 'K9+', 'GO+', 'ERA+', 'PPG']

POS = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'SP', 'RP', 'OF', 'IF']

SCRATCH_LEVELS = {'C': -5,
                  '1B': -12.5,
                  '2B': 2.5,
                  '3B': 2.5,
                  'SS': 7.5,
                  'LF': -7.5,
                  'CF': 2.5,
                  'RF': -7.5}

TABLE_PROPERTIES = {'border': 'none',
                    'border-bottom': '1px solid #C8C8C8',
                    'text-align': 'left',
                    'padding': '10px',
                    'margin-bottom': '40px'}

DRAFT_YEARS = ['2027', '2026', '2025', '2024', '2023', '2022']

phrases = ['Now "upgraded" to OOTP19!',
           'In the wise words of Homer Simpson: TRAMAMPOLINE! TRAMBOPOLINE!',
           "Helping provide conditions you just can't work in for two years",
           'Bite my shiny metal ass',
           'Because pushing spreadsheets is fun now, I guess',
           'Sex Cauldron?  I thought they closed that place down',
           'Inflammable means flammable? what a country',
           "I'm sorry, I thought he was a party robit",
           'Does anyone else find it creepy Zoidberg is harmonizing with himself?',
           "Hooray I'm useful",
           'Now Zoidberg is the popular one!',
           'Owner Goal: TCR 15 prospects into aces',
           '0 out of 1 dads agree, this is a good use of time',
           'Now the leading OBL programming time sink',
           'Fan interest is for cowards',
           'Needless code rewrites will continue until morale improves',
           'Do nothing and hope it works - Red Sox brand in real life and in game',
           'Probably better than whatever the actual Rockies currently use',
           'Also known as "The Bigger Red Machine" or "Get a life dude"']

months = ['apr28', 'mar28', 'feb28', 'jan28', 'dec27', 'nov27', 'oct27', 'aug27', 'jun27', 'apr27', 'mar27', 'feb27', 'jan27']
currMonth = months[0]
reversed_months = [i for i in reversed(months)]

full_team_name = {
  'CIN': 'Cincinnati Reds', 
  'KC': 'Kansas City Royals', 
  'MIN': 'Minnesota Twins', 
  'PIT': 'Pittsburgh Pirates', 
  'TB': 'Tampa Bay Rays', 
  'CHC': 'Chicago Cubs', 
  'DET': 'Detroit Tigers', 
  'MIA': 'Miami Marlins', 
  'OAK': 'Oakland Athletics', 
  'SEA': 'Seattle Mariners', 
  'WAS': 'Washington Nationals', 
  'BAL': 'Baltimore Orioles', 
  'CLE': 'Cleveland Indians', 
  'ANA': 'Los Angeles Angels', 
  'NYM': 'New York Mets', 
  'SD': 'San Diego Padres', 
  'TEX': 'Texas Rangers', 
  'ARI': 'Arizona Diamondbacks', 
  'CWS': 'Chicago White Sox', 
  'HOU': 'Houston Astros', 
  'MIL': 'Milwaukee Brewers', 
  'PHI': 'Philadelphia Phillies', 
  'STL': 'St. Louis Cardinals', 
  'BOS': 'Boston Red Sox', 
  'COL': 'Colorado Rockies', 
  'LAD': 'Los Angeles Dodgers', 
  'NYY': 'New York Yankees', 
  'SF': 'San Francisco Giants', 
  'TOR': 'Toronto Blue Jays', 
  'ATL': 'Atlanta Braves',
  'LAA': 'The Los Angeles Angeles',
  'FA': 'Free Agents',
}