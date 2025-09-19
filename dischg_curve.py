import streamlit as st
import pandas as pd
import numpy as np
import warnings
import plotly.express as px


df1 = pd.read_excel('SOC-OCV与放电曲线.xlsx', sheet_name='OCV_SOC')
df1.rename(columns={'SOC/%': 'SOC'}, inplace=True)
df2 = pd.read_excel('SOC-OCV与放电曲线.xlsx', sheet_name='0.5C放电曲线')
df3 = pd.read_excel('SOC-OCV与放电曲线.xlsx', sheet_name='0.04C放电曲线')

TOTAL_POINT = 1000
soc_points = np.linspace(0, TOTAL_POINT, TOTAL_POINT + 1, dtype=int)
soc_index = soc_points / TOTAL_POINT * 100


df1_resampled = pd.DataFrame()
df1_resampled['OCV-SOC电压'] = np.interp(soc_index, df1['SOC'], df1['25放电'])

df2_resampled = pd.DataFrame()
df2_resampled['0.5C放电电压'] = df2.iloc[np.linspace(0, len(df2) - 1, TOTAL_POINT + 1, dtype=int)]['电压(V)']
df2_resampled = df2_resampled.iloc[::-1].reset_index(drop=True)

df3_resampled = pd.DataFrame()
df3_resampled['0.04C放电电压'] = df3.iloc[np.linspace(0, len(df3) - 1, TOTAL_POINT + 1, dtype=int)]['实际电压(V)']
df3_resampled = df3_resampled.reset_index(drop=True)

df_merged = pd.concat([df1_resampled, df2_resampled, df3_resampled], axis=1)


fig = px.line(df_merged, title='海辰280Ah放电和OCV_SOC曲线', color_discrete_sequence=['red', 'green', 'blue'], width=1500, height=600)
# fig.update_traces(line=dict(width=2))
# fig.for_each_trace(
#     lambda t: t.update(line_color='red') if t.name == 'OCV_SOC电压' else t.update(line_color='green')
# )

# fig.add_scatter(x=df1_resampled['SOC/%'], y=df1_resampled['25放电'], mode='lines', name='OCV_SOC曲线')
# fig.add_scatter(x=df2_resampled['SOC'], y=df2_resampled['电压(V)'], mode='lines', name='放电SOC曲线')
# fig.data[1].line.color = 'green'
# fig.data[2].line.color = 'red'
# fig.update_xaxes(ticks="outside", ticklen=10, tickcolor='black')
fig.update_layout(xaxis_title='SOC（%）', yaxis_title='电压(V)', xaxis_dtick=10)
fig.show()