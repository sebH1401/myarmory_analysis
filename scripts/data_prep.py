import pandas as pd
import requests
import numpy as np


#retrieve data
log_urls = '/home/seb/dev/c#/lotus/myarmory_analysis/data/log_list.txt'

with open(log_urls, 'r') as file:
    log_url_list = pd.Series(file.readlines())


pre_url = 'https://dps.report/getJson?permalink='




def process_log(log_url: str) -> pd.DataFrame:
    match_ids_boons = {
        718: 'regen',
        740: 'might',
        1187: 'quick',
        30328: 'alac',
        725: 'fury'
        }
    response = requests.get(pre_url+log_url)
    log_data = response.json()
    dur_str = log_data['duration']
    dur_str = dur_str.replace('m', '')
    dur_str = dur_str.replace('s', '')
    dur_str = dur_str.split()
    time = float(dur_str[0])*60+float(dur_str[1])
    encounter_name = log_data['fightName']
    is_CM = log_data['isCM']
    is_success = log_data['success']
    player_stats = []
    for player in log_data['players']:
        acc_name = player['account']
        dps = player['dpsAll'][0]['dps']
        dmg_taken = player['defenses'][0]['damageTaken']
        downed = player['defenses'][0]['downCount']
        if 'deadDuration' in player['defenses'][0].keys():
            dead_duration = player['defenses'][0]['deadDuration']/100
        else:
            dead_duration = 0
        cleanse = player['support'][0]['condiCleanse']
        profession = player['profession']
        stack_dist = player['statsAll'][0]['stackDist']
        boons = player['buffUptimesActive']
        boons_uptimes = {
            'might': None,
            'fury': None,
            'quick': None,
            'alac': None,
            'regen': None
            }
        
        for boon in boons:
            if boon['id'] in match_ids_boons.keys():
                boons_uptimes[match_ids_boons[boon['id']]] = boon['buffData'][0]['uptime']
                
        boons = player.get('groupBuffsActive')
        boons_generated = {
            'might': None,
            'fury': None,
            'quick': None,
            'alac': None,
            'regen': None
            }
        
        if boons is not None:
            for boon in boons:
                if boon['id'] in match_ids_boons.keys():
                    boons_generated[match_ids_boons[boon['id']]] = boon['buffData'][0]['generation']
        
        if player['statsTargets'][0][0]['connectedPowerCount']==0:
            above90=0;
        else:
            above90 =100*player['statsTargets'][0][0]['connectedPowerAbove90HPCount']/player['statsTargets'][0][0]['connectedPowerCount']

        
        dataset= {
            'encounter': encounter_name,
            'is_cm': is_CM,
            'is_success': is_success,
            'time': time,
            'player': acc_name,
            'profession': profession,
            'dps': dps,
            'might up': boons_uptimes['might'],
            'fury up': boons_uptimes['fury'],
            'quick up': boons_uptimes['quick'],
            'alac up': boons_uptimes['alac'],
            'regen up': boons_uptimes['regen'],
            'might out': boons_generated['might'],
            'fury out': boons_generated['fury'],
            'quick out': boons_generated['quick'],
            'alac out': boons_generated['alac'],
            'regen out': boons_generated['regen'],
            'dmgTaken': dmg_taken,
            'stack_dist': stack_dist,
            'downed': downed,
            'dead_duration': dead_duration,
            'cleanses': cleanse,
            'above90%': above90,
            'log': log_url
            }
        player_stats.append(dataset)
    return pd.DataFrame(player_stats)

def process_log_list(log_url_list: pd.Series)-> list:
    df_log = log_url_list.apply(process_log)
    return df_log

frames = process_log_list(log_url_list)
df = pd.concat(list(frames))

fill_dict=  {
    'might out': 0,
    'fury out': 0,
    'quick out': 0,
    'alac out': 0,
    'regen out': 0
}

df = df.fillna(fill_dict)

def filter_df(df: pd.DataFrame, min_time: int, min_alive: float) -> pd.DataFrame:
    #wipes and co
    df_filter = df[~(df['time']<= min_time) | (df['is_success'])]
    df_filter = df_filter[df_filter['dead_duration']/df_filter['time']<=min_alive]
    df_filter = df_filter[df_filter['above90%'] != 0]
    df_filter = df_filter[df_filter['dps'] != 0]
    #weird players
    df_filter = df_filter[~df_filter['player'].isin(['Conjured Sword', 'Saul D\'Alessio', 'Shackled Prisoner'])]
    
    #sort out hks
    df_filter = df_filter[~((df_filter['encounter'].str.match('Deimos')) & (df_filter['stack_dist'] >=700))]
    return df_filter

df_filter = filter_df(df, 90, 0.60)

df_filter.to_csv('/home/seb/dev/c#/lotus/analysis/data/data_raw.csv')





