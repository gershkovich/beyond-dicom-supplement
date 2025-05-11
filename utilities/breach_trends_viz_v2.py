#!/usr/bin/env python3
"""
Healthcare Breach Trends Visualization V2
Shows trends of hacking incidents targeting different systems over time, with customizable date ranges.
Focuses specifically on Network Servers, Email, and Electronic Medical Records (EMR).
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
                          entity_type='Healthcare Provider', start_date=None, end_date=None,
                          time_period='month'):
    """
    Generate a chart showing trends of hacking incidents targeting different systems over time.
    
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
    start_date : str, default=None
        Start date for filtering (YYYY-MM-DD format)
    end_date : str, default=None
        End date for filtering (YYYY-MM-DD format)  
    time_period : str, default='month'
        Time period for grouping data: 'month', 'quarter', or 'year'
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
        suffix = f"_{time_period}"
        if start_date:
            suffix += f"_from_{start_date}"
        if end_date:
            suffix += f"_to_{end_date}"
        output_path = project_root / 'figures' / f"breach_trends{suffix}.png"
    
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
        
        # Convert submission date to datetime for filtering
        df['Breach Submission Date'] = pd.to_datetime(df['Breach Submission Date'], errors='coerce')
        df = df.dropna(subset=['Breach Submission Date'])
        
        # Filter by start date if specified
        if start_date is not None:
            try:
                start_dt = pd.to_datetime(start_date)
                df = df[df['Breach Submission Date'] >= start_dt]
                print(f"Filtered data to entries submitted since {start_dt.strftime('%Y-%m-%d')}, resulting in {len(df)} records.")
            except ValueError:
                print(f"Error: Invalid start date format '{start_date}'. Please use YYYY-MM-DD format.")
                return None
        
        # Filter by end date if specified
        if end_date is not None:
            try:
                end_dt = pd.to_datetime(end_date)
                df = df[df['Breach Submission Date'] <= end_dt]
                print(f"Further filtered to entries submitted before {end_dt.strftime('%Y-%m-%d')}, resulting in {len(df)} records.")
            except ValueError:
                print(f"Error: Invalid end date format '{end_date}'. Please use YYYY-MM-DD format.")
                return None
        
        # Focus on hacking incidents
        hacking_df = df[df['Type of Breach'].str.contains('Hacking', na=False)]
        print(f"Found {len(hacking_df)} hacking incidents")
        
        # Check date range
        min_date = hacking_df['Breach Submission Date'].min()
        max_date = hacking_df['Breach Submission Date'].max()
        print(f"Date range in filtered data: {min_date.strftime('%m/%d/%Y')} to {max_date.strftime('%m/%d/%Y')}")
        
        # Create focused categories for location analysis - specifically target our key categories
        def categorize_location(location):
            if pd.isna(location):
                return "Other"
            
            location = str(location).lower()
            
            if 'network server' in location:
                return "Network Server"
            elif 'email' in location:
                return "Email"
            elif 'electronic medical record' in location or 'emr' in location or 'ehr' in location:
                return "Electronic Medical Record"
            else:
                return "Other"
        
        # Apply categorization
        hacking_df['System_Category'] = hacking_df['Location of Breached Information'].apply(categorize_location)
        
        # Add time period columns
        hacking_df['Year'] = hacking_df['Breach Submission Date'].dt.year
        hacking_df['Month'] = hacking_df['Breach Submission Date'].dt.month
        hacking_df['Quarter'] = hacking_df['Breach Submission Date'].dt.quarter
        
        # Group by time period and system category
        if time_period == 'month':
            # Format as year-month for clear x-axis labeling
            hacking_df['Period'] = hacking_df['Breach Submission Date'].dt.strftime('%Y-%m')
            date_format = '%b %Y'
            locator_interval = 3  # Show every 3 months for readability
        elif time_period == 'quarter':
            # Format as year-Q# for quarters
            hacking_df['Period'] = hacking_df.apply(lambda x: f"{x['Year']}-Q{x['Quarter']}", axis=1)
            date_format = '%Y-Q%q'
            locator_interval = 1  # Show every quarter
        elif time_period == 'year':
            # Just use year
            hacking_df['Period'] = hacking_df['Year']
            date_format = '%Y'
            locator_interval = 1  # Show every year
        else:
            print(f"Error: Invalid time period '{time_period}'. Use 'month', 'quarter', or 'year'.")
            return None
        
        # Group by period and system category
        grouped = hacking_df.groupby(['Period', 'System_Category']).size().unstack(fill_value=0)
        
        # Ensure all categories exist
        for category in ["Network Server", "Email", "Electronic Medical Record", "Other"]:
            if category not in grouped.columns:
                grouped[category] = 0
        
        # Sort by period
        grouped = grouped.sort_index()
        
        # Setup figure
        plt.figure(figsize=(16, 10), facecolor='white')
        ax = plt.subplot(111)
        
        # Set up colors
        colors = {
            "Network Server": "#1f77b4",    # Blue
            "Email": "#ff7f0e",             # Orange
            "Electronic Medical Record": "#2ca02c",  # Green
            "Other": "#7f7f7f"              # Gray
        }
        
        # Plot the data - we want a line for each key category
        periods = grouped.index.tolist()
        
        # Define specific markers for each category for clarity
        markers = {
            "Network Server": "o",          # Circle
            "Email": "s",                   # Square
            "Electronic Medical Record": "D", # Diamond
            "Other": "^"                    # Triangle
        }
        
        # Plot each category
        for category in ["Network Server", "Email", "Electronic Medical Record", "Other"]:
            ax.plot(periods, 
                    grouped[category], 
                    marker=markers[category], 
                    markersize=10, 
                    linewidth=3, 
                    color=colors[category], 
                    label=category)
        
        # Add data labels for meaningful data points (avoid clutter for monthly)
        if time_period != 'month' or len(periods) < 15:
            for i, period in enumerate(periods):
                for category in ["Network Server", "Email", "Electronic Medical Record"]:
                    # Only label non-zero values
                    if grouped[category].iloc[i] > 0:
                        ax.annotate(f"{grouped[category].iloc[i]}",
                                  xy=(i, grouped[category].iloc[i]),
                                  xytext=(0, 7), 
                                  textcoords='offset points',
                                  ha='center', 
                                  va='bottom', 
                                  fontweight='bold', 
                                  color=colors[category])
        
        # Format x-axis for better readability
        if time_period == 'month':
            # For months, show every X months to avoid overcrowding
            x_interval = max(1, len(periods) // 8)  # Show approximately 8 tick marks
            plt.xticks(range(0, len(periods), x_interval), [periods[i] for i in range(0, len(periods), x_interval)])
        else:
            # For quarters and years, show every period
            plt.xticks(range(len(periods)), periods)
            
        plt.xticks(rotation=45, ha='right')
        
        # Format y-axis to use integers only
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Labels and title
        plt.xlabel(f'Time Period ({time_period.capitalize()})', fontsize=18, labelpad=15)
        plt.ylabel('Number of Hacking Incidents', fontsize=18, labelpad=15)
        
        title = f"Trends of Healthcare Hacking Incidents by Target System"
        if start_date or end_date:
            date_range = ""
            if start_date:
                date_range += f"From {start_date} "
            if end_date:
                date_range += f"To {end_date}"
            title += f"\n({date_range})"
        elif entity_type:
            title += f"\n({entity_type}s Only)"
            
        plt.title(title, fontsize=24, pad=20, fontweight='bold')
        
        # Add legend
        legend = plt.legend(title="Target Systems", loc='upper left', bbox_to_anchor=(1.01, 1), 
                          frameon=True, fontsize=16)
        legend.get_title().set_fontsize(18)
        
        # Add a border to the legend for better visual separation
        legend.get_frame().set_linewidth(1.5)
        legend.get_frame().set_edgecolor('#333333')
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Calculate and add total statistics as a text box
        total_stats = grouped.sum().to_dict()
        total_incidents = sum(total_stats.values())
        
        stats_text = (
            f"Summary Statistics:\n"
            f"Total Hacking Incidents: {total_incidents}\n"
            f" • Network Server: {total_stats['Network Server']} ({total_stats['Network Server']/total_incidents*100:.1f}%)\n"
            f" • Email: {total_stats['Email']} ({total_stats['Email']/total_incidents*100:.1f}%)\n"
            f" • Electronic Medical Record: {total_stats['Electronic Medical Record']} ({total_stats['Electronic Medical Record']/total_incidents*100:.1f}%)\n"
            f" • Other Systems: {total_stats['Other']} ({total_stats['Other']/total_incidents*100:.1f}%)"
        )
        
        # Add text box with statistics - position under the legend on the right side
        plt.figtext(0.86, 0.45, stats_text, fontsize=14, ha='center',
                  bbox=dict(facecolor='whitesmoke', alpha=0.8, boxstyle='round,pad=0.8', 
                           edgecolor='lightgray'))
        
        # Adjust layout - provide more space on the right for legend and stats
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.12, right=0.75)
        
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
    parser.add_argument("--start-date", help="Only include breaches submitted on or after this date (YYYY-MM-DD)", default=None)
    parser.add_argument("--end-date", help="Only include breaches submitted on or before this date (YYYY-MM-DD)", default=None)
    parser.add_argument("--period", choices=["month", "quarter", "year"], default="month",
                      help="Time period for grouping data: month, quarter, or year")
    
    args = parser.parse_args()
    
    result = generate_trends_chart(
        args.input, 
        args.output, 
        args.sheet, 
        args.entity if args.entity != "all" else None,
        args.start_date,
        args.end_date,
        args.period
    )
    
    if result:
        print("✓ Done!")
    else:
        print("✗ Failed to generate visualization")
        sys.exit(1)
