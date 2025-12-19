# Deploying to Render.com

This guide walks you through deploying your Django School Management System with PostgreSQL on Render.com.

## Prerequisites

- A GitHub repository with your code (already done!)
- A Render.com account (free tier available)

## Step-by-Step Deployment

### 1. Create a Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub (easiest option)
- Authorize Render to access your GitHub account

### 2. Create PostgreSQL Database on Render

1. **Dashboard** → Click **"New +"** → Select **"PostgreSQL"**
2. **Configure Database:**
   - Name: `school-management-db`
   - Database: `schoolms_db`
   - User: `schoolms_user`
   - Region: Select closest to your location (e.g., Ohio, Frankfurt)
   - Plan: Free tier (0.5GB, auto-pauses after 15 minutes of inactivity)
3. **Copy the Internal Database URL** - you'll need this for the web service

### 3. Create Web Service on Render

1. **Dashboard** → Click **"New +"** → Select **"Web Service"**
2. **Connect Repository:**
   - Select your GitHub repository
   - Select branch: `master`
3. **Configure Service:**
   - Name: `school-management`
   - Environment: `Python 3`
   - Region: Same as your database
   - Branch: `master`
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn school_management.wsgi --log-file -`
   - Plan: Free tier

### 4. Set Environment Variables

In the **Web Service** settings, go to **"Environment"** and add these variables:

```
DEBUG=False
USE_POSTGRESQL=True
SECRET_KEY=your-secret-key-here (generate a secure one)
ALLOWED_HOSTS=your-service-name.onrender.com
DATABASE_URL=<paste the internal database URL from step 2>
```

**To generate a secure SECRET_KEY:**
```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Deploy

1. Click the **"Deploy"** button (or it may deploy automatically on push)
2. Watch the **Logs** tab for build progress
3. Once deployed, your app will be at: `https://your-service-name.onrender.com`

## Important Notes

### Free Tier Limitations
- **Web Service**: Auto-pauses after 15 minutes of inactivity
- **Database**: 0.5GB storage, auto-pauses after 15 minutes of inactivity
- To keep services active, either:
  - Upgrade to paid plan
  - Use external monitoring service to ping your site every 14 minutes

### Static Files
- WhiteNoise is configured to serve static files automatically
- CSS and JS files are compressed and cached
- Media files (if used) should be stored in a separate service or S3-compatible storage

### Database Migrations
- Migrations run automatically during build phase
- If you need to manually run migrations:
  ```
  render-cli connect school-management-db
  python manage.py migrate
  ```

## Troubleshooting

### Service won't start
1. Check **Logs** for error messages
2. Ensure `Procfile` is in root directory
3. Verify `requirements.txt` has all dependencies

### Database connection failed
1. Verify `DATABASE_URL` is correctly set
2. Check database service is running
3. Ensure credentials are correct

### Static files not loading
1. Run: `python manage.py collectstatic`
2. Check `STATIC_ROOT` and `STATIC_URL` in settings
3. Verify WhiteNoise middleware is first in `MIDDLEWARE`

### Application crashes after deployment
1. Check environment variables are set
2. Verify `SECRET_KEY` is set
3. Check database migrations completed
4. Review logs for specific error messages

## Files Added for Render Deployment

- `requirements.txt` - Python dependencies with Gunicorn and WhiteNoise
- `Procfile` - Tells Render how to run the application
- `render.yaml` - Optional: Infrastructure as Code configuration
- Updated `settings.py` - Production security settings and database configuration

## Next Steps

After successful deployment:

1. **Set up a custom domain** (if desired)
   - Go to Web Service settings → Custom Domain
   - Add your domain and follow DNS instructions

2. **Create admin user** (if not migrated from local database)
   ```
   render-cli connect school-management
   python manage.py createsuperuser
   ```

3. **Monitor logs regularly**
   - Check Render dashboard for any errors
   - Monitor database storage usage

4. **Enable auto-deploy**
   - Any push to `master` branch will automatically redeploy

## Database Backup

To backup your PostgreSQL database on Render:
1. Go to database service → "Backups" tab
2. Click "Create Backup"
3. Download backup file for safe storage

## Upgrading Plans

When you're ready for production:
- Upgrade web service to **Starter** ($7/month) - no auto-pause
- Upgrade database to **Standard** ($15/month) - 10GB storage, no auto-pause

---

**Support**: For Render-specific issues, visit [render.com/docs](https://render.com/docs)
