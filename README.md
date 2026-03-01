# 🎓 Ahmerdee Exam Practice (AEP) v1.0

**Nigeria's #1 JAMB CBT Platform** — Built with Flask (Python), OPay-inspired UI.

---

## 🚀 Quick Start

```bash
# 1. Install
pip install flask

# 2. Run
python app.py

# 3. Open browser
http://localhost:5000
```

---

## 👑 Admin Login

| Field    | Value                      |
|----------|----------------------------|
| Email    | `admin@ahmerdee.com`       |
| Password | `Ahmerdee@Admin2026`       |
| Role     | Super Admin (Founder)      |

> ⚠️ Change the admin password after first login via the profile page.

---

## 🌍 Languages Supported

| Code | Language | Script |
|------|----------|--------|
| `en` | English  | LTR    |
| `ha` | Hausa    | LTR    |
| `ar` | Arabic   | RTL ✅ |
| `zh` | Chinese  | LTR    |

Language switcher appears on every page. **English is the default.**

---

## 🔐 Registration System (JAMB Standard)

Students must provide:
- Full Name
- School Attended
- State of Origin
- Home Address
- Date of Birth
- Phone Number
- Email
- Password

After registration → **Unique Reg Number generated automatically**
```
Format: AEP20260001, AEP20260002, AEP20260003...
```

**Login with:** Email + Password  **OR**  Reg Number + Password

---

## 📚 Features

### Student Side
| Feature | Details |
|---------|---------|
| 📝 **Exam Mode** | 40 questions, 40-minute timer, certificate generated |
| 📚 **Practice Mode** | 20 questions, no timer, score only shown |
| ❓ **Quiz Mode** | 10 questions, instant feedback + explanation |
| ⚔️ **Duel Mode** | Challenge another student (UI ready) |
| 🏆 **Leaderboard** | Top students ranked by best exam score |
| 📖 **Library** | Download PDF books uploaded by admin |
| 💬 **Student Chat** | Direct messaging with online/offline status |
| ⚠️ **Report User** | Report inappropriate chat behavior |
| 🎫 **Support** | Send tickets to admin, receive replies |
| 🔔 **Notifications** | Receive broadcast messages from admin |
| 👤 **Profile** | Edit name, phone, address, change password |
| 🔍 **Certificate Verify** | Public verify page: `/verify/<ID>` |

### Admin Panel (`/admin`)
| Feature | Details |
|---------|---------|
| 👥 **Manage Users** | View all, search, warn/block/ban |
| ❓ **Questions** | Add, delete, bulk import per subject |
| 🏆 **Results** | All exam results with verify IDs |
| ⚠️ **Reports** | View and resolve user reports |
| 🎫 **Support** | View and reply to support tickets |
| 📚 **Books** | Upload PDFs for student library |
| 📢 **Broadcast** | Message all students OR specific student |

### Super Admin Only
| Feature | Details |
|---------|---------|
| 👑 **Manage Admins** | Promote/demote students to admin role |
| ⚙️ **Settings** | Exam duration, question count, maintenance mode |

---

## 📊 Subjects Available

26 JAMB subjects seeded with questions:
- English Language (30 Q), Mathematics (30 Q), Physics (30 Q)
- Chemistry (30 Q), Biology (30 Q), Economics (30 Q), Government (30 Q)
- + 19 more subjects (admin can add questions)

---

## 🏆 Certificate System

Exam mode generates:
- **Certificate** with candidate name, subject, score, grade
- **Unique Verify ID** (e.g. `A1B2C3D4`)
- **Ahmerdee watermark** on certificate
- **Anti-tamper**: any modification invalidates the verify ID
- **Public verification** at: `/verify/A1B2C3D4`
- **Admin receives copy** of all results

---

## 📦 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/verify_result/<id>` | GET | Verify certificate JSON |
| `/api/leaderboard` | GET | Top 20 students JSON |
| `/api/stats` | GET | Current user stats |
| `/api/chat/messages/<uid>` | GET | Chat messages |
| `/api/chat/send` | POST | Send chat message |
| `/api/online_status` | POST | Update online status |

---

## 🗂 File Structure

```
aep/
├── app.py                  ← All routes + logic (Flask)
├── requirements.txt        ← pip install flask
├── static/
│   ├── css/style.css       ← OPay-style dark UI
│   └── js/app.js           ← ExamEngine, QuizEngine, ChatEngine
├── templates/
│   ├── login.html
│   ├── register.html       ← JAMB-standard form
│   ├── dashboard.html
│   ├── subjects.html       ← 26 JAMB subjects
│   ├── exam.html           ← CBT with timer + navigator
│   ├── quiz.html           ← Instant quiz mode
│   ├── result.html         ← Certificate + verify ID
│   ├── my_results.html
│   ├── leaderboard.html
│   ├── chat.html           ← Student messaging
│   ├── duel.html           ← Duel challenge UI
│   ├── library.html        ← PDF books
│   ├── profile.html
│   ├── support.html
│   ├── notifications.html
│   ├── verify.html         ← Public certificate verifier
│   └── admin/
│       ├── dashboard.html
│       ├── users.html
│       ├── user_detail.html
│       ├── questions.html
│       ├── results.html
│       ├── reports.html
│       ├── support.html
│       ├── books.html
│       ├── broadcast.html
│       ├── admins.html     ← Super Admin only
│       └── settings.html   ← Super Admin only
└── data/                   ← JSON files (auto-created)
    ├── users.json
    ├── questions.json
    ├── results.json
    ├── chat.json
    ├── books/              ← Uploaded PDFs
    └── ...
```

---

## 🌐 Deployment (Railway / Render)

```bash
# Set environment variable
SECRET_KEY=your_secret_key_here

# For persistent data, mount a volume at /data
# Otherwise data resets on each deploy
```

**Procfile:**
```
web: python app.py
```

---

## 🔒 Security Notes

- Passwords hashed with SHA-256 + random salt
- Sessions permanent (1 year)
- Admin routes protected by role check decorators
- Super Admin cannot be modified by other admins
- Certificate verification IDs are cryptographically random

---

*Built with ❤️ for Nigerian students. Powered by Ahmerdee.*
