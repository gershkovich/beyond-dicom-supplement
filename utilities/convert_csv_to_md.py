#!/usr/bin/env python3
"""
convert_csv_to_md.py - Convert CSV tables to Markdown format

This script reads CSV files and converts them to properly formatted Markdown tables.
It can handle multiple files and supports custom column formatting.

Usage:
    python convert_csv_to_md.py input.csv [--output output.md] [--align center,left,right]

Author: Your Name
"""

import os
import argparse
import pandas as pd
import csv


def get_column_alignments(align_spec, num_columns):
    """
    Parse column alignment specifications.
    
    Args:
        align_spec (str): Comma-separated list of alignment specs ('left', 'center', 'right')
        num_columns (int): Number of columns in the table
        
    Returns:
        list: List of alignment characters for markdown (:---, :---:, ---:)
    """
    if not align_spec:
        return [':---:'] * num_columns  # Default center alignment
    
    alignments = align_spec.split(',')
    markdown_alignments = []
    
    # If fewer alignments than columns, cycle through the provided alignments
    for i in range(num_columns):
        alignment = alignments[i % len(alignments)].strip().lower()
        
        if alignment == 'left':
            markdown_alignments.append(':---')
        elif alignment == 'right':
            markdown_alignments.append('---:')
        else:  # Default to center for anything else
            markdown_alignments.append(':---:')
            
    return markdown_alignments


def csv_to_markdown(csv_file, output_file=None, align_spec=None):
    """
    Convert a CSV file to a Markdown table.
    
    Args:
        csv_file (str): Path to the input CSV file
        output_file (str, optional): Path to the output Markdown file
        align_spec (str, optional): Comma-separated list of alignment specs
        
    Returns:
        str: Markdown table as a string
    """
    # Read the CSV file
    try:
        # First determine if we have a header
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(1024)
            has_header = csv.Sniffer().has_header(sample)
        
        # Now read with pandas
        df = pd.read_csv(csv_file, header=0 if has_header else None)
        
        # If no header was detected, use generic column names
        if not has_header:
            df.columns = [f'Column{i+1}' for i in range(len(df.columns))]
        
        # Get column alignments
        alignments = get_column_alignments(align_spec, len(df.columns))
        
        # Generate the markdown table
        header = ' | '.join(str(col) for col in df.columns)
        separator = ' | '.join(alignments)
        
        rows = []
        for _, row in df.iterrows():
            formatted_row = ' | '.join(str(cell) for cell in row)
            rows.append(formatted_row)
        
        # Combine all parts
        markdown_table = f"| {header} |\n| {separator} |\n"
        markdown_table += '\n'.join(f"| {row} |" for row in rows)
        
        # Write to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_table)
            print(f"Markdown table written to {output_file}")
        
        return markdown_table
        
    except Exception as e:
        print(f"Error converting {csv_file} to Markdown: {e}")
        return None


def get_output_filename(input_file, output_dir=None):
    """
    Generate an output filename based on the input file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_dir (str, optional): Directory for the output file
        
    Returns:
        str: Output filename
    """
    basename = os.path.basename(input_file)
    name, _ = os.path.splitext(basename)
    output_name = f"{name}.md"
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return os.path.join(output_dir, output_name)
    
    return output_name


def main():
    """Main function to handle command line arguments and convert files."""
    parser = argparse.ArgumentParser(description='Convert CSV files to Markdown tables.')
    parser.add_argument('csv_files', nargs='+', help='CSV file(s) to convert')
    parser.add_argument('--output', help='Output Markdown file. If multiple CSVs are provided, this will be treated as a directory.')
    parser.add_argument('--align', help='Column alignments as comma-separated list (left,center,right)')
    parser.add_argument('--output-dir', default='../tables', help='Directory to save output files if --output is not specified')
    args = parser.parse_args()
    
    # Process each CSV file
    for csv_file in args.csv_files:
        if not os.path.exists(csv_file):
            print(f"File not found: {csv_file}")
            continue
        
        # Determine output filename
        if args.output and len(args.csv_files) == 1:
            output_file = args.output
        else:
            output_file = get_output_filename(csv_file, args.output_dir)
        
        # Convert CSV to Markdown
        result = csv_to_markdown(csv_file, output_file, args.align)
        if result:
            print(f"Successfully converted {csv_file} to {output_file}")


if __name__ == "__main__":
    main()
