# Fentanyl Awareness Data Pipeline

An open-source data pipeline that automatically updates and publishes comprehensive fentanyl mortality data from CDC WONDER and the US Census.

## 🎯 What This Project Provides

- **📊 Ready-to-use CSV file**: Clean, validated fentanyl death data (1999-current)
- **📚 Live Documentation**: Interactive docs automatically updated every week
- **🔄 Automated Updates**: Fresh data published every Monday at 12:00 PM UTC
- **📈 Easy Access**: Download CSV, view docs, or analyze with your preferred tool

## 📂 For Different Users

### 🔧 **Data Engineers & Developers**
Want to modify or run the pipeline? See [`data_engineering/`](data_engineering/README.md) for complete technical documentation, setup instructions, and architecture details.

### 📊 **Researchers & Analysts**
Need the data without technical setup? Download [`fact_fentanyl_deaths_over_time.csv`](final_datasets/) - updated weekly with the latest CDC data combined with census demographics.

### 📈 **Visualizers & Presenters**
Create visualizations in your preferred tool (Excel, Tableau, Python, etc.) using the CSV file. Interactive documentation available at:
**https://data-science-link.github.io/fentanyl-awareness/**

## 🚀 Quick Access

- **📁 Download Data**: [`final_datasets/fact_fentanyl_deaths_over_time.csv`](final_datasets/fact_fentanyl_deaths_over_time.csv)
- **📚 View Docs**: https://data-science-link.github.io/fentanyl-awareness/
- **🏗️ Explore Code**: https://github.com/Data-Science-Link/fentanyl-awareness

## 📊 What's In The Data

The CSV includes:
- **Time Range**: 1999 - current
- **Geographic Level**: State-level
- **Metrics**: Death counts, population data, income, unemployment rates
- **Sources**: Official CDC mortality data (1999-2023) + provisional data (2018-current)

See [`final_datasets/README.md`](final_datasets/README.md) for the complete data dictionary.

## 🔄 How It Works

This repository automatically:
1. Processes CDC WONDER mortality data and US Census demographics
2. Validates and tests the data using automated checks
3. Updates the CSV and documentation every Monday
4. Uploads to Google Sheets (optional, for Tableau connections)

Everything runs on GitHub Actions - no manual intervention needed.

## 🤖 Reliability & Security

- **✅ Automated Testing**: Every code change is automatically tested
- **🔒 Security Scanning**: Code and dependencies scanned weekly for vulnerabilities
- **📝 Full History**: Git maintains complete history of all data changes
- **🔄 Automatic Updates**: Fresh data published every week

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CDC WONDER**: For providing comprehensive mortality data
- **US Census Bureau**: For population and economic data
- **GitHub**: For hosting and automation infrastructure

---

**Note**: This data is for educational and awareness purposes. Always verify data accuracy and consult official sources for policy decisions.
