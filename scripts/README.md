# Scripts Directory

This directory contains utility scripts for setting up and managing the CivicLogHOA application.

## Setup Scripts

### `create_admin_user.py`
Creates the initial admin user for the application.
- **Usage**: `python scripts/create_admin_user.py`
- **Purpose**: Sets up the first administrator account

### `create_admin_simple.py`
Creates a simplified admin user setup.
- **Usage**: `python scripts/create_admin_simple.py`
- **Purpose**: Alternative admin user creation with minimal configuration

### `create_test_data.py`
Creates comprehensive test data including HOAs, residents, and violations.
- **Usage**: `python scripts/create_test_data.py`
- **Purpose**: Populates the database with sample data for testing

### `create_test_data_simple.py`
Creates simplified test data.
- **Usage**: `python scripts/create_test_data_simple.py`
- **Purpose**: Creates basic test data with minimal complexity

### `create_test_data_final.py`
Creates the final version of test data with all features.
- **Usage**: `python scripts/create_test_data_final.py`
- **Purpose**: Creates complete test dataset with all HOA features

### `create_violations_only.py`
Creates only violation records without other data.
- **Usage**: `python scripts/create_violations_only.py`
- **Purpose**: Adds violation records to existing HOAs and residents

## Utility Scripts

### `run_performance_migration.py`
Runs performance optimization migrations.
- **Usage**: `python scripts/run_performance_migration.py`
- **Purpose**: Applies database performance improvements

### `deploy_with_optimizations.sh`
Deployment script with performance optimizations.
- **Usage**: `bash scripts/deploy_with_optimizations.sh`
- **Purpose**: Deploys the application with all optimizations enabled

## Usage Notes

1. **Database Connection**: Ensure the database is running before executing scripts
2. **Environment**: Scripts should be run from the project root directory
3. **Dependencies**: Make sure all Python dependencies are installed
4. **Backup**: Consider backing up your database before running data creation scripts

## Example Workflow

```bash
# 1. Create admin user
python scripts/create_admin_user.py

# 2. Create test data
python scripts/create_test_data_final.py

# 3. Run performance optimizations
python scripts/run_performance_migration.py
``` 