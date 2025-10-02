
class ThresholdResult:
    """阈值计算结果数据类"""
    def __init__(self, name, soc, voltage, energy, threshold_value):
        self.name = name
        self.soc = soc
        self.voltage = voltage
        self.energy = energy
        self.threshold_value = threshold_value
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'name': self.name,
            'SOC': self.soc,
            'VTG': self.voltage,
            'Wh': self.energy,            
            'th_val': self.threshold_value
        }