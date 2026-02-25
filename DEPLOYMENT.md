# 🚀 Railway Deployment Guide

This guide will help you deploy Ahmerdee Exam Practice app to Railway.app

## Prerequisites

- GitHub account
- Railway.app account (free tier available)
- Git installed on your computer

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Download and Extract** the zip file
2. **Open Terminal/Command Prompt** in the extracted folder
3. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Ahmerdee Exam Practice"
```

### Step 2: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click the "+" icon → "New repository"
3. Name it `ahmerdee-exam-practice`
4. **Don't** initialize with README (we already have one)
5. Click "Create repository"

### Step 3: Push to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/ahmerdee-exam-practice.git

# Push your code
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Railway

1. **Go to Railway**
   - Visit [railway.app](https://railway.app)
   - Sign up or login (use GitHub for easy integration)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `ahmerdee-exam-practice` repository

3. **Railway Auto-Detection**
   - Railway will automatically detect Node.js
   - It will install dependencies and start the server

### Step 5: Configure Environment Variables

1. **In Railway Dashboard**, click on your deployed service
2. Go to **"Variables"** tab
3. Add these environment variables:

```
PORT=3000
NODE_ENV=production
JWT_SECRET=<generate-a-random-secure-string>
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=<your-secure-admin-password>
```

**To generate JWT_SECRET** (use one of these):
- Random string: `ahmerdee_2024_super_secret_key_$(date +%s)_random`
- Or use online generator: [RandomKeygen.com](https://randomkeygen.com/)

4. **Click "Save"** - Railway will automatically redeploy

### Step 6: Access Your Application

1. In Railway dashboard, find your service
2. Click on **"Settings"** tab
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**
5. Railway will provide a URL like: `https://ahmerdee-exam-practice-production.up.railway.app`

### Step 7: Test Your Deployment

1. Open the Railway-provided URL
2. You should see the Ahmerdee Exam Practice app
3. Test admin login:
   - Email: The one you set in `ADMIN_EMAIL`
   - Password: The one you set in `ADMIN_PASSWORD`

## 🎯 Post-Deployment Tasks

### Change Default Admin Password

1. Login with default credentials
2. Go to Profile/Settings
3. Change password immediately

### Upload Sample Questions

1. Login as admin
2. Go to Admin Panel → Questions
3. Use bulk upload with `sample-questions.json`

### Monitor Your App

Railway provides:
- Real-time logs
- Metrics (CPU, Memory, Network)
- Automatic HTTPS
- Auto-deploy on Git push

## 🔧 Common Issues & Solutions

### Issue: "Application Error"
**Solution**: Check Railway logs
```
1. Go to Railway dashboard
2. Click your service
3. Click "Deployments"
4. View logs for errors
```

### Issue: Database not found
**Solution**: Railway automatically creates the database folder
- No action needed, it's handled automatically

### Issue: Cannot login as admin
**Solution**: Check environment variables
```
1. Ensure ADMIN_EMAIL is set correctly
2. Ensure ADMIN_PASSWORD is set correctly
3. Redeploy after changes
```

### Issue: 502 Bad Gateway
**Solution**: 
```
1. Check if PORT is set to 3000
2. Ensure server.js listens on 0.0.0.0
3. Check Railway logs for startup errors
```

## 📊 Railway Free Tier Limits

- $5 free credit per month
- Enough for development and small production
- Automatic sleep after inactivity (hobby plan)
- Can upgrade to paid plan anytime

## 🔄 Continuous Deployment

Railway automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push origin main
# Railway will automatically deploy
```

## 🌐 Custom Domain (Optional)

1. In Railway dashboard → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain (e.g., exam.yourdomain.com)
4. Follow DNS configuration instructions
5. Railway provides free SSL certificate

## 💾 Database Backup

Railway provides automatic backups, but you can also:

```bash
# Download database manually
railway run sqlite3 database/ahmerdee.db .dump > backup.sql
```

## 📧 Email Configuration (Future)

To add email notifications:
1. Add email service (SendGrid, Mailgun)
2. Update environment variables
3. Implement email routes

## 🔐 Security Best Practices

1. ✅ Change default admin password
2. ✅ Use strong JWT_SECRET
3. ✅ Enable HTTPS (Railway does this automatically)
4. ✅ Regular database backups
5. ✅ Monitor Railway logs

## 📱 Connecting Android App

Use the Railway URL in your Android app:

```java
// In your Android app constants
public static final String BASE_URL = "https://your-app.up.railway.app/api/";
```

## 🆘 Need Help?

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- GitHub Issues: Create issue in your repository

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables configured
- [ ] Domain generated
- [ ] Admin login tested
- [ ] Sample questions uploaded
- [ ] SSL certificate active (automatic)
- [ ] Monitoring setup

## 🎉 Success!

Your Ahmerdee Exam Practice app is now live!

Share your Railway URL with users and start conducting exams!

---

**Questions?** Check Railway logs first, they show detailed error messages.

**Performance Issues?** Upgrade to Railway Pro for better resources.

**Need Changes?** Just push to GitHub and Railway auto-deploys!
