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


TOTAL_POINT = 1000
st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")

# -*- coding: utf-8 -*-
"""
数据加载模块
"""
import pandas as pd


def load_data() -> pd.DataFrame:
    df_merged = pd.read_csv('resampled_data.csv')
    return df_merged

def get_soc_index():
    soc_points = np.linspace(0, TOTAL_POINT, TOTAL_POINT + 1, dtype=int)
    soc_index = soc_points / TOTAL_POINT * 100
    return soc_index, soc_points



def show_fig(df_merged: pd.DataFrame, reversed: bool = False):
    fig = px.line(df_merged, title='LFP储能电芯放电和OCV_SOC曲线', color_discrete_sequence=['red', 'green', 'blue', 'purple', 'orange'], width=1500, height=600)
    fig.update_layout(xaxis_title='SOC（%）', yaxis_title='电压(V)', xaxis_dtick=5)
    if reversed:
        fig.update_xaxes(autorange="reversed")
    fig.update_yaxes(range=[2.5, 3.65])
    st.plotly_chart(fig, use_container_width=True)
    # return fig

if __name__ == "__main__":
    soc_index, soc_points = get_soc_index()
    df_merged = load_data()
    # df_merged.drop(columns=["Unnamed: 0"], inplace=True)
    df_merged['SOC'] = soc_index
    df_merged.set_index('SOC', inplace=True)
    df_merged = df_merged[['亿纬314Ah0.5P放电电压1', '亿纬314Ah0.5P放电电压2']]
    show_fig(df_merged, reversed=True)