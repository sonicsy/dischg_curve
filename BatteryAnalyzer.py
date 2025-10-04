import numpy as np
import pandas as pd
import streamlit as st
from ThresholdResult import ThresholdResult




class BatteryAnalyzer:
    _df_soc_keyword_mapping = {
        "soc": {"SOC", "soc"},
    }

    _df_col_keyword_mapping = {
        "voltage": {"电压", "voltage"},
        "energy": {"能量", "energy"},
        # "capacity": ["容量", "capacity"],
        # "soc": {"SOC", "soc"},
        # "soh": {"SOH", "soh"},
    }
    """电池数据分析器"""
    
    def __init__(self, config):
        self.config = config
        self.total_points = 0               # 读取csv文件后会根据文件的行数进行调整
        self.threshold_results = {}
    
    """
        检查DataFrame列名是否包含指定的关键词
        如果包含，则返回包含关键词的列名
        如果不包含，则抛出 ValueError 异常
    """
    def _check_column_names_(self, df_columns: pd.Index) -> dict:
        results = {}
        for key, keywords in self._df_col_keyword_mapping.items():
            matched_col = [col for col in df_columns if any(keyword in col for keyword in keywords)]
            if len(matched_col) == 0:
                raise ValueError(f"文件格式错误：未找到{key}对应列")
            if len(matched_col) > 1:
                raise ValueError(f"文件格式错误：{key}列名不唯一，匹配到列名：{matched_col}")
            
            # 因为返回的matched_col列表内容只有1个，所以取第一个转为字符串
            results[key] = matched_col[0]

        return results
    
    def _swap_column_names_(self, column_names: dict):
        if column_names is None:
            raise ValueError("column_names 不能为空")
        return dict(zip(list(column_names.values()), list(column_names.keys())))
    
    def _add_soc_column_(self, df: pd.DataFrame) -> None:
        """根据数据行数，添加SOC列, 并保留小数点后2位"""
        matched_col = []
        for key, keywords in self._df_soc_keyword_mapping.items():
            matched_col = [col for col in df.columns if any(keyword in col for keyword in keywords)]
        
        # 如果没找到SOC对应的列，则添加SOC列，如果找到SOC列，则将列名改为soc
        if len(matched_col) == 0:
            soc_index = np.linspace(self.config.min_soc, self.config.max_soc, self.total_points + 1)
            df['soc'] = np.round(soc_index, 2)
        elif len(matched_col) == 1:
            df.rename(columns = {matched_col[0]: "soc"}, inplace=True)

    def load_battery_data(self, uploaded_file):
        """加载电池数据"""
        if uploaded_file is None:
            return None
            
        try:
            df = pd.read_csv(uploaded_file)
            
            if df.isna().any().any():
                raise ValueError("数据包含缺失值，请检查文件")
            
            self.total_points = df.shape[0] - 1
            if self.total_points < 100:
                raise ValueError("数据点不足100，请上传正确文件")
            
            column_names = self._check_column_names_(df.columns)

            df.rename(columns=self._swap_column_names_(column_names), inplace=True)

            # 放电过程中，能量或能量，是严格递减的，电压有采样误差，所以只能通过容量或能量进行排排序
            df.sort_values(by='energy', ascending=False, inplace=True)
            """
            根据数据行数，添加SOC列, 并保留小数点后2位
            SOC范围：0-100%
            """
            self._add_soc_column_(df)

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
            soc=point['soc'],
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