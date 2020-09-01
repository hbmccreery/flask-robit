import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':

    curmo = pd.read_pickle('jun28.pickle')

    for lev in ['A', 'A+', 'AA', 'AAA']:
        at_pos = curmo.loc[(curmo['Lev'] == lev) & (curmo['POS'].isin(['LF', 'CF', 'RF']))]
        starters = at_pos.sort_values('woba', ascending=False).head(100)

        starters.hist('woba')
        plt.show()

