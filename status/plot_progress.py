#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Alex Drlica-Wagner"
import os
from collections import OrderedDict as odict

import numpy as np
import pylab as plt
import ephem
from obztak.utils.fileio import get_datafile
from obztak.utils.database import Database
import obztak.delve
from obztak.utils import fileio
import datetime

from status import *

start = ephem.Date('2019/02/01')
end   = ephem.Date('2020/04/01')

DATES = odict([
    ('2019A',[ephem.Date('2019/02/01'),ephem.Date('2019/08/01')]),
    ('2019B',[ephem.Date('2019/08/01'),ephem.Date('2020/02/01')]),
    ('2020A',[ephem.Date('2020/02/01'),ephem.Date('2020/03/18')]),
])

start = DATES.values()[0][0]
end   = DATES.values()[-1][-1]

sched = obztak.delve.DelveScheduler()
windows = [w for w in sched.windows if (w[0] > start) and (w[1] < end)]

print("Reading %s..."%EXPOSURES)
data = fileio.csv2rec(EXPOSURES)

sel = np.array([start < ephem.Date(d) < end for d in data['date']])
data = data[sel]
good = data[select_good_exposures(data)]

# Mean date of the night
#date  = [ephem.Date(np.mean([tmax,tmin])).datetime() for tmin,tmax in windows]
# Amount of time inthe window (hours)
delta = [0] + [24.0 * (tmax - tmin) for tmin,tmax in windows]

date,delta = [],[]
for i,(tmin,tmax) in enumerate(windows):
    date += [ephem.Date(tmin).datetime(),ephem.Date(tmax).datetime()]
    previous = 0 if not delta else delta[-1]
    delta += [previous, previous + 24*(tmax-tmin)]

# Clouds?
nights = np.array([(ephem.Date(tmin),ephem.Date(tmax)) for tmin,tmax in windows])

night_time,obs_time = [],[]
for tmin,tmax in nights:
    night_time.append(tmax - tmin)
    obs_time.append(sum([ (d['exptime']+30)/3600./24. for d in data if tmin < ephem.Date(d['date']) < tmax]))
night_time = np.array(night_time)
obs_time = np.array(obs_time)

frac = obs_time/night_time
print nights[frac < 0.05]

# Observation datetime

obs = [ephem.Date(d).datetime() for d in data['date']]
# Observing time
obstime = (data['exptime']+30.)/3600. # convert to hours
# Shutter open time (hours)
exptime = data['exptime']/3600. # convert to hours
# Effective observation time (hours)
texptime = np.where(data['qc_teff'] > 0, data['qc_teff']*data['exptime']/3600.,0)

for k,(tstart,tstop) in DATES.items():
    sel = np.array([tstart < ephem.Date(d) < tstop for d in data['date']])
    time = exptime[sel].sum()
    print("%s: %.1f"%(k,time))

# Time meeting minimal requirements on data quality
goodtime = np.copy(obstime)
goodtime[~select_good_exposures(data)] = 0
#goodtime[(data['qc_teff'] >= 0) & (data['qc_teff'] < 0.3)] = 0

fig,ax = plt.subplots(figsize=(8,6))
#plt.fill_between(date,0.2*np.cumsum(delta),np.cumsum(delta),lw=2,edgecolor='k', facecolor='k',alpha=0.2, label='Allocated time')
plt.plot(date,delta,lw=2,c='k',label='Allocated time')
plt.plot(obs,np.cumsum(obstime),lw=2,c='r',label='All observing time')
plt.plot(obs,np.cumsum(goodtime),lw=2,c='b',label='Good observing time')
#plt.plot(obs,np.cumsum(texp),lw=2,c='b',label='Effective exposure time')
[t.set_rotation(-45) for t in ax.get_xticklabels()]
plt.legend(loc='upper left')
plt.ylabel('Time (hours)')
plt.subplots_adjust(bottom=0.12)
plt.savefig('obstime.eps',bbox_inches='tight')
