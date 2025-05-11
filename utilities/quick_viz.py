#!/usr/bin/env python3
"""
Quick Healthcare Breach Visualization - Standalone Version
No 3D dependencies, guaranteed to work with standard matplotlib
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
from datetime import datetime
import argparse
import sys

# Configure basic plot style with larger fonts
plt.style.use('default')
sns.set_style("whitegrid")

# Increase all font sizes globally by approximately 30%
plt.rcParams.update({
    'font.size': 14,  # Base font size
    'axes.titlesize': 20,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 16,
    'legend.title_fontsize': 18,
    'figure.titlesize': 26
})

def generate_chart(excel_path=None, output_path=None, sheet_name='reportResultTable1', start_date=None, end_date=None):
    """Generate a simple, reliable pie chart from healthcare breach data."""
    # Default to project structure if paths not provided
    if excel_path is None:
        # Get the project root directory (2 levels up from this script)
        project_root = Path(__file__).parent.parent
        excel_path = project_root / 'data' / 'breach_report.xlsx'
        
    if output_path is None:
        # Get the project root directory if not already defined
        if 'project_root' not in locals():
            project_root = Path(__file__).parent.parent
        output_path = project_root / 'figures' / 'healthcare_breach_viz.png'
    try:
        # Handle paths
        file_path = Path(excel_path)
        if not file_path.exists():
            print(f"Error: File not found: {excel_path}")
            return None
            
        # Output path is now handled in the function parameters with project structure defaults
        
        # Load data
        print(f"Loading data from {file_path}...")
        data = pd.ExcelFile(file_path)
        df = data.parse(sheet_name)
        
        # Filter by 'Breach Submission Date' if date range is specified
        if 'Breach Submission Date' not in df.columns:
            print("Error: 'Breach Submission Date' column not found in the Excel file.")
            return None
            
        # Convert submission date to datetime for filtering
        df['Breach Submission Date'] = pd.to_datetime(df['Breach Submission Date'], errors='coerce')
        
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
        
        # Filter to healthcare providers
        providers = df[df['Covered Entity Type'] == 'Healthcare Provider']
        print(f"Found {len(providers)} healthcare provider records")
        
        # Group and aggregate data
        grouped = providers.groupby('Location of Breached Information').agg({
            'Name of Covered Entity': 'count',
            'Individuals Affected': 'sum'
        }).rename(columns={
            'Name of Covered Entity': 'Breaches',
            'Individuals Affected': 'Affected'
        })
        
        # Sort and limit to top categories
        grouped = grouped.sort_values('Breaches', ascending=False)
        if len(grouped) > 7:  # Limit for readability
            others = grouped.iloc[7:].copy()
            others_row = pd.DataFrame({
                'Breaches': [others['Breaches'].sum()],
                'Affected': [others['Affected'].sum()]
            }, index=['Other Locations'])
            
            grouped = pd.concat([grouped.iloc[:7], others_row])
        
        # Setup figure - SIMPLE 2D ONLY - same overall size
        plt.figure(figsize=(16, 9), facecolor='white')
        
        # Get a color palette (colorblind-friendly)
        colors = sns.color_palette("colorblind", len(grouped))
        
        # Prepare data
        sizes = grouped['Breaches']
        labels = grouped.index
        total = sizes.sum()
        percentages = (sizes / total * 100).round(1)
        
        # Create explode array for top categories
        explode = [0.05 if i < 3 else 0.02 for i in range(len(grouped))]
        
        # Create axes with specific size to make pie chart smaller
        # Reduce chart size by ~30% by creating a smaller subplot area
        # Shift the entire chart slightly to the right (+0.03)
        ax = plt.axes([0.33, 0.15, 0.5, 0.7])  # [left, bottom, width, height]
        
        # Simple pie chart - NO 3D - smaller relative to figure
        patches, _ = ax.pie(
            sizes, 
            explode=explode,
            colors=colors, 
            startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}  # Thicker border for better visibility
        )
        
        # Add percentage labels manually - 30% larger fonts
        for i, (patch, pct) in enumerate(zip(patches, percentages)):
            if pct >= 3:  # Only label segments >= 3%
                ang = (patch.theta2 + patch.theta1)/2
                x = 0.7 * np.cos(np.radians(ang))
                y = 0.7 * np.sin(np.radians(ang))
                ax.text(x, y, f"{int(pct)}%", ha='center', va='center',
                        fontsize=18, fontweight='bold', color='white')  # Increased from 14 to 18
        
        # Add legend with larger fonts
        legend_labels = [f"{label} ({sizes.iloc[i]:,} breaches, {percentages.iloc[i]}%)" 
                        for i, label in enumerate(labels)]
        
        # In matplotlib, y=0 is bottom, y=1 is top
        # Moving down by 60px in a 900px figure means moving about 0.067 in normalized coordinates
        # Moving left by 10px in a 1600px figure means moving about 0.006 in normalized coordinates
        legend = ax.legend(
            patches, 
            legend_labels,
            title="Breach Locations",
            loc="center left",
            bbox_to_anchor=(1.0, 0.18),  # Moved down and slightly left
            frameon=True,
            fontsize=16
        )
        
        # Increase legend title font size
        legend.get_title().set_fontsize(21)  # Increased from default by ~30%
        
        # Add title - 30% larger font
        plt.suptitle(  # Using suptitle for figure-level title rather than axes-level
            "Healthcare Provider Data Breaches:\nLocation Distribution and Impact",
            fontsize=26,  # Increased from 20 to 26
            y=0.98,  # Position from top
            fontweight='bold'
        )
        
        # Add annotations for affected counts - with larger fonts
        for i, patch in enumerate(patches):
            if percentages.iloc[i] >= 3:
                ang = (patch.theta2 + patch.theta1)/2
                radius = 1.3 + (i * 0.05)  # Stagger
                x = radius * np.cos(np.radians(ang))
                y = radius * np.sin(np.radians(ang))
                
                # Format affected count
                count = grouped['Affected'].iloc[i]
                if count >= 1_000_000:
                    text = f"{count/1_000_000:.1f}M affected"
                elif count >= 1_000:
                    text = f"{count/1_000:.1f}K affected"
                else:
                    text = f"{int(count):,} affected"
                
                # Skip the 'Other' category entirely - no label for it
                segment_name = labels[i]
                if segment_name == 'Other' or segment_name == 'Other Locations':
                    continue
                
                # Apply a generic stagger based on index to reduce label collision
                x += 0.1 * ((i % 3) - 1)  # shift left/right
                y += 0.15 * ((i % 2) - 0.5)  # shift up/down
                
                # Add annotation box with larger font
                # ===== ARROW ANNOTATION SYSTEM - DETAILED EXPLANATION =====
                # This is where we create the labels with the gray arrow connectors
                ax.annotate(
                    text,  # The text shown in the label (e.g., "4.8M affected")
                    
                    # === CONNECTION POINT PARAMETERS ===
                    # This is where the arrow STARTS - closer to the pie chart
                    # Multiplying by 0.7 positions it at 70% of the distance from center to label
                    # EFFECT: Increasing these values moves the arrow start point farther from pie center
                    xy=(0.7*x, 0.7*y),  # Connection point on/near the pie slice
                    
                    # === LABEL POSITION PARAMETERS ===
                    # This is where the arrow ENDS and the text label is positioned
                    # The x,y values were already adjusted above for specific labels
                    # EFFECT: This is the main control for repositioning labels
                    xytext=(x, y),      # Label position with offsets applied
                    
                    # === TEXT STYLING ===
                    fontsize=16,         # Size of the label text
                    fontweight='bold',   # Makes the text bold
                    ha='center',         # Horizontal alignment of text (left, center, right)
                    va='center',         # Vertical alignment of text (top, center, bottom)
                    
                    # === LABEL BOX STYLING ===
                    # This creates the white box around the label text
                    bbox=dict(
                        boxstyle="round,pad=0.6",  # Shape and padding of the box
                                                 # Options: 'round', 'square', 'sawtooth', etc.
                                                 # pad controls the padding inside the box
                        fc="white",              # Fill color of the box
                        ec=colors[i],            # Edge (border) color - matches pie slice
                        lw=2,                    # Line width of the border
                        alpha=0.9                # Transparency (1=opaque, 0=transparent)
                    ),
                    
                    # === ARROW PROPERTIES ===
                    # This is where the GRAY ARROWS are controlled
                    arrowprops=dict(
                        # === ARROW STYLE ===
                        # Controls the arrow head style
                        # Options: '-', '->', '-[', '-|>', '<-', '<->', 'fancy', 'simple', etc.
                        # EFFECT: Change this to modify arrow head appearance
                        arrowstyle='-|>',  # A line with a arrow head at the end
                        
                        # === ARROW COLOR AND WIDTH ===
                        color='gray',       # Color of the entire arrow
                        lw=2,               # Line width of the arrow shaft
                                            # EFFECT: Increasing makes thicker arrows
                        
                        # === ARROW ENDPOINT ADJUSTMENTS ===
                        # Controls how much the arrow is shortened at each end
                        # EFFECT: Increasing these values creates more space between
                        # arrow endpoints and the connected objects
                        shrinkA=5,          # Shrink arrow start by 5 points (near pie)
                        shrinkB=5,          # Shrink arrow end by 5 points (near label)
                        
                        # === ARROW CURVATURE ===
                        # Controls the curvature of the arrow
                        # Options: "arc3", "angle", "angle3", or "arc"
                        # The rad parameter controls curvature amount
                        # EFFECT: rad=0 creates straight arrows, higher values create more curved arrows
                        # rad can be negative to curve the other direction
                        connectionstyle="arc3,rad=0.2"  # Curved connector with slight arc
                    )
                    # ===== END OF ARROW ANNOTATION SYSTEM =====
                )
        
        # Add total with larger font
        plt.figtext(
            0.5, 0.03,  # Moved up slightly
            f"Total: {int(total):,} breaches affecting {int(grouped['Affected'].sum()):,} individuals",
            ha='center',
            fontsize=18,  # Increased from 14 to 18
            fontweight='bold'
        )
        
        # Fine-tune layout to accommodate revised positioning
        # Adjust right margin to ensure legend fits properly with new position
        plt.subplots_adjust(right=0.80, left=0.05)
        
        # Add a border to the legend for better visual separation
        legend.get_frame().set_linewidth(1.5)
        legend.get_frame().set_edgecolor('#333333')
        
        # Save
        print(f"Saving visualization to {output_path}...")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Visualization successfully created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating visualization: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a simple healthcare breach visualization")
    parser.add_argument("-i", "--input", help="Path to Excel file with breach data", default=None)
    parser.add_argument("-o", "--output", help="Output file path (PNG)", default=None)
    parser.add_argument("-s", "--sheet", help="Excel sheet name", default="reportResultTable1")
    parser.add_argument("--start-date", help="Only include breaches submitted on or after this date (YYYY-MM-DD)", default=None)
    parser.add_argument("--end-date", help="Only include breaches submitted on or before this date (YYYY-MM-DD)", default=None)
    
    args = parser.parse_args()
    
    result = generate_chart(args.input, args.output, args.sheet, args.start_date, args.end_date)
    if result:
        print("✓ Done!")
    else:
        print("✗ Failed to generate visualization")
        sys.exit(1)
