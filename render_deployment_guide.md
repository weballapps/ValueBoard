# Render Deployment Guide for Stock Value Dashboard

## Prerequisites
- GitHub account
- Render account (free tier available)
- Your code pushed to a GitHub repository

## Step 1: Prepare Your Repository

Ensure your repository contains these files:
- `requirements.txt` ✓ (already present)
- `stock_value_dashboard.py` ✓ (your main app file)
- `render.yaml` ✓ (created for automatic deployment)

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up using your GitHub account
3. Authorize Render to access your repositories

## Step 3: Deploy Your Application

### Option A: Using render.yaml (Recommended)

1. Push the `render.yaml` file to your repository
2. In Render dashboard, click **"New +"**
3. Select **"Blueprint"**
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` and configure your service

### Option B: Manual Setup

1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Configure the following settings:
   - **Name**: `stock-value-dashboard` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run stock_value_dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false`
   - **Plan**: `Free`

## Step 4: Environment Variables (Optional)

If your app needs environment variables:
1. Go to your service settings
2. Navigate to **"Environment"** tab
3. Add any required variables

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your Streamlit application
3. Deployment typically takes 2-5 minutes

## Step 6: Access Your App

Once deployed:
- Your app will be available at: `https://your-service-name.onrender.com`
- Free tier apps sleep after 15 minutes of inactivity
- Apps wake up automatically when accessed (may take 30-60 seconds)

## Important Notes

### Free Tier Limitations:
- 750 hours/month (usually sufficient for personal projects)
- Apps sleep after 15 minutes of inactivity
- Limited to 512MB RAM
- No custom domains on free tier

### Auto-Deployment:
- Render automatically redeploys when you push to your connected GitHub branch
- Check the **"Logs"** tab for deployment status and errors

### Troubleshooting:

**Build Fails:**
- Check the build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

**App Won't Start:**
- Check start command matches your file structure
- Verify Streamlit configuration flags
- Check application logs for runtime errors

**Performance Issues:**
- Free tier has limited resources
- Consider upgrading to paid tier for production use
- Optimize your app to reduce memory usage

## Security Considerations

- Your repository will be public if using GitHub free tier
- Consider using private repositories for sensitive code
- Don't commit API keys or secrets to your repository
- Use Render's environment variables for sensitive data

## Next Steps

1. Test your deployed application thoroughly
2. Set up monitoring (Render provides basic metrics)
3. Consider setting up a custom domain (paid plans)
4. Implement proper error handling in your app

Your Stock Value Dashboard is now live on Render! 🚀