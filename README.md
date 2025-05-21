# Beyond DICOM Supplement

## Project Title and Purpose

This repository serves as a **structured, modular, interactive supplement** to the academic paper "Wearing a Fur Coat in the Summertime: Should Digital Pathology Redefine Medical Imaging?". It aims to promote transparency, facilitate community feedback, provide reusable examples, and encourage further research in the field of digital pathology imaging standards.

## Link to the Paper

[Wearing a Fur Coat in the Summertime: Should Digital Pathology Redefine Medical Imaging?](https://www.sciencedirect.com/science/article/pii/S2153353925000355?via%3Dihub#:~:text=https%3A//doi.org/10.1016/j.jpi.2025.100450)

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

## Key Resources from the Paper

### Figures

- [DICOM Architecture Diagram](figures/dicom_diagram.svg) - Visual representation of DICOM architecture and its limitations for pathology imaging
- [DICOM Architecture (No Legend)](figures/dicom_no-legend.svg) - Clean version of the architecture diagram without legends
- [Breach Reports Pie Chart](figures/chart_2022-05_to_2025-05.png) - OCR - reported healthcare provider data breaches by location and impact in the past three years.

### Tables

- [DICOM Conformance Statements Analysis](tables/conformance_statements.md) - Comparison of vendor conformance statements and their capabilities

## Interactive Visualizations

Explore our interactive data visualizations that highlight key findings from our paper:

- [Healthcare Data Breach Trends by System Location (2015-2025)](https://gershkovich.github.io/beyond-dicom-supplement/interactive-viz/) - Explore trends in healthcare data breaches across different system locations.

## Using the Utilities

The Python utilities in this repository can be used to generate figures, format tables, and create example files. To use these utilities:

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the desired script: `python utilities/script_name.py`

Specific usage instructions are documented within each script.

### Risk Heat Map Visualization

The repository includes a risk heat map visualization tool that generates a heat map showing the likelihood and impact of various risks related to DICOM in pathology. This visualization helps in understanding and prioritizing potential risks in digital pathology implementations.

To generate the risk heat map:

```bash
# Make sure your virtual environment is activated and dependencies are installed
source venv/bin/activate
pip install -r requirements.txt

# Run the risk heat map script
python utilities/risk_heat_map.py
```

The script will generate a heat map visualization showing various risks positioned according to their likelihood and impact, with color-coding to indicate overall risk levels.

### Healthcare Breach Visualization

The repository includes a healthcare breach visualization tool that generates a pie chart showing the distribution of data breach locations and their impact on healthcare providers. This visualization illustrates security considerations for modular imaging data management.

#### Data Acquisition

To generate this visualization with the latest data:

1. Visit the U.S. Department of Health & Human Services (HHS) Office for Civil Rights (OCR) Breach Portal: [ocrportal.hhs.gov/ocr/breach/breach_report.jsf](https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf)

2. Apply the following filters using the "Advanced Search" options:
   - **Breach Type**: Select only "Hacking/IT Incident" and "Unauthorized Access/Disclosure"
   - **Covered Entity Type**: Select "Healthcare Provider"
   - **State**: Leave as "All States" for nationwide data

3. Click "Search" to display filtered results

4. Click the "Excel" button at the bottom of the page to download the breach report data

5. Save the downloaded Excel file as `breach_report.xlsx` in the `data/` directory of this repository

#### Generating the Visualization

After placing the data file in the correct location, run:

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run the visualization script
python utilities/quick_viz.py
```

The script will generate a pie chart showing the distribution of breach locations and their impact, saving the output to `figures/healthcare_breach_viz.png`.

**Customization Options:**

The visualization can be customized using command-line arguments:

```bash
# Specify a different input file
python utilities/quick_viz.py -i /path/to/your/data.xlsx

# Specify a different output location
python utilities/quick_viz.py -o /path/to/output.png

# Specify a different Excel sheet name
python utilities/quick_viz.py -s "SheetName"
```

The visualization highlights how different locations of breached information affect healthcare providers, emphasizing the importance of security considerations in healthcare data management and storage.

## Discussion Participation

We welcome community engagement with the ideas presented in this repository:

- Use the GitHub **Issues** tab to ask questions or suggest improvements
- Review and comment on documents in the `discussion/` directory
- Submit pull requests with additional examples or improvements to utilities
- Participate in GitHub Discussions (if enabled)

## Citing This Repository

If you use materials from this repository in your research, please cite it as follows:

```bibtex
Gershkovich, P. et al. (2025). Beyond DICOM Supplement: Wearing a Fur Coat in the Summertime. GitHub Repository: https://github.com/[username]/beyond-dicom-supplement
```
Article:

```bibtex
Gershkovich, P. (2025). Wearing a fur coat in the summertime: Should digital pathology redefine medical imaging? Journal of Pathology Informatics, 100450. https://doi.org/10.1016/j.jpi.2025.100450
```

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

For scholarly discussion, collaboration opportunities, or other inquiries related to this work, please contact: <peter.gershkovich@yale.edu>
