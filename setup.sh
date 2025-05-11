#!/bin/bash
# Setup script for beyond-dicom-supplement project
# This script activates the virtual environment and installs required packages

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up the beyond-dicom-supplement environment...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}Installing required packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Setup complete!${NC}"
echo -e "To activate the virtual environment in the future, run: ${YELLOW}source venv/bin/activate${NC}"
echo -e "To run a utility script, make sure the virtual environment is activated, then run: ${YELLOW}python utilities/script_name.py${NC}"
