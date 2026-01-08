import streamlit as st
import pandas as pd
from datetime import datetime

st.title("➕ Add New Smuggling Incident")
st.markdown("Fill in the details of the wildlife smuggling incident below.")

# Create form
with st.form("incident_form", clear_on_submit=True):
    st.subheader("Incident Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        incident_date = st.date_input(
            "Date of Incident *",
            value=datetime.now(),
            max_value=datetime.now()
        )
        
        location = st.text_input(
            "Location *",
            placeholder="e.g., Mumbai Port, Maharashtra, India",
            help="Enter the city, state, and country"
        )
        
        animals = st.text_input(
            "Animal/Product Type *",
            placeholder="e.g., Pangolin scales, Ivory, Tiger parts",
            help="Specify the animal species or wildlife product"
        )
    
    with col2:
        quantity = st.text_input(
            "Quantity",
            placeholder="e.g., 150 kg, 23 specimens, 5 units",
            help="Approximate quantity seized or reported"
        )
        
        source = st.text_input(
            "Information Source *",
            placeholder="e.g., Wildlife Crime Control Bureau, Forest Department",
            help="Organization or source that reported this incident"
        )
        
        status = st.selectbox(
            "Status *",
            options=["Reported", "Investigated", "Prosecuted", "Closed"],
            index=0
        )
    
    # Description
    description = st.text_area(
        "Incident Description *",
        placeholder="Provide detailed description of the incident, including how it was discovered, arrests made, etc.",
        height=150,
        help="Add as much detail as possible for better AI analysis"
    )
    
    # Additional information
    with st.expander("📎 Additional Information (Optional)"):
        suspects = st.text_input("Number of Suspects/Arrests")
        vehicle_info = st.text_input("Vehicle Information")
        value = st.text_input("Estimated Value (in local currency)")
        notes = st.text_area("Additional Notes")
    
    # Submit button
    col_submit, col_cancel = st.columns([1, 3])
    
    with col_submit:
        submitted = st.form_submit_button("✅ Submit Incident", use_container_width=True, type="primary")
    
    # Form validation and submission
    if submitted:
        # Validate required fields
        if not all([location, animals, source, description]):
            st.error("❌ Please fill in all required fields marked with *")
        else:
            # Create new incident record
            new_incident = {
                'date': incident_date.strftime('%Y-%m-%d'),
                'location': location,
                'animals': animals,
                'quantity': quantity if quantity else "Not specified",
                'description': description,
                'source': source,
                'status': status
            }
            
            # Add optional fields if provided
            if suspects:
                new_incident['suspects'] = suspects
            if vehicle_info:
                new_incident['vehicle_info'] = vehicle_info
            if value:
                new_incident['estimated_value'] = value
            if notes:
                new_incident['notes'] = notes
            
            # Append to session state
            new_df = pd.DataFrame([new_incident])
            st.session_state.incidents_data = pd.concat(
                [new_df, st.session_state.incidents_data], 
                ignore_index=True
            )
            
            st.success("✅ Incident added successfully!")
            st.balloons()
            
            # Show summary
            with st.expander("📄 View Submitted Incident", expanded=True):
                st.json(new_incident)
            
            st.info("💡 You can view all incidents in the 'View Incidents' section.")
            
            # Option to add another
            if st.button("➕ Add Another Incident"):
                st.rerun()

# Help section
st.markdown("---")
with st.expander("ℹ️ Tips for Adding Incidents"):
    st.markdown("""
    **Best Practices:**
    
    - **Be Specific**: Include exact locations (city, state, country)
    - **Use Clear Descriptions**: Provide context about how the incident was discovered
    - **Include Quantities**: Always mention the amount seized when known
    - **Cite Sources**: Reference official sources like Wildlife Crime Control Bureau, Forest Department, etc.
    - **Update Status**: Mark the current status of the case accurately
    
    **AI Features (Coming Soon):**
    - Automatic extraction of animal species from text
    - Location standardization
    - Incident summarization
    - Pattern detection across multiple incidents
    """)

# Preview current data
if len(st.session_state.incidents_data) > 0:
    st.markdown("---")
    st.subheader("📊 Recent Entries Preview")
    st.dataframe(
        st.session_state.incidents_data.head(3)[['date', 'location', 'animals', 'status']],
        use_container_width=True,
        hide_index=True
    )