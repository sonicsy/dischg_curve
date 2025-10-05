class ThresholdResult:
    """阈值结果类"""
    
    def __init__(self, soc, voltage, energy, name, threshold_value):
        self.soc = soc
        self.voltage = voltage
        self.energy = energy
        self.name = name
        self.threshold_value = threshold_value
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'soc': self.soc,
            'voltage': self.voltage,
            'energy': self.energy,
            'name': self.name,
            'threshold_value': self.threshold_value
        }