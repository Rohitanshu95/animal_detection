# app.py - Animal Smuggling Incident Reporting System
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Animal Smuggling Tracker",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .stButton button {
        width: 100%;
    }
    .incident-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if 'incidents' not in st.session_state:
    # Sample initial data
    st.session_state.incidents = [
        {
            'id': 1,
            'animal_type': 'Elephant',
            'species': 'African Elephant',
            'incident_type': 'Ivory Trafficking',
            'date': '2024-01-15',
            'location': 'Nairobi, Kenya',
            'quantity': 3,
            'status': 'Under Investigation',
            'description': 'Ivory tusks seized at airport',
            'reported_by': 'Wildlife Officer',
            'severity': 'High'
        },
        {
            'id': 2,
            'animal_type': 'Rhino',
            'species': 'Black Rhino',
            'incident_type': 'Horn Trafficking',
            'date': '2024-01-20',
            'location': 'Kruger Park, SA',
            'quantity': 1,
            'status': 'Arrest Made',
            'description': 'Rhino horn smuggling attempt',
            'reported_by': 'Park Ranger',
            'severity': 'Critical'
        },
        {
            'id': 3,
            'animal_type': 'Parrot',
            'species': 'African Grey',
            'incident_type': 'Pet Trade',
            'date': '2024-01-25',
            'location': 'Lagos, Nigeria',
            'quantity': 15,
            'status': 'Investigation Ongoing',
            'description': 'Illegal bird smuggling ring',
            'reported_by': 'Customs Officer',
            'severity': 'Medium'
        }
    ]

if 'current_id' not in st.session_state:
    st.session_state.current_id = 4

# Function to save data (you can extend this to save to a database)
def save_incident(incident):
    st.session_state.incidents.append(incident)
    st.session_state.current_id += 1
    return True

# Function to export data
def export_to_csv():
    df = pd.DataFrame(st.session_state.incidents)
    csv = df.to_csv(index=False)
    return csv

# Sidebar navigation
with st.sidebar:
    st.title("🦁 Animal Smuggling Tracker")
    st.markdown("---")
    
    # Navigation menu
    page = st.radio(
        "Navigation",
        ["Dashboard", "Report Incident", "View Incidents", "Analytics", "About", "Upload", "Assistant"],
        index=0
    )
    
    st.markdown("---")
    
    # Statistics in sidebar
    st.subheader("📊 Quick Stats")
    total_incidents = len(st.session_state.incidents)
    high_severity = len([i for i in st.session_state.incidents if i['severity'] == 'High' or i['severity'] == 'Critical'])
    under_investigation = len([i for i in st.session_state.incidents if i['status'] == 'Under Investigation'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Incidents", total_incidents)
    with col2:
        st.metric("High Severity", high_severity)
    
    st.metric("Under Investigation", under_investigation)
    
    # Export button
    st.markdown("---")
    if st.button("📥 Export Data (CSV)"):
        csv = export_to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"animal_smuggling_incidents_{date.today()}.csv",
            mime="text/csv"
        )

# Main content area
if page == "Dashboard":
    st.markdown('<h1 class="main-header">Animal Smuggling Incident Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Monitor and track wildlife trafficking incidents in real-time")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", total_incidents, "3 this month")
    with col2:
        unique_animals = len(set(i['animal_type'] for i in st.session_state.incidents))
        st.metric("Animal Types", unique_animals)
    with col3:
        resolved = len([i for i in st.session_state.incidents if i['status'] == 'Arrest Made'])
        st.metric("Cases Resolved", resolved)
    with col4:
        avg_severity = sum(1 for i in st.session_state.incidents if i['severity'] in ['High', 'Critical']) / total_incidents * 100
        st.metric("High Severity %", f"{avg_severity:.1f}%")
    
    st.markdown("---")
    
    # Recent incidents
    st.subheader("🔍 Recent Incidents")
    recent_incidents = st.session_state.incidents[-3:] if len(st.session_state.incidents) >= 3 else st.session_state.incidents
    
    for incident in reversed(recent_incidents):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{incident['animal_type']}** - {incident['incident_type']}")
                st.caption(f"📍 {incident['location']} | 📅 {incident['date']}")
                st.write(incident['description'][:100] + "...")
            with col2:
                st.metric("Quantity", incident['quantity'])
            with col3:
                severity_color = {
                    'Critical': '🔴',
                    'High': '🟠', 
                    'Medium': '🟡',
                    'Low': '🟢'
                }.get(incident['severity'], '⚪')
                st.markdown(f"{severity_color} **{incident['severity']}**")
                st.caption(f"Status: {incident['status']}")
            st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Report New Incident", use_container_width=True):
            st.switch_page("pages/add_incident.py")
    with col2:
        if st.button("📋 View All Incidents", use_container_width=True):
            st.switch_page("pages/view_incidents.py")
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")

elif page == "Report Incident":
    st.markdown('<h1 class="main-header">📝 Report New Incident</h1>', unsafe_allow_html=True)
    
    with st.form("incident_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            animal_type = st.selectbox(
                "Animal Type",
                ["Elephant", "Rhino", "Tiger", "Lion", "Leopard", "Pangolin", 
                 "Parrot", "Snake", "Turtle", "Shark", "Other"]
            )
            
            if animal_type == "Other":
                animal_type = st.text_input("Specify Animal Type")
            
            species = st.text_input("Species (Scientific Name)")
            incident_type = st.selectbox(
                "Incident Type",
                ["Ivory Trafficking", "Horn Trafficking", "Skin/Bone Trade", 
                 "Live Animal Trade", "Pet Trade", "Traditional Medicine", "Other"]
            )
            
            location = st.text_input("Location")
            country = st.selectbox(
                "Country",
                ["Kenya", "South Africa", "Tanzania", "India", "China", 
                 "Vietnam", "Thailand", "Indonesia", "Other"]
            )
        
        with col2:
            quantity = st.number_input("Number of Animals/Items", min_value=1, value=1)
            date_reported = st.date_input("Date of Incident", value=date.today())
            severity = st.select_slider(
                "Severity Level",
                options=["Low", "Medium", "High", "Critical"],
                value="Medium"
            )
            status = st.selectbox(
                "Current Status",
                ["Reported", "Under Investigation", "Evidence Collected", 
                 "Arrest Made", "Case Closed", "Ongoing"]
            )
            reported_by = st.text_input("Reported By")
        
        description = st.text_area("Incident Description", height=150)
        
        # Evidence upload (optional)
        st.subheader("Evidence (Optional)")
        evidence_files = st.file_uploader(
            "Upload evidence files",
            type=["jpg", "jpeg", "png", "pdf", "txt"],
            accept_multiple_files=True
        )
        
        submitted = st.form_submit_button("Submit Incident Report")
        
        if submitted:
            if not location or not description:
                st.error("Please fill in all required fields!")
            else:
                new_incident = {
                    'id': st.session_state.current_id,
                    'animal_type': animal_type,
                    'species': species,
                    'incident_type': incident_type,
                    'date': str(date_reported),
                    'location': f"{location}, {country}",
                    'quantity': quantity,
                    'status': status,
                    'description': description,
                    'reported_by': reported_by if reported_by else "Anonymous",
                    'severity': severity,
                    'timestamp': datetime.now().isoformat()
                }
                
                save_incident(new_incident)
                st.success("✅ Incident report submitted successfully!")
                st.balloons()
                
                # Show summary
                with st.expander("View Submitted Report"):
                    st.json(new_incident)

elif page == "View Incidents":
    st.markdown('<h1 class="main-header">📋 All Reported Incidents</h1>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_animal = st.multiselect(
            "Filter by Animal",
            options=list(set(i['animal_type'] for i in st.session_state.incidents)),
            default=None
        )
    with col2:
        filter_severity = st.multiselect(
            "Filter by Severity",
            options=["Low", "Medium", "High", "Critical"],
            default=None
        )
    with col3:
        filter_status = st.multiselect(
            "Filter by Status",
            options=list(set(i['status'] for i in st.session_state.incidents)),
            default=None
        )
    with col4:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Newest)", "Date (Oldest)", "Severity", "Animal Type"]
        )
    
    # Apply filters
    filtered_incidents = st.session_state.incidents.copy()
    
    if filter_animal:
        filtered_incidents = [i for i in filtered_incidents if i['animal_type'] in filter_animal]
    if filter_severity:
        filtered_incidents = [i for i in filtered_incidents if i['severity'] in filter_severity]
    if filter_status:
        filtered_incidents = [i for i in filtered_incidents if i['status'] in filter_status]
    
    # Sort
    if sort_by == "Date (Newest)":
        filtered_incidents.sort(key=lambda x: x['date'], reverse=True)
    elif sort_by == "Date (Oldest)":
        filtered_incidents.sort(key=lambda x: x['date'])
    elif sort_by == "Severity":
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        filtered_incidents.sort(key=lambda x: severity_order.get(x['severity'], 4))
    elif sort_by == "Animal Type":
        filtered_incidents.sort(key=lambda x: x['animal_type'])
    
    # Display incidents
    if not filtered_incidents:
        st.warning("No incidents match the selected filters.")
    else:
        for incident in filtered_incidents:
            with st.container():
                st.markdown(f"""
                <div class="incident-card" style="border-left-color: {'#EF4444' if incident['severity'] in ['High', 'Critical'] else '#3B82F6'}; background-color: {"#510C03" if incident['severity'] in ['High', 'Critical'] else "#041832"};">
                    <h3>{incident['animal_type']} - {incident['incident_type']}</h3>
                    <p><strong>Location:</strong> {incident['location']} | 
                    <strong>Date:</strong> {incident['date']} | 
                    <strong>Status:</strong> {incident['status']}</p>
                    <p>{incident['description']}</p>
                    <p><strong>Severity:</strong> {incident['severity']} | 
                    <strong>Quantity:</strong> {incident['quantity']} | 
                    <strong>Reported by:</strong> {incident['reported_by']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.info(f"Showing {len(filtered_incidents)} of {total_incidents} incidents")

elif page == "Analytics":
    st.markdown('<h1 class="main-header">📊 Analytics & Insights</h1>', unsafe_allow_html=True)
    
    if len(st.session_state.incidents) < 1:
        st.warning("Not enough data for analytics. Please add some incidents first.")
    else:
        df = pd.DataFrame(st.session_state.incidents)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Incidents by Animal Type")
            animal_counts = df['animal_type'].value_counts()
            fig1 = px.pie(
                values=animal_counts.values,
                names=animal_counts.index,
                hole=0.3
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Incidents by Severity")
            severity_counts = df['severity'].value_counts()
            fig2 = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                color=severity_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Time series
        st.subheader("Incidents Over Time")
        df['date'] = pd.to_datetime(df['date'])
        time_series = df.groupby(df['date'].dt.to_period('M')).size().reset_index()
        time_series.columns = ['Month', 'Count']
        time_series['Month'] = time_series['Month'].astype(str)
        
        fig3 = px.line(
            time_series,
            x='Month',
            y='Count',
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Statistics table
        st.subheader("Detailed Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Most Trafficked Animal", df['animal_type'].mode()[0])
            st.metric("Average Quantity per Incident", f"{df['quantity'].mean():.1f}")
        
        with col2:
            st.metric("Most Common Incident Type", df['incident_type'].mode()[0])
            st.metric("Most Active Location", df['location'].mode()[0])
        
        with col3:
            st.metric("Resolution Rate", 
                     f"{(len(df[df['status'] == 'Arrest Made']) / len(df) * 100):.1f}%")
            st.metric("High Severity Rate", 
                     f"{(len(df[df['severity'].isin(['High', 'Critical'])]) / len(df) * 100):.1f}%")

elif page == "About":
    st.markdown('<h1 class="main-header">About This Application</h1>', unsafe_allow_html=True)
    
    st.write("""
    ## Animal Smuggling Incident Reporting System
    
    ### Purpose
    This application is designed to help track, monitor, and analyze animal smuggling incidents 
    worldwide. It serves as a tool for wildlife conservation organizations, law enforcement 
    agencies, and concerned citizens to report and document illegal wildlife trafficking activities.
    
    ### Features
    - 📝 **Incident Reporting**: Easily report new smuggling incidents with detailed information
    - 📊 **Real-time Dashboard**: Monitor incidents with interactive charts and metrics
    - 📋 **Incident Management**: View, filter, and manage all reported cases
    - 📈 **Analytics**: Gain insights through data visualization and statistics
    - 📥 **Data Export**: Export incident data for further analysis or reporting
    
    ### How to Use
    1. **Report an Incident**: Use the "Report Incident" page to submit new cases
    2. **Monitor**: Check the dashboard for real-time updates and statistics
    3. **Analyze**: Use the analytics page to identify patterns and trends
    4. **Export**: Download data for official reports or further investigation
    
    ### Data Privacy
    All incident data is stored locally in your session. For production use, 
    consider implementing a secure database backend.
    
    ### Support
    For assistance or to report issues, please contact your system administrator.
    
    ---
    *Built with Streamlit | Version 1.0 | For Wildlife Conservation*
    """)
    
    # System info
    with st.expander("System Information"):
        st.write(f"**Total Incidents in Database:** {len(st.session_state.incidents)}")
        st.write(f"**Application Version:** 1.0.0")
        st.write(f"**Last Updated:** {date.today()}")
        
        if st.button("Clear All Data (Demo Only)"):
            st.session_state.incidents = []
            st.session_state.current_id = 1
            st.warning("All data cleared! This is for demo purposes only.")
            st.rerun()

elif page == "Upload":
    st.switch_page("pages/excel_upload.py")

elif page == "Assistant":
    st.switch_page("pages/assistant.py")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.caption("🦁 Animal Smuggling Tracker v1.0 | Report Wildlife Crime | Save Our Wildlife")