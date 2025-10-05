import pandas as pd
from BatteryConfig import BatteryConfig
from BatteryAnalyzer import BatteryAnalyzer

class BatteryAppController:
    """电池应用控制器 - 纯业务逻辑，无Streamlit依赖"""
    
    def __init__(self):
        self.config = BatteryConfig()
        self.analyzer = BatteryAnalyzer(self.config)
        self.current_df = None
        self.calculation_complete = False
    
    def load_data(self, file_content):
        """加载电池数据 - 接收文件内容而非Streamlit对象"""
        if file_content is None:
            return False, "未提供文件内容"
            
        try:
            self.current_df = self.analyzer.load_battery_data(file_content)
            if self.current_df is not None:
                return True, "数据加载成功"
            else:
                return False, "数据加载失败"
        except Exception as e:
            return False, f"数据加载失败: {str(e)}"
    
    def perform_calculation(self):
        """执行计算 - 纯业务逻辑"""
        if self.current_df is None:
            return False, "请先加载数据"
            
        try:
            # 计算阈值点
            self.analyzer.calculate_threshold_points(self.current_df)
            
            # 计算时间
            t1, t2 = self.analyzer.calculate_times()
            
            self.calculation_complete = True
            return True, {
                't1': t1,
                't2': t2
            }
            
        except Exception as e:
            return False, f"计算失败: {str(e)}"
    
    def get_data_preview(self, max_rows=10):
        """获取数据预览信息"""
        if self.current_df is None:
            return None
            
        return {
            'dataframe': self.current_df.head(max_rows),
            'total_rows': len(self.current_df),
            'total_columns': len(self.current_df.columns),
            'columns': list(self.current_df.columns)
        }
    
    def get_config(self):
        """获取配置对象"""
        return self.config
    
    def update_config(self, config_updates):
        """更新配置"""
        for key, value in config_updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def get_current_df(self):
        """获取当前加载的DataFrame"""
        return self.current_df
    
    def get_threshold_results(self):
        """获取阈值结果"""
        return self.analyzer.threshold_results