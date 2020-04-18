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
import skymap
import skymap.survey

from status import *

filename = EXPOSURES
if not os.path.exists(filename):
    db = Database('db-fnal')
    db.connect()
    data = db.query2recarray(QUERY)
    print("Writing %s..."%filename)
    fileio.rec2csv(filename,data)
else:
    print("Reading %s..."%filename)
    data = fileio.csv2rec(filename)

good = data[select_good_exposures(data)]
guid = np.char.rpartition(good['object'].astype(str),' ')[:,-1]
# Unique fields
guid,idx = np.unique(guid,return_index=True)
good = good[idx]

fields = obztak.delve.DelveFieldArray().load(get_datafile(TARGETS))
fuid = fields.unique_id
fields = pd.DataFrame(fields)

fields['DONE'] = 0
# Done fields
fields.loc[select_done_fields(fields),'DONE'] |= 1
# Observed by DELVE
fields.loc[np.in1d(fuid,guid),'DONE'] |= 2

uid=pd.DataFrame({'uid':fuid}).merge(pd.DataFrame({'uid':guid,'DATE':good['date']}),how='left')
fields['DATE'] = uid['DATE']

if np.any(fields['DONE'][~fields['DATE'].isnull()] < 0):
    raise Exception("DATE/DONE mismatch")

date = datetime.datetime.now().strftime('%Y%m%d')
filename = FIELDS
print("Writing %s..."%filename)
to_csv(filename,fields)
