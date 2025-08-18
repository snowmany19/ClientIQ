# ContractGuard.ai - Test Contract Generation & Analysis Scripts

This directory contains scripts for generating realistic test contracts and automatically running them through the ContractGuard.ai AI analysis workflow.

## 🚀 Quick Start

### 1. Generate Test Contracts
```bash
cd scripts
python3 generate_test_contracts_simple.py
```

### 2. Upload & Analyze Contracts
```bash
python3 upload_and_analyze_contracts.py
```

## 📁 Scripts Overview

### `generate_test_contracts_simple.py`
Generates realistic test contracts for all 7 contract types supported by ContractGuard.ai:

- **NDA** (Non-Disclosure Agreement) - 2 contracts
- **MSA** (Master Services Agreement) - 3 contracts  
- **SOW** (Statement of Work) - 3 contracts
- **Employment** - 3 contracts
- **Vendor** - 3 contracts
- **Lease** - 3 contracts
- **Other** - 2 contracts

**Total: 19 contracts** with randomized content for training variety.

### `upload_and_analyze_contracts.py`
Automatically uploads generated contracts through the API and triggers AI analysis:

1. **Login** with admin credentials
2. **Create** contract records in the database
3. **Upload** contract text files
4. **Trigger** AI analysis for each contract
5. **Report** success/failure statistics

## 🔧 Features

### Contract Generation
- **Realistic Content**: Professional contract language and structure
- **Randomized Elements**: Company names, dates, terms, penalties, etc.
- **Category-Specific**: Each contract type has appropriate clauses and focus areas
- **Consistent Format**: Standard legal document structure

### Automated Workflow
- **API Integration**: Uses ContractGuard.ai REST API
- **Error Handling**: Graceful failure handling and reporting
- **Progress Tracking**: Real-time status updates
- **Batch Processing**: Handles multiple contracts efficiently

### Training Data Variety
- **Multiple Categories**: Covers all supported contract types
- **Different Scenarios**: Various business contexts and terms
- **Risk Patterns**: Includes common risk factors for AI training
- **Compliance Elements**: Different governing laws and jurisdictions

## 📊 Generated Contract Examples

### NDA Contracts
- Focus areas: software development, research collaboration, business partnership
- Terms: 2-5 years, perpetual, until termination
- Penalties: $100K-$500K, actual damages, liquidated damages

### MSA Contracts
- Focus areas: IT consulting, marketing services, legal services
- Terms: 1-5 years, auto-renewing
- Payment: Net 30-60, upfront, monthly billing

### SOW Contracts
- Focus areas: website development, mobile apps, system integration
- Deliverables: functional products, documentation, training materials
- Timelines: 30 days to 1 year

### Employment Contracts
- Positions: Software Engineer, Marketing Manager, Sales Representative
- Compensation: salary, hourly, commission-based, equity
- Benefits: health insurance, 401k, stock options, flexible PTO

### Vendor Contracts
- Services: office supplies, cleaning, IT equipment, marketing materials
- Performance: 99% uptime, 24-hour response, same-day delivery
- Payment: Net 30-60, monthly/quarterly billing

### Lease Contracts
- Property types: office space, retail, warehouse, apartment
- Terms: 1-5 years, month-to-month
- Utilities: electricity, water, gas, internet, all included

### Other Contracts
- Types: partnership, collaboration, joint venture, licensing
- Focus: business development, market expansion, technology transfer

## 🎯 Use Cases

### AI Model Training
- **Risk Assessment**: Train AI to identify contract risks
- **Category Classification**: Improve contract type recognition
- **Term Extraction**: Enhance key term identification
- **Compliance Checking**: Train regulatory compliance detection

### System Testing
- **API Endpoints**: Test all contract-related endpoints
- **File Upload**: Verify document processing
- **Analysis Pipeline**: Test AI analysis workflow
- **Performance**: Measure system response times

### Quality Assurance
- **Content Validation**: Ensure generated contracts are realistic
- **Error Handling**: Test system robustness
- **User Experience**: Validate end-to-end workflow
- **Data Consistency**: Verify database integrity

## 🔄 Workflow

### Step 1: Generate Contracts
```bash
python3 generate_test_contracts_simple.py
```
- Creates `test_contracts/` directory
- Generates 19 contract files with realistic content
- Each file named: `Category_Number_Counterparty.txt`

### Step 2: Upload & Analyze
```bash
python3 upload_and_analyze_contracts.py
```
- Logs in as admin user
- Creates contract records in database
- Uploads contract text files
- Triggers AI analysis for each contract

### Step 3: Review Results
- Check ContractGuard.ai dashboard
- Review AI analysis results
- Analyze risk assessments
- Evaluate AI model performance

## 📈 Training Benefits

### For AI Model
- **Diverse Data**: 7 contract categories with multiple examples
- **Realistic Scenarios**: Business-appropriate content and terms
- **Risk Patterns**: Common contract risk factors for learning
- **Compliance Examples**: Various legal jurisdictions and requirements

### For System Testing
- **API Coverage**: Tests all contract endpoints
- **Error Scenarios**: Identifies potential failure points
- **Performance Metrics**: Measures system response times
- **User Workflows**: Validates complete user journeys

## 🛠️ Customization

### Modify Contract Templates
Edit `CONTRACT_TEMPLATES` in `generate_test_contracts_simple.py`:
- Add new contract categories
- Modify focus areas and risk factors
- Adjust company names and scenarios
- Change contract terms and conditions

### Adjust Generation Parameters
- **Contract Count**: Change `num_contracts` per category
- **Content Length**: Modify contract template complexity
- **Randomization**: Adjust date ranges and term variations
- **Company Variety**: Add more company names and scenarios

### Custom Analysis Workflow
Modify `upload_and_analyze_contracts.py`:
- Add custom validation steps
- Implement different analysis triggers
- Add result verification
- Customize error handling

## 📋 Requirements

### System Requirements
- Python 3.7+
- ContractGuard.ai backend running on localhost:8000
- Admin user account (admin/test123)
- Network access to backend API

### Dependencies
- `requests` library for HTTP API calls
- Standard Python libraries (os, sys, json, time, datetime)

## 🚨 Troubleshooting

### Common Issues
1. **Backend Not Running**: Ensure ContractGuard.ai backend is started
2. **Authentication Failed**: Verify admin credentials are correct
3. **API Endpoints**: Check if backend routes are properly configured
4. **File Permissions**: Ensure script can read/write to directories

### Debug Steps
1. Check backend logs for errors
2. Verify API endpoints are accessible
3. Test authentication manually
4. Check file paths and permissions
5. Review network connectivity

## 🔮 Future Enhancements

### Planned Features
- **PDF Generation**: Create PDF versions of contracts
- **Batch Analysis**: Parallel processing for faster analysis
- **Result Export**: Export analysis results to CSV/JSON
- **Custom Templates**: User-defined contract templates
- **Performance Metrics**: Detailed timing and success rate analysis

### Integration Opportunities
- **CI/CD Pipeline**: Automated testing in deployment
- **Load Testing**: Performance testing with large contract volumes
- **Quality Gates**: Automated quality checks for AI analysis
- **Training Loops**: Continuous improvement of AI models

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs for error details
3. Verify API endpoint configurations
4. Test with a single contract first
5. Check network and authentication settings

## 📄 License

These scripts are part of the ContractGuard.ai platform and follow the same licensing terms. 