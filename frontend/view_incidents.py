import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📊 View All Incidents")
st.markdown("Search, filter, and analyze wildlife smuggling incidents.")

# Get data from session state
df = st.session_state.incidents_data.copy()

# Convert date column to datetime for filtering
df['date'] = pd.to_datetime(df['date'])

# Search and Filter Section
st.subheader("🔍 Search & Filter")

col1, col2, col3 = st.columns(3)

with col1:
    search_query = st.text_input(
        "Search",
        placeholder="Search location, animals, description...",
        label_visibility="collapsed"
    )

with col2:
    status_filter = st.multiselect(
        "Filter by Status",
        options=df['status'].unique().tolist(),
        default=df['status'].unique().tolist()
    )

with col3:
    date_range = st.selectbox(
        "Date Range",
        options=["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"]
    )

# Apply filters
filtered_df = df.copy()

# Status filter
if status_filter:
    filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]

# Date range filter
today = pd.Timestamp.now()
if date_range == "Last 7 Days":
    filtered_df = filtered_df[filtered_df['date'] >= today - pd.Timedelta(days=7)]
elif date_range == "Last 30 Days":
    filtered_df = filtered_df[filtered_df['date'] >= today - pd.Timedelta(days=30)]
elif date_range == "Last 90 Days":
    filtered_df = filtered_df[filtered_df['date'] >= today - pd.Timedelta(days=90)]
elif date_range == "This Year":
    filtered_df = filtered_df[filtered_df['date'].dt.year == today.year]

# Search filter
if search_query:
    mask = (
        filtered_df['location'].str.contains(search_query, case=False, na=False) |
        filtered_df['animals'].str.contains(search_query, case=False, na=False) |
        filtered_df['description'].str.contains(search_query, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

# Display results count
st.markdown(f"**Showing {len(filtered_df)} of {len(df)} incidents**")

# Sort options
col_sort1, col_sort2, col_export = st.columns([2, 2, 1])

with col_sort1:
    sort_by = st.selectbox(
        "Sort by",
        options=["Date (Newest)", "Date (Oldest)", "Location", "Status"]
    )

with col_sort2:
    view_mode = st.radio(
        "View Mode",
        options=["Table", "Cards"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_export:
    # Export button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Export",
        data=csv,
        file_name=f"incidents_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Apply sorting
if sort_by == "Date (Newest)":
    filtered_df = filtered_df.sort_values('date', ascending=False)
elif sort_by == "Date (Oldest)":
    filtered_df = filtered_df.sort_values('date', ascending=True)
elif sort_by == "Location":
    filtered_df = filtered_df.sort_values('location')
elif sort_by == "Status":
    filtered_df = filtered_df.sort_values('status')

# Display data
st.markdown("---")

if len(filtered_df) == 0:
    st.warning("No incidents found matching your filters.")
else:
    if view_mode == "Table":
        # Table view with better formatting
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        # Configure column display
        st.dataframe(
            display_df[['date', 'location', 'animals', 'quantity', 'status', 'source']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": st.column_config.TextColumn("Date", width="small"),
                "location": st.column_config.TextColumn("Location", width="medium"),
                "animals": st.column_config.TextColumn("Animals/Products", width="medium"),
                "quantity": st.column_config.TextColumn("Quantity", width="small"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "source": st.column_config.TextColumn("Source", width="medium")
            }
        )
        
        # Detailed view expander
        with st.expander("📋 View Detailed Records"):
            for idx, row in filtered_df.iterrows():
                st.markdown(f"""
                **{row['location']}** - {row['date'].strftime('%Y-%m-%d')}
                - **Animals:** {row['animals']}
                - **Quantity:** {row['quantity']}
                - **Status:** {row['status']}
                - **Source:** {row['source']}
                - **Description:** {row['description']}
                """)
                st.markdown("---")
    
    else:
        # Card view
        for idx, row in filtered_df.iterrows():
            status_color = {
                'Reported': '🟡',
                'Investigated': '🟠',
                'Prosecuted': '🟢',
                'Closed': '⚪'
            }.get(row['status'], '⚪')
            
            with st.container():
                col_card1, col_card2 = st.columns([3, 1])
                
                with col_card1:
                    st.markdown(f"### 📍 {row['location']}")
                    st.markdown(f"**{row['animals']}** • {row['quantity']}")
                    st.markdown(f"📅 {row['date'].strftime('%B %d, %Y')}")
                    
                with col_card2:
                    st.markdown(f"**Status**")
                    st.markdown(f"{status_color} {row['status']}")
                
                with st.expander("View Details"):
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Source:** {row['source']}")
                
                st.markdown("---")

# Statistics sidebar
with st.sidebar:
    st.markdown("### 📈 Current View Stats")
    
    if len(filtered_df) > 0:
        st.metric("Total Incidents", len(filtered_df))
        
        # Status breakdown
        st.markdown("**Status Breakdown:**")
        status_counts = filtered_df['status'].value_counts()
        for status, count in status_counts.items():
            st.write(f"• {status}: {count}")
        
        # Top locations
        st.markdown("**Top Locations:**")
        top_locations = filtered_df['location'].value_counts().head(5)
        for location, count in top_locations.items():
            st.write(f"• {location}: {count}")
    else:
        st.info("Apply filters to see statistics")