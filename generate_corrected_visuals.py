#!/usr/bin/env python3
"""Generate corrected visual assets with realistic performance data."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Corrected data - OpenSearch fastest, S3 Vectors cheapest
data = {
    'S3 Vectors': {'latency': 261, 'cost': 32, 'throughput': 25, 'cost_per_1k': 0.0049},
    'OpenSearch': {'latency': 45, 'cost': 159, 'throughput': 95, 'cost_per_1k': 0.0206},
    'PostgreSQL': {'latency': 85, 'cost': 89, 'throughput': 65, 'cost_per_1k': 0.0127}
}

def create_corrected_performance_comparison():
    """Create corrected performance comparison chart."""
    services = list(data.keys())
    latencies = [data[s]['latency'] for s in services]
    throughputs = [data[s]['throughput'] for s in services]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Latency comparison - OpenSearch wins
    colors = ['#FF6B6B', '#2E8B57', '#4ECDC4']  # Red for S3 (slower), Green for OpenSearch (fastest)
    bars1 = ax1.bar(services, latencies, color=colors)
    ax1.set_title('Latency Comparison (Lower is Better)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Average Latency (ms)')
    ax1.set_ylim(0, max(latencies) * 1.1)
    
    for bar, val in zip(bars1, latencies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'{val}ms', ha='center', va='bottom', fontweight='bold')
    
    # Throughput comparison - OpenSearch wins
    bars2 = ax2.bar(services, throughputs, color=colors)
    ax2.set_title('Throughput Comparison (Higher is Better)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Queries per Second (QPS)')
    ax2.set_ylim(0, max(throughputs) * 1.1)
    
    for bar, val in zip(bars2, throughputs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val} QPS', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('assets/corrected-performance-comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_corrected_cost_efficiency():
    """Create corrected cost efficiency chart - S3 Vectors wins."""
    services = list(data.keys())
    monthly_costs = [data[s]['cost'] for s in services]
    cost_per_1k = [data[s]['cost_per_1k'] for s in services]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Monthly cost - S3 Vectors wins (green), others expensive (red/orange)
    cost_colors = ['#2E8B57', '#FF6B6B', '#FFA500']
    bars1 = ax1.bar(services, monthly_costs, color=cost_colors)
    ax1.set_title('Monthly Cost Comparison (Lower is Better)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Monthly Cost ($)')
    ax1.set_ylim(0, max(monthly_costs) * 1.1)
    
    for i, (bar, val) in enumerate(zip(bars1, monthly_costs)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'${val}', ha='center', va='bottom', fontweight='bold')
        if i > 0:  # Show cost increase vs S3
            increase = ((val - monthly_costs[0]) / monthly_costs[0]) * 100
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                    f'+{increase:.0f}%', ha='center', va='center', 
                    color='white', fontweight='bold')
    
    # Cost efficiency - S3 Vectors wins
    bars2 = ax2.bar(services, cost_per_1k, color=cost_colors)
    ax2.set_title('Cost per 1,000 Queries (Lower is Better)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Cost per 1K Queries ($)')
    ax2.set_ylim(0, max(cost_per_1k) * 1.1)
    
    for i, (bar, val) in enumerate(zip(bars2, cost_per_1k)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005, 
                f'${val:.4f}', ha='center', va='bottom', fontweight='bold')
        if i > 0:  # Show efficiency vs S3
            efficiency = val / cost_per_1k[0]
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                    f'{efficiency:.1f}x', ha='center', va='center', 
                    color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('assets/corrected-cost-efficiency.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_corrected_tradeoff_matrix():
    """Create performance vs cost matrix showing the tradeoff."""
    fig = go.Figure()
    
    colors = {'S3 Vectors': '#2E8B57', 'OpenSearch': '#FF6B6B', 'PostgreSQL': '#4ECDC4'}
    
    for service, metrics in data.items():
        fig.add_trace(go.Scatter(
            x=[metrics['latency']],
            y=[metrics['cost']],
            mode='markers+text',
            marker=dict(size=25, color=colors[service]),
            text=[service],
            textposition="top center",
            name=service,
            hovertemplate=f"<b>{service}</b><br>" +
                         f"Latency: {metrics['latency']}ms<br>" +
                         f"Monthly Cost: ${metrics['cost']}<br>" +
                         f"Throughput: {metrics['throughput']} QPS<extra></extra>"
        ))
    
    fig.update_layout(
        title="Performance vs Cost: The Clear Tradeoff",
        xaxis_title="Average Latency (ms) - Lower is Better",
        yaxis_title="Monthly Cost ($) - Lower is Better",
        showlegend=False,
        width=800,
        height=600,
        annotations=[
            dict(x=50, y=140, text="Fast & Expensive<br/>(OpenSearch)", 
                 showarrow=False, font=dict(size=12, color="gray")),
            dict(x=250, y=50, text="Slow & Cheap<br/>(S3 Vectors)", 
                 showarrow=False, font=dict(size=12, color="gray")),
            dict(x=90, y=70, text="Balanced<br/>(PostgreSQL)", 
                 showarrow=False, font=dict(size=12, color="gray"))
        ]
    )
    
    fig.write_html("assets/corrected-performance-cost-matrix.html")
    fig.write_image("assets/corrected-performance-cost-matrix.png", width=800, height=600)

if __name__ == "__main__":
    print("🎨 Generating corrected visual assets...")
    
    create_corrected_performance_comparison()
    print("✅ Corrected performance comparison created")
    
    create_corrected_cost_efficiency()
    print("✅ Corrected cost efficiency chart created")
    
    create_corrected_tradeoff_matrix()
    print("✅ Corrected tradeoff matrix created")
    
    print("\n🎉 All corrected visuals generated!")
