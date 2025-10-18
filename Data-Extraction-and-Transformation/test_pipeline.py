#!/usr/bin/env python3
"""
Test script for Fentanyl Awareness Data Pipeline

This script runs basic tests to verify the pipeline components work correctly.
"""

import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_extraction_module():
    """Test the extraction module."""
    print("🧪 Testing extraction module...")
    try:
        from extract_data import CDCWonderExtractor
        
        # Create a test extractor
        extractor = CDCWonderExtractor()
        
        # Test XML parsing with a sample file
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <request-parameters>
            <parameter>
                <name>dataset_code</name>
                <value>D77</value>
            </parameter>
            <parameter>
                <name>O_title</name>
                <value>Test Request</value>
            </parameter>
        </request-parameters>"""
        
        # Write sample XML to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_xml)
            temp_file = f.name
        
        try:
            params = extractor.parse_xml_request(temp_file)
            assert params['dataset_code'] == 'D77'
            assert params['O_title'] == 'Test Request'
            print("✅ XML parsing works correctly")
        finally:
            os.unlink(temp_file)
            
        print("✅ Extraction module test passed")
        return True
        
    except Exception as e:
        print(f"❌ Extraction module test failed: {e}")
        return False

def test_dbt_configuration():
    """Test dbt configuration."""
    print("🧪 Testing dbt configuration...")
    try:
        import subprocess
        
        # Check if dbt is installed
        result = subprocess.run(['dbt', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ dbt not found or not working")
            return False
        
        # Check dbt project file
        dbt_project_file = project_root / "dbt_project.yml"
        if not dbt_project_file.exists():
            print("❌ dbt_project.yml not found")
            return False
        
        print("✅ dbt configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ dbt configuration test failed: {e}")
        return False

def test_google_sheets_module():
    """Test Google Sheets module."""
    print("🧪 Testing Google Sheets module...")
    try:
        from load_gcloud import GoogleSheetsLoader
        
        # Test class instantiation (without actual API calls)
        loader = GoogleSheetsLoader("dummy_creds.json", "dummy_sheet_id")
        
        print("✅ Google Sheets module test passed")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets module test failed: {e}")
        return False

def test_data_models():
    """Test dbt data models."""
    print("🧪 Testing dbt data models...")
    try:
        # Check if staging models exist
        staging_dir = project_root / "dbt" / "models" / "staging"
        if not staging_dir.exists():
            print("❌ Staging models directory not found")
            return False
        
        staging_files = list(staging_dir.glob("*.sql"))
        if len(staging_files) == 0:
            print("❌ No staging model files found")
            return False
        
        # Check if mart models exist
        marts_dir = project_root / "dbt" / "models" / "marts"
        if not marts_dir.exists():
            print("❌ Marts models directory not found")
            return False
        
        marts_files = list(marts_dir.glob("*.sql"))
        if len(marts_files) == 0:
            print("❌ No mart model files found")
            return False
        
        print("✅ Data models test passed")
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        return False

def test_github_actions():
    """Test GitHub Actions workflow."""
    print("🧪 Testing GitHub Actions workflow...")
    try:
        workflow_file = project_root / ".github" / "workflows" / "monthly_update.yml"
        if not workflow_file.exists():
            print("❌ GitHub Actions workflow not found")
            return False
        
        # Check if workflow file has content
        content = workflow_file.read_text()
        if len(content) < 100:
            print("❌ GitHub Actions workflow appears to be empty")
            return False
        
        print("✅ GitHub Actions workflow test passed")
        return True
        
    except Exception as e:
        print(f"❌ GitHub Actions workflow test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running Fentanyl Awareness Data Pipeline Tests\n")
    
    tests = [
        test_extraction_module,
        test_dbt_configuration,
        test_google_sheets_module,
        test_data_models,
        test_github_actions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The pipeline is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
