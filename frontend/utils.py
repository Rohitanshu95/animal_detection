"""
Utility functions for the Wildlife Smuggling Tracker frontend
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import re


def validate_incident_data(data: dict) -> tuple[bool, str]:
    """
    Validate incident data before submission
    
    Args:
        data: Dictionary containing incident information
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    required_fields = ['location', 'animals', 'description', 'source']
    
    for field in required_fields:
        if not data.get(field) or data.get(field).strip() == '':
            return False, f"Required field '{field}' is missing or empty"
    
    # Validate date
    if 'date' in data:
        try:
            incident_date = pd.to_datetime(data['date'])
            if incident_date > pd.Timestamp.now():
                return False, "Incident date cannot be in the future"
        except:
            return False, "Invalid date format"
    
    return True, ""


def format_date(date_str: str, format: str = "%B %d, %Y") -> str:
    """
    Format date string to readable format
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        format: Desired output format
        
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(format)
    except:
        return date_str


def get_status_emoji(status: str) -> str:
    """
    Get emoji representation for incident status
    
    Args:
        status: Status string
        
    Returns:
        Emoji character
    """
    status_emojis = {
        'Reported': '🟡',
        'Investigated': '🟠',
        'Prosecuted': '🟢',
        'Closed': '⚪',
        'Under Investigation': '🔵'
    }
    return status_emojis.get(status, '⚫')


def calculate_statistics(df: pd.DataFrame) -> dict:
    """
    Calculate statistics from incidents dataframe
    
    Args:
        df: Pandas DataFrame with incident data
        
    Returns:
        Dictionary with statistics
    """
    if df.empty:
        return {
            'total': 0,
            'this_month': 0,
            'investigated': 0,
            'prosecuted': 0,
            'top_locations': [],
            'top_animals': []
        }
    
    # Convert date column if not already datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    today = pd.Timestamp.now()
    month_ago = today - pd.Timedelta(days=30)
    
    stats = {
        'total': len(df),
        'this_month': len(df[df['date'] >= month_ago]),
        'investigated': len(df[df['status'] == 'Investigated']),
        'prosecuted': len(df[df['status'] == 'Prosecuted']),
        'top_locations': df['location'].value_counts().head(5).to_dict(),
        'top_animals': df['animals'].value_counts().head(5).to_dict()
    }
    
    return stats


def search_incidents(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Search incidents by query string
    
    Args:
        df: DataFrame with incident data
        query: Search query string
        
    Returns:
        Filtered DataFrame
    """
    if not query or query.strip() == '':
        return df
    
    query = query.lower()
    
    mask = (
        df['location'].str.lower().str.contains(query, na=False) |
        df['animals'].str.lower().str.contains(query, na=False) |
        df['description'].str.lower().str.contains(query, na=False) |
        df['source'].str.lower().str.contains(query, na=False)
    )
    
    return df[mask]


def filter_by_date_range(df: pd.DataFrame, date_range: str) -> pd.DataFrame:
    """
    Filter dataframe by date range
    
    Args:
        df: DataFrame with incident data
        date_range: One of ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"]
        
    Returns:
        Filtered DataFrame
    """
    if date_range == "All Time":
        return df
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    today = pd.Timestamp.now()
    
    if date_range == "Last 7 Days":
        cutoff = today - pd.Timedelta(days=7)
    elif date_range == "Last 30 Days":
        cutoff = today - pd.Timedelta(days=30)
    elif date_range == "Last 90 Days":
        cutoff = today - pd.Timedelta(days=90)
    elif date_range == "This Year":
        return df[df['date'].dt.year == today.year]
    else:
        return df
    
    return df[df['date'] >= cutoff]


def export_to_csv(df: pd.DataFrame, filename: str = None) -> str:
    """
    Export dataframe to CSV string
    
    Args:
        df: DataFrame to export
        filename: Optional filename
        
    Returns:
        CSV string
    """
    if filename is None:
        filename = f"incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return df.to_csv(index=False)


def load_sample_data() -> pd.DataFrame:
    """
    Load sample incident data for demonstration
    
    Returns:
        DataFrame with sample incidents
    """
    sample_data = [
        {
            'date': '2024-12-15',
            'location': 'Mumbai Port, India',
            'animals': 'Pangolin scales',
            'quantity': '150 kg',
            'description': 'Customs officials seized 150kg of pangolin scales hidden in seafood containers',
            'source': 'Wildlife Crime Control Bureau',
            'status': 'Investigated'
        },
        {
            'date': '2024-12-10',
            'location': 'Delhi Airport, India',
            'animals': 'Star tortoises',
            'quantity': '23 specimens',
            'description': 'Passenger caught attempting to smuggle endangered star tortoises in luggage',
            'source': 'Airport Customs',
            'status': 'Prosecuted'
        },
        {
            'date': '2024-11-28',
            'location': 'Chennai, Tamil Nadu',
            'animals': 'Red sanders wood',
            'quantity': '500 kg',
            'description': 'Illegal transportation of red sanders worth 50 lakhs intercepted',
            'source': 'Forest Department',
            'status': 'Reported'
        },
        {
            'date': '2024-11-15',
            'location': 'Kolkata Port, West Bengal',
            'animals': 'Exotic birds',
            'quantity': '45 birds',
            'description': 'Rare exotic birds found in shipping container from Southeast Asia',
            'source': 'Customs Department',
            'status': 'Investigated'
        },
        {
            'date': '2024-10-22',
            'location': 'Goa Border, India',
            'animals': 'Tiger claws and teeth',
            'quantity': '12 pieces',
            'description': 'Vehicle stopped at border checkpoint found carrying tiger body parts',
            'source': 'Wildlife Protection Society',
            'status': 'Prosecuted'
        }
    ]
    
    return pd.DataFrame(sample_data)


def extract_keywords(text: str) -> list:
    """
    Extract keywords from description text
    (Placeholder for AI-powered extraction)
    
    Args:
        text: Description text
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction - can be replaced with AI later
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                   'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
    
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if len(w) > 3 and w not in common_words]
    
    # Return top 10 most common
    return list(set(keywords))[:10]


def display_notification(message: str, type: str = "info"):
    """
    Display notification message
    
    Args:
        message: Message to display
        type: Type of notification (info, success, warning, error)
    """
    if type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)
    else:
        st.info(message)


def create_summary_card(title: str, value: str, delta: str = None, icon: str = "📊"):
    """
    Create a summary statistics card
    
    Args:
        title: Card title
        value: Main value to display
        delta: Optional delta/change value
        icon: Emoji icon
    """
    st.markdown(f"""
        <div style="
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #1f4788;
        ">
            <div style="font-size: 0.9rem; color: #666;">{icon} {title}</div>
            <div style="font-size: 2rem; font-weight: bold; color: #1f4788;">{value}</div>
            {f'<div style="font-size: 0.8rem; color: #28a745;">{delta}</div>' if delta else ''}
        </div>
    """, unsafe_allow_html=True)