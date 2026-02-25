# ⚡ QUICK START GUIDE

Get Ahmerdee Exam Practice running in 5 minutes!

## 🎯 What You'll Get

✅ Full-stack exam practice application  
✅ Offline & Online exam modes  
✅ Complete admin control panel  
✅ User management system  
✅ Question bank management  
✅ Automatic certificate generation  
✅ Beautiful OPay-inspired UI  
✅ Ready for Railway deployment  

---

## 🚀 Option 1: Deploy to Railway (RECOMMENDED)

### 1️⃣ Extract & Push to GitHub (2 minutes)

```bash
# Extract the zip file
unzip ahmerdee-exam-app-complete.zip
cd ahmerdee-exam-app

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
# (Create repo at github.com first)
git remote add origin https://github.com/YOUR_USERNAME/ahmerdee-exam-app.git
git push -u origin main
```

### 2️⃣ Deploy to Railway (2 minutes)

1. Go to **[railway.app](https://railway.app)**
2. Sign up/Login with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select **ahmerdee-exam-app**
5. Railway will auto-deploy ✨

### 3️⃣ Configure Environment (1 minute)

In Railway dashboard:
1. Click your service → **"Variables"**
2. Add these:
   ```
   PORT=3000
   NODE_ENV=production
   JWT_SECRET=ahmerdee_super_secret_2024_change_this
   ADMIN_EMAIL=admin@yourdomain.com
   ADMIN_PASSWORD=YourSecurePassword123!
   ```
3. Click **"Save"** (Railway will redeploy)

### 4️⃣ Get Your URL

1. Click **"Settings"** → **"Domains"**
2. Click **"Generate Domain"**
3. Copy your URL (e.g., `https://ahmerdee-xxx.up.railway.app`)

### ✅ DONE! Your app is live!

---

## 💻 Option 2: Run Locally

### Prerequisites
- Node.js 18+ installed
- Terminal/Command Prompt

### Steps

```bash
# Extract zip
unzip ahmerdee-exam-app-complete.zip
cd ahmerdee-exam-app

# Install dependencies
npm install

# Start server
npm start
```

### Access App
- URL: `http://localhost:3000`
- Admin Email: `admin@ahmerdee.com`
- Admin Password: `Admin@123`

---

## 🔑 First Login

### Admin Access
1. Open your app URL
2. Click **"Admin Login"** or go to `/admin`
3. Login with:
   - Email: Your `ADMIN_EMAIL` from env
   - Password: Your `ADMIN_PASSWORD` from env

### What You Can Do as Admin
- ✅ View dashboard statistics
- ✅ Manage users
- ✅ Upload questions (bulk or single)
- ✅ View all exam results
- ✅ Manage subjects
- ✅ Download certificates

---

## 📤 Upload Sample Questions

1. Login as admin
2. Go to **"Admin Panel"** → **"Questions"**
3. Click **"Bulk Upload"**
4. Upload `sample-questions.json` (included in zip)
5. ✨ 13 sample questions added!

---

## 👥 Create Student Account

### For Testing
1. Open app homepage
2. Click **"Register"**
3. Fill form:
   - Name: Test Student
   - Email: student@test.com
   - Password: password123
4. Login and take exams!

---

## 📱 Key Features

### For Students
- 📚 **Offline Practice**: No internet needed
- 🌐 **Online Exams**: Full JAMB simulation
- 📊 **Progress Tracking**: See your improvement
- 🎓 **Certificates**: Auto-generated PDFs
- 📈 **Statistics**: Performance analytics

### For Admins
- 👥 **User Management**: Full control
- 📝 **Question Bank**: Add, edit, delete
- 📤 **Bulk Upload**: JSON file upload
- 📊 **Analytics**: Dashboard metrics
- 🎯 **Results**: View all scores

---

## 🎨 Subjects Available

1. 🔢 Mathematics
2. ⚗️ Chemistry
3. ⚛️ Physics
4. 🧬 Biology
5. 📖 English
6. 🌍 Geography

---

## 📂 What's Included

```
ahmerdee-exam-app/
├── 📄 README.md              - Full documentation
├── 📄 DEPLOYMENT.md          - Railway deployment guide
├── 📄 API.md                 - Complete API docs
├── 📄 QUICKSTART.md          - This file!
├── 🗂️ routes/                - API endpoints
├── 🗂️ database/              - SQLite database
├── 🗂️ public/                - Frontend UI
├── 📦 package.json           - Dependencies
├── ⚙️ server.js              - Express server
├── 📋 sample-questions.json  - Test questions
└── 🚀 railway.json           - Railway config
```

---

## 🔧 Common Tasks

### Add More Questions
```bash
# Use the bulk upload feature in admin panel
# Or add manually one by one
```

### Change Admin Password
```bash
# Login → Profile → Change Password
# Or update ADMIN_PASSWORD in Railway
```

### View Logs (Railway)
```bash
# Railway Dashboard → Your Service → Deployments → View Logs
```

### Backup Database
```bash
# Railway automatically backs up
# Or download from Railway dashboard
```

---

## 📞 Need Help?

### Check These First:
1. ✅ Railway logs (if deployed)
2. ✅ Environment variables set correctly
3. ✅ Using Node.js 18+
4. ✅ All dependencies installed

### Documentation:
- 📖 **README.md** - Full features & setup
- 🚀 **DEPLOYMENT.md** - Deployment guide
- 📡 **API.md** - API documentation

### Support:
- Create issue on GitHub
- Check Railway Discord
- Email: admin@ahmerdee.com

---

## 🎉 Next Steps

1. ✅ **Upload Questions**: Use bulk upload with JSON
2. ✅ **Customize**: Change branding, colors, subjects
3. ✅ **Test**: Create test accounts and take exams
4. ✅ **Share**: Give URL to students
5. ✅ **Monitor**: Check Railway dashboard

---

## 🔐 Security Checklist

- [ ] Changed default admin password
- [ ] Set strong JWT_SECRET
- [ ] Updated ADMIN_EMAIL to your domain
- [ ] Tested login/logout flow
- [ ] Verified HTTPS is working (Railway auto-enables)

---

## 💡 Pro Tips

1. **Custom Domain**: Add your domain in Railway settings
2. **Email Alerts**: Integrate SendGrid for notifications
3. **Backups**: Download database weekly
4. **Monitoring**: Use Railway metrics dashboard
5. **Updates**: Pull changes and Railway auto-deploys

---

## 🚀 You're Ready!

Your Ahmerdee Exam Practice app is now:
- ✅ Deployed to Railway (or running locally)
- ✅ Accessible via HTTPS
- ✅ Admin panel configured
- ✅ Sample questions loaded
- ✅ Ready for students!

**Start URL**: Your Railway URL or `http://localhost:3000`

**Admin Login**: Your credentials from .env

**Have fun! 🎊**

---

Made with ❤️ by Ahmerdee Team
