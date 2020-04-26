import pandas as pd
from typing import Tuple, List

from ootp_helper.constants import DEF_RAT_COLUMNS


def runs_to_ratings(positions):
    ratings = [
        ((((float(positions[0]) + -12.5) * 2 / 0.3) + 162) - 100) * .3 + 50,
        (((float(positions[1]) + 12.5 + 11.069) / .103) - 100) * .3 + 50,
        (((float(positions[2]) + -2.5 + 18.465) / .166) - 100) * .3 + 50,
        (((float(positions[3]) + -2.5 + 28.333) / .230) - 100) * .3 + 50,
        (((float(positions[4]) + -7.5 + 24.2282) / .217) - 100) * .3 + 50,
        (((float(positions[5]) + 7.5 + 18.559) / .167) - 100) * .3 + 50,
        (((float(positions[6]) + -2.5 + 35.312) / .323) - 100) * .3 + 50,
        (((float(positions[7]) + 7.5 + 25.238) / .2015) - 100) * .3 + 50
    ]

    for i in range(0, 8):
        ratings[i] = round(ratings[i], 0)
        ratings[i] = max(min(ratings[i], 80), 20)

    return ratings


def ratings_to_runs(ratings):
    ratings = ratings.apply(lambda x: (((x - 50) / 0.3) + 100))

    zr = [
        ((ratings[0] - 162) * 0.3 / 2) + 12.5,
        (ratings[1] * 0.103) - 11.069 - 12.5,
        (ratings[2] * 0.166) - 18.465 + 2.5,
        (ratings[3] * 0.230) - 28.333 + 2.5,
        (ratings[4] * 0.217) - 24.228 + 7.5,
        (ratings[5] * 0.202) - 25.238 - 7.5,
        (ratings[6] * 0.323) - 35.312 + 2.5,
        (ratings[7] * 0.167) - 18.559 - 7.5
    ]

    return pd.Series(zr, index=DEF_RAT_COLUMNS)


def parse_splits_list(rating_list: List[dict]) -> dict:
    return {
        item['index'].replace(' vR', '').replace(' vL', ''): ((item['current'] - 50) * (10 / 3)) + 100
        for item
        in rating_list
    }


def calculate_batting_runs(rating_list: List[dict]) -> Tuple[float, float]:
    ratings = parse_splits_list(rating_list)

    # non ball-in-play stats
    bb = 600.0 * (0.001042504 * ratings['EYE'] - 0.01787)
    ks = 600.0 * (-0.001647982 * ratings['K'] + 0.358502558)

    # estimated number bip
    bip = 600 - bb - ks

    # dingerzzzz
    dingers = bip * (0.0005162834 * ratings['POW'] - 0.0126321178)

    # hits
    hits = (600 - bb) * (0.1934301352 + 0.0006371253 * ratings['CON'])

    # power distribution of hits
    xbh = 0.0134255742 + 0.0004200824 * ratings['GAP']
    doubles = (7.0 / 8.0) * xbh
    triples = xbh - doubles
    singles = hits - xbh

    # calculate wOBA
    woba = (.69 * bb + .72 * 9 + .89 * singles + 1.27 * doubles + 1.62 * triples + 2.1 * dingers) / 600

    # then the runs off of it
    bat_runs = ((woba - .318) / 1.212) * 600

    return woba, bat_runs


def calculate_pitching_runs(rating_list: List[dict]) -> Tuple[float, float]:
    ratings = parse_splits_list(rating_list)

    # just give everyone 250 bf for now, change if we try to distinguish sp/rp
    bf = 250

    # then churn out some stats
    ks = (ratings['STU'] * 0.00140922 - 0.006688082) * bf
    bbs = ((ratings['CTL'] * (-0.0007415113)) + 0.1563597198) * bf
    hra = (0.0534373594 + (ratings['MOV'] * (-0.0002220408))) * (bf - ks - bbs)
    ha = (0.3678884382 + (ratings['MOV'] * (-0.0005239651))) * (bf - ks - bbs - hra)
    fip = ((13 * hra) + (3 * bbs) - (2 * ks)) / ((bf - bbs - ha - hra) / 3) + 3.2
    war = (((4.19 - fip) / 9.778) + .12) * ((bf - bbs - ha - hra) / 3) / 9

    return fip, war
