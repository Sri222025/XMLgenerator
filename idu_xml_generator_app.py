"""
IDU Device Data Processor & XML Generator
Combines chunk generation (IDU model filtering) and XML generation in one app
"""

import streamlit as st
import pandas as pd
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import zipfile
import tempfile
import shutil
from typing import List, Dict, Tuple

# Check for required dependencies
def check_dependencies():
    """Check if required Excel reading dependencies are installed"""
    missing_deps = []
    
    try:
        import openpyxl
    except ImportError:
        missing_deps.append("openpyxl")
    
    try:
        import xlrd
    except ImportError:
        missing_deps.append("xlrd")
    
    if missing_deps:
        st.error(f"❌ Missing required dependencies: {', '.join(missing_deps)}")
        st.info(f"💡 Please install them by running: `pip install {' '.join(missing_deps)}`")
        st.info("Or install all requirements: `pip install -r requirements_idu_xml.txt`")
        st.stop()
    
    return True

# Page configuration
st.set_page_config(
    page_title="IDU XML Generator",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --danger: #d62728;
        --text: #1e293b;
        --gray: #64748b;
        --border: #e2e8f0;
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
    }
    
    h1 {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.2) !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid var(--border);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CHUNK_SIZE = 25000
ALLOWED_VERSIONS = ["R2.0.18.2", "R2.0.18", "R2.0.19", "R2.0.19.5", "R2.0.16", "R2.0.19.6"]
DEVICE_MODELS = [
    "JIDU6601", "JIDU6611", "JIDU6401", "JIDU6701", "JIDU6801",
    "JIDU6101", "JIDU6111", "JIDU6311", "JIDU6411", "JIDU6811", "JIDU6911"
]

# Manufacturer mapping
MANUFACTURER_MAP = {
    "JIDU6101": "Arcadyan",
    "JIDU6111": "Arcadyan",
    "JIDU6311": "Bluebank",
    "JIDU6401": "Sercomm",
    "JIDU6411": "Sercomm",
    "JIDU6601": "Speedtech",
    "JIDU6611": "Speedtech",
    "JIDU6701": "Skyworth",
    "JIDU6801": "Telpa",
    "JIDU6811": "Telpa",
    "JIDU6911": "Askey"
}

# Initialize session state
if 'chunks_data' not in st.session_state:
    st.session_state.chunks_data = {}
if 'xml_files' not in st.session_state:
    st.session_state.xml_files = {}
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False


def validate_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate that the dataframe has the required columns"""
    required_columns = ['Device Model', 'Serial Number', 'Version']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    return True, "Data validated successfully"


def create_chunks(df: pd.DataFrame, target_model: str, allowed_versions: List[str], chunk_size: int) -> List[pd.DataFrame]:
    """
    Create chunks for a specific device model based on IDU filtering criteria
    
    Args:
        df: Input dataframe with columns: Device Model, Serial Number, Version
        target_model: Device model to filter (e.g., "JIDU6601")
        allowed_versions: List of allowed versions
        chunk_size: Maximum rows per chunk
        
    Returns:
        List of dataframes, each representing a chunk
    """
    # Filter data for this model
    filtered_df = df[
        (df['Device Model'].str.strip() == target_model) &
        (df['Serial Number'].str.strip() != '') &
        (df['Version'].str.strip() != '') &
        (df['Version'].str.strip().isin(allowed_versions))
    ].copy()
    
    if filtered_df.empty:
        return []
    
    # Create chunks
    chunks = []
    num_chunks = (len(filtered_df) + chunk_size - 1) // chunk_size  # Ceiling division
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(filtered_df))
        chunk_df = filtered_df.iloc[start_idx:end_idx].copy()
        chunks.append(chunk_df)
    
    return chunks


def generate_xml_from_chunk(chunk_df: pd.DataFrame, device_model: str, chunk_number: int) -> str:
    """
    Generate XML content from a chunk dataframe
    
    Args:
        chunk_df: Dataframe with Serial Number column
        device_model: Device model name
        chunk_number: Chunk number for filename
        
    Returns:
        XML content as string
    """
    # Get manufacturer
    manufacturer = MANUFACTURER_MAP.get(device_model, "Unknown")
    
    # Create XML root
    root = ET.Element("serials")
    
    # Add serial elements
    for _, row in chunk_df.iterrows():
        serial_number = str(row['Serial Number']).strip()
        if serial_number:
            serial_elem = ET.SubElement(root, "serial")
            serial_elem.set("Model", device_model)
            serial_elem.set("Manufacturer", manufacturer)
            serial_elem.text = serial_number
    
    # Convert to pretty XML string
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Remove the XML declaration line that minidom adds (we'll add our own)
    lines = pretty_xml.split('\n')
    lines = [line for line in lines if line.strip() and not line.strip().startswith('<?xml')]
    pretty_xml = '\n'.join(lines)
    
    # Add proper XML declaration
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
    
    return final_xml


def process_data_to_xml(df: pd.DataFrame) -> Dict[str, List[Tuple[str, str]]]:
    """
    Process data: create chunks and generate XML files
    
    Args:
        df: Input dataframe
        
    Returns:
        Dictionary mapping device_model to list of (filename, xml_content) tuples
    """
    all_xml_files = {}
    
    # Process each device model
    for device_model in DEVICE_MODELS:
        # Create chunks for this model
        chunks = create_chunks(df, device_model, ALLOWED_VERSIONS, CHUNK_SIZE)
        
        if chunks:
            xml_files = []
            for chunk_num, chunk_df in enumerate(chunks, 1):
                # Generate XML
                xml_content = generate_xml_from_chunk(chunk_df, device_model, chunk_num)
                filename = f"{device_model}_Chunk{chunk_num}.xml"
                xml_files.append((filename, xml_content))
            
            all_xml_files[device_model] = xml_files
    
    return all_xml_files


def create_zip_file(xml_files_dict: Dict[str, List[Tuple[str, str]]]) -> str:
    """Create a ZIP file containing all XML files"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "xml_files.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for device_model, files in xml_files_dict.items():
            for filename, xml_content in files:
                zipf.writestr(filename, xml_content)
    
    return zip_path


# Check dependencies at startup
check_dependencies()

# Header
st.title("📦 IDU XML Generator")
st.markdown(
    "<p style='text-align: center; color: var(--gray); font-size: 1.1rem;'>"
    "Generate Chunks & XML Files from Device Data in One Click</p>",
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("📋 Device Models")
    for model in DEVICE_MODELS:
        manufacturer = MANUFACTURER_MAP.get(model, "Unknown")
        st.text(f"{model} → {manufacturer}")
    
    st.divider()
    
    st.subheader("✅ Allowed Versions")
    for version in ALLOWED_VERSIONS:
        st.text(f"• {version}")
    
    st.divider()
    
    st.subheader("📊 Settings")
    st.info(f"**Chunk Size:** {CHUNK_SIZE:,} rows per chunk")
    
    st.divider()
    
    st.info("""
    **How it works:**
    1. Upload CSV/Excel file with columns:
       - Device Model
       - Serial Number
       - Version
    2. Click "Generate Chunks & XML Files"
    3. Download the generated XML files
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["📄 Input Data", "📊 Processing Results", "📥 Download XML Files"])

with tab1:
    st.header("Upload or Paste Data")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload File", "Paste CSV"],
        horizontal=True
    )
    
    df = None
    
    if input_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload a CSV or Excel file",
            type=['csv', 'xlsx', 'xls', 'xlsm'],
            help="File should have columns: Device Model, Serial Number, Version. Supports CSV, XLSX, XLS, and XLSM formats."
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls', '.xlsm')):
                    # Check if openpyxl is needed for .xlsx/.xlsm files
                    if uploaded_file.name.endswith(('.xlsx', '.xlsm')):
                        try:
                            import openpyxl
                        except ImportError:
                            st.error("❌ Missing dependency 'openpyxl'. Please install it: `pip install openpyxl`")
                            st.stop()
                    
                    # Check if xlrd is needed for .xls files
                    if uploaded_file.name.endswith('.xls'):
                        try:
                            import xlrd
                        except ImportError:
                            st.error("❌ Missing dependency 'xlrd'. Please install it: `pip install xlrd`")
                            st.stop()
                    
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File uploaded: {uploaded_file.name} ({len(df)} rows)")
                
                # Show preview
                with st.expander("📄 Preview uploaded data"):
                    st.dataframe(df.head(20), use_container_width=True)
                    st.info(f"Total rows: {len(df)}")
                
            except ImportError as e:
                error_msg = str(e)
                if 'openpyxl' in error_msg:
                    st.error("❌ Missing dependency 'openpyxl'. Please install it: `pip install openpyxl`")
                    st.info("💡 Or install all requirements: `pip install -r requirements_idu_xml.txt`")
                elif 'xlrd' in error_msg:
                    st.error("❌ Missing dependency 'xlrd'. Please install it: `pip install xlrd`")
                    st.info("💡 Or install all requirements: `pip install -r requirements_idu_xml.txt`")
                else:
                    st.error(f"❌ Missing dependency: {error_msg}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                if "openpyxl" in str(e).lower() or "xlrd" in str(e).lower():
                    st.info("💡 Make sure you have installed: `pip install openpyxl xlrd`")
    
    else:  # Paste CSV
        csv_text = st.text_area(
            "Paste CSV data here (include header row):",
            height=300,
            placeholder="Device Model,Serial Number,Version\nJIDU6601,SN123456,R2.0.19\n..."
        )
        
        if csv_text:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(csv_text))
                st.success(f"✅ CSV parsed: {len(df)} rows")
                
                with st.expander("📄 Preview pasted data"):
                    st.dataframe(df.head(20), use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Error parsing CSV: {str(e)}")
    
    # Process button
    if df is not None:
        # Validate data
        is_valid, message = validate_data(df)
        
        if is_valid:
            st.divider()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                process_button = st.button(
                    "🚀 Generate Chunks & XML Files",
                    type="primary",
                    use_container_width=True
                )
            
            if process_button:
                with st.spinner("🔄 Processing data and generating XML files..."):
                    try:
                        # Process data
                        xml_files_dict = process_data_to_xml(df)
                        
                        # Store in session state
                        st.session_state.xml_files = xml_files_dict
                        st.session_state.processing_complete = True
                        
                        # Count total files
                        total_files = sum(len(files) for files in xml_files_dict.values())
                        total_chunks = sum(len(chunks) for chunks in [
                            create_chunks(df, model, ALLOWED_VERSIONS, CHUNK_SIZE)
                            for model in DEVICE_MODELS
                        ])
                        
                        st.success(f"✅ Processing complete! Generated {total_files} XML files from {total_chunks} chunks.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error during processing: {str(e)}")
                        st.exception(e)
        else:
            st.warning(f"⚠️ {message}")

with tab2:
    st.header("📊 Processing Results")
    
    if st.session_state.processing_complete and st.session_state.xml_files:
        xml_files_dict = st.session_state.xml_files
        
        # Summary metrics
        total_files = sum(len(files) for files in xml_files_dict.values())
        total_models = len(xml_files_dict)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Device Models Processed", total_models)
        
        with col2:
            st.metric("Total XML Files Generated", total_files)
        
        with col3:
            total_serial_numbers = sum(
                sum(xml_content.count('<serial') for _, xml_content in files)
                for files in xml_files_dict.values()
            )
            st.metric("Total Serial Numbers", f"{total_serial_numbers:,}")
        
        st.divider()
        
        # Detailed breakdown by device model
        st.subheader("📋 Breakdown by Device Model")
        
        for device_model, files in sorted(xml_files_dict.items()):
            manufacturer = MANUFACTURER_MAP.get(device_model, "Unknown")
            
            with st.expander(f"🔹 {device_model} ({manufacturer}) - {len(files)} XML file(s)"):
                for filename, xml_content in files:
                    # Count serials in this file
                    serial_count = xml_content.count('<serial')
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"📄 {filename}")
                    with col2:
                        st.text(f"{serial_count:,} serials")
                    
                    # Show XML preview
                    with st.expander(f"Preview {filename}"):
                        st.code(xml_content[:1000] + "..." if len(xml_content) > 1000 else xml_content, language='xml')
        
        st.divider()
        
        # Statistics
        st.subheader("📈 Statistics")
        
        stats_data = []
        for device_model, files in xml_files_dict.items():
            total_serials = sum(
                xml_content.count('<serial')
                for _, xml_content in files
            )
            stats_data.append({
                "Device Model": device_model,
                "Manufacturer": MANUFACTURER_MAP.get(device_model, "Unknown"),
                "XML Files": len(files),
                "Total Serials": total_serials
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("👆 Go to the 'Input Data' tab to upload data and generate XML files")

with tab3:
    st.header("📥 Download XML Files")
    
    if st.session_state.processing_complete and st.session_state.xml_files:
        xml_files_dict = st.session_state.xml_files
        
        # Download all as ZIP
        st.subheader("📦 Download All XML Files (ZIP)")
        
        zip_path = create_zip_file(xml_files_dict)
        
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
        
        st.download_button(
            label="⬇️ Download All XML Files (ZIP)",
            data=zip_bytes,
            file_name="xml_files.zip",
            mime="application/zip",
            use_container_width=True
        )
        
        st.divider()
        
        # Download individual files
        st.subheader("📄 Download Individual XML Files")
        
        for device_model, files in sorted(xml_files_dict.items()):
            st.markdown(f"### {device_model} ({MANUFACTURER_MAP.get(device_model, 'Unknown')})")
            
            for filename, xml_content in files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(filename)
                with col2:
                    st.download_button(
                        label="⬇️ Download",
                        data=xml_content,
                        file_name=filename,
                        mime="application/xml",
                        key=f"download_{device_model}_{filename}"
                    )
        
        st.success("✅ All XML files are ready for download!")
    
    else:
        st.info("👆 Generate XML files first to download them")

# Footer
st.divider()
st.markdown(
    "<p style='text-align: center; color: var(--gray); font-size: 0.9rem;'>"
    "IDU Device Data Processor • Chunk Generation • XML Export</p>",
    unsafe_allow_html=True
)

