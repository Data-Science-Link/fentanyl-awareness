# Data Build Tool (dbt)

This folder contains the complete dbt project for transforming fentanyl awareness data from raw sources into analytical models.

## 📁 Structure

```
data_build_tool/
├── dbt/                          # dbt project files
│   ├── models/
│   │   ├── staging/              # Data cleaning models
│   │   └── marts/                # Final analytical models
│   ├── seeds/                     # Raw data files
│   ├── tests/                     # Data quality tests
│   └── macros/                    # Reusable SQL macros
├── dbt_project.yml               # dbt configuration
├── packages.yml                   # Package dependencies
├── package-lock.yml               # Locked package versions
├── fentanyl_awareness.duckdb     # DuckDB database
├── logs/                          # dbt execution logs
├── target/                        # Compiled artifacts
└── dbt_packages/                  # Installed packages
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- dbt-core
- dbt-duckdb

### Installation
```bash
# Install dbt and DuckDB adapter
pip install dbt-core dbt-duckdb

# Install package dependencies
dbt deps
```

### Running the Pipeline
```bash
# Load raw data
dbt seed

# Transform data
dbt run

# Test data quality
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## 📊 Data Models

### Staging Models
- `stg_cdc_api_provisional_overdose_counts` - Provisional drug overdose death counts from CDC API
- `stg_census_state_population` - Population estimates
- `stg_census_state_economic` - Economic indicators

### Mart Models
- `fact_fentanyl_deaths_over_time` - Final analytical dataset

## 🔧 Configuration

### dbt_project.yml
Main configuration file defining:
- Project name and version
- Model configurations
- Test configurations
- Macro paths
- Seed configurations

### packages.yml
Defines external package dependencies:
- `dbt_utils` - Utility macros and tests

## 📈 Data Flow

```
Raw Data Sources → Seeds → Staging Models → Mart Models → Final Dataset
     ↓               ↓           ↓              ↓            ↓
CDC SODA API    → Seeds     → Cleaned Data → Analytics → CSV Export
Census Data     → Seeds     → Validated    → Combined  → Google Sheets
Other Sources  → Raw Data  → Standardized → Enriched  → Final Output
```

## 🧪 Testing

### Built-in Tests
- **Unique tests** - Ensure primary key uniqueness
- **Not null tests** - Validate required fields
- **Accepted values** - Check value constraints
- **Relationships** - Verify foreign key integrity

### Custom Tests
- **Data freshness** - Check data recency
- **Completeness** - Validate data coverage
- **Consistency** - Cross-source validation

### Running Tests
```bash
# Run all tests
dbt test

# Run specific test
dbt test --select test_name

# Run tests for specific model
dbt test --select model_name
```

## 📝 Documentation

### Model Documentation
Each model includes:
- **Description** - Purpose and business logic
- **Columns** - Field descriptions and types
- **Tests** - Data quality checks
- **Dependencies** - Upstream models

### Generating Docs
```bash
# Generate documentation
dbt docs generate

# Serve locally
dbt docs serve
```

## 🔍 Querying Data

### Using DuckDB CLI
```bash
# Connect to database
duckdb fentanyl_awareness.duckdb

# List tables
.tables

# Query data
SELECT * FROM fact_fentanyl_deaths_over_time LIMIT 10;
```

### Using Python
```python
import duckdb

# Connect and query
conn = duckdb.connect('fentanyl_awareness.duckdb')
df = conn.execute('SELECT * FROM fact_fentanyl_deaths_over_time').fetchdf()
conn.close()
```

## 🛠️ Development

### Adding New Models
1. Create SQL file in appropriate folder
2. Add model documentation
3. Define tests
4. Update schema.yml

### Adding New Tests
1. Create test SQL file
2. Reference in schema.yml
3. Run with `dbt test`

### Debugging
- Check logs in `logs/` folder
- Use `dbt compile` to check SQL
- Use `dbt parse` to validate syntax

## 📊 Performance

### Optimization Tips
- Use incremental models for large datasets
- Implement proper indexing strategies
- Monitor query performance
- Use materialized views for complex calculations

### Monitoring
- Review execution logs
- Monitor model run times
- Check test failures
- Validate data quality metrics

## 🔄 Automation

The data engineering pipeline is automated via GitHub Actions:
- **Weekly runs** - Automated data refresh
- **Quality checks** - Automated testing
- **Documentation** - Auto-generated docs
- **Deployment** - Automated model deployment

## 📞 Support

For issues with the data engineering pipeline:
1. Check the logs in `logs/` folder
2. Review model documentation
3. Run tests to identify issues
4. Check dbt documentation
5. Open a GitHub issue with details
