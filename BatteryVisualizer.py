import plotly.express as px

class BatteryVisualizer:
    """电池数据可视化类 - 使用实例方法，支持配置和状态管理"""
    
    def __init__(self, default_reversed_x=True, default_y_range=(2.5, 3.6)):
        """初始化可视化器"""
        self.default_reversed_x = default_reversed_x
        self.default_y_range = default_y_range
        self._chart_count = 0  # 用于跟踪生成的图表数量
    
    def create_voltage_soc_plot(self, df, threshold_results, reversed_x=None):
        """创建电压-SOC曲线图"""
        # 使用实例配置或参数覆盖
        use_reversed_x = reversed_x if reversed_x is not None else self.default_reversed_x
        
        fig = px.line(df, x='soc', y=['voltage'])
        
        if use_reversed_x:
            fig.update_xaxes(autorange="reversed")
            
        fig.update_yaxes(range=self.default_y_range)
        fig.update_layout(
            xaxis_title='SOC（%）', 
            yaxis_title='电压(V)', 
            xaxis_dtick=5, 
            showlegend=False
        )
        
        # 添加阈值标注
        self._add_threshold_annotations(fig, threshold_results)
        
        self._chart_count += 1
        return fig
    
    def _add_threshold_annotations(self, fig, threshold_results):
        """添加阈值标注到图表"""
        annotations = []
        scatter_points = []
        
        for result in threshold_results.values():
            annotations.append({
                'x': result.soc,
                'y': result.voltage,
                'text': f"{result.soc:.1f}%SOC {result.name}"
            })
            
            scatter_points.append({
                'x': [result.soc],
                'y': [result.voltage],
                'name': result.name
            })
        
        # 添加标注
        for anno in annotations:
            fig.add_annotation(
                x=anno['x'],
                y=anno['y'],
                text=anno['text'],
                showarrow=True,
                arrowcolor="red",
                arrowhead=1,
                ax=-60,
                ay=30,
                font=dict(size=14)
            )
        
        # 添加散点
        for point in scatter_points:
            fig.add_scatter(
                x=point['x'],
                y=point['y'],
                mode='markers',
                marker=dict(size=6, color='blue'),
                name=point['name']
            )
    
    def create_multiple_plots(self, df, threshold_results):
        """创建多个图表（预留扩展功能）"""
        # 可以扩展为创建多个相关图表
        return {
            'voltage_soc': self.create_voltage_soc_plot(df, threshold_results)
        }
    
    def get_chart_count(self):
        """获取已生成的图表数量"""
        return self._chart_count
    
    def reset_chart_count(self):
        """重置图表计数器"""
        self._chart_count = 0