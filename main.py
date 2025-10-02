import warnings
import pandas as pd
import streamlit as st
from BatteryConfig import BatteryConfig
from BatteryAnalyzer import BatteryAnalyzer
from BatteryVisualizer import BatteryVisualizer
from BatteryAppUI import BatteryAppUI

def main():
    """主程序"""
    # 初始化
    warnings.filterwarnings("ignore")
    BatteryAppUI.setup_page()
    
    # 创建配置和 analyzer
    config = BatteryConfig()
    analyzer = BatteryAnalyzer(config)
    
    # 文件上传
    st.header("数据文件上传")
    uploaded_file = st.file_uploader(
        "上传电池放电数据文件", 
        type=['csv'],
        help="请上传包含电压(V)、容量(Ah)、能量(Wh)三列的CSV文件"
    )
    
    if uploaded_file is not None:
        # 加载数据
        df = analyzer.load_battery_data(uploaded_file)
        
        if df is not None:
            # 参数配置界面
            BatteryAppUI.create_parameter_inputs(config)
            
            # 计算按钮
            if BatteryAppUI.create_calculate_button():
                with st.spinner("计算中..."):
                    # 计算阈值点
                    analyzer.calculate_threshold_points(df)
                    
                    # 计算时间
                    t1, t2 = analyzer.calculate_times()
                    
                    # 显示结果
                    BatteryAppUI.display_results(t1, t2, analyzer.threshold_results)
                    
                    # 显示图表
                    st.header("放电曲线图")
                    fig = BatteryVisualizer.create_voltage_soc_plot(
                        df, analyzer.threshold_results, reversed_x=True
                    )
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()