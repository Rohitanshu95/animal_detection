"""
Excel Upload Page
Upload and process Excel files with wildlife incident data
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import io


# Page config
st.set_page_config(
    page_title="Upload Excel Data",
    page_icon="📤",
    layout="wide"
)

# Backend API URL
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
except:
    API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None
if 'enriched_data' not in st.session_state:
    st.session_state.enriched_data = None
if 'selected_incidents' not in st.session_state:
    st.session_state.selected_incidents = set()
if 'processing_stage' not in st.session_state:
    st.session_state.processing_stage = 'upload'  # upload, review, complete


st.title("📤 Upload Excel Data")
st.markdown("Upload Excel files with wildlife incident reports for automated processing and enrichment.")

# Stage 1: File Upload
if st.session_state.processing_stage == 'upload':
    st.markdown("---")
    st.subheader("Step 1: Upload Excel File")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx, .xls)",
        type=['xlsx', 'xls'],
        help="Upload Excel files with incident data. The system will automatically parse quarterly reports and extract incidents."
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔍 Parse Excel", type="primary", use_container_width=True):
                with st.spinner("Parsing Excel file..."):
                    try:
                        # Read file content
                        file_content = uploaded_file.read()
                        
                        # Send to backend for parsing
                        response = requests.post(
                            f"{API_BASE_URL}/excel/parse",
                            files={"file": ("upload.xlsx", file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.parsed_data = result
                            
                            if result['success']:
                                st.success(f"✅ Parsed {result['incident_count']} incidents from {result['total_rows']} rows")
                                st.session_state.processing_stage = 'review'
                                st.rerun()
                            else:
                                st.error(f"❌ Parsing failed: {', '.join(result.get('errors', []))}")
                        else:
                            st.error(f"❌ Server error: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col2:
            st.info("ℹ️ The parser will:\n- Extract quarterly report headers\n- Parse incident data rows\n- Clean and validate dates\n- Identify data quality issues")


# Stage 2: Review and Enrich
elif st.session_state.processing_stage == 'review':
    st.markdown("---")
    st.subheader("Step 2: Review & Enrich Data")
    
    parsed_data = st.session_state.parsed_data
    incidents = parsed_data.get('incidents', [])
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", len(incidents))
    with col2:
        valid_count = sum(1 for i in incidents if i.get('is_valid', True))
        st.metric("Valid", valid_count)
    with col3:
        invalid_count = len(incidents) - valid_count
        st.metric("Need Review", invalid_count, delta_color="inverse")
    with col4:
        enriched = st.session_state.enriched_data is not None
        st.metric("AI Enriched", "Yes" if enriched else "No")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if not enriched:
            if st.button("✨ Enrich with AI", type="primary", use_container_width=True):
                with st.spinner("Enriching incidents with AI... This may take a moment."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/excel/enrich",
                            json={"incidents": incidents}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.enriched_data = result.get('incidents', [])
                            # Select all by default
                            st.session_state.selected_incidents = set(range(len(st.session_state.enriched_data)))
                            st.success("✅ Data enriched successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Enrichment failed: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("🔄 Back to Upload", use_container_width=True):
            st.session_state.processing_stage = 'upload'
            st.session_state.parsed_data = None
            st.session_state.enriched_data = None
            st.session_state.selected_incidents = set()
            st.rerun()
    
    with col3:
        if enriched and len(st.session_state.selected_incidents) > 0:
            if st.button(f"📤 Upload {len(st.session_state.selected_incidents)} Selected", type="primary", use_container_width=True):
                with st.spinner("Uploading to database..."):
                    try:
                        # Get selected incidents
                        selected = [st.session_state.enriched_data[i] for i in st.session_state.selected_incidents]
                        
                        # Format for backend API
                        formatted_incidents = []
                        for inc in selected:
                            formatted_incidents.append({
                                "date": inc.get('date', ''),
                                "location": inc.get('location', ''),
                                "animals": inc.get('animals', ''),
                                "quantity": inc.get('quantity'),
                                "description": inc.get('description', ''),
                                "source": inc.get('source', ''),
                                "status": inc.get('status', 'Reported'),
                                "suspects": inc.get('suspects'),
                                "vehicle_info": inc.get('vehicle_info'),
                                "estimated_value": inc.get('estimated_value'),
                                "notes": f"Q{inc.get('quarter_number', '')} - {inc.get('quarter_date_range', '')}"
                            })
                        
                        response = requests.post(
                            f"{API_BASE_URL}/incidents/bulk-upload",
                            json=formatted_incidents
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.upload_result = result
                            st.session_state.processing_stage = 'complete'
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # Display incidents
    st.markdown("---")
    st.subheader("Incident Review")
    
    # Use enriched data if available, otherwise parsed data
    display_data = st.session_state.enriched_data if enriched else incidents
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        show_only_issues = st.checkbox("Show only incidents with issues", value=False)
    with col2:
        if enriched:
            select_all = st.checkbox("Select All", value=len(st.session_state.selected_incidents) == len(display_data))
            if select_all:
                st.session_state.selected_incidents = set(range(len(display_data)))
            elif not select_all and len(st.session_state.selected_incidents) == len(display_data):
                st.session_state.selected_incidents = set()
    
    # Display each incident
    for idx, incident in enumerate(display_data):
        has_issues = len(incident.get('validation_issues', [])) > 0
        
        if show_only_issues and not has_issues:
            continue
        
        with st.expander(f"Incident {idx + 1}: {incident.get('description', '')[:80]}..." + 
                        (" ⚠️" if has_issues else " ✅")):
            
            # Selection checkbox (if enriched)
            if enriched:
                selected = st.checkbox(
                    "Include in upload",
                    value=idx in st.session_state.selected_incidents,
                    key=f"select_{idx}"
                )
                if selected:
                    st.session_state.selected_incidents.add(idx)
                else:
                    st.session_state.selected_incidents.discard(idx)
            
            # Display data in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Data:**")
                st.text(f"Date: {incident.get('raw_date', incident.get('date', 'N/A'))}")
                st.text(f"Location: {incident.get('location', 'N/A')}")
                st.text(f"Quarter: Q{incident.get('quarter_number', 'N/A')} ({incident.get('quarter_date_range', 'N/A')})")
                st.text_area("Description:", incident.get('description', ''), height=100, key=f"desc_orig_{idx}", disabled=True)
            
            with col2:
                if enriched:
                    st.markdown("**AI-Enriched Data:**")
                    st.text(f"Animals: {incident.get('animals', 'N/A')}")
                    st.text(f"Quantity: {incident.get('quantity', 'N/A')}")
                    st.text(f"Source: {incident.get('source', 'N/A')}")
                    st.text(f"Status: {incident.get('status', 'N/A')}")
                    st.text(f"Suspects: {incident.get('suspects', 'N/A')}")
                    st.text(f"Vehicle: {incident.get('vehicle_info', 'N/A')}")
                    st.text(f"Value: {incident.get('estimated_value', 'N/A')}")
                    
                    if incident.get('ai_summary'):
                        st.info(f"**Summary:** {incident.get('ai_summary')}")
                else:
                    st.markdown("**Status:**")
                    st.text(f"Valid: {incident.get('is_valid', True)}")
            
            # Show validation issues
            if has_issues:
                st.warning(f"⚠️ Issues: {', '.join(incident.get('validation_issues', []))}")


# Stage 3: Complete
elif st.session_state.processing_stage == 'complete':
    st.markdown("---")
    st.subheader("✅ Upload Complete!")
    
    result = st.session_state.get('upload_result', {})
    
    # Display results
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", result.get('total_records', 0))
    with col2:
        st.metric("Successfully Inserted", result.get('inserted_records', 0))
    with col3:
        st.metric("Failed", result.get('failed_records', 0), delta_color="inverse")
    
    if result.get('errors'):
        st.error("**Errors:**")
        for error in result['errors']:
            st.write(f"- {error}")
    
    st.success("Your data has been uploaded to the database!")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Upload More Data", type="primary", use_container_width=True):
            st.session_state.processing_stage = 'upload'
            st.session_state.parsed_data = None
            st.session_state.enriched_data = None
            st.session_state.selected_incidents = set()
            st.session_state.upload_result = None
            st.rerun()
    
    with col2:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page("app.py")


# Sidebar
with st.sidebar:
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Upload** your Excel file
    2. **Review** parsed data
    3. **Enrich** with AI extraction
    4. **Select** incidents to upload
    5. **Upload** to database
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ Supported Formats")
    st.markdown("""
    - Excel files (.xlsx, .xls)
    - Quarterly report structure
    - Columns: Date, Division, Page, Description
    """)
    
    st.markdown("---")
    st.markdown("### 🤖 AI Features")
    st.markdown("""
    - Animal species extraction
    - Quantity detection
    - Source identification
    - Status inference
    - Data validation
    """)
