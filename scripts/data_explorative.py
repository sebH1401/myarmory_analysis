#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 22:46:57 2024

@author: seb
"""

import pandas as pd
import seaborn as sns

data_dir = '/home/seb/dev/c#/lotus/myarmory_analysis/data/'

df = pd.read_csv(data_dir + 'data_labeled.csv')
roles = df['role']
roles_simp = []
for role in roles:
    if role in ['aHeal', 'qHeal']:
        roles_simp.append('heal')
    elif role in ['qDPS', 'aDPS']:
        roles_simp.append('boon_dps')
    else:
        roles_simp.append('dps')
df['role_simp'] = roles_simp

#create boonoutput number
df['boon_output'] = (df['might out'] + df['fury out'] + 8+df['quick out'] + 8+df['alac out'])/10

def create_boss_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_result = pd.DataFrame()
    groups = df.groupby(['encounter', 'role_simp'])
    mean_dps = groups['dps'].mean()
    mean_quick = groups['quick out'].mean()
    mean_alac = groups['alac out'].mean()
    mean_boon = groups['boon_output'].mean()
    std_dps = groups['dps'].std()
    std_quick = groups['quick out'].std()
    std_alac = groups['alac out'].std()
    std_boon = groups['boon_output'].std()
    return pd.DataFrame({
            'dps_mean': mean_dps,
            'dps_std': std_dps,
            'quick_out_mean': mean_quick,
            'quick_out_std': std_quick,
            'alac_out_mean': mean_alac,
            'alac_out_std': std_alac,
            'boon_out_mean': mean_boon,
            'boon_out_std': std_boon,
            'n': groups.size()
            })
    
df_boss = create_boss_dataframe(df)

def create_plots(df:pd.DataFrame, value: str):
    groups = df.groupby(['encounter'])
    g = sns.FacetGrid(df, col="encounter", col_wrap=5, hue='role_simp')
    g.map(sns.kdeplot, value)

#dps plots indicate a normal distribution    
create_plots(df, 'dps')
    
def create_standardized_values(df: pd.DataFrame, df_boss: pd.DataFrame):
    dps_std = []
    quick_out_std = []
    alac_out_std = []
    boon_out_std = []
    for index, row in df.iterrows():
        key = (row['encounter'], row['role_simp'])
        descr_stat = df_boss.loc[key]
        dps_std.append((row['dps']-descr_stat['dps_mean'])/descr_stat['dps_std'])
        quick_out_std.append((row['quick out']-descr_stat['quick_out_mean'])/descr_stat['quick_out_std'])
        alac_out_std.append((row['alac out']-descr_stat['alac_out_mean'])/descr_stat['alac_out_std'])
        boon_out_std.append((row['boon_output']-descr_stat['boon_out_mean'])/descr_stat['boon_out_std'])
    df['dps_std'] = dps_std
    df['quick_out_std'] = quick_out_std
    df['alac_out_std'] = alac_out_std
    df['boon_out_std'] = boon_out_std
    return (df)

#standardize distributions
create_standardized_values(df, df_boss)
create_plots(df, 'dps_std')
create_plots(df, 'quick_out_std')
create_plots(df, 'alac_out_std')
create_plots(df, 'boon_out_std')

def create_score_df(df: pd.DataFrame) -> pd.DataFrame:
    weights = {
        'role': ['heal', 'boon_dps', 'dps'],
        'dps_std': [2,14,48],
        'quick_out_std': [24, 18, 1],
        'alac_out_std': [24, 18, 1],
        'boon_out_std': [24, 18, 1]
        }
    df_weights = pd.DataFrame(
        data=weights)
    groups = df.groupby(['player', 'role_simp'])
    df_score = pd.DataFrame({
        'dps_mean': groups['dps_std'].mean(),
        'quick_out_mean': groups['quick_out_std'].mean(),
        'alac_out_mean': groups['alac_out_std'].mean(),
        'boon_out_mean': groups['boon_out_std'].mean(),
        }
    )
    scores = []
    scores_boon = []
    for row in df_score.itertuples():
        weight = df_weights[df_weights['role'] == row.Index[1]]
        result = weight['dps_std']*row.dps_mean + weight['quick_out_std']*row.quick_out_mean + weight['alac_out_std']*row.alac_out_mean
        result_boon = weight['dps_std']*row.dps_mean + weight['boon_out_std']*row.boon_out_mean
        scores.append(result.values[0])
        scores_boon.append(result_boon.values[0])
    df_score['score'] = scores
    df_score['score_boon'] = scores_boon
    return (df_score)

df_score =create_score_df(df)
df_score.to_csv(data_dir + 'data_scoresv2.csv')
sns.kdeplot(data=df_score, x="score_boon")
sns.histplot(data=df_score, x="score_boon")