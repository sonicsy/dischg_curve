import numpy as np
import pandas as pd
import streamlit as st
from ThresholdResult import ThresholdResult

class BatteryAnalyzer:
    """电池数据分析器"""
    
    def __init__(self, config):
        self.config = config
        self.total_points = 1000            # 默认值，读取csv文件后会根据行数进行调整
        self.threshold_results = {}
        
    def load_battery_data(self, uploaded_file):
        """加载电池数据"""
        if uploaded_file is None:
            return None
            
        try:
            df = pd.read_csv(uploaded_file)
            required_cols = {'电压(V)', '容量(Ah)', '能量(Wh)'}
            
            if not required_cols.issubset(set(df.columns)):
                raise ValueError("文件格式错误：缺少必要的列")

            df.rename(columns={
                '电压(V)': 'voltage', 
                '能量(Wh)': 'energy', 
                '容量(Ah)': 'capacity'
            }, inplace=True)
            self.total_points = df.shape[0] - 1
            if self.total_points < 1000:
                raise ValueError("数据点不足1000，请上传正确文件")
            
            # 容量或能量，是严格递增递减的，电压有采样误差，所以只能通过容量或能量进行排排序
            df.sort_values(by='energy', ascending=False, inplace=True)
            # 添加SOC列, 并保留小数点后2位
            soc_index = np.linspace(0, 100, self.total_points + 1)
            df['SOC'] = np.round(soc_index, 2)

            return df
            
        except Exception as e:
            st.error(f"数据加载失败: {str(e)}")
            return None
    
    def calculate_threshold_points(self, df):
        """计算各阈值对应的点"""
        thresholds = [
            (self.config.discharge_cutoff_voltage, "停止充放电"),
            (self.config.force_charge_threshold, "置强制充电标志"),
            (self.config.level1_alarm_voltage, "断开直流主回路"),
            (self.config.circuit_breaker_voltage, "微断脱扣阈值")
        ]
        
        self.threshold_results = {}
        for threshold_voltage, description in thresholds:
            result = self._find_threshold_point(df, threshold_voltage, description)
            if result is not None:
                self.threshold_results[description] = result
    
    def _find_threshold_point(self, df, threshold_voltage, description):
        """查找特定阈值对应的数据点"""
        below_threshold = df[df['voltage'] < threshold_voltage]
        if below_threshold.empty:
            return None
        
        # 电压从小到大排序，取比阈值小的最大的一个点（最接近阈值的点）
        point = below_threshold.iloc[-1]
        return ThresholdResult(
            soc=point['SOC'],
            voltage=float(point['voltage']),
            energy=float(point['energy']),
            name=description,
            threshold_value=threshold_voltage
        )
    
    def calculate_times(self):
        """计算T1和T2时间"""
        if not all(key in self.threshold_results for key in ["停止充放电", "置强制充电标志", "断开直流主回路"]):
            return None, None
            
        stop_discharge = self.threshold_results["停止充放电"]
        force_charge = self.threshold_results["置强制充电标志"]
        level1_alarm = self.threshold_results["断开直流主回路"]
        
        # 停止放电到强充标志置位时间 T1 (秒)
        t1 = (self.config.battery_series * (force_charge.energy - stop_discharge.energy) / 
              1000 * 3600 / self.config.ess_power)
        
        # 停止放电到断开主回路接触器时间 T2 (小时)
        energy_diff = (self.config.battery_series * 
                      (level1_alarm.energy - stop_discharge.energy) - 
                      self.config.ess_power * 1000 * self.config.system_response_time / 3600)
        t2 = energy_diff / self.config.standby_power * self.config.system_loss
        
        return t1, t2