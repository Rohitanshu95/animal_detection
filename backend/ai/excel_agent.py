"""
Excel Processing Agent
Handles parsing, cleaning, and validating Excel files with wildlife incident data
"""

import pandas as pd
import re
from datetime import datetime
from dateutil import parser
from typing import Dict, List, Tuple, Optional
import io


class ExcelParser:
    """Parses Excel files with quarterly wildlife incident reports"""
    
    def __init__(self):
        self.quarterly_pattern = r"n°\s*(\d+)\s*/\s*(.+?)(?=\n|$)"
        self.date_patterns = [
            r"(\d{1,2})\.(\d{1,2})\.(\d{4})",  # DD.MM.YYYY
            r"(\w+)\s+(\d{4})",  # Month YYYY
            r"(\w+)\s+(\d{1,2}),?\s+(\d{4})",  # Month DD, YYYY
            r"(\d{4})",  # YYYY only
        ]
        
    def parse_excel(self, file_content: bytes) -> Dict:
        """
        Parse Excel file and extract incidents with context
        
        Args:
            file_content: Binary content of Excel file
            
        Returns:
            Dictionary with incidents and metadata
        """
        try:
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            
            # Initialize results
            incidents = []
            current_quarter = None
            current_quarter_info = {}
            
            # Process each row
            for idx, row in df.iterrows():
                # Check if this is a quarterly header
                quarter_info = self._extract_quarterly_header(row)
                if quarter_info:
                    current_quarter = quarter_info['quarter_number']
                    current_quarter_info = quarter_info
                    continue
                
                # Check if this is a data row (has date)
                if self._is_data_row(row):
                    incident = self._extract_incident_from_row(row, current_quarter_info)
                    if incident:
                        incidents.append(incident)
            
            return {
                'success': True,
                'total_rows': len(df),
                'incidents': incidents,
                'incident_count': len(incidents),
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'total_rows': 0,
                'incidents': [],
                'incident_count': 0,
                'errors': [str(e)]
            }
    
    def _extract_quarterly_header(self, row) -> Optional[Dict]:
        """Extract quarterly report information from header row"""
        row_str = ' '.join([str(val) for val in row.values if pd.notna(val)])
        
        match = re.search(self.quarterly_pattern, row_str, re.IGNORECASE)
        if match:
            quarter_num = match.group(1)
            date_range = match.group(2).strip()
            
            return {
                'quarter_number': quarter_num,
                'date_range': date_range,
                'raw_header': row_str
            }
        return None
    
    def _is_data_row(self, row) -> bool:
        """Check if row contains incident data (not header/empty)"""
        # Row should have at least a date and description
        has_date = pd.notna(row.iloc[0]) if len(row) > 0 else False
        has_description = pd.notna(row.iloc[3]) if len(row) > 3 else False
        
        # Check if first column looks like a date
        if has_date:
            first_col = str(row.iloc[0])
            # Skip if it's obviously a header
            if any(keyword in first_col.lower() for keyword in ['date', 'division', 'page', 'description']):
                return False
            return has_description
        
        return False
    
    def _extract_incident_from_row(self, row, quarter_info: Dict) -> Optional[Dict]:
        """Extract incident data from a data row"""
        try:
            # Extract basic fields (adjust indices based on actual Excel structure)
            raw_date = str(row.iloc[0]) if len(row) > 0 else None
            division = str(row.iloc[1]) if len(row) > 1 else None
            page_no = str(row.iloc[2]) if len(row) > 2 else None
            description = str(row.iloc[3]) if len(row) > 3 else None
            
            # Clean and validate
            if not description or description == 'nan':
                return None
            
            # Clean date
            cleaned_date = self._clean_date(raw_date, quarter_info)
            
            return {
                'raw_date': raw_date,
                'date': cleaned_date,
                'location': division if division != 'nan' else None,
                'page_no': page_no if page_no != 'nan' else None,
                'description': description,
                'quarter_number': quarter_info.get('quarter_number'),
                'quarter_date_range': quarter_info.get('date_range'),
                'needs_enrichment': True,
                'validation_issues': []
            }
            
        except Exception as e:
            return None
    
    def _clean_date(self, raw_date: str, quarter_info: Dict) -> str:
        """
        Clean and standardize date format
        Handles various formats and fixes obvious errors
        """
        if not raw_date or raw_date == 'nan':
            return None
        
        try:
            # Try to parse with dateutil
            parsed_date = parser.parse(raw_date, fuzzy=True)
            
            # Check for obvious errors (like year 1900 when it should be recent)
            if parsed_date.year < 2000:
                # Try to infer year from quarter info
                year = self._extract_year_from_quarter(quarter_info)
                if year:
                    parsed_date = parsed_date.replace(year=year)
            
            return parsed_date.strftime('%Y-%m-%d')
            
        except:
            # If parsing fails, try to extract year from quarter info
            year = self._extract_year_from_quarter(quarter_info)
            if year:
                return f"{year}-01-01"  # Default to Jan 1 if can't parse
            return None
    
    def _extract_year_from_quarter(self, quarter_info: Dict) -> Optional[int]:
        """Extract year from quarterly date range"""
        if not quarter_info or 'date_range' not in quarter_info:
            return None
        
        date_range = quarter_info['date_range']
        # Look for 4-digit year
        match = re.search(r'(\d{4})', date_range)
        if match:
            return int(match.group(1))
        return None


class DataValidator:
    """Validates and cleans incident data"""
    
    @staticmethod
    def validate_incident(incident: Dict) -> Tuple[bool, List[str]]:
        """
        Validate incident data
        Returns (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        if not incident.get('description'):
            issues.append("Missing description")
        
        if not incident.get('date'):
            issues.append("Missing or invalid date")
        
        if not incident.get('location'):
            issues.append("Missing location/division")
        
        # Check description length
        desc = incident.get('description', '')
        if len(desc) < 10:
            issues.append("Description too short (less than 10 characters)")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,;:()\[\]{}]', '', text)
        
        return text.strip()


# Convenience functions
def parse_excel_file(file_content: bytes) -> Dict:
    """Parse Excel file and return incidents"""
    parser = ExcelParser()
    return parser.parse_excel(file_content)


def validate_incidents(incidents: List[Dict]) -> List[Dict]:
    """Validate list of incidents and add validation results"""
    validator = DataValidator()
    
    for incident in incidents:
        is_valid, issues = validator.validate_incident(incident)
        incident['is_valid'] = is_valid
        incident['validation_issues'] = issues
        
        # Clean text fields
        if incident.get('description'):
            incident['description'] = validator.clean_text(incident['description'])
        if incident.get('location'):
            incident['location'] = validator.clean_text(incident['location'])
    
    return incidents
