df <- read.csv('/home/seb/dev/c#/lotus/analysis/some_df.csv')

df.scourge <- df[df['profession']=='Scourge',]
df.scourge.heal <- df.scourge[df.scourge['primary_role']=='heal',]
df.scourge.boon <- df.scourge[df.scourge['primary_role']=='boon dps',]
df.scourge.dps <- df.scourge[df.scourge['primary_role']=='dps',]

df.scourge.dps <- df.scourge.dps[df.scourge.dps['dps']>=1500,]
df.scourge.boon <- df.scourge.boon[df.scourge.dps['dps']>=1500,]

df.scourge.players <- setNames(aggregate(dps~ player, df.scourge.dps, mean), c("player", "DPS: meanDPS"))
df.scourge.players <- merge(df.scourge.players, setNames(aggregate(dps~ player, df.scourge.boon, mean), c("player", "Boon: meanDPS")), by='player')
df.scourge.players 