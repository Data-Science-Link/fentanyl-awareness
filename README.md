# Fentanyl Awareness Data Pipeline

An open-source data pipeline that automatically updates and publishes comprehensive fentanyl mortality data from CDC WONDER and the US Census.

## 🎯 What This Project Provides

- **📊 Ready-to-use CSV file**: Clean, validated fentanyl death data (1999-current)
- **Interactive Data Portal**: Browse, filter, and export data directly from your browser
- **📚 Live Documentation**: Complete pipeline and data lineage docs updated weekly
- **🔄 Automated Updates**: Fresh data published every Monday at 12:00 PM UTC
- **📈 Easy Access**: Download CSV, explore online, or analyze with your preferred tool

## 📂 For Different Users

### 🔧 **Data Engineers & Developers**
Want to modify or run the pipeline? See [`data_engineering/`](data_engineering/README.md) for complete technical documentation, setup instructions, and architecture details.

### 📊 **Researchers & Analysts**
Need the data without technical setup? Use our **[Interactive Data Explorer](https://data-science-link.github.io/fentanyl-awareness/)** to browse the data or download [`fact_fentanyl_deaths_over_time.csv`](Final_Datasets/).

### 📈 **Visualizers & Presenters**
Explore the data online or download for use in Excel, R, or Python. Interactive documentation and data portal available at:
**https://data-science-link.github.io/fentanyl-awareness/**

## 🚀 Quick Access

- **🌐 Data Portal**: https://data-science-link.github.io/fentanyl-awareness/
- **📁 Download Data**: [`Final_Datasets/fact_fentanyl_deaths_over_time.csv`](Final_Datasets/fact_fentanyl_deaths_over_time.csv)
- **🏗️ Explore Code**: https://github.com/Data-Science-Link/fentanyl-awareness

## 📊 What's In The Data

The CSV includes:
- **Time Range**: 1999 - current
- **Geographic Level**: State-level
- **Metrics**: Death counts, population data, income, unemployment rates
- **Sources**: Official CDC mortality data (1999-2023) + provisional data (2018-current)

See [`Final_Datasets/README.md`](Final_Datasets/README.md) for the complete data dictionary.

## 🔄 How It Works

This repository automatically:
1. Processes CDC SODA API mortality data and US Census demographics
2. Validates and tests the data using automated checks
3. Updates the CSV, interactive portal, and documentation every Monday

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
