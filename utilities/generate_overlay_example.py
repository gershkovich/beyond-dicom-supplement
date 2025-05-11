#!/usr/bin/env python3
"""
generate_overlay_example.py - Generate mock PHI masking overlay examples

This script creates examples of modular PHI masking overlays for
whole slide images (WSI) using GeoJSON format.

Usage:
    python generate_overlay_example.py [--output-dir=PATH]

Author: Your Name
"""

import os
import json
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from datetime import datetime


def create_sample_wsi(width=1024, height=768, save_path=None):
    """
    Create a sample WSI image with simulated tissue and annotations.
    
    Args:
        width (int): Width of the sample image
        height (int): Height of the sample image
        save_path (str, optional): Path to save the image
        
    Returns:
        PIL.Image: Generated sample image
    """
    # Create a blank image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simulated tissue area (light pink background)
    tissue_shape = [(100, 100), (width-100, height-100)]
    draw.rectangle(tissue_shape, fill=(255, 240, 240))
    
    # Draw some "cellular structures" as small circles
    np.random.seed(42)  # For reproducibility
    for _ in range(200):
        x = np.random.randint(150, width-150)
        y = np.random.randint(150, height-150)
        radius = np.random.randint(3, 8)
        color_value = np.random.randint(180, 220)
        draw.ellipse(
            [(x-radius, y-radius), (x+radius, y+radius)], 
            fill=(color_value, color_value, color_value)
        )
    
    # Add some "tissue features" with different colors
    for _ in range(20):
        x = np.random.randint(150, width-150)
        y = np.random.randint(150, height-150)
        radius = np.random.randint(10, 25)
        r = np.random.randint(180, 240)
        g = np.random.randint(180, 240)
        b = np.random.randint(180, 240)
        draw.ellipse(
            [(x-radius, y-radius), (x+radius, y+radius)], 
            fill=(r, g, b), outline=(r-30, g-30, b-30)
        )
    
    # Add some text as "PHI" that will need to be masked
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        # Fall back to default font if Arial not available
        font = ImageFont.load_default()
    
    # Patient information as PHI (to be masked)
    phi_elements = [
        {"text": "Patient: John Doe", "position": (50, 30)},
        {"text": "DOB: 01/15/1965", "position": (50, 60)},
        {"text": "MRN: 12345678", "position": (width-200, 30)},
        {"text": "Accession: WSI20230601", "position": (width-250, 60)}
    ]
    
    for phi in phi_elements:
        draw.text(
            phi["position"], phi["text"], 
            fill=(0, 0, 0), font=font
        )
    
    # Add a scale bar
    draw.rectangle([(width-150, height-50), (width-50, height-40)], fill=(0, 0, 0))
    draw.text((width-150, height-40), "100 μm", fill=(0, 0, 0), font=font)
    
    # Save the image if a path is provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)
        print(f"Sample WSI saved to {save_path}")
    
    return image, phi_elements


def create_phi_mask_geojson(phi_elements, image_width, image_height, save_path=None):
    """
    Create a GeoJSON file with PHI masking regions.
    
    Args:
        phi_elements (list): List of PHI elements with text and position
        image_width (int): Width of the reference image
        image_height (int): Height of the reference image
        save_path (str, optional): Path to save the GeoJSON file
        
    Returns:
        dict: GeoJSON object
    """
    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": [],
        "properties": {
            "name": "PHI Masking Overlay",
            "description": "Protected Health Information masking regions",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "image_dimensions": {
                "width": image_width,
                "height": image_height
            }
        }
    }
    
    # Create features for each PHI element (add bounding boxes around text)
    for i, phi in enumerate(phi_elements):
        # Estimate text dimensions based on length and font size
        text = phi["text"]
        pos_x, pos_y = phi["position"]
        
        # Approximate text size (this varies by font, but we use estimates)
        # Assume average character is 15px wide and 30px high
        text_width = len(text) * 15
        text_height = 30
        
        # Create a bounding box with some padding
        padding = 5
        x1 = pos_x - padding
        y1 = pos_y - padding
        x2 = pos_x + text_width + padding
        y2 = pos_y + text_height + padding
        
        # Create a feature for this PHI element
        feature = {
            "type": "Feature",
            "id": f"phi-mask-{i}",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [x1, y1],
                    [x2, y1],
                    [x2, y2],
                    [x1, y2],
                    [x1, y1]  # Close the polygon
                ]]
            },
            "properties": {
                "type": "phi-mask",
                "category": "patient-identifier",
                "mask_method": "rectangle",
                "mask_color": "#000000",
                "text_description": "Patient identifiable information"
            }
        }
        
        geojson["features"].append(feature)
    
    # Save the GeoJSON if a path is provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        print(f"PHI mask GeoJSON saved to {save_path}")
    
    return geojson


def apply_phi_mask(image, geojson, save_path=None):
    """
    Apply the PHI mask to the image based on GeoJSON regions.
    
    Args:
        image (PIL.Image): The image to mask
        geojson (dict): GeoJSON object with masking regions
        save_path (str, optional): Path to save the masked image
        
    Returns:
        PIL.Image: Masked image
    """
    # Create a copy of the image to mask
    masked_image = image.copy()
    draw = ImageDraw.Draw(masked_image)
    
    # Apply each masking region
    for feature in geojson["features"]:
        if feature["geometry"]["type"] == "Polygon":
            # Get coordinates and flatten the list
            coords = feature["geometry"]["coordinates"][0]  # First and only ring
            
            # Draw a filled polygon as the mask
            mask_color = feature["properties"].get("mask_color", "#000000")
            
            # Convert hex color to RGB if needed
            if isinstance(mask_color, str) and mask_color.startswith('#'):
                # Convert hex to RGB tuple
                mask_color = mask_color.lstrip('#')
                mask_color = tuple(int(mask_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Draw the mask
            draw.polygon([tuple(c) for c in coords], fill=mask_color)
    
    # Save the masked image if a path is provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        masked_image.save(save_path)
        print(f"Masked WSI saved to {save_path}")
    
    return masked_image


def create_comparison_figure(original_image, masked_image, save_path=None):
    """
    Create a comparison figure showing original and masked images side by side.
    
    Args:
        original_image (PIL.Image): Original unmasked image
        masked_image (PIL.Image): Image with PHI masks applied
        save_path (str, optional): Path to save the comparison figure
    """
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Display original image
    ax1.imshow(np.array(original_image))
    ax1.set_title('Original Image with PHI', fontsize=14)
    ax1.axis('off')
    
    # Display masked image
    ax2.imshow(np.array(masked_image))
    ax2.set_title('Image with PHI Masking Applied', fontsize=14)
    ax2.axis('off')
    
    plt.tight_layout()
    
    # Save the comparison figure if a path is provided
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison figure saved to {save_path}")
        plt.close()
    else:
        plt.show()


def main():
    """
    Main function to generate PHI masking overlay examples.
    """
    parser = argparse.ArgumentParser(description='Generate PHI masking overlay examples.')
    parser.add_argument('--output-dir', default='../examples', 
                      help='Directory to save output files (default: ../examples)')
    args = parser.parse_args()
    
    # Create output directories
    examples_dir = args.output_dir
    os.makedirs(examples_dir, exist_ok=True)
    
    # Create a sample WSI image
    sample_wsi_path = os.path.join(examples_dir, 'sample_wsi.png')
    sample_image, phi_elements = create_sample_wsi(save_path=sample_wsi_path)
    
    # Create GeoJSON PHI masking overlay
    geojson_path = os.path.join(examples_dir, 'phi_mask_overlay.geojson')
    phi_geojson = create_phi_mask_geojson(
        phi_elements, 
        sample_image.width, 
        sample_image.height, 
        save_path=geojson_path
    )
    
    # Apply the PHI mask to the image
    masked_wsi_path = os.path.join(examples_dir, 'masked_wsi.png')
    masked_image = apply_phi_mask(sample_image, phi_geojson, save_path=masked_wsi_path)
    
    # Create comparison figure
    comparison_path = os.path.join(examples_dir, 'phi_masking_comparison.png')
    create_comparison_figure(sample_image, masked_image, save_path=comparison_path)
    
    print("PHI masking overlay examples generated successfully.")


if __name__ == "__main__":
    main()
