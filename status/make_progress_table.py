#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Alex Drlica-Wagner"
import os, os.path

import numpy as np
import pylab as plt
from collections import OrderedDict as odict
import pandas as pd

import ephem
from obztak.utils import fileio
from obztak.utils.fileio import get_datafile, to_csv, read_csv
from obztak.utils.database import Database

import obztak.delve
import datetime

from status import *

filename = EXPOSURES
if not os.path.exists(filename):
    print("Loading exposures from DB...")
    db = Database('db-fnal')
    db.connect()
    data = db.query2recarray(QUERY)
    print("Writing exposures %s..."%filename)
    fileio.rec2csv(filename,data)

print("Reading exposures %s..."%filename)
data = fileio.csv2rec(filename)
# Select good exposures
good = data[select_good_exposures(data)]
guid = np.char.rpartition(good['object'].astype(str),' ')[:,-1]

print("Loading fields: %s..."%FIELDS)
fields = read_csv(FIELDS)
fields = fields[~select_extra_fields(fields)]

done  = fields[fields['DONE']  > 0]
delve = fields[fields['DONE']  > 1]
todo  = fields[fields['DONE'] == 0]

results=[]
for row in QUALITY.to_records():
    prog = row['program']
    band = row['filter']

    d = data[(data['program'] == prog) & (data['filter'] == band)]
    d_uid = np.char.rpartition(d['object'].astype(str),' ')[:,-1]

    sel = select_good_exposures(d)
    bad = d[~sel]
    good = d[sel]
    g_uid=d_uid[sel]

    f = fields[(fields['PROGRAM']==prog)&(fields['FILTER']==band)]

    # Exposures that are done
    done  = f[f['DONE']  > 0]
    delve = f[f['DONE']  > 1]
    todo  = f[f['DONE'] == 0]

    res = odict()
    res['program'] = prog
    res['band']    = band
    res['nfield']  = len(f)
    res['ndone']   = len(done)
    res['nother']  = len(done) - len(delve)
    res['ndelve']  = len(delve)
    res['ntodo']   = len(todo)
    res['nexp']    = len(d)
    res['nbad']    = len(bad)
    res['ngood']   = len(good)
    res['hours']   = d['exptime'].sum()/3600.
    try:
        res['frac']    = np.float(len(delve))/(len(delve) + len(todo))*100
    except ZeroDivisionError:
        res['frac']    = 100
    results.append(res)

df = pd.DataFrame(results)
pd.set_option('display.width',None)
kwargs = dict(float_format='{:.2f}'.format)
print(df.to_string(**kwargs))
print('---')
kwargs.update(float_format='{:.1f}'.format)
print(df[['program','band','hours','ndelve','ntodo','frac']].to_string(**kwargs))
