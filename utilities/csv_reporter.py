import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class CSVReporter:
    """Handles output of security test results to CSV files."""
    
    def __init__(self, output_dir: str = 'test_results'):
        """Initialize CSV reporter with output directory.
        
        Args:
            output_dir: Directory to store CSV reports. Created if doesn't exist.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def write_test_results(self, test_results: Dict[str, Any], filename: str = None) -> str:
        """Write test results to CSV file.
        
        Args:
            test_results: Dictionary containing test metrics and results
            filename: Output filename. If None, generates from timestamp.
            
        Returns:
            Path to created CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'security_test_{timestamp}.csv'
        
        filepath = self.output_dir / filename
        
        # Flatten nested results into rows
        rows = self._flatten_results(test_results)
        
        if not rows:
            return str(filepath)
        
        # Write to CSV
        fieldnames = rows[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return str(filepath)
    
    def _flatten_results(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten nested test results into list of row dictionaries.
        
        Args:
            test_results: Nested dictionary of test results
            
        Returns:
            List of dictionaries suitable for CSV writing
        """
        rows = []
        timestamp = datetime.now().isoformat()
        
        for test_name, test_data in test_results.items():
            if isinstance(test_data, dict):
                row = {
                    'timestamp': timestamp,
                    'test_name': test_name,
                    'status': test_data.get('status', 'unknown'),
                    'passed': test_data.get('passed', False),
                    'metrics': self._dict_to_string(test_data.get('metrics', {})),
                    'details': test_data.get('details', ''),
                }
                rows.append(row)
            else:
                row = {
                    'timestamp': timestamp,
                    'test_name': test_name,
                    'status': 'completed',
                    'passed': bool(test_data),
                    'metrics': str(test_data),
                    'details': '',
                }
                rows.append(row)
        
        return rows
    
    def _dict_to_string(self, d: Dict[str, Any]) -> str:
        """Convert dictionary to pipe-separated string.
        
        Args:
            d: Dictionary to convert
            
        Returns:
            Pipe-separated key=value pairs
        """
        if not d:
            return ''
        items = [f'{k}={v}' for k, v in d.items()]
        return ' | '.join(items)
    
    def write_summary(self, summary: Dict[str, Any], filename: str = 'test_summary.csv') -> str:
        """Write summary statistics to CSV file.
        
        Args:
            summary: Dictionary with summary statistics
            filename: Output filename
            
        Returns:
            Path to created CSV file
        """
        filepath = self.output_dir / filename
        
        rows = []
        for key, value in summary.items():
            rows.append({
                'metric': key,
                'value': value,
                'timestamp': datetime.now().isoformat(),
            })
        
        if rows:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'metric', 'value'])
                writer.writeheader()
                writer.writerows(rows)
        
        return str(filepath)
    
    def get_latest_report(self) -> str:
        """Get path to the most recently created report.
        
        Returns:
            Path to latest CSV file or None if no reports exist
        """
        csv_files = list(self.output_dir.glob('security_test_*.csv'))
        if not csv_files:
            return None
        return str(max(csv_files, key=lambda p: p.stat().st_mtime))
