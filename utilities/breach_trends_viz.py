#!/usr/bin/env python3
"""
Healthcare Breach Trends Visualization
Shows monthly trends of hacking incidents targeting different systems (network servers vs. other systems)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
from datetime import datetime
import argparse
import sys
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

# Configure basic plot style
plt.style.use('default')
sns.set_style("whitegrid")

# Increase font sizes globally
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 20,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 16,
    'legend.title_fontsize': 18,
    'figure.titlesize': 26
})

def generate_trends_chart(excel_path=None, output_path=None, sheet_name='reportResultTable1', 
                         entity_type='Healthcare Provider', include_all_years=True):  # Default to showing all available years
    """
    Generate a chart showing monthly trends of hacking incidents targeting different systems.
    
    Parameters:
    -----------
    excel_path : str or Path, optional
        Path to Excel file with breach data
    output_path : str or Path, optional
        Path to save the output visualization
    sheet_name : str, default='reportResultTable1'
        Name of the sheet in the Excel file
    entity_type : str, default='Healthcare Provider'
        Type of covered entity to filter on (or None for all)
    include_all_years : bool, default=False
        If True, show all years in the data; if False, focus on the most recent 12-month period
    """
    # Default to project structure if paths not provided
    if excel_path is None:
        # Get the project root directory (2 levels up from this script)
        project_root = Path(__file__).parent.parent
        excel_path = project_root / 'data' / 'breach_report.xlsx'
        
    if output_path is None:
        # Get the project root directory if not already defined
        if 'project_root' not in locals():
            project_root = Path(__file__).parent.parent
        output_path = project_root / 'figures' / 'breach_trends_viz.png'
    
    try:
        # Handle paths
        file_path = Path(excel_path)
        if not file_path.exists():
            print(f"Error: File not found: {excel_path}")
            return None
            
        # Load data
        print(f"Loading data from {file_path}...")
        data = pd.ExcelFile(file_path)
        df = data.parse(sheet_name)
        
        # Filter to the specified entity type if provided
        if entity_type:
            df = df[df['Covered Entity Type'] == entity_type]
            print(f"Found {len(df)} {entity_type} records")
        else:
            print(f"Found {len(df)} total records")
        
        # Focus on hacking incidents
        hacking_df = df[df['Type of Breach'].str.contains('Hacking', na=False)]
        print(f"Found {len(hacking_df)} hacking incidents")
        
        # Convert submission date to datetime properly, handling different date formats
        # Create a copy to avoid SettingWithCopyWarning
        hacking_df = hacking_df.copy()
        # Convert to datetime 
        hacking_df['Breach Submission Date'] = pd.to_datetime(hacking_df['Breach Submission Date'], errors='coerce')
        
        # Remove rows with invalid dates
        hacking_df = hacking_df.dropna(subset=['Breach Submission Date'])
        
        # Check date range (for logging)
        min_date = hacking_df['Breach Submission Date'].min()
        max_date = hacking_df['Breach Submission Date'].max()
        print(f"Date range in data: {min_date.strftime('%m/%d/%Y')} to {max_date.strftime('%m/%d/%Y')}")
        print(f"Year distribution: {hacking_df['Breach Submission Date'].dt.year.value_counts().sort_index().to_dict()}")
        
        # Extract month and year
        hacking_df['Month_Year'] = hacking_df['Breach Submission Date'].dt.to_period('M')
        
        # If using only recent 12 months
        if not include_all_years:
            twelve_months_ago = max_date - pd.DateOffset(months=11)  # to get 12 months total
            hacking_df = hacking_df[hacking_df['Breach Submission Date'] >= twelve_months_ago]
            print(f"Focusing on 12-month period: {twelve_months_ago.strftime('%m/%Y')} to {max_date.strftime('%m/%Y')}")
        else:
            print(f"Using full date range from {min_date.strftime('%m/%Y')} to {max_date.strftime('%m/%Y')}")
        
        # Create categories for location analysis
        def categorize_location(location):
            if pd.isna(location):
                return "Unknown"
            location = str(location).lower()
            if 'network server' in location:
                return "Network Server"
            elif 'electronic medical record' in location or 'emr' in location or 'ehr' in location:
                return "Electronic Medical Record"
            else:
                return "Other Systems"
        
        # Apply categorization
        hacking_df['System_Category'] = hacking_df['Location of Breached Information'].apply(categorize_location)
        
        # Group by month and system category
        monthly_counts = hacking_df.groupby(['Month_Year', 'System_Category']).size().unstack(fill_value=0)
        
        # Ensure all three categories exist in the data
        for category in ["Network Server", "Electronic Medical Record", "Other Systems"]:
            if category not in monthly_counts.columns:
                monthly_counts[category] = 0
        
        # Sort by month
        monthly_counts = monthly_counts.sort_index()
        
        # Prepare for plotting - convert Period index to datetime for better plotting
        monthly_counts.index = monthly_counts.index.to_timestamp()
        
        # Setup figure
        plt.figure(figsize=(16, 10), facecolor='white')
        ax = plt.subplot(111)
        
        # Plot the data
        network_color = "#1f77b4"  # Blue
        emr_color = "#ff7f0e"     # Orange
        other_color = "#2ca02c"   # Green
        
        # Line plots with markers
        ax.plot(monthly_counts.index, monthly_counts['Network Server'], 
                marker='o', markersize=10, linewidth=3, color=network_color, label='Network Server')
        
        ax.plot(monthly_counts.index, monthly_counts['Electronic Medical Record'], 
                marker='s', markersize=10, linewidth=3, color=emr_color, label='Electronic Medical Record')
        
        ax.plot(monthly_counts.index, monthly_counts['Other Systems'], 
                marker='^', markersize=10, linewidth=3, color=other_color, label='Other Systems')
        
        # Add data labels on top of each point
        for i, date in enumerate(monthly_counts.index):
            # Network Server data labels
            if monthly_counts['Network Server'].iloc[i] > 0:
                ax.annotate(f"{monthly_counts['Network Server'].iloc[i]}",
                          xy=(date, monthly_counts['Network Server'].iloc[i]),
                          xytext=(0, 10), textcoords='offset points',
                          ha='center', va='bottom', fontweight='bold', color=network_color)
            
            # EMR data labels
            if monthly_counts['Electronic Medical Record'].iloc[i] > 0:
                ax.annotate(f"{monthly_counts['Electronic Medical Record'].iloc[i]}",
                          xy=(date, monthly_counts['Electronic Medical Record'].iloc[i]),
                          xytext=(0, 10), textcoords='offset points',
                          ha='center', va='bottom', fontweight='bold', color=emr_color)
            
            # Other Systems data labels
            if monthly_counts['Other Systems'].iloc[i] > 0:
                ax.annotate(f"{monthly_counts['Other Systems'].iloc[i]}",
                          xy=(date, monthly_counts['Other Systems'].iloc[i]),
                          xytext=(0, 10), textcoords='offset points',
                          ha='center', va='bottom', fontweight='bold', color=other_color)
        
        # Format the x-axis to show month and year
        # Use appropriate tick spacing based on how many months we're showing
        num_months = len(monthly_counts)
        if num_months <= 12:
            # For 12 or fewer months, show every month
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        else:
            # For more than 12 months, show every 3 months to avoid overcrowding
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            # Add minor ticks for the months in between
            ax.xaxis.set_minor_locator(mdates.MonthLocator())
        
        plt.xticks(rotation=45, ha='right')
        
        # Format y-axis to use integers only
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Labels and title
        plt.xlabel('Month', fontsize=18, labelpad=15)
        plt.ylabel('Number of Hacking Incidents', fontsize=18, labelpad=15)
        
        title = f"Monthly Trends of Healthcare Hacking Incidents by Target System"
        if entity_type:
            title += f"\n({entity_type}s Only)"
        plt.title(title, fontsize=24, pad=20, fontweight='bold')
        
        # Add legend
        legend = plt.legend(title="Target Systems", loc='upper left', bbox_to_anchor=(1.01, 1), 
                          frameon=True, fontsize=16)
        legend.get_title().set_fontsize(18)
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Calculate and add total statistics as a text box
        total_network = monthly_counts['Network Server'].sum()
        total_emr = monthly_counts['Electronic Medical Record'].sum()
        total_other = monthly_counts['Other Systems'].sum()
        
        stats_text = (
            f"Summary Statistics:\n"
            f"Total Hacking Incidents: {total_network + total_emr + total_other}\n"
            f" • Network Server: {total_network} ({total_network/(total_network + total_emr + total_other)*100:.1f}%)\n"
            f" • Electronic Medical Record: {total_emr} ({total_emr/(total_network + total_emr + total_other)*100:.1f}%)\n"
            f" • Other Systems: {total_other} ({total_other/(total_network + total_emr + total_other)*100:.1f}%)"
        )
        
        # Add text box with statistics
        plt.figtext(0.1, 0.01, stats_text, fontsize=14, ha='left',
                  bbox=dict(facecolor='whitesmoke', alpha=0.8, boxstyle='round,pad=0.8', 
                           edgecolor='lightgray'))
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.17, right=0.85)
        
        # Save the figure
        print(f"Saving visualization to {output_path}...")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Visualization successfully created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate healthcare breach trends visualization")
    parser.add_argument("-i", "--input", help="Path to Excel file with breach data", default=None)
    parser.add_argument("-o", "--output", help="Output file path (PNG)", default=None)
    parser.add_argument("-s", "--sheet", help="Excel sheet name", default="reportResultTable1")
    parser.add_argument("-e", "--entity", help="Covered entity type to filter on", default="Healthcare Provider")
    parser.add_argument("--all-years", help="Include all years in the data", action="store_true")
    
    args = parser.parse_args()
    
    result = generate_trends_chart(
        args.input, 
        args.output, 
        args.sheet, 
        args.entity if args.entity != "all" else None,
        args.all_years
    )
    
    if result:
        print("✓ Done!")
    else:
        print("✗ Failed to generate visualization")
        sys.exit(1)
