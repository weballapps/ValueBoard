# 🔧 Favorites Setup Guide - Google Sheets Integration

This guide explains how to set up the Google Sheets API for the Favorites functionality.

## 📋 Overview

The Favorites system uses Google Sheets to store user favorites persistently across sessions and deployments. Each user can maintain their own favorites organized by categories.

## 🚀 Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Name it something like "Stock-Dashboard-Favorites"

### 2. Enable Google Sheets API

1. In the Google Cloud Console, go to **APIs & Services > Library**
2. Search for "Google Sheets API"
3. Click on it and press **Enable**
4. Also enable "Google Drive API" (required for creating/accessing sheets)

### 3. Create Service Account

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > Service Account**
3. Enter details:
   - **Service Account Name**: `favorites-manager`
   - **Description**: `Service account for managing user favorites`
4. Click **Create and Continue**
5. Skip role assignment (click **Continue**)
6. Click **Done**

### 4. Generate Service Account Key

1. Click on the created service account email
2. Go to **Keys** tab
3. Click **Add Key > Create New Key**
4. Select **JSON** format
5. Click **Create** - this downloads the JSON file
6. **Keep this file secure!** It contains your credentials

### 5. Create Google Sheet (Optional)

The app will create the sheet automatically, but you can create it manually:

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new sheet named "Stock_Favorites"
3. Share it with your service account email (from step 3)
   - Give **Editor** permissions
   - Service account email looks like: `favorites-manager@your-project.iam.gserviceaccount.com`

## 🔧 Streamlit Configuration

### For Local Development

Create `.streamlit/secrets.toml` file:

```toml
[google_sheets]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
client_email = "favorites-manager@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/favorites-manager%40your-project.iam.gserviceaccount.com"

favorites_sheet_name = "Stock_Favorites"
```

**Note**: Replace all `your-*` values with actual values from your JSON file.

### For Render Deployment

1. Go to your Render dashboard
2. Select your app
3. Go to **Environment** tab
4. Add these environment variables:

```
GOOGLE_SHEETS_TYPE = service_account
GOOGLE_SHEETS_PROJECT_ID = your-project-id
GOOGLE_SHEETS_PRIVATE_KEY_ID = your-private-key-id
GOOGLE_SHEETS_PRIVATE_KEY = -----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n
GOOGLE_SHEETS_CLIENT_EMAIL = favorites-manager@your-project.iam.gserviceaccount.com
GOOGLE_SHEETS_CLIENT_ID = your-client-id
GOOGLE_SHEETS_AUTH_URI = https://accounts.google.com/o/oauth2/auth
GOOGLE_SHEETS_TOKEN_URI = https://oauth2.googleapis.com/token
GOOGLE_SHEETS_AUTH_PROVIDER_X509_CERT_URL = https://www.googleapis.com/oauth2/v1/certs
GOOGLE_SHEETS_CLIENT_X509_CERT_URL = https://www.googleapis.com/robot/v1/metadata/x509/favorites-manager%40your-project.iam.gserviceaccount.com

FAVORITES_SHEET_NAME = Stock_Favorites
```

## 📊 Sheet Structure

The system automatically creates a sheet with these columns:

| user_id | symbol | symbol_type | category    | company_name | date_added      |
|---------|--------|-------------|-------------|--------------|-----------------|
| john    | AAPL   | stock       | Tech        | Apple Inc    | 2024-01-15 10:30|
| mary    | SPY    | etf         | Core        | S&P 500 ETF  | 2024-01-16 14:20|

## 🎯 Features

### Multi-User Support
- Each user identified by username
- Separate favorites for each user
- User switching in Favorites tab

### Categories
- Custom categories for organization
- Default categories: Tech, Finance, Healthcare, Energy, Consumer, Industrial
- Users can create new categories
- Reorganize favorites between categories

### Cross-Tab Integration
- Add favorites from Individual Stock Analysis
- Add favorites from ETF Dashboard  
- Add favorites from Company Search results
- Quick navigation from Favorites back to analysis

## 🔒 Security Notes

1. **Never commit** your service account JSON file to version control
2. Use environment variables for production deployments
3. Service account has minimal permissions (only Sheets and Drive access)
4. Consider rotating service account keys periodically

## 🐛 Troubleshooting

### "Google Sheets credentials not found"
- Check your secrets.toml file format
- Ensure all required fields are present
- Verify indentation in TOML file

### "Permission denied" errors
- Ensure the service account email has access to the sheet
- Check that both Google Sheets API and Google Drive API are enabled
- Verify the service account key is valid

### "Spreadsheet not found"
- The app will create the sheet automatically
- Make sure the service account has Drive API access
- Check the sheet name in your configuration

## 📝 Usage

1. **Set Username**: Go to Favorites tab, enter your username
2. **Add Favorites**: Use ⭐ buttons throughout the app
3. **Organize**: Create categories and move favorites between them
4. **Quick Analysis**: Click 📊 Analyze from Favorites to jump to detailed analysis

## 🚀 Next Steps

After setup, test the system:
1. Start the app: `streamlit run stock_value_dashboard.py`
2. Go to Favorites tab
3. Enter a username
4. Navigate to other tabs and add some favorites
5. Return to Favorites tab to see them organized by category