# IDU XML Generator App

A Python application that combines chunk generation (based on IDU model filtering) and XML file generation in one click.

## Features

- **Chunk Generation**: Automatically filters device data by IDU models and allowed versions, creating chunks of 25,000 rows each
- **XML Generation**: Converts chunks into properly formatted XML files with manufacturer mapping
- **One-Click Processing**: Upload data and generate all XML files with a single button click
- **Batch Download**: Download all XML files as a ZIP archive or individual files

## Supported Device Models

- JIDU6101, JIDU6111 → Arcadyan
- JIDU6311 → Bluebank
- JIDU6401, JIDU6411 → Sercomm
- JIDU6601, JIDU6611 → Speedtech
- JIDU6701 → Skyworth
- JIDU6801, JIDU6811 → Telpa
- JIDU6911 → Askey

## Allowed Versions

- R2.0.18.2
- R2.0.18
- R2.0.19
- R2.0.19.5
- R2.0.16
- R2.0.19.6

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements_idu_xml.txt
   ```

## Usage

### Running the App

**Option 1: Using the batch file (Windows)**
```bash
run_idu_xml_generator.bat
```

**Option 2: Using command line**
```bash
streamlit run idu_xml_generator_app.py
```

### Input Data Format

Your input file (CSV, Excel, or Excel Macro-Enabled) must have these columns:
- **Device Model**: Device model name (e.g., JIDU6601)
- **Serial Number**: Serial number of the device
- **Version**: Firmware version (e.g., R2.0.19)

### Processing Steps

1. **Upload Data**: Upload a CSV, Excel (.xlsx, .xls), or Excel Macro-Enabled (.xlsm) file, or paste CSV data directly
2. **Generate**: Click "Generate Chunks & XML Files" button
3. **Download**: Download individual XML files or all files as a ZIP archive

### Output Format

Each XML file follows this structure:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<serials>
  <serial Model="JIDU6601" Manufacturer="Speedtech">SN123456</serial>
  <serial Model="JIDU6601" Manufacturer="Speedtech">SN789012</serial>
  ...
</serials>
```

## How It Works

1. **Data Filtering**: The app filters data by:
   - Device Model (must match one of the supported JIDU models)
   - Version (must be in the allowed versions list)
   - Serial Number (must not be empty)

2. **Chunk Creation**: For each device model, data is split into chunks of 25,000 rows maximum

3. **XML Generation**: Each chunk is converted to an XML file with:
   - Proper XML structure
   - Device model and manufacturer attributes
   - All serial numbers from the chunk

## File Structure

```
├── idu_xml_generator_app.py      # Main application file
├── requirements_idu_xml.txt      # Python dependencies
├── README_IDU_XML_GENERATOR.md   # This file
└── run_idu_xml_generator.bat     # Windows batch file to run the app
```

## Example

Input CSV:
```csv
Device Model,Serial Number,Version
JIDU6601,SN001,R2.0.19
JIDU6601,SN002,R2.0.19
JIDU6401,SN003,R2.0.18
```

Output: XML files named `JIDU6601_Chunk1.xml`, `JIDU6401_Chunk1.xml`, etc.

## Notes

- Chunks are automatically created when data exceeds 25,000 rows per device model
- Only data matching the allowed versions and device models is processed
- Empty serial numbers are automatically skipped
- The app runs in your web browser (default: http://localhost:8501)

