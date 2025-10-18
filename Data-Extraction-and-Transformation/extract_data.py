#!/usr/bin/env python3
"""
CDC WONDER Data Extraction Script

This script reads XML request files and queries the CDC WONDER API to extract
synthetic opioid mortality data from three datasets:
- D77: Official 1999-2020 (Multiple Cause of Death)
- D157: Official 2018-2023 (Multiple Cause of Death, Single Race)
- D176: Provisional 2023-Current (Provisional Mortality Statistics)

The extracted data is saved as TSV files in the dbt seeds directory.
"""

import os
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import time
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CDCWonderExtractor:
    """Extract data from CDC WONDER API using XML request files."""
    
    def __init__(self, base_url: str = "https://wonder.cdc.gov/controller/datarequest", timeout: int = 600):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        
        # Alternative endpoints to try
        self.alternative_endpoints = [
            "https://wonder.cdc.gov/controller/datarequest",
            "https://wonder.cdc.gov/wonder/help/wonder-api.html",
            "https://wonder.cdc.gov/controller/datarequest/D77",
            "https://wonder.cdc.gov/controller/datarequest/D157", 
            "https://wonder.cdc.gov/controller/datarequest/D176"
        ]
        
    def parse_xml_request(self, xml_file_path: str) -> Dict[str, Any]:
        """Parse XML request file and extract parameters."""
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        params = {}
        for param in root.findall('parameter'):
            name = param.find('name').text
            value_elements = param.findall('value')
            
            if len(value_elements) == 1:
                params[name] = value_elements[0].text
            else:
                # Handle multiple values (like in D176 for years 2023, 2024, 2025)
                params[name] = [elem.text for elem in value_elements]
        
        return params
    
    def submit_request(self, params: Dict[str, Any]) -> str:
        """Submit request to CDC WONDER API and return the result."""
        logger.info(f"Submitting request for dataset: {params.get('dataset_code', 'Unknown')}")
        
        # Add required data use restrictions parameter
        params['accept_datause_restrictions'] = 'true'
        
        try:
            # Try different approaches for the API request
            # Method 1: Direct POST with form data
            response = self.session.post(
                self.base_url,
                data=params,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 502:
                logger.warning("502 Bad Gateway - CDC WONDER API might be temporarily unavailable")
                # Try alternative endpoint
                alt_url = "https://wonder.cdc.gov/controller/datarequest/D77"
                logger.info(f"Trying alternative endpoint: {alt_url}")
                response = self.session.post(alt_url, data=params, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
            
            response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def extract_dataset(self, xml_file_path: str, output_file_path: str) -> bool:
        """Extract data for a single dataset."""
        try:
            # Parse XML parameters
            params = self.parse_xml_request(xml_file_path)
            
            # Submit request
            data = self.submit_request(params)
            
            # Save to file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            
            logger.info(f"Successfully extracted data to {output_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract data from {xml_file_path}: {e}")
            return False
    
    def extract_all_datasets(self, source_dir: str, output_dir: str) -> Dict[str, bool]:
        """Extract data from all XML files in the source directory."""
        results = {}
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Define dataset mappings
        dataset_mappings = {
            "Official 1999-2020 (Synthetic Opioid Deaths)-req.xml": "d77_official_1999_2020.tsv",
            "Official 2018-2023 (Synthetic Opioid Deaths)-req.xml": "d157_official_2018_2023.tsv", 
            "Provisional 2023-Current (Synthetic Opioid Deaths)-req.xml": "d176_provisional_2023_current.tsv"
        }
        
        for xml_file, output_file in dataset_mappings.items():
            xml_path = os.path.join(source_dir, xml_file)
            output_path = os.path.join(output_dir, output_file)
            
            if os.path.exists(xml_path):
                logger.info(f"Processing {xml_file}...")
                success = self.extract_dataset(xml_path, output_path)
                results[xml_file] = success
                
                # Add delay between requests to be respectful to the API
                time.sleep(2)
            else:
                logger.warning(f"XML file not found: {xml_path}")
                results[xml_file] = False
        
        return results

def main():
    """Main function to run the extraction process."""
    # Set up paths
    project_root = Path(__file__).parent
    source_dir = project_root / "elt" / "extract" / "source_wonder"
    output_dir = project_root / "dbt" / "seeds"
    
    # Create extractor
    extractor = CDCWonderExtractor()
    
    # Extract all datasets
    logger.info("Starting CDC WONDER data extraction...")
    results = extractor.extract_all_datasets(str(source_dir), str(output_dir))
    
    # Report results
    logger.info("Extraction completed. Results:")
    for xml_file, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"  {xml_file}: {status}")
    
    # Check if all extractions succeeded
    all_success = all(results.values())
    if all_success:
        logger.info("All datasets extracted successfully!")
        return 0
    else:
        logger.error("Some datasets failed to extract.")
        return 1

if __name__ == "__main__":
    exit(main())
