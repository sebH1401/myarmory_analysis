#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 04:02:35 2023

@author: seb
"""

import pandas as pd

df = pd.read_csv('/home/seb/dev/c#/lotus/analysis/data_filtered.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)

df_scourge = df[df['profession']=='Scourge']
df_scourge_dps = df_scourge[df_scourge['primary role']=='dps']
df_scourge_heal = df_scourge[df_scourge['primary role']=='heal']
