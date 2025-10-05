import pandas as pd
import streamlit as st
from BatteryVisualizer import BatteryVisualizer

class BatteryAppUI:
    """电池应用用户界面 - 包含所有Streamlit操作"""
    
    def __init__(self):
        self._setup_page()
    
    def _setup_page(self):
        """设置页面配置"""
        st.set_page_config(
            page_title="电池放电曲线分析",
            layout="wide",
            page_icon="🔋"
        )
        st.title("🔋 电池放电曲线分析系统")
    
    def run_application(self, controller):
        """运行完整的应用程序"""
        # 文件上传
        uploaded_file = self._file_upload()
        
        if uploaded_file is not None:
            # 加载数据
            success, message = controller.load_data(uploaded_file)
            if success:
                st.success(message)
                # self._render_data_preview(controller)
                self._render_parameter_configuration(controller)
                self._render_calculation_section(controller)
            else:
                st.error(message)
    
    def _file_upload(self):
        """渲染文件上传组件"""
        st.header("数据文件上传")
        return st.file_uploader(
            "上传电池放电数据文件", 
            type=['csv'],
            help="请上传包含电压、能量两列数据的CSV文件"
        )
    
    def _render_data_preview(self, controller):
        """渲染数据预览"""
        preview_data = controller.get_data_preview()
        if preview_data:
            with st.expander("数据预览"):
                st.dataframe(preview_data['dataframe'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总数据点数", preview_data['total_rows'])
                with col2:
                    st.metric("数据列数", preview_data['total_columns'])
                with col3:
                    st.metric("数据列名", ", ".join(preview_data['columns']))
    
    def _render_parameter_configuration(self, controller):
        """渲染参数配置界面"""
        st.header("系统参数配置")
        config = controller.get_config()
        
        # 电压阈值配置
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            discharge_cutoff_voltage = st.number_input(
                "放电截止电压（V）", 
                min_value=2.0, 
                max_value=3.65, 
                value=config.discharge_cutoff_voltage,
                help="放电截止电压，即单体欠压二级报警值"
            )
        with col2:
            force_charge_threshold = st.number_input(
                "强制充电请求阈值（V）", 
                min_value=2.0, 
                max_value=3.65, 
                value=config.force_charge_threshold,
                help="单体电压低于该电压值，置强充标志位"
            )
        with col3:
            level1_alarm_voltage = st.number_input(
                "一级报警电压（V）", 
                min_value=2.0, 
                max_value=3.65, 
                value=config.level1_alarm_voltage,
                help="单体欠压一级报警，断开主正主负接触器"
            )
        with col4:
            circuit_breaker_voltage = st.number_input(
                "微断脱扣电压（V）", 
                min_value=2.0, 
                max_value=3.65, 
                value=config.circuit_breaker_voltage,
                help="断开DCDC微断"
            )

        # 系统参数配置
        col1, col2, col3, col4 = st.columns(4)
        with col1:        
            ess_type = st.selectbox(
                "储能柜类型", 
                ["50kW/120kWh", "60kW/120kWh", "125kW/261kWh"],
                help="选择储能柜类型"
            )
            config.update_from_ess_type(ess_type)
        with col2:
            system_response_time = st.number_input(
                "系统响应时间（s）", 
                min_value=0.0, 
                max_value=60.0, 
                value=config.system_response_time,
                help="系统响应时间"
            )
        with col3:
            standby_power = st.number_input(
                "储能柜待机功率（W）", 
                min_value=0.0, 
                max_value=500.0, 
                value=config.standby_power,
                help="停电状态下，待机时储能柜DCDC消耗的功率"
            )
        with col4:
            system_loss = st.number_input(
                "系统损耗", 
                min_value=0.0, 
                max_value=1.0, 
                value=config.system_loss,
                help="ESS系统的效率损耗，如DCDC损耗"
            )
        
        # 更新配置
        config_updates = {
            'discharge_cutoff_voltage': discharge_cutoff_voltage,
            'force_charge_threshold': force_charge_threshold,
            'level1_alarm_voltage': level1_alarm_voltage,
            'circuit_breaker_voltage': circuit_breaker_voltage,
            'system_response_time': system_response_time,
            'standby_power': standby_power,
            'system_loss': system_loss
        }
        controller.update_config(config_updates)
    
    def _render_calculation_section(self, controller):
        """渲染计算部分"""
        if st.button("开始计算", type="primary", use_container_width=True):
            with st.spinner("计算中..."):
                success, result = controller.perform_calculation()
                
                if success:
                    self._render_results(result, controller)
                else:
                    st.error(result)
    
    def _render_results(self, result, controller):
        """渲染计算结果"""
        t1 = result['t1']
        t2 = result['t2']
        threshold_results = controller.get_threshold_results()
        
        st.success(f"""
        **计算结果：**
        
        - 停止放电到强充标志置位时间 T1: **{t1:.0f}秒**
        - 停止放电到断开主回路接触器时间 T2: **{t2:.1f}小时**
        
        *若储能柜辅助电源为储能电池供电（直流取电）*
        """)
        
        # 显示阈值点详情
        with st.expander("查看详细阈值点数据"):
            result_data = []
            for name, threshold_result in threshold_results.items():
                result_data.append({
                    '阈值类型': name,
                    '电压(V)': f"{threshold_result.voltage:.3f}",
                    'SOC(%)': f"{threshold_result.soc:.2f}",
                    '能量(Wh)': f"{threshold_result.energy:.2f}"
                })
            
            st.table(pd.DataFrame(result_data))

        self._render_curve(controller, threshold_results)
    
    # 显示图表
    def _render_curve(self, controller, threshold_results):
        """渲染放电曲线图"""
        df = controller.get_current_df()
        if df is not None and threshold_results:
            batteryVisualizer = BatteryVisualizer()
            fig = batteryVisualizer.create_voltage_soc_plot(df, threshold_results, reversed_x=True)
            st.header("放电曲线图")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("无法生成图表：缺少必要的数据或阈值结果")