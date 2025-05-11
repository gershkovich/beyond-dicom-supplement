#!/usr/bin/env python3
"""
generate_sample_dicom.py - Generate a sample DICOM file for a pathology whole slide image

This script creates a synthetic DICOM file that represents a pathology whole slide image (WSI)
with appropriate metadata, fake patient information, and annotations. It demonstrates the
DICOM approach to storing digital pathology data in a monolithic file format.

Usage:
    python generate_sample_dicom.py [--output OUTPUT_DIR] [--with-pixel-data]

Author: Peter Gershkovich
"""

import os
import sys
import numpy as np
import argparse
import datetime
import random
from pathlib import Path
import warnings
from faker import Faker  # For generating fake patient data
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid, ExplicitVRLittleEndian, ImplicitVRLittleEndian
from pydicom.valuerep import DA, DT, TM
import matplotlib.pyplot as plt
from PIL import Image


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


def create_sample_image(width=1024, height=768, pyramid_levels=3):
    """
    Create a synthetic image to serve as WSI content.
    Creates a pyramid of images at different resolutions.
    """
    # Create base pyramid level (highest resolution)
    # We'll create a simple pattern that looks tissue-like
    base_img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Fill with a beige background
    base_img[:, :] = [220, 200, 180]
    
    # Add some "cellular structures" as random darker spots
    num_cells = 1000
    cell_positions = np.random.randint(0, min(width, height), size=(num_cells, 2))
    cell_sizes = np.random.randint(3, 12, size=num_cells)
    
    # Draw cells
    for (x, y), size in zip(cell_positions, cell_sizes):
        if x < width - size and y < height - size:
            # Random cell color (purplish - like H&E stain)
            cell_color = np.array([
                np.random.randint(100, 180),  # R
                np.random.randint(50, 100),   # G
                np.random.randint(150, 220)   # B
            ])
            
            # Draw a circular cell
            for i in range(-size, size+1):
                for j in range(-size, size+1):
                    if i*i + j*j <= size*size:
                        if 0 <= y+i < height and 0 <= x+j < width:
                            base_img[y+i, x+j] = cell_color
    
    # Add some darker "tissue structures"
    num_structures = 5
    for _ in range(num_structures):
        struct_x = np.random.randint(50, width-100)
        struct_y = np.random.randint(50, height-100)
        struct_w = np.random.randint(100, 200)
        struct_h = np.random.randint(100, 200)
        
        # Draw tissue structure (browner)
        base_img[struct_y:struct_y+struct_h, struct_x:struct_x+struct_w] = [
            np.random.randint(160, 200),  # R
            np.random.randint(140, 160),  # G
            np.random.randint(100, 130)   # B
        ]
    
    # Create image pyramid
    pyramid = [base_img]
    current_img = base_img
    
    for _ in range(1, pyramid_levels):
        # Downsample by 2
        h, w = current_img.shape[:2]
        smaller_img = np.zeros((h//2, w//2, 3), dtype=np.uint8)
        
        for i in range(h//2):
            for j in range(w//2):
                smaller_img[i, j] = current_img[i*2, j*2]
        
        pyramid.append(smaller_img)
        current_img = smaller_img
    
    return pyramid


def create_annotation_sequence():
    """
    Create a DICOM sequence containing annotations for the WSI.
    This demonstrates how annotations are stored within DICOM.
    """
    # Create a simple annotation - a rectangle marking a region of interest
    annotation_seq = Sequence()
    
    # Basic annotation dataset
    annotation = Dataset()
    annotation.GraphicType = "POLYLINE"
    annotation.GraphicData = [100, 100, 300, 100, 300, 300, 100, 300, 100, 100]  # Rectangle coordinates
    annotation.GraphicFilled = "Y"
    annotation.TextValue = "Region of Interest"
    
    # Create a second annotation
    annotation2 = Dataset()
    annotation2.GraphicType = "CIRCLE"
    annotation2.GraphicData = [500, 400, 40]  # Circle center and radius
    annotation2.GraphicFilled = "N"
    annotation2.TextValue = "Suspicious Area"
    
    annotation_seq.append(annotation)
    annotation_seq.append(annotation2)
    
    return annotation_seq


def create_pathology_metadata():
    """
    Create pathology-specific metadata attributes.
    These would typically be stored in specialized DICOM modules.
    """
    specimen = Dataset()
    
    # Specimen Collection module attributes
    specimen.ContainerIdentifier = "CONTAINER-12345"
    specimen.SpecimenIdentifier = "SPECIMEN-67890"
    specimen.SpecimenUID = generate_uid()
    specimen.SpecimenShortDescription = "Liver biopsy"
    specimen.SpecimenDetailedDescription = "Liver biopsy from segment 7"
    
    # Specimen Preparation module attributes
    preparation_steps = Sequence()
    
    fixation_step = Dataset()
    fixation_step.SpecimenPreparationStepContentItemSequence = Sequence()
    fixation_item = Dataset()
    fixation_item.ValueType = "TEXT"
    fixation_item.ConceptNameCodeSequence = Sequence()
    fixation_code = Dataset()
    fixation_code.CodeValue = "111701"
    fixation_code.CodingSchemeDesignator = "DCM"
    fixation_code.CodeMeaning = "Processing type"
    fixation_item.ConceptNameCodeSequence.append(fixation_code)
    fixation_item.TextValue = "FORMALIN FIXED PARAFFIN EMBEDDED"
    fixation_step.SpecimenPreparationStepContentItemSequence.append(fixation_item)
    
    staining_step = Dataset()
    staining_step.SpecimenPreparationStepContentItemSequence = Sequence()
    staining_item = Dataset()
    staining_item.ValueType = "TEXT"
    staining_item.ConceptNameCodeSequence = Sequence()
    staining_code = Dataset()
    staining_code.CodeValue = "111702"
    staining_code.CodingSchemeDesignator = "DCM"
    staining_code.CodeMeaning = "Staining"
    staining_item.ConceptNameCodeSequence.append(staining_code)
    staining_item.TextValue = "H&E"
    staining_step.SpecimenPreparationStepContentItemSequence.append(staining_item)
    
    preparation_steps.append(fixation_step)
    preparation_steps.append(staining_step)
    
    specimen.SpecimenPreparationSequence = preparation_steps
    
    return specimen


def create_custom_pathology_tags():
    """
    Create custom pathology-specific DICOM tags.
    These might be vendor-specific or institution-specific extensions.
    """
    custom_tags = Dataset()
    
    # These tags are for demonstration purposes only - custom tags would have proper DICOM tags
    # In a real DICOM file, these would use private tags in the proper format
    
    # Example of custom data that might be added by a pathology system
    custom_tags.ScannerManufacturer = "ACME Digital Pathology"
    custom_tags.ScannerModelName = "ACME WSI Scanner 3000"
    custom_tags.ScannerSerialNumber = "WSI30000123"
    custom_tags.ScanDate = datetime.datetime.now().strftime('%Y%m%d')
    custom_tags.ScanTime = datetime.datetime.now().strftime('%H%M%S')
    custom_tags.MagnificationFactor = "40x"
    custom_tags.LensNumericalAperture = "0.95"
    custom_tags.PixelSpacing = "0.25"  # Microns per pixel
    
    # Example of slide quality metrics
    custom_tags.FocusQualityScore = "0.92"  # Example metric
    custom_tags.StainQualityScore = "0.88"  # Example metric
    custom_tags.TissueDetectedPercentage = "76.4"  # Example metric
    
    # Example of a custom annotation format (simplified)
    custom_tags.NumberOfAnnotations = "2"
    custom_tags.AnnotationFormat = "DICOM"
    
    return custom_tags


def create_dicom_file(output_path, with_pixel_data=True):
    """
    Create a complete DICOM file with all necessary elements:
    - File Meta
    - Patient Information
    - Study/Series Information
    - Whole Slide Image data (if with_pixel_data is True)
    - Annotations
    - Pathology-specific metadata
    - Custom tags
    """
    # Generate fake patient data
    patient_info = create_fake_patient()
    
    # Create a unique SOP Instance UID
    sop_instance_uid = generate_uid()
    
    # Create a unique Series Instance UID
    series_instance_uid = generate_uid()
    
    # Create a unique Study Instance UID
    study_instance_uid = generate_uid()
    
    # Generate current date and time for various timestamps
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    current_time = datetime.datetime.now().strftime('%H%M%S')
    
    # Create a synthetic image if pixel data is requested
    image_pyramid = None
    if with_pixel_data:
        image_pyramid = create_sample_image()
    
    # Create file meta information
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.77.1.6"  # VL Whole Slide Microscopy Image Storage
    file_meta.MediaStorageSOPInstanceUID = sop_instance_uid
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.ImplementationVersionName = "DICOM-WSI-DEMO"
    
    # Create the FileDataset instance
    # Create an empty dataset first to avoid is_original_encoding issue
    ds = Dataset()
    # Add the file meta information
    ds.file_meta = file_meta
    # Set the preamble
    ds.preamble = b"\0" * 128
    # Set transfer syntax for writing
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    # Add the standard DICOM data elements
    
    # Patient Module attributes
    ds.PatientName = patient_info['name']
    ds.PatientID = patient_info['mrn']
    ds.PatientBirthDate = patient_info['dob']
    ds.PatientSex = patient_info['gender']
    ds.PatientAddress = patient_info['address']
    
    # Patient Clinical Trial Module attributes (optional)
    # This is just for demonstration purposes
    ds.ClinicalTrialSponsorName = "ACME Research"
    ds.ClinicalTrialProtocolID = "PATHOLOGY-2023-001"
    ds.ClinicalTrialProtocolName = "Advanced Digital Pathology Workflow Study"
    
    # General Study Module attributes
    ds.StudyInstanceUID = study_instance_uid
    ds.StudyDate = current_date
    ds.StudyTime = current_time
    ds.ReferringPhysicianName = "Smith^John"
    ds.StudyID = f"STUDY-{random.randint(1000, 9999)}"
    ds.AccessionNumber = patient_info['accession_number']
    ds.StudyDescription = "Liver biopsy, suspected carcinoma"
    
    # Patient Study Module attributes
    ds.AdmittingDiagnosesDescription = "Suspected hepatocellular carcinoma"
    
    # General Series Module attributes
    ds.Modality = "SM"  # Slide Microscopy
    ds.SeriesInstanceUID = series_instance_uid
    ds.SeriesNumber = "1"
    ds.SeriesDescription = "H&E stained slide"
    
    # Frame of Reference Module attributes
    ds.FrameOfReferenceUID = generate_uid()
    
    # General Equipment Module attributes
    ds.Manufacturer = "ACME Digital Pathology"
    ds.ManufacturerModelName = "ACME WSI Scanner 3000"
    ds.SoftwareVersions = "1.0"
    
    # General Image Module attributes
    ds.InstanceNumber = "1"
    ds.PatientOrientation = ""
    ds.ContentDate = current_date
    ds.ContentTime = current_time
    ds.ImageType = ["ORIGINAL", "PRIMARY"]
    
    # Image Pixel Module attributes
    if with_pixel_data:
        base_image = image_pyramid[0]
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"
        ds.PlanarConfiguration = 0  # Color channels stored interleaved
        ds.Rows = base_image.shape[0]
        ds.Columns = base_image.shape[1]
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        
        # The pixel data itself (the base image from our pyramid)
        # In a real WSI, this would be much more complex with multiple frames and tiled storage
        ds.PixelData = base_image.tobytes()
    
    # WSI-specific attributes
    
    # Whole Slide Microscopy Image Module attributes
    ds.ImagedVolumeWidth = 15.0  # mm
    ds.ImagedVolumeHeight = 15.0  # mm
    ds.ImagedVolumeDepth = 0.004  # mm (4 microns)
    ds.TotalPixelMatrixColumns = 40000  # Example size for a WSI
    ds.TotalPixelMatrixRows = 30000
    
    # Optical Path Module attributes
    optical_path_seq = Sequence()
    optical_path = Dataset()
    optical_path.OpticalPathIdentifier = "1"
    optical_path.OpticalPathDescription = "Brightfield illumination"
    optical_path.IlluminationTypeCodeSequence = Sequence()
    illumination_type = Dataset()
    illumination_type.CodeValue = "111741"
    illumination_type.CodingSchemeDesignator = "DCM"
    illumination_type.CodeMeaning = "Brightfield illumination"
    optical_path.IlluminationTypeCodeSequence.append(illumination_type)
    
    # Add some stain information
    optical_path.ICC_Profile = b''  # Would contain actual ICC profile in real WSI
    optical_path.LuminanceOfSingleReferencePercent = 70.0  # Example value
    optical_path_seq.append(optical_path)
    ds.OpticalPathSequence = optical_path_seq
    
    # Add annotations
    ds.GraphicAnnotationSequence = create_annotation_sequence()
    
    # Add pathology-specific metadata
    specimen_data = create_pathology_metadata()
    ds.SpecimenDescriptionSequence = Sequence([specimen_data])
    
    # Add custom tags
    custom_data = create_custom_pathology_tags()
    for attr in dir(custom_data):
        if not attr.startswith('_') and attr not in ['is_implicit_VR', 'is_little_endian', 'values']:
            setattr(ds, attr, getattr(custom_data, attr))
    
    # Set the specific character set for encoding extended characters
    ds.SpecificCharacterSet = 'ISO_IR 192'  # UTF-8
    
    # SOP Common Module attributes
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    
    # Save the DICOM file with proper method
    # Convert any non-standard attributes to private tags to avoid warnings
    # This would typically be done with proper private tags in a real DICOM implementation
    from pydicom.datadict import add_private_dict_entry
    from pydicom._private_dict import private_dictionaries
    
    try:
        # Save to file by writing binary data directly
        with open(output_path, 'wb') as f:
            pydicom.filewriter.write_file(f, ds)
        print(f"DICOM file saved to: {output_path}")
    except Exception as e:
        print(f"Error saving DICOM file: {str(e)}")
        # Try alternative saving method
        try:
            ds.save_as(output_path)
            print(f"DICOM file saved using alternative method to: {output_path}")
        except Exception as e2:
            raise Exception(f"Failed to save DICOM file: {str(e2)}")
    
    return ds


def create_sample_dicom_thumbnail(dicom_path, output_path):
    """
    Create a thumbnail visualization of the generated DICOM file
    to provide a quick preview of its contents.
    """
    # Load the DICOM file
    ds = pydicom.dcmread(dicom_path)
    
    # Create a figure with multiple subplots to show different aspects
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"Sample Pathology DICOM - {ds.PatientName}", fontsize=16)
    
    # Plot 1: Image data if available
    if hasattr(ds, 'PixelData'):
        try:
            # Extract the image data
            if ds.SamplesPerPixel == 3:
                img_shape = (ds.Rows, ds.Columns, 3)
                img = np.frombuffer(ds.PixelData, dtype=np.uint8).reshape(img_shape)
                axs[0, 0].imshow(img)
            else:
                img_shape = (ds.Rows, ds.Columns)
                img = np.frombuffer(ds.PixelData, dtype=np.uint8).reshape(img_shape)
                axs[0, 0].imshow(img, cmap='gray')
            
            axs[0, 0].set_title("WSI Preview (Synthetic Data)")
            axs[0, 0].axis('off')
        except Exception as e:
            axs[0, 0].text(0.5, 0.5, f"Error displaying image: {str(e)}", 
                         ha='center', va='center', transform=axs[0, 0].transAxes)
            axs[0, 0].axis('off')
    else:
        axs[0, 0].text(0.5, 0.5, "No image data available", 
                      ha='center', va='center', transform=axs[0, 0].transAxes)
        axs[0, 0].axis('off')
    
    # Plot 2: Annotations visualization - use simplified representation
    axs[0, 1].set_title("Annotation Visualization")
    if hasattr(ds, 'GraphicAnnotationSequence'):
        # Create a simplified representation of annotations
        axs[0, 1].set_xlim(0, 500)
        axs[0, 1].set_ylim(0, 500)
        
        # Fill with light background
        axs[0, 1].set_facecolor('#f0f0f0')
        
        # Draw annotations as matplotlib objects
        for ann in ds.GraphicAnnotationSequence:
            if hasattr(ann, 'GraphicType') and ann.GraphicType == "POLYLINE":
                # Draw polyline
                points = np.array(ann.GraphicData).reshape(-1, 2)
                points = points * 500 / 1024  # Scale to our canvas
                
                # Draw as a matplotlib line
                x_points = points[:, 0]
                y_points = points[:, 1]
                axs[0, 1].plot(x_points, y_points, 'r-', linewidth=2)
                
                # Add label if available
                if hasattr(ann, 'TextValue'):
                    text_x = np.mean(x_points)
                    text_y = np.mean(y_points)
                    axs[0, 1].text(text_x, text_y, ann.TextValue, ha='center', 
                                  va='center', bbox=dict(facecolor='white', alpha=0.7))
            
            elif hasattr(ann, 'GraphicType') and ann.GraphicType == "CIRCLE":
                # Draw circle
                data = ann.GraphicData
                # Center and radius, scaled to our canvas
                cx, cy, radius = data[0] * 500 / 1024, data[1] * 500 / 1024, data[2] * 500 / 1024
                
                # Draw as a matplotlib circle
                circle = plt.Circle((cx, cy), radius, fill=False, color='blue', linewidth=2)
                axs[0, 1].add_artist(circle)
                
                # Add label if available
                if hasattr(ann, 'TextValue'):
                    axs[0, 1].text(cx, cy, ann.TextValue, ha='center', 
                                  va='center', bbox=dict(facecolor='white', alpha=0.7))
    else:
        axs[0, 1].text(0.5, 0.5, "No annotations available", 
                      ha='center', va='center', transform=axs[0, 1].transAxes)
    axs[0, 1].axis('off')
    
    # Plot 3: Patient and Study Information
    axs[1, 0].set_title("Patient & Study Information")
    axs[1, 0].axis('off')
    
    info_text = f"""
    Patient Name: {ds.PatientName}
    Patient ID: {ds.PatientID}
    Patient Sex: {ds.PatientSex}
    Patient DOB: {ds.PatientBirthDate}
    
    Accession #: {ds.AccessionNumber}
    Study Date: {ds.StudyDate}
    Study Description: {ds.StudyDescription}
    Modality: {ds.Modality} (Slide Microscopy)
    """
    
    axs[1, 0].text(0.1, 0.9, info_text, ha='left', va='top', 
                 transform=axs[1, 0].transAxes, fontfamily='monospace')
    
    # Plot 4: Specimen and Custom Information
    axs[1, 1].set_title("Specimen & Technical Information")
    axs[1, 1].axis('off')
    
    specimen_text = ""
    if hasattr(ds, 'SpecimenDescriptionSequence'):
        specimen = ds.SpecimenDescriptionSequence[0]
        specimen_text = f"""
        Specimen ID: {specimen.SpecimenIdentifier}
        Description: {specimen.SpecimenShortDescription}
        Container: {specimen.ContainerIdentifier}
        """
    
    custom_text = f"""
    Scanner: {ds.ScannerManufacturer} {ds.ScannerModelName}
    Scan Date: {ds.ScanDate}
    Magnification: {ds.MagnificationFactor}
    Pixel Spacing: {ds.PixelSpacing} µm
    Focus Quality: {ds.FocusQualityScore}
    Stain Quality: {ds.StainQualityScore}
    """
    
    full_text = specimen_text + "\n" + custom_text
    axs[1, 1].text(0.1, 0.9, full_text, ha='left', va='top', 
                 transform=axs[1, 1].transAxes, fontfamily='monospace')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"DICOM visualization saved to: {output_path}")


# No longer need the line function since we're using matplotlib for drawing


def main():
    """Main function to parse arguments and generate DICOM files."""
    parser = argparse.ArgumentParser(description='Generate a sample DICOM file for a pathology whole slide image')
    parser.add_argument('--output', '-o', default=None, help='Output directory for the generated DICOM file')
    parser.add_argument('--with-pixel-data', '-p', action='store_true', help='Include pixel data in the DICOM file')
    
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
    
    # Create DICOM file output path
    dicom_path = output_dir / 'sample_pathology_wsi.dcm'
    
    # Create a visualization output path
    visualization_path = output_dir / 'sample_pathology_wsi_preview.png'
    
    # Generate the DICOM file
    try:
        create_dicom_file(str(dicom_path), with_pixel_data=args.with_pixel_data)
        
        # Generate a visualization
        create_sample_dicom_thumbnail(str(dicom_path), str(visualization_path))
        
        print("\nSuccessfully created:")
        print(f"1. DICOM file: {dicom_path}")
        print(f"2. Preview image: {visualization_path}")
        print("\nThese files demonstrate the traditional DICOM approach to storing pathology data.")
        print("The generated DICOM file contains patient information, specimen data, image data,")
        print("annotations, and custom pathology metadata within a single monolithic file.")
    except Exception as e:
        print(f"Error generating DICOM file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
