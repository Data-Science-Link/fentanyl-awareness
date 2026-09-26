#!/usr/bin/env python3
"""Set up a local environment for the Fentanyl Awareness data pipeline."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd_list, description):
    print(f"🔄 {description}...")
    try:
        subprocess.run(cmd_list, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def setup_environment():
    print("🚀 Setting up Fentanyl Awareness Data Pipeline...")

    if not check_python_version():
        return False

    if not run_command(["pip", "install", "-r", "requirements.txt"], "Installing Python dependencies"):
        return False

    for directory in ["data_build_tool/dbt/seeds", "data_build_tool/logs"]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

    if not run_command(["dbt", "--version"], "Checking dbt installation"):
        return False

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy ../.env.example to ../.env and add CENSUS_API_KEY if you need a census refresh")
    print("2. Run: python data_sources/cdc_api/soda_extractor.py")
    print("3. Run: python data_sources/census_acs/census_extractor.py")
    print("4. Run: cd data_build_tool && dbt seed && dbt run && dbt test")
    return True


def test_pipeline():
    print("\n🧪 Testing pipeline components...")
    if not run_command(
        ["python", "-c", "from data_sources.cdc_api.soda_extractor import CDCSodaExtractor; print('CDC extractor OK')"],
        "Testing CDC extractor import",
    ):
        return False
    if not run_command(["dbt", "--version"], "Checking dbt installation"):
        return False
    print("✅ All tests passed!")
    return True


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        return test_pipeline()
    return setup_environment()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
