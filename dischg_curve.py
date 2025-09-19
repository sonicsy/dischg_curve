import streamlit as st
import pandas as pd
import numpy as np
import warnings
import plotly.express as px


# df1 = pd.read_excel('SOC-OCV与放电曲线.xlsx', sheet_name='OCV_SOC')
# df1.rename(columns={'SOC/%': 'SOC'}, inplace=True)
# df2 = pd.read_excel('SOC-OCV与放电曲线.xlsx', sheet_name='0.5C放电曲线')
# df3 = pd.read_excel('SOC-OCV与放电曲线.xlsx', sheet_name='0.04C放电曲线')

# TOTAL_POINT = 1000
# soc_points = np.linspace(0, TOTAL_POINT, TOTAL_POINT + 1, dtype=int)
# soc_index = soc_points / TOTAL_POINT * 100


# df1_resampled = pd.DataFrame()
# df1_resampled['OCV-SOC电压'] = np.interp(soc_index, df1['SOC'], df1['25放电'])

# df2_resampled = pd.DataFrame()
# df2_resampled['0.5C放电电压'] = df2.iloc[np.linspace(0, len(df2) - 1, TOTAL_POINT + 1, dtype=int)]['电压(V)']
# df2_resampled = df2_resampled.iloc[::-1].reset_index(drop=True)

# df3_resampled = pd.DataFrame()
# df3_resampled['0.04C放电电压'] = df3.iloc[np.linspace(0, len(df3) - 1, TOTAL_POINT + 1, dtype=int)]['实际电压(V)']
# df3_resampled = df3_resampled.reset_index(drop=True)

# df_merged = pd.concat([df1_resampled, df2_resampled, df3_resampled], axis=1)

st.set_page_config(layout="wide")

TOTAL_POINT = 1000
soc_points = np.linspace(0, TOTAL_POINT, TOTAL_POINT + 1, dtype=int)
soc_index = soc_points / TOTAL_POINT * 100

df_merged = pd.read_csv('resampled_data.csv')
df_merged.drop(columns=['Unnamed: 0'], inplace=True)
df_merged['SOC'] = soc_index
df_merged.set_index('SOC', inplace=True)


fig = px.line(df_merged, title='海辰280Ah放电和OCV_SOC曲线', color_discrete_sequence=['red', 'green', 'blue'], width=1500, height=600)
fig.update_layout(xaxis_title='SOC（%）', yaxis_title='电压(V)', xaxis_dtick=5)
st.plotly_chart(fig, use_container_width=True)
