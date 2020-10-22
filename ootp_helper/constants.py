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

FRONT_PAGE_COLS = ['_id'] + PLAYER_DISP[1:] + ['POT', 'old grade', 'og-1', 'mwar_mean', 'mwar-1', 'fip_mean', 'woba_mean']

POT_COLS = ['CON P', 'GAP P', 'POW P', 'EYE P', 'K P', 'STU P', 'MOV P', 'CTL P']

CLEAN_TABLES_COLS = [
    'HELPER', 'POS', 'Name', 'Lev', 'Age', 'SLR', 'YL', 'old grade', 'og-1', 'POT', 'mwar_mean', 'mwar-1', 'woba',
    'woba_rhp', 'woba_lhp', 'woba_mean', 'ip', 'fip', 'fip_rhb', 'fip_lhb', 'fip_mean'
]

PLAYER_SUBSET = ['Month', 'POS', 'Lev', 'Age', 'old grade', 'og-1', 'POT', 'mwar_mean', 'mwar-1', 'woba', 'bwar',
                 'woba_mean', 'pwoba-1', 'bwar_mean', 'ip', 'fip', 'pwar', 'fip_mean', 'pfip-1', 'pwar_mean']

DEF_STAT_COLUMNS = ['C_runs', '1B_runs', '2B_runs', '3B_runs', 'SS_runs', 'LF_runs', 'CF_runs', 'RF_runs']

DEF_RAT_COLUMNS = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']

BAT_RAT_COLUMNS = ['CON', 'GAP', 'POW', 'EYE', 'K', 'CON P', 'GAP P', 'POW P', 'EYE P', 'K P']

PIT_RAT_COLUMNS = ['STU', 'MOV', 'CTL', 'STU P', 'MOV P', 'CTL P']

IND_PIT_COLUMNS = ['FB', 'CH', 'CB', 'SL', 'SI', 'SP', 'CT', 'FO', 'CC', 'SC', 'KC', 'KN']
IND_PIT_POT_COLUMNS = [col + 'P' for col in IND_PIT_COLUMNS]

OTHER_RAT_COLUMNS = ['SPE', 'STE', 'RUN', 'STM']

ALL_STAT_COLS = ['TM', 'Name'] + PLAYER_SUBSET[1:] + DEF_STAT_COLUMNS + ['og-2', 'POT-1', 'POT-2']

# rounding 
THREE_DEC = ['woba', 'woba_mean']

TWO_DEC = ['old grade', 'og-1', 'og-2', 'POT', 'POT-1', 'POT-2', 'fip', 'fip_mean']

ONE_DEC = ['bwar', 'bwar_mean', 'pwar', 'pwar_mean'] + DEF_STAT_COLUMNS

BIO_COLS = ['HELPER', 'POS', 'Name', 'TM', 'Lev', 'Age', 'INJ', 'Type', 
            'CV', 'YL', 'SLR', 'ECV', 'ETY', 'MLY', 'PROY', 'OPTU', 'ON40',
            'PA', 'BB+', 'SO+', 'ISO+', 'OPS+', 'SB', 'BsR',
            'IP', 'HR9+', 'BB9+', 'K9+', 'GO+', 'ERA+', 'PPG']

POS = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'SP', 'RP', 'OF', 'IF']

OTHER_SCOUT_COLUMN_ORDER = [
    'HELPER',
    'POS',
    'Name',
    'Lev',
    'Age',
    'old grade',
    'mwar_mean',
    'POT',
]

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

PHRASES = [
    'Now "upgraded" to OOTP20!',
    'In the wise words of Homer Simpson: TRAMAMPOLINE! TRAMBOPOLINE!',
    "Helping provide conditions you just can't work in",
    'Bite my shiny metal ass',
    'Because pushing spreadsheets is fun now, I guess',
    'Sex Cauldron?  I thought they closed that place down',
    'Inflammable means flammable? what a country',
    "I'm sorry, I thought he was a party robit",
    'Does anyone else find it creepy Zoidberg is harmonizing with himself?',
    "Hooray I'm useful",
    'Owner Goal: TCR 15 prospects into aces',
    '0 out of 1 dads agree, this is a good use of time',
    'Now the leading OBL programming time sink',
    'Fan interest is for cowards',
    'Also known as "The Bigger Red Machine" or "Get a life dude"',
    'Now boasting a longer pandemic-free streak than most other MLB universes',
    'Hopefully this doesn\'t trigger an FBI investivagion',
    'This product proven to make you fun at parties',
    'Do you want to know the terrifying truth, or do you want to see the Reds sock a few dingers?'
]

months = ['oct30', 'aug30', 'jun30', 'mar30', 'jan30', 'dec29', 'nov29', 'oct29', 'aug29', 'jun29', 'apr29', 'mar29']
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
  'DRAFT': 'Draft Pool',
}

BUTTON_STRING = '<input type="button" value="Player Page" onclick="window.location.href=\'/player/{}\'" />'
COMPARISON_SEARCH_STRING = '<input type="button" value="Player Page" onclick="window.location.href=\'/compare/{}\'" />'
COMPARISON_PAGE_STRING = '<input type="button" value="Player Page" onclick="window.location.href=\'/compare/{0}/{1}\'" />'

DB_USER = 'read_connection'
DB_PASS = 'password123'
DB_CONNECTION_STRING = f'mongodb://{DB_USER}:{DB_PASS}@ds253368.mlab.com:53368/flask_robit?retryWrites=false'
DB_NAME_STRING = 'flask_robit'
DB_STATSPLUS_TABLE = 'statsplus'
DB_DISTRIBUTIONS_TABLE = 'dist_data'
DB_TRANSACTIONS_TABLE = 'transactions'
DB_TEAM_STATSPLUS_TABLE = 'statsplus_team'

STATSPLUS_PLAYER_FORMAT = 'https://statsplus.net/oblootp/player/{id}?page={page}'

TXN_TYPE_MAP = {
    'contract_renewed': 'Renewal',
    'majors_signing': 'FA Signing',
    'trade': 'Trade',
    'minors_signing': 'MiLB Deal',
    'waiver_claim': 'Waivers',
    'drafted': 'Drafted',
}

INJ_TYPE_MAP = {
    'new_injury': 'New',
    'setback': 'Setback',
}

STATSPLUS_TEAM_ID_MAP = {
    31: 'ARI',
    32: 'ATL',
    33: 'BAL',
    34: 'BOS',
    35: 'CWS',
    36: 'CHC',
    37: 'CIN',
    38: 'CLE',
    39: 'COL',
    40: 'DET',
    41: 'MIA',
    42: 'HOU',
    43: 'KC',
    44: 'LAA',
    45: 'LAD',
    46: 'MIL',
    47: 'MIN',
    48: 'NYY',
    49: 'NYM',
    50: 'OAK',
    51: 'PHI',
    52: 'PIT',
    53: 'SD',
    54: 'SEA',
    55: 'SF',
    56: 'STL',
    57: 'TB',
    58: 'TEX',
    59: 'TOR',
    60: 'WAS',
}
