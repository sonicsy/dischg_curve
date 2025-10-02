import pandas as pd
import streamlit as st

class BatteryAppUI:
    # """电池应用用户界面"""
    
    @staticmethod
    def setup_page():
        """设置页面配置"""
        st.set_page_config(
            page_title="电池放电曲线分析",
            layout="wide",
            page_icon="🔋"
        )
        st.title("🔋 电池放电曲线分析系统")
        
    @staticmethod
    def create_parameter_inputs(config):
        """创建参数输入界面"""
        st.header("系统参数配置")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            config.discharge_cutoff_voltage = st.number_input(
                "放电截止电压（V）", 
                min_value=2.0, 
                max_value=3.5, 
                value=2.95,
                help="放电截止电压，即单体欠压二级报警值"
            )
            
        with col2:
            config.force_charge_threshold = st.number_input(
                "强制充电请求阈值（V）", 
                min_value=2.0, 
                max_value=3.5, 
                value=2.85,
                help="单体电压低于该电压值，置强充标志位"
            )
            
        with col3:
            config.level1_alarm_voltage = st.number_input(
                "一级报警电压（V）", 
                min_value=2.0, 
                max_value=3.5, 
                value=2.7,
                help="单体欠压一级报警，断开主正主负接触器"
            )

        with col4:
            config.circuit_breaker_voltage = st.number_input(
                "微断脱扣电压（V）", 
                min_value=2.0, 
                max_value=3.5, 
                value=2.6,
                help="断开DCDC微断"
            ) 

        col1, col2, col3, col4 = st.columns(4)

        with col1:        
            ess_type = st.selectbox(
                "储能柜类型", 
                ["50kW/120kWh", "60kW/120kWh", "125kW/261kWh"],
                help="选择储能柜类型"
            )
            config.update_from_ess_type(ess_type)
            
        with col2:
            config.system_response_time = st.number_input(
                "系统响应时间（s）", 
                min_value=0.0, 
                max_value=60.0, 
                value=10.0,
                help="系统响应时间"
            )
            
        with col3:
            config.standby_power = st.number_input(
                "储能柜待机功率（W）", 
                min_value=0.0, 
                max_value=500.0, 
                value=100.0,
                help="储能柜待机功率"
            )
            
        with col4:
            config.system_loss = st.number_input(
                "系统损耗", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.7,
                help="ESS系统的效率损耗"
            )

    @staticmethod
    def create_calculate_button():
        """创建计算按钮"""
        return st.button("开始计算", type="primary", use_container_width=True)

    @staticmethod
    def display_results(t1, t2, threshold_results):
        """显示计算结果"""
        if t1 is not None and t2 is not None:
            st.success(f"""
            **计算结果：**
            
            - 停止放电到强充标志置位时间 T1: **{t1:.0f}秒**
            - 停止放电到断开主回路接触器时间 T2: **{t2:.1f}小时**
            
            *若储能柜辅助电源为储能电池供电（直流取电）*
            """)
            
            # 显示阈值点详情
            with st.expander("查看详细阈值点数据"):
                result_data = []
                for name, result in threshold_results.items():
                    result_data.append({
                        '阈值类型': name,
                        '电压(V)': f"{result.voltage:.3f}",
                        'SOC(%)': f"{result.soc:.2f}",
                        '能量(Wh)': f"{result.energy:.2f}"
                    })
                
                st.table(pd.DataFrame(result_data))