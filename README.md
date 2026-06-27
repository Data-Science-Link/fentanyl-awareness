# Fentanyl Awareness Data Pipeline

This project was born out of a grave concern for the fentanyl crisis in the United States. I had heard how devastating the situation was, but when I tried to find granular, state-level, monthly data to understand if it was getting better or worse, I couldn't find a single, easily accessible, cleaned national source. While some states have excellent dashboards, a comprehensive national view was missing.

Every life lost to this epidemic is a tragedy. We remember the victims, we feel for their families, and we hope that by making this data transparent and accessible, we can contribute to getting this situation under control so that fewer loved ones are taken from us too soon. This is not just a data project; it is an effort to bring visibility to a serious public health crisis.

## 🎯 What This Project Provides

- **📊 Granular Data**: State-level monthly death counts (provisional and official).
- **Interactive Data Portal**: Browse, filter, and export data directly from your browser.
- **📚 Live Documentation**: Complete pipeline and data lineage docs updated weekly.
- **🔄 Automated Updates**: Fresh data published every Monday at 12:00 PM UTC.
- **📈 Easy Access**: Download CSV, explore online, or analyze with your preferred tool.

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
- **💻 Frontend Source**: [`website/`](website/)

## 📊 What's In The Data

The CSV includes:
- **Time Range**: 1999 - current
- **Geographic Level**: State-level
- **Metrics**: Death counts, population data, income, unemployment rates
- **Sources**: Official CDC mortality data (1999-2023) + provisional data (2018-current)

See [`Final_Datasets/README.md`](Final_Datasets/README.md) for the complete data dictionary.

## 🔄 How It Works

This repository automatically:
1. Processes CDC SODA API mortality data and US Census demographics.
2. Validates and tests the data using automated checks.
3. Updates the CSV, interactive portal, and documentation every Monday.

Everything runs on GitHub Actions - no manual intervention needed.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CDC WONDER**: For providing comprehensive mortality data.
- **US Census Bureau**: For population and economic data.
- **GitHub**: For hosting and automation infrastructure.

---

**Note**: This data is for educational and awareness purposes. Every death represented here is a human tragedy. Always verify data accuracy and consult official sources for policy decisions.
