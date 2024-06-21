import pandas as pd


df_1 = pd.read_csv('datos_completos_AUDNZD_otc.csv')
df_2 = pd.read_csv('datos_completos_AUDNZD_otc_2.csv')

df_full = pd.concat([df_1, df_2], axis=0)
print(df_full.shape)
df_full.to_csv('datos_full_AUDNZD_otc.csv', index=False)
