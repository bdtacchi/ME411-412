#!/usr/bin/env python3

import pickle
import os
import numpy as np

print('hey')
print(os.getcwd())

dbfile = open('Pickles/data_4650_04_12_22_17_02_19.pickle', 'rb')     
db = pickle.load(dbfile)
print(db)
dbfile.close()

filename = 'elec_test_COOLIO.csv'

np.savetxt(filename, db, delimiter=',')