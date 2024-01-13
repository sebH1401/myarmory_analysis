#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 00:53:28 2023

@author: seb
"""

import pandas as pd
import numpy as np
import chardet
import json
import requests
import re
import time
import datetime
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn import linear_model
import statsmodels.api as sm

wd = '/home/seb/dev/c#/lotus/analysis/'

df = pd.read_csv(wd + 'data_filtered.csv')
df =  df[df['above90%'] != 0]
df =  df[df['dps'] != 0]
#sort out hks
df = df[~((df['encounter'].str.match('Deimos')) & (df['stack_dist'] >=700))]


#clustering v1
X = df[['dps', 'boon_out']]

inertias= []
for i in range(1,8):
    kmeans = KMeans(n_clusters=i)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)

plt.plot(range(1,8), inertias, marker='o')


kmeans = KMeans(n_clusters=4)
kmeans.fit(X)

plt.scatter(X['dps'], X['boon_out'], c=kmeans.labels_)
plt.show()
kmeans.cluster_centers_


match_roles = {
    0: 'dps',
    1: 'heal',
    2: 'leftover/trash/whatever',
    3: 'boon dps'
    }
pred_role = kmeans.predict(X)

df['role_pred_kmeans'] = pred_role

def assign_role(role_id_list):
    roles = []
    for id in role_id_list:
        roles.append(match_roles[id])
    return roles;

df = df.assign(role_pred_kmeans= lambda x: assign_role(x.role_pred_kmeans))
diff_labels = (df['role_pred_kmeans'] == df['primary_role'])
labels_vs_kmeans = diff_labels.values.sum()/df.shape[0]

#clustering v2
#outdated normalization
df_dps_mean = df.groupby(['encounter'])['dps'].mean()
df_dps_sd = df.groupby(['encounter'])['dps'].std()
df_boon_out_mean = df.groupby(['encounter'])['boon_out'].mean()
df_boon_out_sd = df.groupby(['encounter'])['boon_out'].std()

df_cluster = df[['encounter', 'dps', 'boon_out']]
df_cluster = df_cluster.join(df_dps_mean, 'encounter', rsuffix='_mean')
df_cluster = df_cluster.join(df_dps_sd, 'encounter', rsuffix='_sd')
df_cluster = df_cluster.join(df_boon_out_mean, 'encounter', rsuffix='_mean')
df_cluster = df_cluster.join(df_boon_out_sd, 'encounter', rsuffix='_sd')
df_cluster['dps_standard'] = (df_cluster['dps']-df_cluster['dps_mean'])/df_cluster['dps_sd']
df_cluster['boon_out_standard']  = (df_cluster['boon_out']-df_cluster['boon_out_mean'])/df_cluster['boon_out_sd']


p_dps_ = df_cluster['dps_standard'].plot(kind='kde', title='dps_standard')
p_boonout = df_cluster['boon_out_standard'].plot(kind='kde', title='boonno')


kmeansV2 = KMeans(n_clusters=3)
kmeansV2.fit(df_cluster[['dps_standard', 'boon_out_standard']])
plt.scatter(df_cluster['dps_standard'], df_cluster['boon_out_standard'], c=kmeansV2.labels_)
plt.show()
kmeansV2.cluster_centers_

match_rolesV2 = {
    0: 'dps',
    1: 'boon dps',
    2: 'heal'
    }
pred_roleV2 = kmeansV2.predict(df_cluster[['dps_standard', 'boon_out_standard']])

def assign_roleV2(role_id_list):
    roles = []
    for id in role_id_list:
        roles.append(match_rolesV2[id])
    return roles

df['role_pred_kmeansV2'] = pred_roleV2
df = df.assign(role_pred_kmeansV2= lambda x: assign_roleV2(x.role_pred_kmeansV2))
diff_labelsV2 = (df['role_pred_kmeansV2'] == df['primary_role'])
labels_vs_kmeansV2 = diff_labelsV2.values.sum()/df.shape[0]



from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')
                                
df_logreg= df[['dps', 'encounter','boon_out', 'primary role']]
df_logreg = pd.get_dummies(df_logreg, columns=['encounter', 'primary role'], drop_first=True)
np.random.seed(42)
X_train, X_test, Y_train, Y_test = train_test_split(df_logreg[['dps','boon_out', 'encounter']],df_logreg['primary role'], test_size=0.25)
model_logreg = LogisticRegression()
model_logreg.fit(X_train, Y_train)
model_logreg.score(X_test, Y_test)

df_logreg.to_csv('logreg.csv')
df.to_csv('some_df.csv')