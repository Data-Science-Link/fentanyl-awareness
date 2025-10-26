#!/usr/bin/env python3
"""
Setup script for Fentanyl Awareness Data Pipeline

This script helps users set up the project environment and run initial tests.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        # Use shell=False and pass command as list to avoid shell injection
        # Split command into list for safer execution
        cmd_parts = command.split()
        result = subprocess.run(cmd_parts, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_environment():
    """Set up the Python environment."""
    print("🚀 Setting up Fentanyl Awareness Data Pipeline...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Create necessary directories
    directories = [
        "dbt/seeds",
        "dbt/models/staging", 
        "dbt/models/marts",
        "data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check if dbt is working
    if not run_command("dbt --version", "Checking dbt installation"):
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Set up Google Sheets API credentials")
    print("3. Run: python extract_data.py")
    print("4. Run: cd dbt && dbt run")
    print("5. Run: python load_gcloud.py")
    
    return True

def test_pipeline():
    """Test the pipeline components."""
    print("\n🧪 Testing pipeline components...")
    
    # Test data extraction (dry run)
    if not run_command("python -c 'from extract_data import CDCWonderExtractor; print(\"Extraction module OK\")'", 
                      "Testing extraction module"):
        return False
    
    # Test Google Sheets integration (dry run)
    if not run_command("python -c 'from load_gcloud import GoogleSheetsLoader; print(\"Google Sheets module OK\")'", 
                      "Testing Google Sheets module"):
        return False
    
    # Test dbt configuration
    if not run_command("cd dbt && dbt debug", "Testing dbt configuration"):
        return False
    
    print("✅ All tests passed!")
    return True

def main():
    """Main setup function."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        return test_pipeline()
    else:
        return setup_environment()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
