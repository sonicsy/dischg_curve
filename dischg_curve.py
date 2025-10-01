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


TOTAL_POINT = 3000
st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")

# 二级报警阈值（V）
TH_LEVEL2 = 2.95
# 强制充电请求阈值（V）
TH_FORCE_CHG = 2.85
# 一级报警阈值，断开接触器（V）
TH_LEVEL1 = 2.7
# 微断脱扣阈值（V）
TH_OFF_QF = 2.6
# 储能柜功率(kW)
ESS_POWER = 125
# 系统响应时间（s）
SYS_RESP_T = 10
# 待机功耗（W）
STANDBY_P = 100
# 电池串数
BATT_SERIES = 260
# 系统损耗
SYS_LOSS = 0.7

T1 = 0
T2 = 0

se_th_level2 = pd.DataFrame()
se_th_force_chg = pd.DataFrame()
se_th_level1 = pd.DataFrame()
se_th_off_qf = pd.DataFrame()


# -*- coding: utf-8 -*-
"""
数据加载模块
"""
import pandas as pd


def load_data() -> pd.DataFrame:
    df = pd.read_csv('亿纬314Ah0.5P放电曲线1_full.csv')
    df.rename(columns={'实际电压(V)': 'VTG', '能量(Wh)': 'Wh', '容量(Ah)': 'Ah',}, inplace=True)
    df.sort_values(by='VTG', inplace=True)
    return df

def get_soc_index():
    soc_points = np.linspace(0, TOTAL_POINT, TOTAL_POINT + 1, dtype=int)
    soc_index = soc_points / TOTAL_POINT * 100
    return soc_index, soc_points

def add_threshold(anno_lst, df_th):
    anno_lst.append({'x': df_th['SOC'], 'y': df_th['VTG'], 'text': f"{df_th['SOC']:.1f}%SOC {df_th['name']}"})
    
def add_annotation(fig, anno_lst: list):
    for anno in anno_lst:
        fig.add_annotation(
            x=anno['x'],
            y=anno['y'],
            text=anno['text'],
            showarrow=True,
            arrowcolor="red",
            arrowhead=1,
            ax=-60,
            ay=30,
            font=dict(size=14)
        )

def add_scatter(fig, anno_lst: list):
    for anno in anno_lst:
        fig.add_scatter(
            x=[anno['x']],
            y=[anno['y']],
            mode='markers',
            marker=dict(size=6, color='blue'),
            name=anno['text']
        )

def show_fig(df: pd.DataFrame, reversed: bool = False):
    fig = px.line(df, x='SOC', y=['VTG'], title='EVE314Ah0.5P放电曲线', width=1500, height=600)
    if reversed:
        fig.update_xaxes(autorange="reversed")
    fig.update_yaxes(range=[2.5, 3.6])
    # fig.data[1].update(visible=False)  # 默认隐藏第一条线
    fig.update_layout(xaxis_title='SOC（%）', yaxis_title='电压(V)', xaxis_dtick=5, showlegend=False)

    anno_lst = []

    if se_th_level2.empty is False:
        # anno_lst.append({'x': se_th_level2.name, 'y': float(se_th_level2['VTG'].iloc[0]), 'text': f"二级报警阈值 {TH_LEVEL2}V\nSOC={se_th_level2.name:.1f}%\nWh={se_th_level2['Wh']:.1f}Wh"})
        # st.text(f"{se_th_level2}")
        # st.text(f"{se_th_level2.index} aaa {se_th_level2}")
        add_threshold(anno_lst, se_th_level2)
        add_threshold(anno_lst, se_th_force_chg)
        add_threshold(anno_lst, se_th_level1)

        add_annotation(fig, anno_lst)

        add_scatter(fig, anno_lst)
    st.plotly_chart(fig, use_container_width=True)
    # return fig

def calc_th_params(df: pd.DataFrame):
    
    global se_th_level2, se_th_force_chg, se_th_level1, se_th_off_qf

    se_th_level2 = df[df['VTG'] < TH_LEVEL2].iloc[-1]
    se_th_level2['name'] = '停止充放电'
    se_th_level2['th_val'] = TH_LEVEL2

    se_th_force_chg = df[df['VTG'] < TH_FORCE_CHG].iloc[-1]
    se_th_force_chg['name'] = '置强制充电标志'
    se_th_force_chg['th_val'] = TH_FORCE_CHG

    se_th_level1 = df[df['VTG'] < TH_LEVEL1].iloc[-1]
    se_th_level1['name'] = '断开直流主回路'
    se_th_level1['th_val'] = TH_LEVEL1

    se_th_off_qf = df[df['VTG'] < TH_OFF_QF].iloc[-1]
    se_th_off_qf['name'] = '微断脱扣阈值'
    se_th_off_qf['th_val'] = TH_OFF_QF

def calc_th_time():
    # 停止放电到强充标志置位时间（S）T1
    global T1, T2
    T1 = BATT_SERIES*(se_th_force_chg['Wh'] - se_th_level2['Wh']) / 1000 * 3600 / ESS_POWER

    T2 = (BATT_SERIES*(se_th_level1['Wh'] - se_th_level2['Wh']) - ESS_POWER * 1000 * SYS_RESP_T/3600) / STANDBY_P * SYS_LOSS

def show_table(df: pd.DataFrame):
    global TH_LEVEL2, TH_FORCE_CHG, TH_LEVEL1, TH_OFF_QF, SYS_RESP_T, STANDBY_P, ESS_POWER, BATT_SERIES, SYS_LOSS
    st.divider()
    # 创建4列
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        TH_LEVEL2 = float(st.text_input("放电截止电压（V）", placeholder="请输入放电截止电压", value="2.95", help="放电截止电压，即单体欠压二级报警值，默认2.9V"))
        
    with col2:
        TH_FORCE_CHG = float(st.text_input("强制充电请求阈值（V）", placeholder="请输入强制充电请求阈值", value="2.85", help="单体电压低于该电压值，置强充标志位，默认2.85V"))
        
    with col3:
        TH_LEVEL1 = float(st.text_input("一级报警电压（V）", placeholder="请输入一级报警电压", value="2.7", help="单体欠压一级报警，断开主正主负接触器，默认2.7V"))

    with col4:
        TH_OFF_QF = float(st.text_input("微断脱扣电压（V）", placeholder="请输入微断脱扣电压", value="2.6", help="断开DCDC微断，默认2.6V")) 

    col1, col2, col3, col4 = st.columns(4)

    with col1:        
        ESS_TYPE = st.selectbox("储能柜类型", ["50kW/120kWh", "60kW/120kWh", "125kW/261kWh"],placeholder="请选择储能柜类型", help="选择储能柜类型")
    with col2:
        SYS_RESP_T = float(st.text_input("系统响应时间（s）", placeholder="请输入系统响应时间", value="10", help="系统响应时间"))
    with col3:
        STANDBY_P = float(st.text_input("储能柜待机功率（W）", placeholder="请输入储能柜待机功率", value="100", help="储能柜待机功率"))
    with col4:
        SYS_LOSS = float(st.text_input("系统损耗（%）", placeholder="请输入系统损耗", value="0.7", help="ESS系统的效率损耗，如考虑DCDC效率（约为90%）电池的衰减（EOL为70%）等") )

    # 定义红色按钮样式
    # 定义红色按钮的 CSS 样式
    red_button_style = """
    <style>
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    div.stButton > button:first-child:hover {
        background-color: #ff3333;
        color: white;
        border: none;
    }

    div.stButton > button:first-child:focus {
        background-color: #ff1a1a;
        color: white;
        border: none;
        box-shadow: none;
    }
    </style>
    """

    # 应用样式
    st.markdown(red_button_style, unsafe_allow_html=True)
    
#  help="点击计算", args=None, kwargs=None, on_click=None, type="primary", use_container_width=False, disabled=False, 
    if st.button("计算", width=200, key="calculate_button"):
        ESS_POWER = 50 if ESS_TYPE == "50kW/120kWh" else 60 if ESS_TYPE == "60kW/120kWh" else 125
        BATT_SERIES = 120 if ESS_TYPE == "50kW/120kWh" else 120 if ESS_TYPE == "60kW/120kWh" else 260
        calc_th_params(df)
        calc_th_time()
#         T1 = BATT_SERIES*(se_th_force_chg['能量(Wh)'] - se_th_level2['能量(Wh)']) / 1000 * 3600 / ESS_POWER

# T2 = (BATT_SERIES*(se_th_level1['能量(Wh)'] - se_th_level2['能量(Wh)']) - ESS_POWER * 1000 * SYS_RESP_T/3600) / STANDBY_P * SYS_LOSS
        result = f"停止放电到强充标志置位时间 T1: {T1:.0f}秒\n\n停止放电到断开主回路接触器时间 T2: {T2:.1f}小时"
        st.success(result)



if __name__ == "__main__":
    soc_index, soc_points = get_soc_index()
    df = load_data()
    # df_merged.drop(columns=["Unnamed: 0"], inplace=True)
    df['SOC'] = soc_index
    # df.set_index('SOC', inplace=True)
    # df_merged = df_merged[['亿纬314Ah0.5P放电电压1', '亿纬314Ah0.5P放电电压2']]
    show_table(df)
    show_fig(df, reversed=True)
   
    