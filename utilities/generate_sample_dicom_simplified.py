#!/usr/bin/env python3
"""
generate_sample_dicom_simplified.py - Generate a sample DICOM file example for pathology

This script creates a sample DICOM file structure and metadata JSON that represents
what would be found in a pathology whole slide image (WSI) DICOM file. It demonstrates
the approach of storing digital pathology data in a monolithic DICOM format.

Instead of generating an actual DICOM file which might encounter compatibility issues,
this script:
1. Creates a realistic JSON representation of a DICOM file's metadata
2. Generates a sample image that would represent the image data
3. Creates a visual representation showing how the different components are organized

Usage:
    python generate_sample_dicom_simplified.py [--output OUTPUT_DIR]

Author: Peter Gershkovich
"""

import os
import sys
import numpy as np
import argparse
import datetime
import random
import json
from pathlib import Path
import warnings
from faker import Faker  # For generating fake patient data
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


def create_fake_patient():
    """Create fake but realistic-looking patient information."""
    fake = Faker()
    
    # Set seed for reproducibility
    Faker.seed(42)
    random.seed(42)
    
    # Generate basic patient info
    gender = random.choice(['M', 'F'])
    first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
    last_name = fake.last_name()
    
    # Generate a medical record number (MRN)
    mrn = f"{random.randint(1000000, 9999999)}"
    
    # Generate a date of birth (between 18 and 90 years old)
    dob = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y%m%d')
    
    # Generate an address
    address = fake.address().replace('\n', ', ')
    
    # Create a dictionary with all patient information
    patient = {
        'name': f"{last_name}^{first_name}",
        'mrn': mrn,
        'dob': dob,
        'gender': gender,
        'address': address,
        'ssn': fake.ssn(),  # US Social Security Number
        'phone': fake.phone_number(),
        'specimen_id': f"SP-{random.randint(10000, 99999)}",
        'accession_number': f"A{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    }
    
    return patient


def create_sample_image(width=1024, height=768):
    """
    Create a synthetic image to serve as WSI content.
    Returns a PIL Image object.
    """
    # Create base image
    image = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    # Add a tissue-like background
    tissue_rect = [(100, 100), (width-100, height-100)]
    draw.rectangle(tissue_rect, fill=(220, 200, 180))
    
    # Draw some "cellular structures" as random spots
    random.seed(42)  # For reproducibility
    for _ in range(1000):
        x = random.randint(150, width-150)
        y = random.randint(150, height-150)
        radius = random.randint(2, 8)
        # Random purple-ish color (like H&E stain)
        color = (
            random.randint(120, 180),  # R
            random.randint(50, 100),   # G
            random.randint(150, 220)   # B
        )
        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=color)
    
    # Add some larger tissue structures
    for _ in range(5):
        struct_x = random.randint(120, width-200)
        struct_y = random.randint(120, height-200)
        struct_w = random.randint(80, 180)
        struct_h = random.randint(80, 180)
        # Brown-ish color
        color = (
            random.randint(160, 200),  # R
            random.randint(140, 160),  # G
            random.randint(100, 130)   # B
        )
        draw.rectangle([(struct_x, struct_y), (struct_x+struct_w, struct_y+struct_h)], fill=color)
    
    # Draw annotations
    # Rectangle ROI
    draw.rectangle([(200, 200), (400, 350)], outline=(255, 0, 0), width=3)
    # Circle annotation
    draw.ellipse([(600, 350), (680, 430)], outline=(0, 0, 255), width=3)
    
    # Add text describing annotations
    try:
        font = ImageFont.truetype("Arial", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((300, 180), "Region of Interest", fill=(255, 0, 0), font=font)
    draw.text((640, 340), "Suspicious Area", fill=(0, 0, 255), font=font)
    
    return image


def generate_dicom_metadata(patient_info):
    """
    Generate a dictionary representing DICOM metadata for a pathology whole slide image.
    This demonstrates the structure and types of metadata included in a DICOM file.
    """
    # Generate UIDs (using timestamp+random for demonstration)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = f"{random.randint(10000, 99999)}"
    
    study_uid = f"1.2.840.10008.1.2.3.4.{timestamp}.1{random_suffix}"
    series_uid = f"1.2.840.10008.1.2.3.4.{timestamp}.2{random_suffix}"
    instance_uid = f"1.2.840.10008.1.2.3.4.{timestamp}.3{random_suffix}"
    
    # Current date/time
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    current_time = datetime.datetime.now().strftime('%H%M%S')
    
    # Create metadata structure
    metadata = {
        "FileMetaInformation": {
            "MediaStorageSOPClassUID": "1.2.840.10008.5.1.4.1.1.77.1.6",  # VL Whole Slide Microscopy Image Storage
            "MediaStorageSOPInstanceUID": instance_uid,
            "TransferSyntaxUID": "1.2.840.10008.1.2.1",  # Explicit VR Little Endian
            "ImplementationClassUID": "1.2.3.4.5.6.7.8.9",
            "ImplementationVersionName": "DICOM-WSI-DEMO"
        },
        
        "PatientModule": {
            "PatientName": patient_info['name'],
            "PatientID": patient_info['mrn'],
            "PatientBirthDate": patient_info['dob'],
            "PatientSex": patient_info['gender'],
            "PatientAddress": patient_info['address']
        },
        
        "ClinicalTrialSubjectModule": {
            "ClinicalTrialSponsorName": "ACME Research",
            "ClinicalTrialProtocolID": "PATHOLOGY-2025-001",
            "ClinicalTrialProtocolName": "Advanced Digital Pathology Workflow Study"
        },
        
        "GeneralStudyModule": {
            "StudyInstanceUID": study_uid,
            "StudyDate": current_date,
            "StudyTime": current_time,
            "ReferringPhysicianName": "Smith^John",
            "StudyID": f"ST{random.randint(1000, 9999)}",
            "AccessionNumber": patient_info['accession_number'],
            "StudyDescription": "Liver biopsy, suspected carcinoma"
        },
        
        "PatientStudyModule": {
            "AdmittingDiagnosesDescription": "Suspected hepatocellular carcinoma"
        },
        
        "GeneralSeriesModule": {
            "Modality": "SM",  # Slide Microscopy
            "SeriesInstanceUID": series_uid,
            "SeriesNumber": "1",
            "SeriesDescription": "H&E stained slide"
        },
        
        "FrameOfReferenceModule": {
            "FrameOfReferenceUID": f"1.2.840.10008.1.2.3.4.{timestamp}.4{random_suffix}"
        },
        
        "GeneralEquipmentModule": {
            "Manufacturer": "ACME Digital Pathology",
            "ManufacturerModelName": "ACME WSI Scanner 3000",
            "SoftwareVersions": "1.0"
        },
        
        "GeneralImageModule": {
            "InstanceNumber": "1",
            "PatientOrientation": "",
            "ContentDate": current_date,
            "ContentTime": current_time,
            "ImageType": ["ORIGINAL", "PRIMARY"]
        },
        
        "ImagePixelModule": {
            "SamplesPerPixel": 3,
            "PhotometricInterpretation": "RGB",
            "PlanarConfiguration": 0,
            "Rows": 40000,  # Example size for a real WSI
            "Columns": 30000,
            "BitsAllocated": 8,
            "BitsStored": 8,
            "HighBit": 7,
            "PixelRepresentation": 0
        },
        
        "WholeSlideMicroscopyImageModule": {
            "ImagedVolumeWidth": 15.0,  # mm
            "ImagedVolumeHeight": 15.0,  # mm
            "ImagedVolumeDepth": 0.004,  # mm (4 microns)
            "TotalPixelMatrixColumns": 40000,  # Example size for a WSI
            "TotalPixelMatrixRows": 30000,
            "OpticalPathSequence": [
                {
                    "OpticalPathIdentifier": "1",
                    "OpticalPathDescription": "Brightfield illumination",
                    "IlluminationTypeCodeSequence": {
                        "CodeValue": "111741",
                        "CodingSchemeDesignator": "DCM",
                        "CodeMeaning": "Brightfield illumination"
                    },
                    "LuminanceOfSingleReferencePercent": 70.0
                }
            ]
        },
        
        "SpecimenModule": {
            "SpecimenDescriptionSequence": [
                {
                    "SpecimenIdentifier": patient_info['specimen_id'],
                    "SpecimenUID": f"1.2.840.10008.1.2.3.4.{timestamp}.5{random_suffix}",
                    "SpecimenShortDescription": "Liver biopsy",
                    "SpecimenDetailedDescription": "Liver biopsy from segment 7",
                    "SpecimenPreparationSequence": [
                        {
                            "PreparationType": "FORMALIN FIXED PARAFFIN EMBEDDED",
                            "StainingMethod": "H&E"
                        }
                    ]
                }
            ]
        },
        
        "AnnotationModule": {
            "GraphicAnnotationSequence": [
                {
                    "GraphicType": "POLYLINE",
                    "GraphicData": [200, 200, 400, 200, 400, 350, 200, 350, 200, 200],
                    "GraphicFilled": "Y",
                    "TextValue": "Region of Interest"
                },
                {
                    "GraphicType": "CIRCLE",
                    "GraphicData": [640, 390, 40],
                    "GraphicFilled": "N",
                    "TextValue": "Suspicious Area"
                }
            ]
        },
        
        "PathologyExtensions": {
            "ScannerManufacturer": "ACME Digital Pathology",
            "ScannerModelName": "ACME WSI Scanner 3000",
            "ScannerSerialNumber": "WSI30000123",
            "ScanDate": current_date,
            "ScanTime": current_time,
            "MagnificationFactor": "40x",
            "LensNumericalAperture": "0.95",
            "PixelSpacing": "0.25",  # Microns per pixel
            "FocusQualityScore": "0.92",
            "StainQualityScore": "0.88",
            "TissueDetectedPercentage": "76.4"
        },
        
        "SOPCommonModule": {
            "SOPClassUID": "1.2.840.10008.5.1.4.1.1.77.1.6",
            "SOPInstanceUID": instance_uid
        }
    }
    
    return metadata


def create_visualization(metadata, sample_image, output_path):
    """
    Create a visualization that shows the various components of a DICOM file
    and how they are structured in a monolithic format, with contrast to modular approaches.
    """
    # Create the figure with multiple parts
    fig = plt.figure(figsize=(24, 18))
    
    # Use a grid layout
    grid = plt.GridSpec(12, 12, figure=fig)
    
    # Title
    fig.suptitle("DICOM Format for Digital Pathology WSI (Monolithic Approach)", fontsize=26, fontweight='bold', y=0.98)
    
    # Add subtitle explaining the purpose
    plt.figtext(0.5, 0.945, 
               "This diagram illustrates how pathology whole slide images and associated metadata are stored in a single DICOM file,\n"
               "demonstrating the monolithic approach discussed in 'Wearing a Fur Coat in the Summertime'",
               fontsize=16, ha='center')
    
    # 1. DICOM File Structure Overview (left column)
    structure_ax = fig.add_subplot(grid[0:8, 0:3])
    structure_ax.axis('off')
    
    # Create a diagram showing DICOM file structure
    # This will be a visual representation of a DICOM file's components
    file_structure = [
        ("DICOM Header", "128-byte preamble + DICM prefix"),
        ("File Meta Information", "Media Storage SOP Class UID\nTransfer Syntax UID\nImplementation UID"),
        ("Patient Module", "Name, ID, DOB, Sex, Address"),
        ("Study Module", "Study Description\nAccession Number\nStudy Date/Time"),
        ("Series Module", "Series Description\nModality (SM)"),
        ("Equipment Module", "Manufacturer\nScanner Model\nSoftware Version"),
        ("Specimen Module", "Specimen ID\nPreparation\nStaining Method"),
        ("Whole Slide Microscopy Module", "Optical Path\nVolume Dimensions\nTotal Pixel Matrix"),
        ("Image Pixel Module", "Photometric Interpretation\nSamples Per Pixel\nBits Allocated"),
        ("Image Data", "Pixel Data Element (7FE0,0010)\nMulti-resolution pyramid\nImage frames"),
        ("Annotations", "Graphic Type\nGraphic Data\nText Value"),
        ("Pathology Extensions", "Scanner Details\nScan Parameters\nQuality Metrics")
    ]
    
    # Increase spacing between boxes to avoid overlapping text
    y_positions = np.linspace(0.97, 0.03, len(file_structure))
    box_height = 0.06  # Increased from 0.05
    
    for (title, details), y_pos in zip(file_structure, y_positions):
        # Draw box
        rect = plt.Rectangle((0.1, y_pos-box_height/2), 0.8, box_height, 
                            facecolor='lightsteelblue', edgecolor='navy', alpha=0.7)
        structure_ax.add_patch(rect)
        
        # Add text with better spacing
        structure_ax.text(0.5, y_pos+0.005, title, ha='center', fontsize=12, fontweight='bold')
        structure_ax.text(0.5, y_pos-0.025, details, ha='center', fontsize=9, 
                         va='top', wrap=True)
    
    structure_ax.set_title("DICOM File Structure (Monolithic)", fontsize=18, pad=15)
    
    # 2. Sample Image (center top)
    img_ax = fig.add_subplot(grid[0:4, 3:7])
    img_ax.imshow(sample_image)
    img_ax.axis('off')
    img_ax.set_title("WSI Image Data", fontsize=18, pad=15)
    
    # 3. Annotations Visual (center middle)
    annot_ax = fig.add_subplot(grid[4:8, 3:7])
    # Create a zoomed version of the annotations
    roi_img = sample_image.crop((180, 180, 420, 370))
    annot_ax.imshow(roi_img)
    annot_ax.axis('off')
    annot_ax.set_title("Region of Interest (Annotation)", fontsize=18, pad=15)
    
    # 4. Metadata Example (center-right column)
    meta_ax = fig.add_subplot(grid[0:8, 7:10])
    meta_ax.axis('off')
    
    # Show selected metadata fields
    meta_items = [
        ("Patient Information", [
            f"Name: {metadata['PatientModule']['PatientName']}",
            f"ID: {metadata['PatientModule']['PatientID']}",
            f"DOB: {metadata['PatientModule']['PatientBirthDate']}",
            f"Sex: {metadata['PatientModule']['PatientSex']}"
        ]),
        ("Study Information", [
            f"Accession #: {metadata['GeneralStudyModule']['AccessionNumber']}",
            f"Study Date: {metadata['GeneralStudyModule']['StudyDate']}",
            f"Description: {metadata['GeneralStudyModule']['StudyDescription']}"
        ]),
        ("Specimen Information", [
            f"ID: {metadata['SpecimenModule']['SpecimenDescriptionSequence'][0]['SpecimenIdentifier']}",
            f"Description: {metadata['SpecimenModule']['SpecimenDescriptionSequence'][0]['SpecimenShortDescription']}",
            f"Preparation: {metadata['SpecimenModule']['SpecimenDescriptionSequence'][0]['SpecimenPreparationSequence'][0]['PreparationType']}",
            f"Stain: {metadata['SpecimenModule']['SpecimenDescriptionSequence'][0]['SpecimenPreparationSequence'][0]['StainingMethod']}"
        ]),
        ("WSI Information", [
            f"Scanner: {metadata['PathologyExtensions']['ScannerManufacturer']} {metadata['PathologyExtensions']['ScannerModelName']}",
            f"Magnification: {metadata['PathologyExtensions']['MagnificationFactor']}",
            f"Pixel Spacing: {metadata['PathologyExtensions']['PixelSpacing']} µm",
            f"Width: {metadata['ImagePixelModule']['Columns']} pixels",
            f"Height: {metadata['ImagePixelModule']['Rows']} pixels"
        ]),
        ("Technical Information", [
            f"SOP Class: Whole Slide Microscopy Image Storage",
            f"Transfer Syntax: Explicit VR Little Endian",
            f"Photometric Interpretation: {metadata['ImagePixelModule']['PhotometricInterpretation']}",
            f"Bits Allocated: {metadata['ImagePixelModule']['BitsAllocated']}"
        ])
    ]
    
    # Create a light box background for metadata
    meta_bg = plt.Rectangle((0.02, 0.02), 0.96, 0.96, facecolor='#f8f8f8', 
                           edgecolor='#cccccc', alpha=0.8, transform=meta_ax.transAxes)
    meta_ax.add_patch(meta_bg)
    
    text_y = 0.95
    for category, items in meta_items:
        meta_ax.text(0.05, text_y, category, fontsize=15, fontweight='bold')
        text_y -= 0.04  # Increased spacing
        
        for item in items:
            meta_ax.text(0.1, text_y, item, fontsize=12)
            text_y -= 0.03  # Increased spacing
        
        text_y -= 0.04  # More space between categories
    
    meta_ax.set_title("DICOM Metadata (Selected Fields)", fontsize=18, pad=15)
    
    # 5. Add a comparison with modular approach (right column)
    comparison_ax = fig.add_subplot(grid[0:8, 10:12])
    comparison_ax.axis('off')
    comparison_ax.set_title("Modular Approach Comparison", fontsize=18, pad=15)
    
    # Background for the comparison section
    comp_bg = plt.Rectangle((0.02, 0.02), 0.96, 0.96, facecolor='#eaf4f4', 
                           edgecolor='#2c7873', alpha=0.8, transform=comparison_ax.transAxes)
    comparison_ax.add_patch(comp_bg)
    
    # Add comparison text
    comparison_text = (
        "In contrast, a modular approach would:\n\n"
        "• Separate components into specialized files\n"
        "  - OME-TIFF for image data\n"
        "  - FHIR for patient/clinical metadata\n"
        "  - GeoJSON for annotations\n\n"
        "• Enable independent security mechanisms\n"
        "  - Different access controls per component\n"
        "  - Role-based permissions\n\n"
        "• Facilitate immutability\n"
        "  - Base image data remains unchanged\n"
        "  - Annotations stored separately\n\n"
        "• Allow cryptographic signatures\n"
        "  - Easily signed immutable components\n"
        "  - Verifiable data integrity\n\n"
        "• Support distributed storage\n"
        "  - Scalable cloud architecture\n"
        "  - Flexible database approaches"
    )
    
    comparison_ax.text(0.05, 0.95, comparison_text, fontsize=12, 
                      va='top', linespacing=1.3, transform=comparison_ax.transAxes)
    
    # 6. Add security and immutability comparison table (bottom section)
    security_ax = fig.add_subplot(grid[8:11, 2:10])
    security_ax.axis('off')
    security_ax.set_title("Security & Immutability Comparison", fontsize=18, pad=15)
    
    # Create table data
    table_data = [
        ["Feature", "DICOM (Monolithic)", "Modular Approach"],
        ["Data Modifications", "All components change together", "Components evolve independently"],
        ["Annotation Updates", "Requires modifying entire file", "Updates only annotation files"],
        ["Access Control", "All-or-nothing file access", "Granular component-level access"],
        ["Cryptographic Signing", "Challenging (file changes frequently)", "Simple (immutable components)"],
        ["PHI Protection", "PHI embedded within file", "PHI separated from image data"],
        ["Audit Trail", "Complex to implement", "Native versioning of components"]
    ]
    
    # Create a colored table
    table = security_ax.table(
        cellText=table_data,
        loc='center',
        cellLoc='center',
        colWidths=[0.2, 0.35, 0.35]
    )
    
    # Customize table appearance
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    
    # Set header row
    for j in range(3):
        table[0, j].set_facecolor('#4472c4')
        table[0, j].set_text_props(color='white', fontweight='bold')
    
    # Set row colors
    for i in range(1, len(table_data)):
        table[i, 0].set_facecolor('#d9e1f2')
        table[i, 1].set_facecolor('#e9ecf5')
        table[i, 2].set_facecolor('#c6e0b4')  # Green for modular approach
    
    # Adjust cell heights
    for i in range(len(table_data)):
        for j in range(3):
            table[i, j].set_height(0.12)
    
    # Draw a border around the whole figure
    border_ax = fig.add_axes([0, 0, 1, 1])
    border_ax.patch.set_alpha(0)
    border_ax.spines['top'].set_color('navy')
    border_ax.spines['right'].set_color('navy')
    border_ax.spines['bottom'].set_color('navy')
    border_ax.spines['left'].set_color('navy')
    border_ax.spines['top'].set_linewidth(2)
    border_ax.spines['right'].set_linewidth(2)
    border_ax.spines['bottom'].set_linewidth(2)
    border_ax.spines['left'].set_linewidth(2)
    border_ax.set_xticks([])
    border_ax.set_yticks([])
    
    # Add explanatory note at the bottom
    plt.figtext(0.5, 0.015, 
               "Note: This visualization compares DICOM's monolithic file format with a modular approach to digital pathology data management.\n"
               "The monolithic approach bundles all components in a single file, while the modular approach separates concerns, enhancing flexibility, security, and immutability.",
               fontsize=14, ha='center', bbox=dict(facecolor='lightyellow', alpha=0.6, boxstyle='round,pad=0.5'))
    
    # Adjust layout and save - Using more conservative tight_layout settings to avoid warnings
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.04, right=0.96, hspace=0.3, wspace=0.3)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Enhanced DICOM visualization diagram saved to: {output_path}")


def main():
    """Main function to parse arguments and generate DICOM visualization."""
    parser = argparse.ArgumentParser(description='Generate a sample DICOM visualization for digital pathology')
    parser.add_argument('--output', '-o', default=None, help='Output directory for the generated files')
    
    args = parser.parse_args()
    
    # Default to project structure if path not provided
    if args.output is None:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        output_dir = project_root / 'examples'
    else:
        output_dir = Path(args.output)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the sample data
    print("Generating fake patient data...")
    patient_info = create_fake_patient()
    
    print("Generating sample WSI...")
    sample_image = create_sample_image()
    
    print("Generating DICOM metadata structure...")
    dicom_metadata = generate_dicom_metadata(patient_info)
    
    # Save the outputs
    # 1. Save the DICOM metadata as JSON
    json_path = output_dir / 'sample_dicom_metadata.json'
    with open(json_path, 'w') as f:
        json.dump(dicom_metadata, f, indent=2)
    print(f"DICOM metadata saved to: {json_path}")
    
    # 2. Save the sample image
    image_path = output_dir / 'sample_wsi_image.png'
    sample_image.save(image_path)
    print(f"Sample WSI image saved to: {image_path}")
    
    # 3. Create and save the visualization
    vis_path = output_dir / 'dicom_wsi_structure.png'
    create_visualization(dicom_metadata, sample_image, vis_path)
    
    print("\nSuccessfully created:")
    print(f"1. DICOM metadata JSON: {json_path}")
    print(f"2. Sample WSI image: {image_path}")
    print(f"3. DICOM structure visualization: {vis_path}")
    print("\nThese files demonstrate the traditional DICOM approach to storing pathology data.")
    print("The visualization shows how patient information, metadata, images, and annotations")
    print("are all contained within a single monolithic DICOM file format.")


if __name__ == "__main__":
    main()
