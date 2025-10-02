import plotly.express as px

class BatteryVisualizer:
    """电池数据可视化类"""
    
    @staticmethod
    def create_voltage_soc_plot(df, threshold_results, reversed_x=False):
        """创建电压-SOC曲线图"""
        fig = px.line(df, x='SOC', y=['voltage'])
        
        if reversed_x:
            fig.update_xaxes(autorange="reversed")
            
        fig.update_yaxes(range=[2.5, 3.6])
        fig.update_layout(
            xaxis_title='SOC（%）', 
            yaxis_title='电压(V)', 
            xaxis_dtick=5, 
            showlegend=False
        )
        
        # 添加阈值标注
        BatteryVisualizer._add_threshold_annotations(fig, threshold_results)
        
        return fig
    
    @staticmethod
    def _add_threshold_annotations(fig, threshold_results):
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