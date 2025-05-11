# Beyond DICOM Supplement

## Project Title and Purpose

This repository serves as a **structured, modular, interactive supplement** to the academic paper "Wearing a Fur Coat in the Summertime: Should Digital Pathology Redefine Medical Imaging?". It aims to promote transparency, facilitate community feedback, provide reusable examples, and encourage further research in the field of digital pathology imaging standards.

## Link to the Paper

[Paper DOI: (Add paper DOI when published)] <!-- Replace with actual DOI when available -->

## Repository Goals

This repository is guided by the following principles:

- **Modularity**: Separating concerns in digital pathology data handling
- **Standards Adoption**: Leveraging existing standards rather than creating pathology-specific extensions
- **Transparency**: Making design choices explicit and open to discussion
- **Reusability**: Providing examples and utilities that others can adapt for their work

## Directory Guide

- **figures/**: Contains all visual materials used in the paper, provided in both high-resolution and editable formats (SVG, PDF)
- **tables/**: Houses machine-readable data tables (.csv and .md) referenced in the paper
- **examples/**: Includes sample files (FHIR JSON, GeoJSON, modular annotation formats, OME-TIFF metadata snippets) that demonstrate the concepts discussed
- **utilities/**: Contains Python scripts used to generate visualizations, tables, and preprocess data
- **data/**: Provides sample data files with de-identified, artificial, or simulated content for demonstration purposes
- **discussion/**: Serves as a narrative workspace with Markdown files covering design choices, community questions, and future directions
- **references/**: Includes bibliographic information in structured formats (BibTeX, CSL-JSON, or Markdown) with DOIs where available
- **.github/workflows/**: Houses optional CI configurations for testing and validation

## Using the Utilities

The Python utilities in this repository can be used to generate figures, format tables, and create example files. To use these utilities:

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the desired script: `python utilities/script_name.py`

Specific usage instructions are documented within each script.

## Discussion Participation

We welcome community engagement with the ideas presented in this repository:

- Use the GitHub **Issues** tab to ask questions or suggest improvements
- Review and comment on documents in the `discussion/` directory
- Submit pull requests with additional examples or improvements to utilities
- Participate in GitHub Discussions (if enabled)

## Citing This Repository

If you use materials from this repository in your research, please cite it as follows:

```bibtex
Gershkovich, P. et al. (2023). Beyond DICOM Supplement: Wearing a Fur Coat in the Summertime. GitHub Repository: https://github.com/[username]/beyond-dicom-supplement
```

If a Zenodo DOI is available (for archived releases), please cite that instead.

## Licensing

- Code in this repository is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
- Images, diagrams, and other content are licensed under CC BY 4.0 unless otherwise noted

## Contributing

We welcome contributions that improve the examples, fix errors, or add valuable discussion points:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your contributions align with the goals and scope of the supplement.

## Contact

For scholarly discussion, collaboration opportunities, or other inquiries related to this work, please contact: [Your Email or Contact Information] <!-- Replace with actual contact -->
