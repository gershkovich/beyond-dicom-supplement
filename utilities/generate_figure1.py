#!/usr/bin/env python3
"""
generate_figure1.py - Generate architecture diagrams for the paper

This script creates a comparison diagram of DICOM versus modular
architecture approaches for digital pathology.

Usage:
    python generate_figure1.py [--output-dir=PATH]

Author: Your Name
"""

import os
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np


def create_dicom_architecture():
    """
    Create a visual representation of the monolithic DICOM architecture.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Draw the monolithic DICOM container
    rect = patches.Rectangle((0.1, 0.1), 0.8, 0.8, 
                             linewidth=2, edgecolor='navy', 
                             facecolor='lightsteelblue', alpha=0.7)
    ax.add_patch(rect)
    
    # Add sections within the monolithic structure
    sections = [
        ('Image Data', 0.15, 0.65, 0.7, 0.2),
        ('Metadata', 0.15, 0.45, 0.7, 0.15),
        ('Annotations', 0.15, 0.25, 0.7, 0.15),
        ('DICOM Headers', 0.15, 0.15, 0.7, 0.05)
    ]
    
    for section, x, y, w, h in sections:
        section_rect = patches.Rectangle((x, y), w, h, 
                                         linewidth=1, edgecolor='darkblue', 
                                         facecolor='white', alpha=0.9)
        ax.add_patch(section_rect)
        ax.text(x + w/2, y + h/2, section, 
                ha='center', va='center', fontsize=12)
    
    # Add title
    ax.text(0.5, 0.95, 'Monolithic DICOM Architecture', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Remove axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    return fig


def create_modular_architecture():
    """
    Create a visual representation of the modular architecture approach.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create boxes for different modules
    modules = [
        ('Image Data\n(OME-TIFF)', 0.1, 0.6, 0.35, 0.25),
        ('Clinical Metadata\n(FHIR JSON)', 0.55, 0.6, 0.35, 0.25),
        ('Annotations\n(GeoJSON)', 0.1, 0.25, 0.35, 0.25),
        ('Analysis Results\n(Custom JSON)', 0.55, 0.25, 0.35, 0.25)
    ]
    
    # Draw connection lines between modules
    # Create meshgrid of module centers
    centers = [(x + w/2, y + h/2) for _, x, y, w, h in modules]
    
    # Draw connecting lines
    for i, (cx1, cy1) in enumerate(centers):
        for j, (cx2, cy2) in enumerate(centers):
            if i < j:  # Only draw each connection once
                ax.plot([cx1, cx2], [cy1, cy2], 'k-', alpha=0.2, linewidth=1)
    
    # Draw module boxes
    for module, x, y, w, h in modules:
        module_rect = patches.Rectangle((x, y), w, h, 
                                       linewidth=2, edgecolor='forestgreen', 
                                       facecolor='palegreen', alpha=0.7)
        ax.add_patch(module_rect)
        ax.text(x + w/2, y + h/2, module, 
                ha='center', va='center', fontsize=12)
    
    # Add title
    ax.text(0.5, 0.95, 'Modular Architecture Approach', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Remove axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    return fig


def main():
    """
    Main function to generate the architecture comparison figure.
    """
    parser = argparse.ArgumentParser(description='Generate architecture diagrams.')
    parser.add_argument('--output-dir', default='../figures', 
                      help='Directory to save the output files (default: ../figures)')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Generate DICOM architecture diagram
    dicom_fig = create_dicom_architecture()
    dicom_path = os.path.join(args.output_dir, 'dicom_architecture.png')
    dicom_fig.savefig(dicom_path, dpi=300, bbox_inches='tight')
    print(f"DICOM architecture diagram saved to {dicom_path}")
    
    # Generate modular architecture diagram
    modular_fig = create_modular_architecture()
    modular_path = os.path.join(args.output_dir, 'modular_architecture.png')
    modular_fig.savefig(modular_path, dpi=300, bbox_inches='tight')
    print(f"Modular architecture diagram saved to {modular_path}")
    
    # Generate combined figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Recreate DICOM architecture in first subplot
    rect = patches.Rectangle((0.1, 0.1), 0.8, 0.8, 
                             linewidth=2, edgecolor='navy', 
                             facecolor='lightsteelblue', alpha=0.7,
                             transform=ax1.transAxes)
    ax1.add_patch(rect)
    
    sections = [
        ('Image Data', 0.15, 0.65, 0.7, 0.2),
        ('Metadata', 0.15, 0.45, 0.7, 0.15),
        ('Annotations', 0.15, 0.25, 0.7, 0.15),
        ('DICOM Headers', 0.15, 0.15, 0.7, 0.05)
    ]
    
    for section, x, y, w, h in sections:
        section_rect = patches.Rectangle((x, y), w, h, 
                                         linewidth=1, edgecolor='darkblue', 
                                         facecolor='white', alpha=0.9,
                                         transform=ax1.transAxes)
        ax1.add_patch(section_rect)
        ax1.text(x + w/2, y + h/2, section, 
                 ha='center', va='center', fontsize=12,
                 transform=ax1.transAxes)
    
    ax1.text(0.5, 0.95, 'Monolithic DICOM Architecture', 
             ha='center', va='center', fontsize=14, fontweight='bold',
             transform=ax1.transAxes)
    
    # Recreate modular architecture in second subplot
    modules = [
        ('Image Data\n(OME-TIFF)', 0.1, 0.6, 0.35, 0.25),
        ('Clinical Metadata\n(FHIR JSON)', 0.55, 0.6, 0.35, 0.25),
        ('Annotations\n(GeoJSON)', 0.1, 0.25, 0.35, 0.25),
        ('Analysis Results\n(Custom JSON)', 0.55, 0.25, 0.35, 0.25)
    ]
    
    centers = [(x + w/2, y + h/2) for _, x, y, w, h in modules]
    
    for i, (cx1, cy1) in enumerate(centers):
        for j, (cx2, cy2) in enumerate(centers):
            if i < j:
                ax2.plot([cx1, cx2], [cy1, cy2], 'k-', alpha=0.2, linewidth=1,
                         transform=ax2.transAxes)
    
    for module, x, y, w, h in modules:
        module_rect = patches.Rectangle((x, y), w, h, 
                                       linewidth=2, edgecolor='forestgreen', 
                                       facecolor='palegreen', alpha=0.7,
                                       transform=ax2.transAxes)
        ax2.add_patch(module_rect)
        ax2.text(x + w/2, y + h/2, module, 
                ha='center', va='center', fontsize=12,
                transform=ax2.transAxes)
    
    ax2.text(0.5, 0.95, 'Modular Architecture Approach', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            transform=ax2.transAxes)
    
    # Remove axis ticks and labels for both subplots
    for ax in [ax1, ax2]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    plt.suptitle('DICOM vs. Modular Architecture for Digital Pathology', 
                 fontsize=16, fontweight='bold')
    
    # Save the combined figure
    combined_path = os.path.join(args.output_dir, 'architecture_comparison.png')
    fig.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"Combined architecture comparison saved to {combined_path}")
    
    plt.close('all')


if __name__ == "__main__":
    main()
