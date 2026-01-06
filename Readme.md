# IDU XML Generator

A Python application that combines chunk generation (based on IDU model filtering) and XML file generation in one click. The app automatically installs missing dependencies.

## Features

- **Automatic Dependency Installation**: Installs required packages automatically if missing
- **Chunk Generation**: Automatically filters device data by IDU models and allowed versions, creating chunks of 25,000 rows each
- **XML Generation**: Converts chunks into properly formatted XML files with manufacturer mapping
- **One-Click Processing**: Upload data and generate all XML files with a single button click
- **Batch Download**: Download all XML files as a ZIP archive or individual files
- **Multiple File Formats**: Supports CSV, XLSX, XLS, and XLSM formats

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

## Installation & Usage

### Quick Start

1. **Install Python 3.8 or higher** (if not already installed)

2. **Run the app:**
   ```bash
   streamlit run main.py
   ```

   The app will automatically:
   - Check for required dependencies
   - Install any missing packages (pandas, openpyxl, xlrd)
   - Launch in your web browser (default: http://localhost:8501)

### Manual Installation (Optional)

If you prefer to install dependencies manually:
```bash
pip install -r requirements.txt
```

## Input Data Format

Your input file (CSV, Excel, or Excel Macro-Enabled) must have these columns:
- **Device Model**: Device model name (e.g., JIDU6601)
- **Serial Number**: Serial number of the device
- **Version**: Firmware version (e.g., R2.0.19)

### Example CSV:
```csv
Device Model,Serial Number,Version
JIDU6601,SN001,R2.0.19
JIDU6601,SN002,R2.0.19
JIDU6401,SN003,R2.0.18
```

## How to Use

1. **Upload Data**: 
   - Upload a CSV, XLSX, XLS, or XLSM file
   - Or paste CSV data directly in the app

2. **Generate**: 
   - Click "Generate Chunks & XML Files" button
   - The app will:
     - Filter data by device models and allowed versions
     - Create chunks of 25,000 rows per device model
     - Generate XML files for each chunk

3. **Download**: 
   - Download individual XML files
   - Or download all files as a ZIP archive

## Output Format

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
├── main.py              # Main application (handles everything)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Notes

- Chunks are automatically created when data exceeds 25,000 rows per device model
- Only data matching the allowed versions and device models is processed
- Empty serial numbers are automatically skipped
- The app runs in your web browser (default: http://localhost:8501)
- Dependencies are installed automatically on first run

## Troubleshooting

If you encounter any issues:

1. **Dependencies not installing**: Make sure you have internet connection and pip is working
2. **File upload errors**: Check that your file has the correct columns (Device Model, Serial Number, Version)
3. **Python not found**: Make sure Python 3.8+ is installed and added to your PATH

## Requirements

- Python 3.8 or higher
- Internet connection (for automatic dependency installation)
