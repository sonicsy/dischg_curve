class BatteryConfig:
    """电池系统配置类"""
    def __init__(self):
        self.discharge_cutoff_voltage = 2.95  # 放电截止电压(V)
        self.force_charge_threshold = 2.85    # 强制充电请求阈值(V)
        self.level1_alarm_voltage = 2.7       # 一级报警电压(V)
        self.circuit_breaker_voltage = 2.6    # 微断脱扣电压(V)
        self.ess_power = 125                  # 储能柜功率(kW)
        self.system_response_time = 10.0      # 系统响应时间(s)
        self.standby_power = 100.0            # 待机功耗(W)
        self.battery_series = 260.0           # 电池串数
        self.system_loss = 0.7                # 系统损耗
        self.min_soc = 0                      # 最小SOC(%)
        self.max_soc = 100                    # 最大SOC(%)
    
    def to_dict(self):
        """将配置转换为字典，便于序列化和日志记录"""
        return {
            'discharge_cutoff_voltage': self.discharge_cutoff_voltage,
            'force_charge_threshold': self.force_charge_threshold,
            'level1_alarm_voltage': self.level1_alarm_voltage,
            'circuit_breaker_voltage': self.circuit_breaker_voltage,
            'ess_power': self.ess_power,
            'system_response_time': self.system_response_time,
            'standby_power': self.standby_power,
            'battery_series': self.battery_series,
            'system_loss': self.system_loss,
            'min_soc': self.min_soc,
            'max_soc': self.max_soc
        }
    
    def load_config_file(self, config_file: str):
        """从配置文件加载配置"""
        # 待实现：从JSON或YAML文件加载配置
        pass
    
    def save_config_file(self, config_file: str):
        """保存配置到文件"""
        # 待实现：保存配置到JSON或YAML文件
        pass
    
    def update_from_ess_type(self, ess_type):
        """根据储能柜类型更新配置"""
        ess_configs = {
            "50kW/120kWh": {"power": 50, "series": 120},
            "60kW/120kWh": {"power": 60, "series": 120},
            "125kW/261kWh": {"power": 125, "series": 260}
        }
        if ess_type in ess_configs:
            config = ess_configs[ess_type]
            self.ess_power = config["power"]
            self.battery_series = config["series"]
        else:
            raise ValueError(f"未知储能柜类型: {ess_type}")