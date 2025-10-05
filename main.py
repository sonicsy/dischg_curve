import warnings
from BatteryAppController import BatteryAppController
from BatteryAppUI import BatteryAppUI

def main():
    """主程序 - 仅负责初始化和调用UI"""
    warnings.filterwarnings("ignore")
    
    # 初始化UI和控制器
    app_ui = BatteryAppUI()
    controller = BatteryAppController()
    
    # 运行应用
    app_ui.run_application(controller)

if __name__ == "__main__":
    main()