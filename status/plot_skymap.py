#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Alex Drlica-Wagner"
import os, os.path
import numpy as np
import matplotlib
#matplotlib.use('ps')
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
from skymap.constants import DECAM
from status import *

fields = read_csv(FIELDS)

done  = fields[fields['DONE']  > 0]
delve = fields[fields['DONE']  > 1]
todo  = fields[fields['DONE'] == 0]

datasets = [('DELVE Complete',delve),('All Complete',done),('DELVE ToDo',todo)]

for title, d in datasets:
    continue
    for b in BANDS:
        plt.figure()
        plt.title(title + ' (%s-band)'%b)

        f = d[d['FILTER'] == b]

        tilings = [1,2,3]
        if 'Complete' not in title: tilings = tilings[::-1]

        smap = skymap.survey.MaglitesSkymap(); suffix='_ortho'
        #smap = skymap.survey.SurveyMcBryde(); suffix='_mbtpq'

        for i in tilings:
            t = f[f['TILING'] == i].to_records(index=False)
            color = COLORS[b][i]
            smap.draw_fields(t, c=color,label='Tiling %i'%i)

        #kwargs = dict(facecolor='none',edgecolor='k',lw=1,zorder=10)
        #smap.tissot(0,-90,DECAM,100,**kwargs)

        smap.draw_milky_way()
        smap.draw_des(color='k',lw=2)
        plt.legend(numpoints=1,scatterpoints=1)
        filename = title.lower().replace(' ','_')+suffix+'_%s.eps'%b
        plt.savefig(filename,bbox_inches='tight',rasterized=True)
        plt.savefig(filename.replace('.eps','.png'),bbox_inches='tight')


for title, d in datasets[:1]:
    title = 'MC '+title
    for b in BANDS:
        plt.figure()
        plt.title(title + ' (%s-band)'%b,y=1.05)

        f = d[(d['FILTER'] == b) & (d['PROGRAM'] == 'delve-mc')]

        tilings = [1,2,3]
        if 'Complete' not in title: tilings = tilings[::-1]

        smap = skymap.survey.MaglitesSkymap(); suffix='_ortho'
        #smap = skymap.survey.SurveyMcBryde(); suffix='_mbtpq'

        for i in tilings:
            t = f[f['TILING'] == i].to_records(index=False)
            color = COLORS[b][i]
            smap.draw_fields(t, c=color,label='Tiling %i'%i)

        #kwargs = dict(facecolor='none',edgecolor='k',lw=1,zorder=10)
        #smap.tissot(0,-90,DECAM,100,**kwargs)

        smap.draw_milky_way()
        smap.draw_des(color='k',lw=2)
        plt.legend(numpoints=1,scatterpoints=1)
        filename = title.lower().replace(' ','_')+suffix+'_%s.pdf'%b
        print('Writing %s...'%filename)
        plt.savefig(filename,bbox_inches='tight',rasterized=True)
        plt.savefig(filename.replace('.pdf','.png'),bbox_inches='tight')

