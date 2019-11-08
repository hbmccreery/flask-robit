import pandas as pd

from ootp_helper.constants import DEF_RAT_COLUMNS

def runs_to_ratings(positions):
    ratings = []

    ratings.append(((((float(positions[0]) + -12.5) * 2 / 0.3) + 162) -100 )* .3 + 50)
    ratings.append((((float(positions[1]) + 12.5 + 11.069) / .103)  -100 )* .3 + 50)
    ratings.append((((float(positions[2]) + -2.5 + 18.465) / .166)  -100 )* .3 + 50)
    ratings.append((((float(positions[3]) + -2.5 + 28.333) / .230)  -100 )* .3 + 50)
    ratings.append((((float(positions[4]) + -7.5 + 24.2282) / .217)  -100 )* .3 + 50)
    ratings.append((((float(positions[5]) + 7.5 + 18.559) / .167)  -100 )* .3 + 50)
    ratings.append((((float(positions[6]) + -2.5 + 35.312) / .323)  -100 )* .3 + 50)
    ratings.append((((float(positions[7]) + 7.5 + 25.238) / .2015)  -100 )* .3 + 50)

    for i in range(0,8):
        ratings[i] = round(ratings[i], 0)
        if ratings[i] >= 80:
            ratings[i] = 80
        if ratings[i] <= 20:
            ratings[i] = 20

    return ratings


def ratings_to_runs(ratings):
    ratings = ratings.apply(lambda x: (((x - 50) / 0.3) + 100))

    zr = []

    zr.append(((ratings[0] - 162) * 0.3 / 2) + 12.5)
    zr.append((ratings[1] * 0.103) - 11.069 - 12.5)
    zr.append((ratings[2] * 0.166) - 18.465 + 2.5)
    zr.append((ratings[3] * 0.230) - 28.333 + 2.5)
    zr.append((ratings[4] * 0.217) - 24.228 + 7.5)
    zr.append((ratings[5] * 0.202) - 25.238 - 7.5)
    zr.append((ratings[6] * 0.323) - 35.312 + 2.5)
    zr.append((ratings[7] * 0.167) - 18.559 - 7.5)

    return pd.Series(zr, index = DEF_RAT_COLUMNS)
