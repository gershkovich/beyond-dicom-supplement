# Design Choices

This document outlines the justification behind key architecture, format, and standard choices proposed in "Wearing a Fur Coat in the Summertime: Should Digital Pathology Redefine Medical Imaging?"

## Modular Approach vs. Monolithic DICOM

The paper proposes a modular approach to digital pathology data rather than extending the monolithic DICOM standard. Key reasoning includes:

- **Separation of Concerns**: Allowing different aspects (image data, annotations, metadata) to evolve independently
- **Standard Reuse**: Leveraging existing standards (FHIR, GeoJSON, etc.) rather than creating pathology-specific extensions
- **Interoperability**: Easier integration with modern cloud-native and web technologies
- **Reduced Complexity**: More accessible developer experience compared to full DICOM implementation

## Format Choices

### OME-TIFF for Base Image Data

- Industry adoption in microscopy
- Support for multi-resolution pyramid storage
- Open specification

### FHIR for Clinical Metadata

- Modern REST API design
- JSON-based for web compatibility
- Healthcare-specific semantics
- Growing adoption across healthcare IT

### GeoJSON/SVG for Annotations

- Web-native formats
- Broad tool support
- Simpler than DICOM SR for many annotation needs

## Standards Evolution Strategy

This document will evolve to include:

- Updates based on community feedback
- New standards as they emerge
- Implementation experiences from early adopters
