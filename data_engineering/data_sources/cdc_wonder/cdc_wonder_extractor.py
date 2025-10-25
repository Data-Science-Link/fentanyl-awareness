#!/usr/bin/env python3
"""
CDC WONDER Data Extraction Script

This script reads XML request files and queries the CDC WONDER API to extract
synthetic opioid mortality data from multiple datasets:
- D77: Official 1999-2020 (Multiple Cause of Death)
- D157: Official 2018-2023 (Multiple Cause of Death, Single Race)
- D176: Provisional 2018-Current (Provisional Mortality Statistics)

The extracted data is saved as CSV files in the dbt seeds directory.
This script is specifically designed for CDC WONDER API automation.

Usage:
    python3 cdc_wonder_extractor.py
"""

import os
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import time
from typing import Dict, Any
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CDCWonderExtractor:
    """Extract data from CDC WONDER API using XML request files."""
    
    def __init__(self, base_url: str = "https://wonder.cdc.gov/controller/datarequest", timeout: int = 1200):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        
        # Alternative endpoints to try
        self.alternative_endpoints = [
            "https://wonder.cdc.gov/controller/datarequest",
            "https://wonder.cdc.gov/wonder/help/wonder-api.html",
            "https://wonder.cdc.gov/controller/datarequest/D77",
            "https://wonder.cdc.gov/controller/datarequest/D157", 
            "https://wonder.cdc.gov/controller/datarequest/D176",
            "https://wonder.cdc.gov/controller/datarequest/D77.V1",
            "https://wonder.cdc.gov/controller/datarequest/D157.V1",
            "https://wonder.cdc.gov/controller/datarequest/D176.V1"
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
                value = value_elements[0].text
                # Handle None values and clean up whitespace
                if value is not None:
                    value = value.strip()
                    # Skip empty values
                    if value == '':
                        continue
                params[name] = value
            else:
                # Handle multiple values (like in D176 for years 2023, 2024, 2025)
                values = []
                for elem in value_elements:
                    if elem.text is not None and elem.text.strip():
                        values.append(elem.text.strip())
                if values:  # Only add if we have non-empty values
                    params[name] = values
        
        return params
    
    def submit_request(self, params: Dict[str, Any], max_retries: int = 3) -> str:
        """Submit request to CDC WONDER API with retry logic and return the result."""
        logger.info(f"Submitting request for dataset: {params.get('dataset_code', 'Unknown')}")
        
        # Use all parameters from the XML file (the new request file should be properly formatted)
        # Skip None values and empty strings, but include all other parameters
        request_params = {}
        for key, value in params.items():
            if value is not None and value != '' and value != '*None*':
                request_params[key] = value
        
        # Use the full request from the XML file - no scope restrictions
        # This will request all data as specified in the original XML file
        
        # Ensure we have the essential parameters
        if 'dataset_code' not in request_params:
            request_params['dataset_code'] = 'D176'
        if 'stage' not in request_params:
            request_params['stage'] = 'request'
        if 'action-Send' not in request_params:
            request_params['action-Send'] = 'Send'
        
        # Debug: Print the parameters being sent
        logger.info(f"Using request parameters: {request_params}")
        
        # Retry logic for temporary service issues
        for attempt in range(max_retries):
            try:
                # Use POST request with all parameters from the new request file
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Trying POST request with new request file parameters...")
                response = self.session.post(
                    self.base_url,
                    data=request_params,
                    timeout=self.timeout,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Origin': 'https://wonder.cdc.gov',
                        'Referer': 'https://wonder.cdc.gov/'
                    }
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 400:
                    logger.error(f"400 Bad Request - Response content: {response.text[:1000]}")
                    logger.error("This might indicate the API format has changed or parameters are invalid")
                    # Try to save the full response for debugging
                    with open('debug_response.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info("Full response saved to debug_response.html")
                    response.raise_for_status()
                    
                elif response.status_code == 502:
                    logger.warning(f"502 Bad Gateway - CDC WONDER API might be temporarily unavailable (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                        logger.info(f"Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Max retries reached for 502 errors")
                        response.raise_for_status()
                        
                elif response.status_code == 504:
                    logger.warning(f"504 Gateway Timeout - Request is taking too long (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                        logger.info(f"Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Max retries reached for 504 errors")
                        logger.info("This suggests the request format is valid but the dataset is large")
                        # Save the response for debugging
                        with open('timeout_response.html', 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        logger.info("Timeout response saved to timeout_response.html")
                        response.raise_for_status()
                
                response.raise_for_status()
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    logger.info(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Max retries reached")
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
        
        # Define dataset mappings - using the new request file and original files
        dataset_mappings = {
            "Provisional_Mortality_Statistics_2018_through_Last_Week_1760806798363-req.xml": "d176_provisional_2018_current.csv",
            "Official_1999-2020_Synthetic_Opioid_Deaths-req.xml": "d77_official_1999_2020.csv",
            "Official_2018-2023_Synthetic_Opioid_Deaths-req.xml": "d157_official_2018_2023.csv"
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
    # Set up paths - script is now in the CDC WONDER folder
    script_dir = Path(__file__).parent
    source_dir = script_dir  # XML files are in the same directory
    output_dir = script_dir.parent.parent / "dbt" / "seeds"  # Go up to project root, then to dbt/seeds
    
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
