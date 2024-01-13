import pandas as pd
import requests


#start down, this is just for retrieving data
log_urls = '/home/seb/dev/c#/lotus/analysis/log_list.txt'

with open(log_urls, 'r') as file:
    log_url_list = pd.Series(file.readlines())


pre_url = 'https://dps.report/getJson?permalink='

match_ids_boons = {
    718: 'regen',
    740: 'might',
    1187: 'quick',
    30328: 'alac',
    725: 'fury'
    }


def process_log(log_url: str) -> pd.DataFrame:
    response  = requests.get(pre_url+log_url)
    log_data = response.json()
    dur_str =log_data['duration']
    dur_str = dur_str.replace('m', '')
    dur_str = dur_str.replace('s', '')
    dur_str = dur_str.split()
    time = float(dur_str[0])*60+float(dur_str[1])
    encounter_name =log_data['fightName']
    is_CM = log_data['isCM']
    is_success = log_data['success']
    player_stats = []
    for player in log_data['players']:
        acc_name = player['account']
        dps = player['dpsTargets'][0][0]['dps']
        dmg_taken = player['defenses'][0]['damageTaken']
        downed = player['defenses'][0]['downCount']
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
            'cleanses': cleanse,
            'above90%': above90
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
df.to_csv('/home/seb/dev/c#/lotus/analysis/raw_data.csv')
df2 = df
#start here
df_labeled = pd.read_excel('/home/seb/dev/c#/lotus/analysis/data_labeled.xlsx')
df.drop('Unnamed: 0', axis=1, inplace=True)
df['boon_out'] = 50*(df['might out'] + df['fury out'] +8*df['quick out'] + 8*df['alac out'])
#df['is_success'] = df2['is_success'].tolist()
#df['stack_dist'] = df['stack_dist'].tolist()
#df['profession'] = df['profession'].tolist()
df['primary role'] = df_labeled['primary role'].str.lower()
df['secondary_role'] = df_labeled['secondary role'].str.lower()

df.to_csv('/home/seb/dev/c#/lotus/analysis/data_labeled.csv')

#filter 'strange data'
df_filtered = df[(df['time'] >= 90) | (df['is_success']!=False) & (df['time'] <= 90)]
df_filtered = df_filtered[~df_filtered['player'].isin(['Conjured Sword', 'Saul D\'Alessio', 'Shackled Prisoner'])]
df_filtered = df_filtered[df_filtered['above90%'] != 0]
df_filtered = df_filtered[df_filtered['dps'] != 0]
#sort out hks
df_filtered = df_filtered[~((df_filtered['encounter'].str.match('Deimos')) & (df_filtered['stack_dist'] >=700))]

df_filtered.to_csv('/home/seb/dev/c#/lotus/analysis/data_filtered.csv')





