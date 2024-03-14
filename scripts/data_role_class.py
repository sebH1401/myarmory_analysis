#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 23:13:49 2024

@author: seb
"""

import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

data_dir = '/home/seb/dev/c#/lotus/myarmory_analysis/data/'

df = pd.read_csv(data_dir + 'data_labeled.csv')

roles = df['role']
roles_simp_main = []
roles_simp_boon = []
for role in roles:
    if role in ['aHeal', 'qHeal']:
        roles_simp_main.append('heal')
    else:
        roles_simp_main.append('dps')
    if role in ['aDPS', 'aHeal']:
        roles_simp_boon.append('alac')
    elif role in ['qDPS', 'qHeal']:
        roles_simp_boon.append('quick')   
    else:
        roles_simp_boon.append('None')
df['role_simp_main'] = roles_simp_main
df['role_simp_boon'] = roles_simp_boon

def create_boss_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_result = pd.DataFrame()
    groups = df.groupby(['encounter'])
    mean_dps = groups['dps'].mean()
    mean_quick = groups['quick out'].mean()
    mean_alac = groups['alac out'].mean()
    mean_regen = groups['regen out'].mean()
    mean_might = groups['might out'].mean()
    mean_fury = groups['fury out'].mean()
    std_dps = groups['dps'].std()
    std_quick = groups['quick out'].std()
    std_alac = groups['alac out'].std()
    std_regen = groups['regen out'].std()
    std_might = groups['might out'].std()
    std_fury = groups['fury out'].std()
    return pd.DataFrame({
            'dps_mean': mean_dps,
            'dps_std': std_dps,
            'quick_out_mean': mean_quick,
            'quick_out_std': std_quick,
            'alac_out_mean': mean_alac,
            'alac_out_std': std_alac,
            'regen_out_mean': mean_regen,
            'regen_out_std': std_regen,
            'might_out_mean': mean_might,
            'might_out_std': std_might,
            'fury_out_mean': mean_fury,
            'fury_out_std': std_fury,
            'n': groups.size()
            })
    
df_boss = create_boss_dataframe(df)

def create_standardized_values(df: pd.DataFrame, df_boss: pd.DataFrame):
    dps_std = []
    quick_out_std = []
    alac_out_std = []
    regen_out_std = []
    might_out_std = []
    fury_out_std = []
    for index, row in df.iterrows():
        descr_stat = df_boss.loc[row['encounter']]
        dps_std.append((row['dps']-descr_stat['dps_mean'])/descr_stat['dps_std'])
        quick_out_std.append((row['quick out']-descr_stat['quick_out_mean'])/descr_stat['quick_out_std'])
        alac_out_std.append((row['alac out']-descr_stat['alac_out_mean'])/descr_stat['alac_out_std'])
        regen_out_std.append((row['regen out']-descr_stat['regen_out_mean'])/descr_stat['regen_out_std'])
        might_out_std.append((row['might out']-descr_stat['might_out_mean'])/descr_stat['might_out_std'])
        fury_out_std.append((row['fury out']-descr_stat['fury_out_mean'])/descr_stat['fury_out_std'])
    df['dps_std'] = dps_std
    df['quick_out_std'] = quick_out_std
    df['alac_out_std'] = alac_out_std
    df['regen_out_std'] = regen_out_std
    df['might_out_std'] = might_out_std
    df['fury_out_std'] = fury_out_std
    return (df)

#standardize distributions
create_standardized_values(df, df_boss)
df_reg_total = df[['player', 'role_simp_main', 'role_simp_boon', 'dps_std', 
             'quick_out_std', 'alac_out_std', 'regen_out_std', 'might_out_std',
             'fury_out_std']]
df_reg_total.fillna(0, inplace=True)

#70-30-split
train, test = train_test_split(df_reg_total, test_size=0.3)
df_reg_x = train[['dps_std', 'quick_out_std', 'alac_out_std', 'regen_out_std', 'might_out_std','fury_out_std']]
df_reg_y_boon = train['role_simp_boon']
df_reg_y_dps = train['role_simp_main']
df_reg_x_test = test[['dps_std', 'quick_out_std', 'alac_out_std', 'regen_out_std', 'might_out_std','fury_out_std']]
df_reg_y_dps_test = test['role_simp_main']
df_reg_y_boon_test = test['role_simp_boon']

#train logistic regression model for role classification: dps or heal?
model_dps = LogisticRegression(random_state=0).fit(df_reg_x, df_reg_y_dps)
score_dps_train = model_dps.score(df_reg_x, df_reg_y_dps)
score_dps_test = model_dps.score(df_reg_x_test, df_reg_y_dps_test)

#train logistic regression model for role classification: boon provider? quick or alac?
model_boon = LogisticRegression(random_state=0).fit(df_reg_x, df_reg_y_boon)
score_boon_train = model_boon.score(df_reg_x, df_reg_y_boon)
score_boon_test = model_boon.score(df_reg_x_test, df_reg_y_boon_test)

confusion_matrix(df_reg_total['role_simp_main'], 
                 model_dps.predict(df_reg_total[['dps_std', 'quick_out_std', 
                                                 'alac_out_std', 'regen_out_std', 
                                                 'might_out_std','fury_out_std']]))

confusion_matrix(df_reg_total['role_simp_boon'], 
                 model_boon.predict(df_reg_total[['dps_std', 'quick_out_std', 
                                                 'alac_out_std', 'regen_out_std', 
                                                 'might_out_std','fury_out_std']]))