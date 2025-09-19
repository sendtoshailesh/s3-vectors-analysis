#!/usr/bin/env python3
"""Generate visual assets for GitHub publication."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Data from real benchmarks
data = {
    'S3 Vectors': {'latency': 261, 'cost': 32, 'throughput': 25, 'cost_per_1k': 0.0049},
    'OpenSearch': {'latency': 649, 'cost': 159, 'throughput': 1.5, 'cost_per_1k': 0.0206},
    'PostgreSQL': {'latency': 145, 'cost': 89, 'throughput': 52, 'cost_per_1k': 0.0127}
}

def create_performance_comparison():
    """Create performance comparison chart."""
    services = list(data.keys())
    latencies = [data[s]['latency'] for s in services]
    throughputs = [data[s]['throughput'] for s in services]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Latency comparison
    bars1 = ax1.bar(services, latencies, color=['#2E8B57', '#FF6B6B', '#4ECDC4'])
    ax1.set_title('Average Latency Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Latency (ms)')
    ax1.set_ylim(0, max(latencies) * 1.1)
    
    # Add value labels
    for bar, val in zip(bars1, latencies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                f'{val}ms', ha='center', va='bottom', fontweight='bold')
    
    # Throughput comparison
    bars2 = ax2.bar(services, throughputs, color=['#2E8B57', '#FF6B6B', '#4ECDC4'])
    ax2.set_title('Throughput Comparison', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Queries per Second (QPS)')
    ax2.set_ylim(0, max(throughputs) * 1.1)
    
    # Add value labels
    for bar, val in zip(bars2, throughputs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val} QPS', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('assets/performance-comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_cost_efficiency_chart():
    """Create cost efficiency visualization."""
    services = list(data.keys())
    monthly_costs = [data[s]['cost'] for s in services]
    cost_per_1k = [data[s]['cost_per_1k'] for s in services]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Monthly cost comparison
    bars1 = ax1.bar(services, monthly_costs, color=['#2E8B57', '#FF6B6B', '#4ECDC4'])
    ax1.set_title('Monthly Cost Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Monthly Cost ($)')
    ax1.set_ylim(0, max(monthly_costs) * 1.1)
    
    # Add value labels and savings
    for i, (bar, val) in enumerate(zip(bars1, monthly_costs)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'${val}', ha='center', va='bottom', fontweight='bold')
        if i > 0:  # Show savings vs S3 Vectors
            savings = ((val - monthly_costs[0]) / monthly_costs[0]) * 100
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                    f'+{savings:.0f}%', ha='center', va='center', 
                    color='white', fontweight='bold')
    
    # Cost per 1K queries
    bars2 = ax2.bar(services, cost_per_1k, color=['#2E8B57', '#FF6B6B', '#4ECDC4'])
    ax2.set_title('Cost per 1,000 Queries', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Cost per 1K Queries ($)')
    ax2.set_ylim(0, max(cost_per_1k) * 1.1)
    
    # Add value labels and efficiency
    for i, (bar, val) in enumerate(zip(bars2, cost_per_1k)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005, 
                f'${val:.4f}', ha='center', va='bottom', fontweight='bold')
        if i > 0:  # Show efficiency vs S3 Vectors
            efficiency = val / cost_per_1k[0]
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                    f'{efficiency:.1f}x', ha='center', va='center', 
                    color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('assets/cost-efficiency-chart.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_cost_matrix():
    """Create performance vs cost scatter plot."""
    fig = go.Figure()
    
    for service, metrics in data.items():
        color = {'S3 Vectors': '#2E8B57', 'OpenSearch': '#FF6B6B', 'PostgreSQL': '#4ECDC4'}[service]
        
        fig.add_trace(go.Scatter(
            x=[metrics['latency']],
            y=[metrics['cost']],
            mode='markers+text',
            marker=dict(size=20, color=color),
            text=[service],
            textposition="top center",
            name=service,
            hovertemplate=f"<b>{service}</b><br>" +
                         f"Latency: {metrics['latency']}ms<br>" +
                         f"Monthly Cost: ${metrics['cost']}<br>" +
                         f"Throughput: {metrics['throughput']} QPS<extra></extra>"
        ))
    
    fig.update_layout(
        title="Performance vs Cost Matrix",
        xaxis_title="Average Latency (ms)",
        yaxis_title="Monthly Cost ($)",
        showlegend=False,
        width=800,
        height=600
    )
    
    # Add quadrant labels
    fig.add_annotation(x=200, y=150, text="High Performance<br>High Cost", 
                      showarrow=False, font=dict(size=12, color="gray"))
    fig.add_annotation(x=600, y=150, text="Low Performance<br>High Cost", 
                      showarrow=False, font=dict(size=12, color="gray"))
    fig.add_annotation(x=200, y=50, text="High Performance<br>Low Cost", 
                      showarrow=False, font=dict(size=12, color="gray"))
    fig.add_annotation(x=600, y=50, text="Low Performance<br>Low Cost", 
                      showarrow=False, font=dict(size=12, color="gray"))
    
    fig.write_html("assets/performance-cost-matrix.html")
    fig.write_image("assets/performance-cost-matrix.png", width=800, height=600)

def create_decision_tree():
    """Create use case decision tree."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Decision tree structure
    boxes = [
        # Root
        {'xy': (5, 9), 'text': 'Vector Database\nSelection', 'color': '#E8E8E8'},
        
        # First level
        {'xy': (2, 7.5), 'text': 'Cost Priority?\n(<$50/month)', 'color': '#FFE4B5'},
        {'xy': (8, 7.5), 'text': 'Performance Priority?\n(<100ms latency)', 'color': '#FFE4B5'},
        
        # Second level - Cost branch
        {'xy': (1, 6), 'text': 'Batch Processing?\n(>200ms OK)', 'color': '#E0F6FF'},
        {'xy': (3, 6), 'text': 'Mixed Workload?\n(100-200ms)', 'color': '#E0F6FF'},
        
        # Second level - Performance branch
        {'xy': (7, 6), 'text': 'High Throughput?\n(>50 QPS)', 'color': '#E0F6FF'},
        {'xy': (9, 6), 'text': 'Real-time Apps?\n(<50ms)', 'color': '#E0F6FF'},
        
        # Solutions
        {'xy': (1, 4.5), 'text': 'S3 Vectors\n$32/month\n261ms avg', 'color': '#90EE90'},
        {'xy': (3, 4.5), 'text': 'PostgreSQL\n$89/month\n145ms avg', 'color': '#87CEEB'},
        {'xy': (7, 4.5), 'text': 'PostgreSQL\n(Scaled)\n$200+/month', 'color': '#87CEEB'},
        {'xy': (9, 4.5), 'text': 'OpenSearch\n(Large Instance)\n$500+/month', 'color': '#FFB6C1'},
    ]
    
    # Draw boxes
    for box in boxes:
        if 'S3 Vectors' in box['text']:
            bbox = dict(boxstyle="round,pad=0.3", facecolor=box['color'], edgecolor='green', linewidth=2)
        else:
            bbox = dict(boxstyle="round,pad=0.3", facecolor=box['color'], edgecolor='black')
            
        ax.text(box['xy'][0], box['xy'][1], box['text'], 
               ha='center', va='center', fontsize=10, fontweight='bold',
               bbox=bbox)
    
    # Draw arrows
    arrows = [
        ((5, 8.7), (2, 7.8)),  # Root to cost
        ((5, 8.7), (8, 7.8)),  # Root to performance
        ((2, 7.2), (1, 6.3)),  # Cost to batch
        ((2, 7.2), (3, 6.3)),  # Cost to mixed
        ((8, 7.2), (7, 6.3)),  # Performance to throughput
        ((8, 7.2), (9, 6.3)),  # Performance to real-time
        ((1, 5.7), (1, 4.8)),  # Batch to S3
        ((3, 5.7), (3, 4.8)),  # Mixed to PostgreSQL
        ((7, 5.7), (7, 4.8)),  # Throughput to PostgreSQL scaled
        ((9, 5.7), (9, 4.8)),  # Real-time to OpenSearch
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    plt.title('Vector Database Selection Decision Tree', fontsize=16, fontweight='bold', pad=20)
    plt.savefig('assets/decision-tree.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_interactive_dashboard():
    """Create interactive Plotly dashboard."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Latency Comparison', 'Cost Comparison', 
                       'Throughput Comparison', 'Cost Efficiency'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    services = list(data.keys())
    colors = ['#2E8B57', '#FF6B6B', '#4ECDC4']
    
    # Latency
    fig.add_trace(go.Bar(
        x=services, 
        y=[data[s]['latency'] for s in services],
        name='Latency (ms)',
        marker_color=colors,
        text=[f"{data[s]['latency']}ms" for s in services],
        textposition='outside'
    ), row=1, col=1)
    
    # Cost
    fig.add_trace(go.Bar(
        x=services,
        y=[data[s]['cost'] for s in services],
        name='Monthly Cost ($)',
        marker_color=colors,
        text=[f"${data[s]['cost']}" for s in services],
        textposition='outside'
    ), row=1, col=2)
    
    # Throughput
    fig.add_trace(go.Bar(
        x=services,
        y=[data[s]['throughput'] for s in services],
        name='Throughput (QPS)',
        marker_color=colors,
        text=[f"{data[s]['throughput']} QPS" for s in services],
        textposition='outside'
    ), row=2, col=1)
    
    # Cost efficiency
    fig.add_trace(go.Bar(
        x=services,
        y=[data[s]['cost_per_1k'] for s in services],
        name='Cost per 1K queries ($)',
        marker_color=colors,
        text=[f"${data[s]['cost_per_1k']:.4f}" for s in services],
        textposition='outside'
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="S3 Vectors vs OpenSearch vs PostgreSQL - Interactive Dashboard",
        showlegend=False,
        height=800
    )
    
    fig.write_html("assets/interactive-dashboard.html")

if __name__ == "__main__":
    print("🎨 Generating visual assets...")
    
    create_performance_comparison()
    print("✅ Performance comparison chart created")
    
    create_cost_efficiency_chart()
    print("✅ Cost efficiency chart created")
    
    create_performance_cost_matrix()
    print("✅ Performance vs cost matrix created")
    
    create_decision_tree()
    print("✅ Decision tree diagram created")
    
    create_interactive_dashboard()
    print("✅ Interactive dashboard created")
    
    print("\n🎉 All visual assets generated in assets/ folder!")
