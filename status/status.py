#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Alex Drlica-Wagner"
import pandas as pd
import numpy as np

PROGRAMS = ['delve-wide','delve-mc','delve-deep']
BANDS = ['g','r','i']
COLORS = {
    'g': {1:'lightgreen', 2:'limegreen', 3:'darkgreen'},
    'r': {1:'coral',      2:'red',       3:'maroon'},
    'i': {1:'gold',       2:'goldenrod', 3:'chocolate'},
}

TARGETS = "delve-target-fields-v14.csv.gz"
FIELDS  = "../data/delve-fields-20200414.csv.gz"
EXPOSURES = '../data/delve-exposures-20200414.csv.gz'

QUERY = """
SELECT object, seqid, seqnum, telra as RA, teldec as dec,
expTime, filter,
to_char(date, 'YYYY/MM/DD HH24:MI:SS.MS') AS DATE,
COALESCE(airmass,-1) as AIRMASS, COALESCE(moonangl,-1) as MOONANGLE,
COALESCE(ha, -1) as HOURANGLE, COALESCE(slewangl,-1) as SLEW, PROGRAM,
COALESCE(qc_teff,-1) as QC_TEFF,
COALESCE(qc_fwhm,-1) as QC_FWHM
FROM exposure where propid = '2019A-0305' and exptime > 89
and discard = False and delivered = True and flavor = 'object'
and object like 'DELVE field: %'
and date between '2019-02-01' and '2020-04-01'
ORDER BY date
"""

COLUMNS=['program','filter','teff_min','fwhm_max','done','extra']
QUALITY = [
    ['delve-wide','g', 0.3, 1.5, -1 , 4],
    ['delve-wide','i', 0.3, 1.5, -1 , 4],
    ['delve-mc',  'g', 0.2, 2.0, -1 , 4],
    ['delve-mc',  'r', 0.2, 2.0, -1 , 4],
    ['delve-mc',  'i', 0.2, 2.0, -1 , 4],
    ['delve-deep','g', 0.0, 1.2, -99, np.nan],
    ['delve-deep','r', 0.0, 1.2, -99, np.nan],
    ['delve-deep','i', 0.0, 1.2, -99, np.nan],
]
QUALITY = pd.DataFrame(QUALITY, columns=COLUMNS)

def select_good_exposures(data):
    tmp = pd.DataFrame(data)
    tmp = tmp.merge(QUALITY,how='left',on=['program','filter'])
    bad  = ((tmp['qc_teff'] >= 0) & (tmp['qc_teff'] < tmp['teff_min']))
    bad |= (tmp['qc_fwhm'] > tmp['fwhm_max'])
    return ~bad

def select_done_fields(fields):
    tmp = pd.DataFrame(fields)
    tmp = tmp.merge(QUALITY,how='left',left_on=['PROGRAM','FILTER'],right_on=['program','filter'])
    done = tmp['PRIORITY'] == tmp['done']
    return done

def select_extra_fields(fields):
    #tmp = pd.DataFrame(np.copy(fields))
    tmp = fields.merge(QUALITY,how='left',left_on=['PROGRAM','FILTER'],right_on=['program','filter'])
    extra = tmp['PRIORITY'] == tmp['extra']
    return extra
