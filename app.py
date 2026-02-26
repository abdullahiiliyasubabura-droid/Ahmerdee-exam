"""
Ahmerdee Exam Practice (AEP) v1.0
- JAMB CBT Platform
- 4 Languages: English (default), Hausa, Arabic, Chinese
- OPay/PalmPay-inspired Mobile UI
- Admin + Super Admin Panel
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import json, os, hashlib, secrets, random, string, re, io
from datetime import datetime, timedelta
from functools import wraps

_HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            template_folder=os.path.join(_HERE, "templates"),
            static_folder=os.path.join(_HERE, "static"))
app.secret_key = os.environ.get("SECRET_KEY", "aep_secret_key_ahmerdee_2026_xk9z")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 365

APP_NAME = "Ahmerdee Exam Practice"
APP_SHORT = "AEP"
VERSION = "1.0"

# ============================================================
# DATA PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOLUME_DIR = "/data"
LOCAL_DIR = os.path.join(BASE_DIR, "data")
if os.path.exists(VOLUME_DIR) and os.access(VOLUME_DIR, os.W_OK):
    DATA_DIR = VOLUME_DIR
else:
    DATA_DIR = LOCAL_DIR

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "books"), exist_ok=True)

def dp(f): return os.path.join(DATA_DIR, f)

USERS_FILE        = dp("users.json")
QUESTIONS_FILE    = dp("questions.json")
EXAMS_FILE        = dp("exams.json")
RESULTS_FILE      = dp("results.json")
CHAT_FILE         = dp("chat.json")
REPORTS_FILE      = dp("reports.json")
BOOKS_FILE        = dp("books.json")
SUPPORT_FILE      = dp("support.json")
BROADCAST_FILE    = dp("broadcasts.json")
DUELS_FILE        = dp("duels.json")
SETTINGS_FILE     = dp("settings.json")

# ============================================================
# SUPER ADMIN
# ============================================================
SUPER_ADMIN_EMAIL    = "admin@ahmerdee.com"
SUPER_ADMIN_PASSWORD = "Ahmerdee@Admin2026"
SUPER_ADMIN_NAME     = "Ahmerdee (Founder)"

# ============================================================
# TRANSLATIONS
# ============================================================
TRANSLATIONS = {
    "en": {
        "app_name": "Ahmerdee Exam Practice",
        "app_short": "AEP",
        "tagline": "Nigeria's #1 JAMB CBT Platform",
        "login": "Login",
        "register": "Register",
        "email": "Email Address",
        "password": "Password",
        "full_name": "Full Name",
        "school": "School Attended",
        "state": "State of Origin",
        "address": "Home Address",
        "dob": "Date of Birth",
        "phone": "Phone Number",
        "confirm_password": "Confirm Password",
        "create_account": "Create Account",
        "login_now": "Login Now",
        "welcome_back": "Welcome back",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "exam_mode": "Exam Mode",
        "practice_mode": "Practice Mode",
        "quiz_mode": "Quiz Mode",
        "duel_mode": "Duel Mode",
        "library": "Book Library",
        "chat": "Student Chat",
        "profile": "Profile",
        "support": "Support",
        "logout": "Logout",
        "start_exam": "Start Exam",
        "start_practice": "Start Practice",
        "start_quiz": "Start Quiz",
        "challenge": "Challenge",
        "submit": "Submit",
        "next": "Next",
        "previous": "Previous",
        "finish": "Finish Exam",
        "result": "Result",
        "certificate": "Certificate",
        "score": "Your Score",
        "reg_number": "Registration Number",
        "my_results": "My Results",
        "leaderboard": "Leaderboard",
        "notifications": "Notifications",
        "send_message": "Send Message",
        "report": "Report User",
        "block": "Block",
        "warn": "Warn",
        "ban": "Ban",
        "admin_panel": "Admin Panel",
        "manage_questions": "Manage Questions",
        "manage_users": "Manage Users",
        "manage_books": "Manage Books",
        "broadcast": "Broadcast",
        "view_results": "View Results",
        "add_question": "Add Question",
        "edit": "Edit",
        "delete": "Delete",
        "save": "Save",
        "cancel": "Cancel",
        "search": "Search",
        "online": "Online",
        "offline": "Offline",
        "winner": "Winner",
        "loser": "Loser",
        "time_left": "Time Left",
        "question": "Question",
        "of": "of",
        "correct": "Correct!",
        "wrong": "Wrong!",
        "explanation": "Explanation",
        "read": "Read",
        "download": "Download",
        "upload_book": "Upload Book",
        "complaint": "Send Complaint",
        "reply": "Reply",
        "all_users": "All Users",
        "user_detail": "User Detail",
        "registration_success": "Registration successful! Your Reg. Number is:",
        "login_reg": "Login with Reg. Number",
        "or": "OR",
        "choose_subject": "Choose Subject",
        "select_lang": "Select Language",
        "lang_en": "English",
        "lang_ha": "Hausa",
        "lang_ar": "Arabic",
        "lang_zh": "Chinese",
        "super_admin": "Super Admin",
        "add_admin": "Add Admin",
        "remove_admin": "Remove Admin",
        "promote_admin": "Promote",
        "demote_admin": "Demote",
    },
    "ha": {
        "app_name": "Ahmerdee Jarrabawar Karatu",
        "app_short": "AEP",
        "tagline": "Babban Dandalin CBT na JAMB a Najeriya",
        "login": "Shiga",
        "register": "Yi Rajista",
        "email": "Adireshin Imel",
        "password": "Kalmar Sirri",
        "full_name": "Cikakken Suna",
        "school": "Makaranta da Ka/Ki Kammala",
        "state": "Jihar Asali",
        "address": "Adireshi na Gida",
        "dob": "Ranar Haihuwa",
        "phone": "Lambar Waya",
        "confirm_password": "Tabbatar da Kalmar Sirri",
        "create_account": "Buɗe Asusun",
        "login_now": "Shiga Yanzu",
        "welcome_back": "Maraba da dawowa",
        "dashboard": "Allon Sarrafa",
        "subjects": "Darussan",
        "exam_mode": "Yanayin Jarrabawa",
        "practice_mode": "Yanayin Aiki",
        "quiz_mode": "Yanayin Tambayoyi",
        "duel_mode": "Yakin Jita-Jita",
        "library": "Ɗakin Karatu",
        "chat": "Tattaunawa",
        "profile": "Bayanan Kai",
        "support": "Taimako",
        "logout": "Fita",
        "start_exam": "Fara Jarrabawa",
        "start_practice": "Fara Aiki",
        "start_quiz": "Fara Tambayoyi",
        "challenge": "Yi Kalubale",
        "submit": "Aika",
        "next": "Gaba",
        "previous": "Baya",
        "finish": "Kammala Jarrabawa",
        "result": "Sakamakon",
        "certificate": "Takardar Shaidar",
        "score": "Maki naka",
        "reg_number": "Lambar Rajista",
        "my_results": "Sakamakonni",
        "leaderboard": "Jerin Mafiya",
        "notifications": "Sanarwa",
        "send_message": "Aika Saƙo",
        "report": "Kai ƙara",
        "block": "Hana",
        "warn": "Yi Gargadi",
        "ban": "Hana Dindindin",
        "admin_panel": "Allon Admin",
        "manage_questions": "Sarrafa Tambayoyi",
        "manage_users": "Sarrafa Masu Amfani",
        "manage_books": "Sarrafa Littattafai",
        "broadcast": "Sanar da Duka",
        "view_results": "Duba Sakamakon",
        "add_question": "Ƙara Tambaya",
        "edit": "Gyara",
        "delete": "Share",
        "save": "Ajiye",
        "cancel": "Soke",
        "search": "Bincika",
        "online": "A layi",
        "offline": "Ba a layi",
        "winner": "Mai Nasara",
        "loser": "Mai Asara",
        "time_left": "Lokaci da ya Rage",
        "question": "Tambaya",
        "of": "na",
        "correct": "Daidai!",
        "wrong": "Kuskure!",
        "explanation": "Bayani",
        "read": "Karanta",
        "download": "Sauke",
        "upload_book": "Loda Littafi",
        "complaint": "Aika Korafi",
        "reply": "Amsa",
        "all_users": "Duk Masu Amfani",
        "user_detail": "Bayanan Mai Amfani",
        "registration_success": "Rajista ta yi nasara! Lambar Rajistarka ita ce:",
        "login_reg": "Shiga da Lambar Rajista",
        "or": "KO",
        "choose_subject": "Zaɓi Darasi",
        "select_lang": "Zaɓi Yare",
        "lang_en": "Turanci",
        "lang_ha": "Hausa",
        "lang_ar": "Larabci",
        "lang_zh": "Sinanci",
        "super_admin": "Babban Admin",
        "add_admin": "Ƙara Admin",
        "remove_admin": "Cire Admin",
        "promote_admin": "Ɗaukaka",
        "demote_admin": "Ragu",
    },
    "ar": {
        "app_name": "أحمردي لممارسة الامتحانات",
        "app_short": "AEP",
        "tagline": "منصة JAMB CBT الأولى في نيجيريا",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "full_name": "الاسم الكامل",
        "school": "المدرسة التي التحقت بها",
        "state": "ولاية الأصل",
        "address": "العنوان المنزلي",
        "dob": "تاريخ الميلاد",
        "phone": "رقم الهاتف",
        "confirm_password": "تأكيد كلمة المرور",
        "create_account": "إنشاء حساب",
        "login_now": "تسجيل الدخول الآن",
        "welcome_back": "مرحبًا بعودتك",
        "dashboard": "لوحة التحكم",
        "subjects": "المواد",
        "exam_mode": "وضع الامتحان",
        "practice_mode": "وضع التدريب",
        "quiz_mode": "وضع الاختبار",
        "duel_mode": "وضع المبارزة",
        "library": "مكتبة الكتب",
        "chat": "محادثة الطلاب",
        "profile": "الملف الشخصي",
        "support": "الدعم",
        "logout": "تسجيل الخروج",
        "start_exam": "ابدأ الامتحان",
        "start_practice": "ابدأ التدريب",
        "start_quiz": "ابدأ الاختبار",
        "challenge": "تحدٍّ",
        "submit": "إرسال",
        "next": "التالي",
        "previous": "السابق",
        "finish": "إنهاء الامتحان",
        "result": "النتيجة",
        "certificate": "الشهادة",
        "score": "درجتك",
        "reg_number": "رقم التسجيل",
        "my_results": "نتائجي",
        "leaderboard": "لوحة المتصدرين",
        "notifications": "الإشعارات",
        "send_message": "إرسال رسالة",
        "report": "الإبلاغ عن مستخدم",
        "block": "حجب",
        "warn": "تحذير",
        "ban": "حظر",
        "admin_panel": "لوحة الإدارة",
        "manage_questions": "إدارة الأسئلة",
        "manage_users": "إدارة المستخدمين",
        "manage_books": "إدارة الكتب",
        "broadcast": "بث رسالة",
        "view_results": "عرض النتائج",
        "add_question": "إضافة سؤال",
        "edit": "تعديل",
        "delete": "حذف",
        "save": "حفظ",
        "cancel": "إلغاء",
        "search": "بحث",
        "online": "متصل",
        "offline": "غير متصل",
        "winner": "الفائز",
        "loser": "الخاسر",
        "time_left": "الوقت المتبقي",
        "question": "سؤال",
        "of": "من",
        "correct": "صحيح!",
        "wrong": "خطأ!",
        "explanation": "الشرح",
        "read": "قراءة",
        "download": "تحميل",
        "upload_book": "رفع كتاب",
        "complaint": "إرسال شكوى",
        "reply": "رد",
        "all_users": "جميع المستخدمين",
        "user_detail": "تفاصيل المستخدم",
        "registration_success": "تم التسجيل بنجاح! رقم تسجيلك هو:",
        "login_reg": "الدخول برقم التسجيل",
        "or": "أو",
        "choose_subject": "اختر المادة",
        "select_lang": "اختر اللغة",
        "lang_en": "الإنجليزية",
        "lang_ha": "الهوسا",
        "lang_ar": "العربية",
        "lang_zh": "الصينية",
        "super_admin": "المشرف الرئيسي",
        "add_admin": "إضافة مشرف",
        "remove_admin": "إزالة مشرف",
        "promote_admin": "ترقية",
        "demote_admin": "تخفيض",
    },
    "zh": {
        "app_name": "Ahmerdee 考试练习",
        "app_short": "AEP",
        "tagline": "尼日利亚第一JAMB CBT平台",
        "login": "登录",
        "register": "注册",
        "email": "电子邮件",
        "password": "密码",
        "full_name": "全名",
        "school": "就读学校",
        "state": "原籍州",
        "address": "家庭住址",
        "dob": "出生日期",
        "phone": "电话号码",
        "confirm_password": "确认密码",
        "create_account": "创建账户",
        "login_now": "立即登录",
        "welcome_back": "欢迎回来",
        "dashboard": "仪表板",
        "subjects": "科目",
        "exam_mode": "考试模式",
        "practice_mode": "练习模式",
        "quiz_mode": "问答模式",
        "duel_mode": "对决模式",
        "library": "图书馆",
        "chat": "学生聊天",
        "profile": "个人资料",
        "support": "支持",
        "logout": "退出",
        "start_exam": "开始考试",
        "start_practice": "开始练习",
        "start_quiz": "开始问答",
        "challenge": "挑战",
        "submit": "提交",
        "next": "下一题",
        "previous": "上一题",
        "finish": "完成考试",
        "result": "结果",
        "certificate": "证书",
        "score": "你的分数",
        "reg_number": "注册号码",
        "my_results": "我的结果",
        "leaderboard": "排行榜",
        "notifications": "通知",
        "send_message": "发送消息",
        "report": "举报用户",
        "block": "封锁",
        "warn": "警告",
        "ban": "禁止",
        "admin_panel": "管理面板",
        "manage_questions": "管理问题",
        "manage_users": "管理用户",
        "manage_books": "管理图书",
        "broadcast": "广播",
        "view_results": "查看结果",
        "add_question": "添加问题",
        "edit": "编辑",
        "delete": "删除",
        "save": "保存",
        "cancel": "取消",
        "search": "搜索",
        "online": "在线",
        "offline": "离线",
        "winner": "获胜者",
        "loser": "失败者",
        "time_left": "剩余时间",
        "question": "问题",
        "of": "共",
        "correct": "正确！",
        "wrong": "错误！",
        "explanation": "解释",
        "read": "阅读",
        "download": "下载",
        "upload_book": "上传书籍",
        "complaint": "发送投诉",
        "reply": "回复",
        "all_users": "所有用户",
        "user_detail": "用户详情",
        "registration_success": "注册成功！您的注册号是：",
        "login_reg": "用注册号登录",
        "or": "或",
        "choose_subject": "选择科目",
        "select_lang": "选择语言",
        "lang_en": "英语",
        "lang_ha": "豪萨语",
        "lang_ar": "阿拉伯语",
        "lang_zh": "中文",
        "super_admin": "超级管理员",
        "add_admin": "添加管理员",
        "remove_admin": "移除管理员",
        "promote_admin": "晋升",
        "demote_admin": "降级",
    }
}

JAMB_SUBJECTS = [
    "English Language", "Mathematics", "Physics", "Chemistry", "Biology",
    "Economics", "Government", "Literature in English", "Geography",
    "History", "Christian Religious Studies", "Islamic Religious Studies",
    "Agricultural Science", "Commerce", "Accounts", "Civic Education",
    "Further Mathematics", "Technical Drawing", "Food and Nutrition",
    "Home Economics", "Visual Art", "Music", "French", "Yoruba", "Igbo", "Hausa"
]

# ============================================================
# DATA HELPERS
# ============================================================
def load(f, default=None):
    try:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except: pass
    return default if default is not None else {}

def save(f, data):
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

def hash_pw(pw, salt=None):
    if salt is None: salt = secrets.token_hex(16)
    h = hashlib.sha256(f"{salt}{pw}".encode()).hexdigest()
    return f"{salt}${h}"

def check_pw(pw, stored):
    try:
        salt, h = stored.split("$", 1)
        return hashlib.sha256(f"{salt}{pw}".encode()).hexdigest() == h
    except: return False

def gen_reg_number():
    users = load(USERS_FILE, {})
    year = datetime.now().year
    count = sum(1 for u in users.values() if u.get("role") == "student") + 1
    return f"AEP{year}{count:04d}"

def get_lang():
    return session.get("lang", "en")

def t(key):
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

# ============================================================
# SEED DATA
# ============================================================
def seed_data():
    users = load(USERS_FILE, {})
    # Super admin
    if "super_admin" not in users:
        users["super_admin"] = {
            "id": "super_admin",
            "email": SUPER_ADMIN_EMAIL,
            "name": SUPER_ADMIN_NAME,
            "password": hash_pw(SUPER_ADMIN_PASSWORD),
            "role": "super_admin",
            "reg_number": "AEP-FOUNDER",
            "created": datetime.now().isoformat(),
            "active": True,
            "warned": False,
            "blocked": False,
            "banned": False,
            "avatar": "",
        }
        save(USERS_FILE, users)

    # Seed questions if empty
    questions = load(QUESTIONS_FILE, {})
    if not questions:
        q_data = {}
        SEED_QUESTIONS = {
  "English Language": [
    {"q":"Which of the following is a noun?","a":["Run","Beautiful","Happiness","Quickly"],"ans":"C","exp":"Happiness names a feeling, making it a noun."},
    {"q":"Identify the correct sentence:","a":["She go to school.","She goes to school.","She gone to school.","She going to school."],"ans":"B","exp":"Third-person singular present requires 's': she goes."},
    {"q":"The plural of 'child' is:","a":["Childs","Childes","Children","Childrens"],"ans":"C","exp":"Child has an irregular plural: children."},
    {"q":"Choose the synonym of 'benevolent':","a":["Cruel","Kind","Angry","Lazy"],"ans":"B","exp":"Benevolent means well-meaning and kind."},
    {"q":"A word opposite in meaning is called:","a":["Synonym","Homonym","Antonym","Acronym"],"ans":"C","exp":"Antonyms are words with opposite meanings."},
    {"q":"'The sun rises in the east.' What type of sentence is this?","a":["Compound","Complex","Simple","Compound-complex"],"ans":"C","exp":"It has one independent clause with no subordinates."},
    {"q":"Which figure of speech is used in: 'The wind whispered through the trees'?","a":["Simile","Metaphor","Personification","Hyperbole"],"ans":"C","exp":"Personification gives human qualities (whispering) to the wind."},
    {"q":"Choose the correct spelling:","a":["Recieve","Receive","Receeve","Receve"],"ans":"B","exp":"'i before e except after c' — receive."},
    {"q":"'Despite the rain, we went out.' Identify the clause type underlined (Despite the rain):","a":["Adverbial clause","Noun clause","Relative clause","Main clause"],"ans":"A","exp":"It modifies the main verb, functioning adverbially."},
    {"q":"What is a clause with a subject and a verb but cannot stand alone called?","a":["Independent clause","Dependent clause","Phrase","Sentence"],"ans":"B","exp":"A dependent (subordinate) clause cannot stand alone."},
    {"q":"The word 'quickly' is a(n):","a":["Adjective","Noun","Adverb","Verb"],"ans":"C","exp":"Quickly modifies verbs/adjectives — it's an adverb."},
    {"q":"Select the correct article: '___ university is nearby.'","a":["A","An","The","No article"],"ans":"A","exp":"'University' starts with a consonant sound /j/, so use 'a'."},
    {"q":"'She is the tallest in the class.' This is a ___ degree of comparison:","a":["Positive","Comparative","Superlative","Absolute"],"ans":"C","exp":"'Tallest' is the superlative form."},
    {"q":"Which sentence contains a gerund?","a":["He runs fast.","Swimming is fun.","She sang beautifully.","They played yesterday."],"ans":"B","exp":"'Swimming' functions as the subject noun — a gerund."},
    {"q":"Choose the passive voice: 'The cat ate the fish.'","a":["The fish is eaten by the cat.","The fish was eaten by the cat.","The fish has been eaten by cat.","The fish will eat by the cat."],"ans":"B","exp":"Simple past passive: was + past participle."},
    {"q":"'A piece of advice' — 'advice' is a ___ noun:","a":["Countable","Uncountable","Proper","Collective"],"ans":"B","exp":"Advice cannot be counted directly; it's uncountable."},
    {"q":"Identify the conjunction in: 'I was tired but I continued working.'","a":["Tired","But","Working","Continued"],"ans":"B","exp":"'But' joins two contrasting clauses — it's a conjunction."},
    {"q":"Which is a conditional sentence?","a":["He sleeps early.","If it rains, we stay inside.","She loves music.","They left yesterday."],"ans":"B","exp":"'If' signals a conditional relationship."},
    {"q":"'A group of lions' is called a:","a":["Pack","Herd","Pride","Flock"],"ans":"C","exp":"The collective noun for lions is 'pride'."},
    {"q":"Select the word with a prefix meaning 'against':","a":["Preview","Antiwar","Remake","Unhappy"],"ans":"B","exp":"'Anti-' means against: antiwar."},
    {"q":"The word 'autobiography' means:","a":["Written by someone else","Written about someone else","Written about oneself","A book of maps"],"ans":"C","exp":"Auto = self; biography = life story."},
    {"q":"Which sentence uses 'their' correctly?","a":["Their going to school.","They left their bags.","Their is no excuse.","Their was a problem."],"ans":"B","exp":"'Their' is a possessive pronoun."},
    {"q":"'Laughter is the best medicine.' This is a:","a":["Metaphor","Proverb","Simile","Idiom"],"ans":"B","exp":"It's a widely known proverbial saying."},
    {"q":"The tense 'She had eaten before he arrived' is:","a":["Simple past","Past continuous","Past perfect","Present perfect"],"ans":"C","exp":"Had + past participle = past perfect."},
    {"q":"Which sentence is in the future perfect tense?","a":["She will eat.","She is eating.","She will have eaten.","She has eaten."],"ans":"C","exp":"Will + have + past participle = future perfect."},
    {"q":"The literary device in 'Peter Piper picked a peck of pickled peppers' is:","a":["Assonance","Alliteration","Rhyme","Onomatopoeia"],"ans":"B","exp":"Repeated 'p' consonant sound = alliteration."},
    {"q":"'The assignment was completed by the students.' The subject is:","a":["Assignment","Students","Completed","The"],"ans":"A","exp":"In passive constructions, the grammatical subject receives the action."},
    {"q":"Identify the preposition: 'She sat beside the window.'","a":["She","Sat","Beside","Window"],"ans":"C","exp":"'Beside' shows spatial relationship — a preposition."},
    {"q":"Which sentence contains a split infinitive?","a":["To boldly go","To go boldly","To really run","A and C"],"ans":"D","exp":"Split infinitives place an adverb between 'to' and the verb."},
    {"q":"'A needle in a haystack' is an example of:","a":["Idiom","Simile","Alliteration","Oxymoron"],"ans":"A","exp":"Idiomatic expression meaning something very hard to find."},
  ],
  "Mathematics": [
    {"q":"What is 15% of 200?","a":["20","25","30","35"],"ans":"C","exp":"15/100 × 200 = 30."},
    {"q":"Solve: 3x + 6 = 18","a":["x=2","x=3","x=4","x=6"],"ans":"C","exp":"3x = 12, x = 4."},
    {"q":"What is the LCM of 4 and 6?","a":["24","12","8","6"],"ans":"B","exp":"LCM(4,6) = 12."},
    {"q":"Simplify: (2³)²","a":["12","32","64","16"],"ans":"C","exp":"2³ = 8, 8² = 64. Or 2^(3×2) = 2⁶ = 64."},
    {"q":"If a = 3, b = 4, find √(a² + b²):","a":["5","7","25","12"],"ans":"A","exp":"√(9+16) = √25 = 5 (3-4-5 right triangle)."},
    {"q":"What is the gradient of the line y = 3x + 5?","a":["5","3","8","15"],"ans":"B","exp":"In y = mx + c, gradient m = 3."},
    {"q":"Factorize: x² - 9","a":["(x-3)(x+3)","(x-9)(x+1)","(x+3)²","(x-3)²"],"ans":"A","exp":"Difference of two squares: a²-b² = (a-b)(a+b)."},
    {"q":"The sum of angles in a triangle is:","a":["90°","180°","270°","360°"],"ans":"B","exp":"Triangle interior angles always sum to 180°."},
    {"q":"What is the area of a circle with radius 7? (π=22/7)","a":["44","154","22","308"],"ans":"B","exp":"A = πr² = (22/7)(7²) = 22×7 = 154."},
    {"q":"If 2^x = 32, what is x?","a":["4","5","6","3"],"ans":"B","exp":"2⁵ = 32, so x = 5."},
    {"q":"Evaluate: log₁₀ 1000","a":["1","2","3","4"],"ans":"C","exp":"10³ = 1000, so log₁₀ 1000 = 3."},
    {"q":"A car travels 120 km in 2 hours. What is its speed?","a":["60 km/h","50 km/h","80 km/h","40 km/h"],"ans":"A","exp":"Speed = Distance/Time = 120/2 = 60 km/h."},
    {"q":"What is the median of: 3, 7, 1, 9, 5?","a":["5","7","4","3"],"ans":"A","exp":"Arranged: 1,3,5,7,9 — middle value is 5."},
    {"q":"Solve the quadratic: x² - 5x + 6 = 0","a":["x=2,3","x=1,6","x=-2,-3","x=2,-3"],"ans":"A","exp":"(x-2)(x-3) = 0, x = 2 or x = 3."},
    {"q":"What is 0.25 as a fraction?","a":["1/2","1/4","1/5","2/5"],"ans":"B","exp":"0.25 = 25/100 = 1/4."},
    {"q":"The circumference of a circle with diameter 14 is: (π=22/7)","a":["44","88","22","154"],"ans":"A","exp":"C = πd = (22/7)(14) = 44."},
    {"q":"If the ratio of boys to girls is 3:5 and there are 24 boys, how many girls are there?","a":["40","35","30","45"],"ans":"A","exp":"3 parts = 24, so 1 part = 8; girls = 5×8 = 40."},
    {"q":"What is the mode of: 2, 3, 3, 4, 5, 3, 7?","a":["3","4","2","5"],"ans":"A","exp":"3 appears most often (3 times)."},
    {"q":"Simplify: (x²y³)/(xy)","a":["xy²","x²y","y²","x"],"ans":"A","exp":"x²/x = x, y³/y = y², result = xy²."},
    {"q":"What is the volume of a cube with side 4 cm?","a":["16 cm³","64 cm³","48 cm³","32 cm³"],"ans":"B","exp":"V = s³ = 4³ = 64 cm³."},
    {"q":"An angle of 135° is:","a":["Acute","Right","Obtuse","Reflex"],"ans":"C","exp":"Obtuse angles are between 90° and 180°."},
    {"q":"Simplify: 3/4 + 1/6","a":["4/10","11/12","5/8","2/3"],"ans":"B","exp":"LCD=12: 9/12 + 2/12 = 11/12."},
    {"q":"If f(x) = 2x² - 3x + 1, find f(2):","a":["3","5","7","9"],"ans":"A","exp":"2(4) - 3(2) + 1 = 8 - 6 + 1 = 3."},
    {"q":"What is the HCF of 12 and 18?","a":["3","6","12","36"],"ans":"B","exp":"Factors of 12: 1,2,3,4,6,12; of 18: 1,2,3,6,9,18; HCF=6."},
    {"q":"The exterior angle of a regular hexagon is:","a":["45°","60°","72°","90°"],"ans":"B","exp":"360°/6 = 60°."},
    {"q":"Evaluate: ⁵C₂","a":["5","10","20","15"],"ans":"B","exp":"⁵C₂ = 5!/(2!3!) = 10."},
    {"q":"Solve: 2|x - 3| = 8","a":["x=7 or x=-1","x=7","x=-1","x=4 or x=2"],"ans":"A","exp":"|x-3|=4, so x-3=4 or x-3=-4; x=7 or x=-1."},
    {"q":"The probability of getting a head in a coin toss is:","a":["1","0","1/2","2"],"ans":"C","exp":"One of two equally likely outcomes."},
    {"q":"What is 2⁻³?","a":["1/8","−8","−1/8","8"],"ans":"A","exp":"2⁻³ = 1/2³ = 1/8."},
    {"q":"The gradient of a horizontal line is:","a":["1","−1","undefined","0"],"ans":"D","exp":"Horizontal lines have zero slope."},
  ],
  "Physics": [
    {"q":"What is the SI unit of force?","a":["Joule","Newton","Watt","Pascal"],"ans":"B","exp":"Force is measured in Newtons (N)."},
    {"q":"The speed of light in vacuum is approximately:","a":["3×10⁶ m/s","3×10⁸ m/s","3×10¹⁰ m/s","3×10⁵ m/s"],"ans":"B","exp":"c ≈ 3×10⁸ m/s."},
    {"q":"What type of energy does a moving car possess?","a":["Potential energy","Chemical energy","Kinetic energy","Nuclear energy"],"ans":"C","exp":"Moving objects have kinetic energy = ½mv²."},
    {"q":"Which law states 'For every action, there is an equal and opposite reaction'?","a":["Newton's 1st Law","Newton's 2nd Law","Newton's 3rd Law","Hooke's Law"],"ans":"C","exp":"Newton's Third Law of Motion."},
    {"q":"The unit of electrical resistance is:","a":["Ampere","Volt","Ohm","Watt"],"ans":"C","exp":"Resistance is measured in Ohms (Ω)."},
    {"q":"Which of the following is NOT a vector quantity?","a":["Velocity","Force","Speed","Displacement"],"ans":"C","exp":"Speed has magnitude only, no direction — it's a scalar."},
    {"q":"The phenomenon of bending of light as it passes from one medium to another is called:","a":["Reflection","Refraction","Diffraction","Dispersion"],"ans":"B","exp":"Refraction occurs due to change in speed of light."},
    {"q":"Ohm's Law states that V = IR. If V = 12V and R = 4Ω, what is I?","a":["3A","48A","0.33A","8A"],"ans":"A","exp":"I = V/R = 12/4 = 3A."},
    {"q":"The energy stored in a spring is ___ energy:","a":["Kinetic","Electrical","Elastic potential","Gravitational potential"],"ans":"C","exp":"Compressed/stretched springs store elastic potential energy."},
    {"q":"Which type of wave does not require a medium to travel?","a":["Sound waves","Water waves","Electromagnetic waves","Seismic waves"],"ans":"C","exp":"EM waves (light, radio) travel through vacuum."},
    {"q":"The unit of power is:","a":["Newton","Joule","Watt","Pascal"],"ans":"C","exp":"Power is measured in Watts (W = J/s)."},
    {"q":"An object at rest tends to stay at rest. This is:","a":["Newton's 2nd Law","Law of gravity","Newton's 1st Law","Hooke's Law"],"ans":"C","exp":"Newton's First Law — inertia."},
    {"q":"The frequency of a wave is 50 Hz. What is its period?","a":["50 s","0.02 s","5 s","0.2 s"],"ans":"B","exp":"T = 1/f = 1/50 = 0.02 s."},
    {"q":"Which instrument measures atmospheric pressure?","a":["Thermometer","Barometer","Ammeter","Voltmeter"],"ans":"B","exp":"A barometer measures air pressure."},
    {"q":"The turning effect of a force about a point is called:","a":["Pressure","Torque/Moment","Impulse","Work"],"ans":"B","exp":"Moment = Force × perpendicular distance."},
    {"q":"Nuclear fission involves:","a":["Combining nuclei","Splitting nuclei","Electron emission","Neutron absorption only"],"ans":"B","exp":"Fission = splitting of heavy nuclei releasing energy."},
    {"q":"What does a convex lens do to parallel rays of light?","a":["Diverges them","Converges them","Has no effect","Reflects them"],"ans":"B","exp":"Convex (converging) lenses bring parallel rays to a focus."},
    {"q":"The process by which a solid changes directly to gas is called:","a":["Evaporation","Melting","Sublimation","Condensation"],"ans":"C","exp":"Sublimation: solid → gas without passing through liquid."},
    {"q":"Which particle in an atom has a negative charge?","a":["Proton","Neutron","Electron","Photon"],"ans":"C","exp":"Electrons carry negative charge."},
    {"q":"The unit of electric charge is the:","a":["Ampere","Coulomb","Volt","Farad"],"ans":"B","exp":"Electric charge is measured in Coulombs (C)."},
    {"q":"Which of the following is a good conductor of heat?","a":["Wood","Rubber","Copper","Glass"],"ans":"C","exp":"Metals, especially copper, are excellent heat conductors."},
    {"q":"The loudness of sound depends on its:","a":["Frequency","Wavelength","Amplitude","Speed"],"ans":"C","exp":"Greater amplitude → louder sound."},
    {"q":"Gravitational potential energy = :","a":["½mv²","mgh","mv","Fd"],"ans":"B","exp":"GPE = mass × gravitational field strength × height."},
    {"q":"At what temperature does water boil at standard pressure?","a":["90°C","95°C","100°C","110°C"],"ans":"C","exp":"Water boils at 100°C (373 K) at 1 atm."},
    {"q":"A transformer steps voltage UP. It is called a:","a":["Step-down transformer","Step-up transformer","Current transformer","Power transformer"],"ans":"B","exp":"Step-up transformers increase voltage."},
    {"q":"The phenomenon of total internal reflection is used in:","a":["Mirrors","Optical fibres","Prisms only","Lenses"],"ans":"B","exp":"Optical fibres use TIR to transmit light signals."},
    {"q":"Force = mass × acceleration. If m=5kg, a=3m/s², F=?","a":["15N","8N","2N","1.67N"],"ans":"A","exp":"F = 5 × 3 = 15 N."},
    {"q":"The unit of wavelength is:","a":["Hz","m/s","metres","Watts"],"ans":"C","exp":"Wavelength is a distance, measured in metres."},
    {"q":"Which colour of light has the highest frequency?","a":["Red","Green","Blue","Violet"],"ans":"D","exp":"Violet has the shortest wavelength and highest frequency in visible light."},
    {"q":"Archimedes' principle relates to:","a":["Gravity","Buoyancy","Friction","Magnetism"],"ans":"B","exp":"Objects immersed in fluid experience upthrust equal to weight of fluid displaced."},
  ],
  "Chemistry": [
    {"q":"What is the chemical symbol for Gold?","a":["Go","Gd","Au","Ag"],"ans":"C","exp":"Gold's symbol Au comes from Latin 'Aurum'."},
    {"q":"The chemical formula for water is:","a":["H₂O₂","HO","H₂O","H₃O"],"ans":"C","exp":"Water has 2 hydrogen and 1 oxygen atom."},
    {"q":"What is the atomic number of Carbon?","a":["12","6","14","8"],"ans":"B","exp":"Carbon has 6 protons, so atomic number = 6."},
    {"q":"Which gas is produced when dilute HCl reacts with zinc?","a":["Oxygen","Carbon dioxide","Hydrogen","Chlorine"],"ans":"C","exp":"Zn + 2HCl → ZnCl₂ + H₂↑"},
    {"q":"The pH of a neutral solution is:","a":["0","7","14","1"],"ans":"B","exp":"pH 7 is neutral; below is acidic, above is basic."},
    {"q":"Which of these is a noble gas?","a":["Nitrogen","Oxygen","Argon","Fluorine"],"ans":"C","exp":"Argon (Ar) is in Group 18, the noble gases."},
    {"q":"The process of converting iron ore to iron is called:","a":["Smelting","Roasting","Calcination","Reduction"],"ans":"A","exp":"Smelting uses heat and a reducing agent (coke) to extract iron."},
    {"q":"What type of bond holds Na and Cl in NaCl?","a":["Covalent bond","Ionic bond","Metallic bond","Hydrogen bond"],"ans":"B","exp":"Na⁺ and Cl⁻ are held by electrostatic attraction — ionic bond."},
    {"q":"The molecular formula of glucose is:","a":["C₆H₁₂O₅","C₆H₁₂O₆","C₁₂H₂₂O₁₁","C₆H₁₀O₅"],"ans":"B","exp":"Glucose: C₆H₁₂O₆."},
    {"q":"Rusting of iron is an example of:","a":["Physical change","Combination reaction","Oxidation","Reduction"],"ans":"C","exp":"Iron + oxygen + water → iron oxide (rust) — oxidation."},
    {"q":"Which element has the highest electronegativity?","a":["Oxygen","Chlorine","Fluorine","Nitrogen"],"ans":"C","exp":"Fluorine is the most electronegative element (Pauling scale: 4.0)."},
    {"q":"Avogadro's number is:","a":["6.02×10²²","6.02×10²³","6.02×10²⁴","3.01×10²³"],"ans":"B","exp":"1 mole = 6.02×10²³ particles."},
    {"q":"The chemical name of salt (NaCl) is:","a":["Sodium chlorate","Sodium chloride","Sodium hypochlorite","Sodium carbonate"],"ans":"B","exp":"NaCl = sodium chloride (common table salt)."},
    {"q":"Which acid is found in vinegar?","a":["Hydrochloric acid","Sulphuric acid","Acetic acid","Nitric acid"],"ans":"C","exp":"Acetic (ethanoic) acid gives vinegar its sour taste."},
    {"q":"The law of conservation of mass states that:","a":["Mass increases in reactions","Mass decreases in reactions","Total mass of reactants = total mass of products","Energy cannot be created"],"ans":"C","exp":"Matter is neither created nor destroyed in a chemical reaction."},
    {"q":"Alkaline solutions turn litmus:","a":["Red","Blue","Yellow","Green"],"ans":"B","exp":"Bases/alkalis turn blue litmus paper — they remain blue."},
    {"q":"The monomer of polyethylene (polythene) is:","a":["Propene","Ethene","Benzene","Methane"],"ans":"B","exp":"Polyethylene is made from repeated ethene (CH₂=CH₂) units."},
    {"q":"Which gas makes up the largest percentage of air?","a":["Oxygen","Carbon dioxide","Nitrogen","Argon"],"ans":"C","exp":"Nitrogen makes up ~78% of the atmosphere."},
    {"q":"An element with atomic number 11 is in which group?","a":["Group 1","Group 2","Group 17","Group 18"],"ans":"A","exp":"Element 11 is Sodium, an alkali metal in Group 1."},
    {"q":"Which of the following is an allotrope of carbon?","a":["Silica","Diamond","Graphite oxide","Carbon monoxide"],"ans":"B","exp":"Diamond and graphite are both allotropes of carbon."},
    {"q":"The reaction of an acid with a base to form salt and water is called:","a":["Oxidation","Neutralisation","Hydrolysis","Electrolysis"],"ans":"B","exp":"Acid + Base → Salt + Water (neutralisation)."},
    {"q":"Calcium carbonate (CaCO₃) is the chemical name of:","a":["Chalk/Limestone","Baking soda","Washing soda","Bleaching powder"],"ans":"A","exp":"CaCO₃ is the main component of chalk and limestone."},
    {"q":"The process of splitting water using electricity is called:","a":["Electrolysis","Hydrolysis","Photosynthesis","Combustion"],"ans":"A","exp":"Electrolysis of water: 2H₂O → 2H₂ + O₂."},
    {"q":"Which of these gases is a greenhouse gas?","a":["Nitrogen","Oxygen","Carbon dioxide","Argon"],"ans":"C","exp":"CO₂ traps heat in the atmosphere causing global warming."},
    {"q":"The symbol for Silver is:","a":["Si","Sv","Ag","Sr"],"ans":"C","exp":"Silver's symbol Ag comes from Latin 'Argentum'."},
    {"q":"Catalysts in reactions:","a":["Are consumed","Increase activation energy","Speed up reactions without being consumed","Change the products"],"ans":"C","exp":"Catalysts lower activation energy and are not used up."},
    {"q":"Which type of isomerism is shown by butane and isobutane?","a":["Chain isomerism","Position isomerism","Functional isomerism","Optical isomerism"],"ans":"A","exp":"Same molecular formula, different chain arrangement = chain isomerism."},
    {"q":"The product of combustion of hydrocarbons in excess oxygen is:","a":["CO and H₂","CO₂ and H₂O","C and H₂O","CO₂ and CO"],"ans":"B","exp":"Complete combustion: hydrocarbon + O₂ → CO₂ + H₂O."},
    {"q":"Which of these is a physical change?","a":["Burning wood","Rusting iron","Dissolving sugar in water","Baking a cake"],"ans":"C","exp":"Dissolving sugar is reversible — a physical change."},
    {"q":"The number of electrons in an atom with atomic number 17 is:","a":["8","17","18","35"],"ans":"B","exp":"Atomic number = number of protons = number of electrons in neutral atom."},
  ],
  "Biology": [
    {"q":"The powerhouse of the cell is the:","a":["Nucleus","Ribosome","Mitochondria","Golgi body"],"ans":"C","exp":"Mitochondria produces ATP energy through cellular respiration."},
    {"q":"Photosynthesis takes place in the:","a":["Mitochondria","Chloroplast","Nucleus","Vacuole"],"ans":"B","exp":"Chloroplasts contain chlorophyll and are the site of photosynthesis."},
    {"q":"Which blood group is the universal donor?","a":["AB","A","B","O"],"ans":"D","exp":"Group O negative can donate to all blood groups."},
    {"q":"The process by which plants make food is called:","a":["Respiration","Photosynthesis","Transpiration","Fermentation"],"ans":"B","exp":"Photosynthesis: CO₂ + H₂O + light → glucose + O₂."},
    {"q":"DNA stands for:","a":["Dioxynucleic Acid","Deoxyribonucleic Acid","Diribonucleic Acid","Deoxyribose Nucleic Acid"],"ans":"B","exp":"DNA = Deoxyribonucleic Acid — carries genetic information."},
    {"q":"The basic unit of life is the:","a":["Organ","Tissue","Cell","Organism"],"ans":"C","exp":"The cell is the fundamental structural and functional unit of life."},
    {"q":"Which organ produces insulin?","a":["Liver","Kidney","Pancreas","Stomach"],"ans":"C","exp":"Beta cells in the pancreas produce insulin."},
    {"q":"Osmosis is the movement of:","a":["Solute from low to high concentration","Water from high to low water potential","Solute from high to low concentration","Water from low to high water potential"],"ans":"B","exp":"Osmosis: water moves from high water potential to low water potential through semi-permeable membrane."},
    {"q":"The heart in humans has how many chambers?","a":["2","3","4","5"],"ans":"C","exp":"Human heart: 2 atria + 2 ventricles = 4 chambers."},
    {"q":"Which vitamin is produced when skin is exposed to sunlight?","a":["Vitamin A","Vitamin B","Vitamin C","Vitamin D"],"ans":"D","exp":"Skin synthesizes vitamin D when exposed to UV radiation."},
    {"q":"Bacteria are classified as:","a":["Eukaryotes","Prokaryotes","Protists","Fungi"],"ans":"B","exp":"Bacteria lack a membrane-bound nucleus — they are prokaryotes."},
    {"q":"The scientific study of heredity is called:","a":["Ecology","Genetics","Taxonomy","Physiology"],"ans":"B","exp":"Genetics deals with inheritance and variation of traits."},
    {"q":"Which part of the brain controls balance and coordination?","a":["Cerebrum","Medulla oblongata","Cerebellum","Thalamus"],"ans":"C","exp":"The cerebellum controls motor coordination and balance."},
    {"q":"Enzymes are biological:","a":["Lipids","Catalysts","Hormones","Vitamins"],"ans":"B","exp":"Enzymes are proteins that catalyze biochemical reactions."},
    {"q":"The sequence in food chain: Grass → Grasshopper → Frog → Snake. The grasshopper is a:","a":["Producer","Primary consumer","Secondary consumer","Decomposer"],"ans":"B","exp":"Primary consumers directly eat the producers (plants)."},
    {"q":"Which gas do plants absorb during photosynthesis?","a":["Oxygen","Nitrogen","Carbon dioxide","Water vapour"],"ans":"C","exp":"CO₂ is the carbon source for photosynthesis."},
    {"q":"Haemoglobin is found in:","a":["White blood cells","Red blood cells","Platelets","Plasma"],"ans":"B","exp":"Haemoglobin is the oxygen-carrying protein in red blood cells."},
    {"q":"The process of cell division that produces gametes is:","a":["Mitosis","Binary fission","Meiosis","Budding"],"ans":"C","exp":"Meiosis produces haploid gametes (sperm and eggs)."},
    {"q":"Which organ filters blood and produces urine?","a":["Liver","Kidney","Heart","Lung"],"ans":"B","exp":"Kidneys filter waste from blood to produce urine."},
    {"q":"Transpiration in plants is the loss of:","a":["CO₂","Water vapour","Oxygen","Glucose"],"ans":"B","exp":"Transpiration: evaporation of water from leaves via stomata."},
    {"q":"The largest organ in the human body is the:","a":["Liver","Lung","Skin","Intestine"],"ans":"C","exp":"The skin is the largest organ by surface area and weight."},
    {"q":"HIV primarily attacks which cells?","a":["Red blood cells","Platelets","CD4+ T helper cells","Neurons"],"ans":"C","exp":"HIV destroys CD4+ T cells, weakening the immune system."},
    {"q":"Peristalsis is the movement of:","a":["Blood in vessels","Food through the alimentary canal","Urine through ureter","Air through windpipe"],"ans":"B","exp":"Peristalsis is wavelike muscle contractions that move food along the gut."},
    {"q":"Which of the following is an example of mutualism?","a":["Tapeworm in human gut","Tick on a dog","Nitrogen-fixing bacteria in legume roots","Mistletoe on a tree"],"ans":"C","exp":"Both organisms benefit: bacteria get carbs, plant gets nitrogen."},
    {"q":"The name for organisms that make their own food is:","a":["Heterotrophs","Autotrophs","Omnivores","Decomposers"],"ans":"B","exp":"Autotrophs (like plants) produce food through photosynthesis."},
    {"q":"Kwashiorkor is caused by deficiency of:","a":["Vitamin C","Iron","Protein","Calcium"],"ans":"C","exp":"Kwashiorkor is a severe protein deficiency disease."},
    {"q":"The term for organisms that break down dead matter is:","a":["Producers","Consumers","Decomposers","Parasites"],"ans":"C","exp":"Decomposers (bacteria, fungi) recycle nutrients from dead organisms."},
    {"q":"How many chromosomes does a normal human cell have?","a":["23","44","46","48"],"ans":"C","exp":"Humans have 46 chromosomes (23 pairs) in somatic cells."},
    {"q":"Breathing in humans occurs in the:","a":["Trachea","Alveoli","Bronchi","Diaphragm"],"ans":"B","exp":"Gas exchange (O₂/CO₂) occurs across the alveoli walls."},
    {"q":"The function of the white blood cells is to:","a":["Carry oxygen","Clot blood","Fight infections","Carry nutrients"],"ans":"C","exp":"White blood cells (leukocytes) are part of the immune system."},
  ],
  "Economics": [
    {"q":"The basic economic problem is:","a":["Inflation","Scarcity","Unemployment","Trade deficit"],"ans":"B","exp":"Scarcity — unlimited wants vs limited resources — is the fundamental economic problem."},
    {"q":"Demand curve normally slopes:","a":["Upward","Downward","Horizontally","Vertically"],"ans":"B","exp":"As price rises, quantity demanded falls — hence downward slope."},
    {"q":"GDP stands for:","a":["Gross Domestic Product","Grand Development Plan","General Domestic Price","Gross Departmental Product"],"ans":"A","exp":"GDP measures the total monetary value of goods/services produced in a country."},
    {"q":"Inflation means:","a":["Rising purchasing power","Falling prices","Sustained rise in general price levels","Decrease in money supply"],"ans":"C","exp":"Inflation is a continuous increase in the general price level."},
    {"q":"A monopoly exists when there is:","a":["Many sellers","Only one seller","Two sellers","Perfect competition"],"ans":"B","exp":"A monopoly has a single seller controlling the entire market."},
    {"q":"The law of diminishing returns states that:","a":["All inputs decrease returns","Adding more of one factor eventually yields smaller increases in output","Output always increases","Returns never diminish"],"ans":"B","exp":"Beyond a point, adding more variable input while keeping others fixed reduces marginal output."},
    {"q":"An example of a direct tax is:","a":["VAT","Import duty","Income tax","Excise duty"],"ans":"C","exp":"Income tax is paid directly by individuals to the government."},
    {"q":"Which of these is NOT a factor of production?","a":["Land","Labour","Capital","Money"],"ans":"D","exp":"Money is a medium of exchange, not a factor of production. The 4 factors are Land, Labour, Capital, Enterprise."},
    {"q":"Price elasticity of demand measures:","a":["How supply responds to price","How demand responds to price changes","Income effects","Cross-price effects only"],"ans":"B","exp":"PED = % change in quantity demanded ÷ % change in price."},
    {"q":"A budget deficit occurs when:","a":["Revenue > Expenditure","Revenue = Expenditure","Expenditure > Revenue","Exports > Imports"],"ans":"C","exp":"Government spending exceeds its revenues."},
    {"q":"The term 'ceteris paribus' means:","a":["All else being equal","Supply equals demand","Price stability","Market equilibrium"],"ans":"A","exp":"Latin for 'all other things being equal' — holding other variables constant."},
    {"q":"Which market structure has the most competition?","a":["Monopoly","Duopoly","Oligopoly","Perfect competition"],"ans":"D","exp":"Perfect competition has many sellers offering identical products."},
    {"q":"Opportunity cost is:","a":["The monetary cost of a good","The value of the next best alternative forgone","The total cost of production","Sunk cost"],"ans":"B","exp":"Opportunity cost = what you give up to make a choice."},
    {"q":"Commercial banks create money through:","a":["Printing notes","Credit creation/fractional reserve banking","Government transfers","Foreign exchange"],"ans":"B","exp":"Banks lend out a fraction of deposits, creating multiple times the original deposit."},
    {"q":"Free trade refers to:","a":["Trade without any cost","Trade between countries without tariffs or restrictions","Government-controlled trade","Trade within a country"],"ans":"B","exp":"Free trade allows goods to flow between countries without barriers."},
    {"q":"The Gini coefficient measures:","a":["Inflation","Income inequality","GDP growth","Trade balance"],"ans":"B","exp":"A Gini of 0 = perfect equality; 1 = maximum inequality."},
    {"q":"Which policy tool controls money supply?","a":["Fiscal policy","Monetary policy","Trade policy","Industrial policy"],"ans":"B","exp":"Monetary policy (managed by central bank) controls money supply and interest rates."},
    {"q":"An indirect tax is borne by:","a":["The producer only","The consumer only","Both producer and consumer","The government"],"ans":"C","exp":"Indirect taxes (like VAT) are passed to consumers but collected by producers."},
    {"q":"Devaluation of currency means:","a":["Currency becomes stronger","Currency becomes weaker against others","Currency is abolished","Inflation decreases"],"ans":"B","exp":"Devaluation lowers the official exchange rate of a currency."},
    {"q":"The multiplier effect means:","a":["Each extra unit of output multiplies profit","An initial injection of spending creates a larger final increase in income","Money supply doubles","Prices multiply with income"],"ans":"B","exp":"Multiplier = 1/(1-MPC); spending ripples through the economy."},
    {"q":"Subsistence farming means:","a":["Farming for profit","Farming only to feed the farmer's family","Commercial farming","Large-scale farming"],"ans":"B","exp":"Subsistence farmers produce just enough for their own consumption."},
    {"q":"Import duties protect domestic industries by:","a":["Lowering prices of imports","Raising prices of imports","Eliminating competition","Subsidising exports"],"ans":"B","exp":"Tariffs raise the price of imports, making domestic goods relatively cheaper."},
    {"q":"Privatisation means:","a":["Government taking over private companies","Transferring state-owned enterprises to private ownership","Nationalising industries","Regulating prices"],"ans":"B","exp":"Privatisation involves selling government assets to private investors."},
    {"q":"The concept of 'wants' in economics refers to:","a":["Basic necessities","Desires beyond basic needs","Goods already produced","Government demands"],"ans":"B","exp":"Wants are desires for goods/services beyond basic survival needs."},
    {"q":"A regressive tax takes a ___ percentage from lower incomes:","a":["Lower","Higher","Equal","Zero"],"ans":"B","exp":"Regressive taxes burden lower-income earners proportionally more."},
    {"q":"Break-even point is where:","a":["Profit is maximum","Total revenue = Total cost","Loss is maximum","Fixed cost = Variable cost"],"ans":"B","exp":"At break-even, the firm makes neither profit nor loss."},
    {"q":"The Central Bank of Nigeria (CBN) is responsible for:","a":["Collecting taxes","Formulating monetary policy","Building roads","Regulating trade"],"ans":"B","exp":"The CBN controls money supply, sets interest rates and manages the naira."},
    {"q":"An increase in the price of a substitute good will:","a":["Decrease demand for the original good","Increase demand for the original good","Have no effect on demand","Decrease supply of original good"],"ans":"B","exp":"If substitute becomes expensive, consumers switch to the original good."},
    {"q":"Collective bargaining is negotiation between:","a":["Two competing firms","Employers and trade unions","Government and firms","Buyers and sellers"],"ans":"B","exp":"Trade unions negotiate wages and conditions on behalf of workers."},
    {"q":"What does 'elasticity of supply' measure?","a":["Price changes","Responsiveness of supply to price changes","Quantity demanded","Production capacity"],"ans":"B","exp":"PES = % change in quantity supplied ÷ % change in price."},
  ],
  "Government": [
    {"q":"Democracy literally means:","a":["Rule by the elite","Rule by the people","Rule by law","Rule by force"],"ans":"B","exp":"From Greek: 'demos' (people) + 'kratos' (rule)."},
    {"q":"The Nigerian constitution in use today was adopted in:","a":["1979","1989","1999","2009"],"ans":"C","exp":"The 1999 Constitution (as amended) is Nigeria's current constitution."},
    {"q":"Separation of powers was advocated by:","a":["John Locke","Jean-Jacques Rousseau","Montesquieu","Thomas Hobbes"],"ans":"C","exp":"Montesquieu proposed the division of government into executive, legislative and judiciary."},
    {"q":"A federal system of government has:","a":["One central government","Two or more levels of government","Only state governments","Military rule"],"ans":"B","exp":"Federalism divides power between national and sub-national governments."},
    {"q":"The legislature in Nigeria is called:","a":["The Cabinet","The Supreme Court","The National Assembly","The Senate only"],"ans":"C","exp":"Nigeria's bicameral legislature = Senate + House of Representatives = National Assembly."},
    {"q":"What is a constitution?","a":["A set of laws made by parliament","The fundamental law of a country","A government policy","An executive order"],"ans":"B","exp":"A constitution is the supreme law that establishes the structure and powers of government."},
    {"q":"Sovereignty refers to:","a":["The ability to trade freely","The supreme authority of a state","The right to vote","Freedom of speech"],"ans":"B","exp":"Sovereignty = absolute and supreme power within a territory."},
    {"q":"Proportional representation (PR) means:","a":["Winner takes all","Seats allocated based on percentage of votes won","First past the post","Runoff elections"],"ans":"B","exp":"Under PR, parties get seats proportional to their share of votes."},
    {"q":"A pressure group aims to:","a":["Win elections","Influence government decisions without seeking office","Take over government","Replace political parties"],"ans":"B","exp":"Pressure groups lobby governments to change policies without contesting elections."},
    {"q":"The first Prime Minister of Nigeria was:","a":["Dr Nnamdi Azikiwe","Chief Obafemi Awolowo","Alhaji Abubakar Tafawa Balewa","General Yakubu Gowon"],"ans":"C","exp":"Abubakar Tafawa Balewa became Nigeria's first (and only) Prime Minister at independence."},
    {"q":"Judicial review allows courts to:","a":["Make laws","Declare laws unconstitutional","Enforce policies","Appoint ministers"],"ans":"B","exp":"Courts can strike down laws that conflict with the constitution."},
    {"q":"Which of the following is a feature of a totalitarian state?","a":["Multi-party system","Free press","One-party control over all aspects of life","Separation of powers"],"ans":"C","exp":"Totalitarian states have authoritarian control over political, economic and social life."},
    {"q":"The head of government in a presidential system is the:","a":["Prime Minister","President","Speaker","Chancellor"],"ans":"B","exp":"In a presidential system, the president is both head of state and head of government."},
    {"q":"Nigeria gained independence from Britain in:","a":["1957","1960","1963","1966"],"ans":"B","exp":"Nigeria became independent on October 1, 1960."},
    {"q":"The concept of checks and balances ensures:","a":["Fast decision-making","No branch has unchecked power","Military control","One-party rule"],"ans":"B","exp":"Each branch can limit the powers of the others."},
    {"q":"A unitary state has:","a":["Strong regional governments","All power concentrated in the central government","Equal power sharing","Federal structure"],"ans":"B","exp":"In a unitary state, the central government holds supreme authority."},
    {"q":"Which body is responsible for conducting elections in Nigeria?","a":["NCC","EFCC","INEC","CBN"],"ans":"C","exp":"INEC — Independent National Electoral Commission — manages Nigerian elections."},
    {"q":"The doctrine of rule of law means:","a":["The government can do anything","Law applies equally to all, including the government","Military can override courts","Law applies only to citizens"],"ans":"B","exp":"Rule of law: everyone, including government officials, is subject to the law."},
    {"q":"What is a by-election?","a":["A general election","An election held to fill a vacant seat between general elections","A local government election","A primary election"],"ans":"B","exp":"By-elections are conducted when a seat becomes vacant due to death, resignation, etc."},
    {"q":"ECOWAS was established in:","a":["1960","1975","1963","1980"],"ans":"B","exp":"The Economic Community of West African States was founded in Lagos in 1975."},
    {"q":"The principle of popular sovereignty means:","a":["Sovereignty rests with the military","The people are the ultimate source of government authority","Only the elite have power","The president is supreme"],"ans":"B","exp":"In democracies, the people are the ultimate authority."},
    {"q":"A confederation is:","a":["Stronger than a federation","A loose alliance of independent states","The same as a unitary state","A military alliance only"],"ans":"B","exp":"In a confederation, member states retain most sovereignty and the central authority is weak."},
    {"q":"Which of these is NOT a function of the executive?","a":["Making laws","Implementing laws","Conducting foreign policy","Managing national security"],"ans":"A","exp":"Making laws is the function of the legislature, not the executive."},
    {"q":"The concept of 'tenure of office' means:","a":["The salary of an official","The period an official serves in office","The duties of an official","The qualifications for office"],"ans":"B","exp":"Tenure refers to the length of time a person may hold a position."},
    {"q":"What is franchise?","a":["Right to trade","Right to vote","Freedom of movement","Right to education"],"ans":"B","exp":"Franchise = the right to vote in elections (suffrage)."},
    {"q":"Public opinion refers to:","a":["The views of government","The collective views of citizens on public matters","The opinion of courts","The media's view"],"ans":"B","exp":"Public opinion reflects the attitudes and beliefs of the general population."},
    {"q":"The Abuja Treaty of 1991 established:","a":["ECOWAS","African Economic Community","African Union","OPEC"],"ans":"B","exp":"The Abuja Treaty created the framework for the African Economic Community."},
    {"q":"Fascism is associated with:","a":["Democracy","Extreme nationalism and dictatorial power","Communism","Socialism"],"ans":"B","exp":"Fascism combines extreme nationalism with authoritarian rule."},
    {"q":"The principle of bicameralism refers to:","a":["Two political parties","Two-chamber legislature","Dual executive","Federal system"],"ans":"B","exp":"A bicameral legislature has two houses (e.g., Senate and House of Representatives)."},
    {"q":"Elections are said to be free and fair when:","a":["The ruling party wins","All citizens can vote without intimidation","Only elites vote","The military supervises"],"ans":"B","exp":"Free and fair elections require universal suffrage, no intimidation, and transparent counting."},
  ],
}
        for subj, qs in SEED_QUESTIONS.items():
            if subj not in q_data:
                q_data[subj] = []
            for i, q in enumerate(qs):
                q_data[subj].append({
                    "id": f"Q{subj[:2].upper()}{i+1:03d}",
                    "question": q["q"],
                    "options": {"A": q["a"][0], "B": q["a"][1], "C": q["a"][2], "D": q["a"][3]},
                    "answer": q["ans"],
                    "explanation": q["exp"],
                    "subject": subj,
                    "created": datetime.now().isoformat()
                })
        save(QUESTIONS_FILE, q_data)

seed_data()

# ============================================================
# DECORATORS
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        users = load(USERS_FILE, {})
        user = users.get(session["user_id"])
        if not user or user.get("role") not in ["admin", "super_admin"]:
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

def super_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        users = load(USERS_FILE, {})
        user = users.get(session["user_id"])
        if not user or user.get("role") != "super_admin":
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# ============================================================
# CONTEXT HELPERS
# ============================================================
def get_user():
    if "user_id" not in session: return None
    users = load(USERS_FILE, {})
    return users.get(session["user_id"])

def base_ctx():
    lang = get_lang()
    user = get_user()
    return {"lang": lang, "t": t, "user": user, "app_name": t("app_name"), "app_short": APP_SHORT, "dir": "rtl" if lang == "ar" else "ltr"}

# ============================================================
# ROUTES - AUTH
# ============================================================
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in ["en", "ha", "ar", "zh"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    ctx = base_ctx()
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()
        users = load(USERS_FILE, {})
        found = None
        for uid, u in users.items():
            if u.get("email","").lower() == identifier.lower() or u.get("reg_number","") == identifier.upper():
                found = (uid, u)
                break
        if found:
            uid, u = found
            if check_pw(password, u["password"]):
                if u.get("banned"):
                    ctx["error"] = "Your account has been banned. Contact support."
                    return render_template("login.html", **ctx)
                session["user_id"] = uid
                session.permanent = True
                if u["role"] in ["admin", "super_admin"]:
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for("dashboard"))
        ctx["error"] = "Invalid credentials. Check your email/reg number and password."
    return render_template("login.html", **ctx)

@app.route("/register", methods=["GET", "POST"])
def register():
    ctx = base_ctx()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        school = request.form.get("school","").strip()
        state = request.form.get("state","").strip()
        address = request.form.get("address","").strip()
        dob = request.form.get("dob","").strip()
        phone = request.form.get("phone","").strip()
        password = request.form.get("password","").strip()
        confirm = request.form.get("confirm","").strip()

        if not all([name, email, school, state, address, dob, phone, password]):
            ctx["error"] = "All fields are required."
            return render_template("register.html", **ctx)
        if password != confirm:
            ctx["error"] = "Passwords do not match."
            return render_template("register.html", **ctx)
        if len(password) < 6:
            ctx["error"] = "Password must be at least 6 characters."
            return render_template("register.html", **ctx)

        users = load(USERS_FILE, {})
        for u in users.values():
            if u.get("email","").lower() == email:
                ctx["error"] = "Email already registered."
                return render_template("register.html", **ctx)

        reg = gen_reg_number()
        uid = secrets.token_hex(10)
        users[uid] = {
            "id": uid,
            "email": email,
            "name": name,
            "school": school,
            "state": state,
            "address": address,
            "dob": dob,
            "phone": phone,
            "password": hash_pw(password),
            "reg_number": reg,
            "role": "student",
            "avatar": "",
            "online": False,
            "created": datetime.now().isoformat(),
            "active": True,
            "warned": False,
            "blocked": False,
            "banned": False,
            "exam_count": 0,
            "practice_count": 0,
        }
        save(USERS_FILE, users)
        ctx["success"] = True
        ctx["reg_number"] = reg
        ctx["student_name"] = name
    return render_template("register.html", **ctx)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ============================================================
# ROUTES - STUDENT
# ============================================================
@app.route("/dashboard")
@login_required
def dashboard():
    ctx = base_ctx()
    user = get_user()
    if user["role"] in ["admin", "super_admin"]:
        return redirect(url_for("admin_dashboard"))
    results = load(RESULTS_FILE, {})
    user_results = [r for r in results.values() if r.get("user_id") == session["user_id"] and r.get("type") == "exam"]
    broadcasts = load(BROADCAST_FILE, [])
    recent_bc = broadcasts[-1] if broadcasts else None
    ctx.update({"user": user, "results_count": len(user_results), "recent_bc": recent_bc})
    return render_template("dashboard.html", **ctx)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    user = users.get(session["user_id"])
    if request.method == "POST":
        user["name"] = request.form.get("name", user["name"]).strip()
        user["phone"] = request.form.get("phone", user["phone"]).strip()
        user["address"] = request.form.get("address", user["address"]).strip()
        new_pw = request.form.get("new_password","").strip()
        if new_pw:
            if len(new_pw) < 6:
                ctx["error"] = "Password must be at least 6 characters."
            else:
                user["password"] = hash_pw(new_pw)
                ctx["success_msg"] = "Password updated."
        users[session["user_id"]] = user
        save(USERS_FILE, users)
        ctx["success_msg"] = ctx.get("success_msg", "Profile updated successfully.")
    ctx["user"] = user
    return render_template("profile.html", **ctx)

@app.route("/subjects")
@login_required
def subjects():
    ctx = base_ctx()
    questions = load(QUESTIONS_FILE, {})
    subject_counts = {s: len(questions.get(s, [])) for s in JAMB_SUBJECTS}
    ctx["subjects"] = JAMB_SUBJECTS
    ctx["subject_counts"] = subject_counts
    return render_template("subjects.html", **ctx)

@app.route("/exam/<subject>", methods=["GET", "POST"])
@login_required
def exam(subject):
    ctx = base_ctx()
    if subject not in JAMB_SUBJECTS:
        return redirect(url_for("subjects"))
    questions = load(QUESTIONS_FILE, {})
    subj_qs = questions.get(subject, [])
    if not subj_qs:
        ctx["error"] = "No questions available for this subject yet."
        ctx["subjects"] = JAMB_SUBJECTS
        return render_template("subjects.html", **ctx)
    selected = random.sample(subj_qs, min(40, len(subj_qs)))
    ctx.update({"subject": subject, "questions": selected, "mode": "exam", "duration": 40 * 60})
    return render_template("exam.html", **ctx)

@app.route("/practice/<subject>")
@login_required
def practice(subject):
    ctx = base_ctx()
    questions = load(QUESTIONS_FILE, {})
    subj_qs = questions.get(subject, [])
    selected = random.sample(subj_qs, min(20, len(subj_qs)))
    ctx.update({"subject": subject, "questions": selected, "mode": "practice", "duration": 0})
    return render_template("exam.html", **ctx)

@app.route("/quiz/<subject>")
@login_required
def quiz(subject):
    ctx = base_ctx()
    questions = load(QUESTIONS_FILE, {})
    subj_qs = questions.get(subject, [])
    selected = random.sample(subj_qs, min(10, len(subj_qs)))
    ctx.update({"subject": subject, "questions": selected, "mode": "quiz"})
    return render_template("quiz.html", **ctx)

@app.route("/submit_exam", methods=["POST"])
@login_required
def submit_exam():
    data = request.get_json()
    mode = data.get("mode")
    subject = data.get("subject")
    answers = data.get("answers", {})
    questions_raw = data.get("questions", [])

    score = 0
    total = len(questions_raw)
    details = []
    for q in questions_raw:
        user_ans = answers.get(q["id"], "")
        correct = q["answer"]
        is_correct = user_ans == correct
        if is_correct: score += 1
        details.append({**q, "user_answer": user_ans, "is_correct": is_correct})

    percentage = round((score / total) * 100) if total else 0
    grade = "A" if percentage >= 70 else "B" if percentage >= 60 else "C" if percentage >= 50 else "F"

    result_id = f"RES{secrets.token_hex(6).upper()}"
    user = get_user()
    result = {
        "id": result_id,
        "user_id": session["user_id"],
        "user_name": user["name"],
        "reg_number": user["reg_number"],
        "subject": subject,
        "mode": mode,
        "score": score,
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "details": details,
        "date": datetime.now().isoformat(),
        "verify_id": secrets.token_hex(8).upper(),
    }

    results = load(RESULTS_FILE, {})
    results[result_id] = result
    save(RESULTS_FILE, results)

    # Update user counts
    users = load(USERS_FILE, {})
    u = users.get(session["user_id"])
    if u:
        if mode == "exam": u["exam_count"] = u.get("exam_count", 0) + 1
        else: u["practice_count"] = u.get("practice_count", 0) + 1
        save(USERS_FILE, users)

    return jsonify({"success": True, "result_id": result_id, "score": score, "total": total, "percentage": percentage, "grade": grade, "mode": mode})

@app.route("/result/<result_id>")
@login_required
def result(result_id):
    ctx = base_ctx()
    results = load(RESULTS_FILE, {})
    res = results.get(result_id)
    if not res or (res["user_id"] != session["user_id"] and get_user().get("role") not in ["admin","super_admin"]):
        return redirect(url_for("dashboard"))
    ctx["result"] = res
    return render_template("result.html", **ctx)

@app.route("/my_results")
@login_required
def my_results():
    ctx = base_ctx()
    results = load(RESULTS_FILE, {})
    my = sorted([r for r in results.values() if r.get("user_id") == session["user_id"]], key=lambda x: x["date"], reverse=True)
    ctx["results"] = my
    return render_template("my_results.html", **ctx)

@app.route("/library")
@login_required
def library():
    ctx = base_ctx()
    books = load(BOOKS_FILE, [])
    ctx["books"] = books
    return render_template("library.html", **ctx)

@app.route("/chat")
@login_required
def chat():
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    students = [u for u in users.values() if u.get("role") == "student" and u["id"] != session["user_id"] and not u.get("blocked") and not u.get("banned")]
    ctx["students"] = students
    return render_template("chat.html", **ctx)

@app.route("/api/chat/messages/<target_id>")
@login_required
def chat_messages(target_id):
    chats = load(CHAT_FILE, {})
    key = "_".join(sorted([session["user_id"], target_id]))
    msgs = chats.get(key, [])
    # Mark read
    for m in msgs:
        if m["to"] == session["user_id"]: m["read"] = True
    save(CHAT_FILE, chats)
    return jsonify(msgs)

@app.route("/api/chat/send", methods=["POST"])
@login_required
def chat_send():
    data = request.get_json()
    target_id = data.get("to")
    message = data.get("message","").strip()
    if not target_id or not message:
        return jsonify({"success": False})
    chats = load(CHAT_FILE, {})
    key = "_".join(sorted([session["user_id"], target_id]))
    if key not in chats: chats[key] = []
    user = get_user()
    chats[key].append({
        "id": secrets.token_hex(6),
        "from": session["user_id"],
        "from_name": user["name"],
        "from_avatar": user.get("avatar",""),
        "to": target_id,
        "message": message,
        "time": datetime.now().isoformat(),
        "read": False,
    })
    save(CHAT_FILE, chats)
    return jsonify({"success": True})

@app.route("/report_user", methods=["POST"])
@login_required
def report_user():
    data = request.get_json()
    target_id = data.get("user_id")
    reason = data.get("reason","").strip()
    if not target_id or not reason:
        return jsonify({"success": False, "message": "Missing data"})
    reports = load(REPORTS_FILE, [])
    user = get_user()
    reports.append({
        "id": secrets.token_hex(6),
        "reporter_id": session["user_id"],
        "reporter_name": user["name"],
        "target_id": target_id,
        "reason": reason,
        "date": datetime.now().isoformat(),
        "status": "pending"
    })
    save(REPORTS_FILE, reports)
    return jsonify({"success": True, "message": "Report submitted to admin."})

@app.route("/support", methods=["GET", "POST"])
@login_required
def support():
    ctx = base_ctx()
    tickets = load(SUPPORT_FILE, [])
    my_tickets = [tk for tk in tickets if tk.get("user_id") == session["user_id"]]
    if request.method == "POST":
        msg = request.form.get("message","").strip()
        if msg:
            user = get_user()
            tickets.append({
                "id": secrets.token_hex(6),
                "user_id": session["user_id"],
                "user_name": user["name"],
                "reg_number": user["reg_number"],
                "message": msg,
                "date": datetime.now().isoformat(),
                "status": "open",
                "replies": []
            })
            save(SUPPORT_FILE, tickets)
            ctx["success_msg"] = "Message sent to admin."
    ctx["tickets"] = sorted(my_tickets, key=lambda x: x["date"], reverse=True)
    return render_template("support.html", **ctx)

@app.route("/notifications")
@login_required
def notifications():
    ctx = base_ctx()
    broadcasts = load(BROADCAST_FILE, [])
    my_bc = [b for b in broadcasts if not b.get("target_id") or b["target_id"] == session["user_id"]]
    ctx["broadcasts"] = sorted(my_bc, key=lambda x: x["date"], reverse=True)
    return render_template("notifications.html", **ctx)

@app.route("/duel")
@login_required
def duel():
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    students = [u for u in users.values() if u.get("role") == "student" and u["id"] != session["user_id"] and not u.get("blocked") and not u.get("banned")]
    ctx["students"] = students
    ctx["subjects"] = JAMB_SUBJECTS
    return render_template("duel.html", **ctx)

@app.route("/api/online_status", methods=["POST"])
@login_required
def online_status():
    users = load(USERS_FILE, {})
    u = users.get(session["user_id"])
    if u:
        u["online"] = True
        u["last_seen"] = datetime.now().isoformat()
        save(USERS_FILE, users)
    return jsonify({"ok": True})

# ============================================================
# ADMIN ROUTES
# ============================================================
@app.route("/admin")
@admin_required
def admin_dashboard():
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    questions = load(QUESTIONS_FILE, {})
    results = load(RESULTS_FILE, {})
    reports = load(REPORTS_FILE, [])
    books = load(BOOKS_FILE, [])
    tickets = load(SUPPORT_FILE, [])
    ctx.update({
        "total_users": sum(1 for u in users.values() if u.get("role") == "student"),
        "total_questions": sum(len(q) for q in questions.values()),
        "total_results": len(results),
        "pending_reports": sum(1 for r in reports if r.get("status") == "pending"),
        "total_books": len(books),
        "open_tickets": sum(1 for t in tickets if t.get("status") == "open"),
        "admins": [u for u in users.values() if u.get("role") in ["admin","super_admin"]],
    })
    return render_template("admin/dashboard.html", **ctx)

@app.route("/admin/users")
@admin_required
def admin_users():
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    q = request.args.get("q","").strip().lower()
    students = [u for u in users.values() if u.get("role") == "student"]
    if q:
        students = [u for u in students if q in u["name"].lower() or q in u.get("reg_number","").lower() or q in u.get("email","").lower()]
    ctx["students"] = sorted(students, key=lambda x: x.get("created",""), reverse=True)
    ctx["q"] = q
    return render_template("admin/users.html", **ctx)

@app.route("/admin/user/<uid>")
@admin_required
def admin_user_detail(uid):
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    user = users.get(uid)
    if not user:
        return redirect(url_for("admin_users"))
    results = load(RESULTS_FILE, {})
    user_results = [r for r in results.values() if r.get("user_id") == uid]
    ctx["target"] = user
    ctx["user_results"] = user_results
    return render_template("admin/user_detail.html", **ctx)

@app.route("/admin/user_action", methods=["POST"])
@admin_required
def admin_user_action():
    data = request.get_json()
    uid = data.get("uid")
    action = data.get("action")
    users = load(USERS_FILE, {})
    user = users.get(uid)
    if not user:
        return jsonify({"success": False, "message": "User not found"})
    if action == "warn": user["warned"] = True
    elif action == "block": user["blocked"] = not user.get("blocked", False)
    elif action == "ban": user["banned"] = not user.get("banned", False)
    save(USERS_FILE, users)
    return jsonify({"success": True, "message": f"Action '{action}' applied."})

@app.route("/admin/questions")
@admin_required
def admin_questions():
    ctx = base_ctx()
    questions = load(QUESTIONS_FILE, {})
    subject = request.args.get("subject", JAMB_SUBJECTS[0])
    ctx["questions"] = questions.get(subject, [])
    ctx["subjects"] = JAMB_SUBJECTS
    ctx["selected_subject"] = subject
    return render_template("admin/questions.html", **ctx)

@app.route("/admin/add_question", methods=["POST"])
@admin_required
def admin_add_question():
    data = request.get_json()
    subject = data.get("subject")
    q_text = data.get("question","").strip()
    options = data.get("options", {})
    answer = data.get("answer","").strip().upper()
    explanation = data.get("explanation","").strip()
    if not all([subject, q_text, options, answer]):
        return jsonify({"success": False, "message": "Missing fields"})
    questions = load(QUESTIONS_FILE, {})
    if subject not in questions: questions[subject] = []
    qid = f"Q{secrets.token_hex(4).upper()}"
    questions[subject].append({
        "id": qid, "question": q_text, "options": options,
        "answer": answer, "explanation": explanation,
        "subject": subject, "created": datetime.now().isoformat()
    })
    save(QUESTIONS_FILE, questions)
    return jsonify({"success": True, "message": "Question added."})

@app.route("/admin/delete_question", methods=["POST"])
@admin_required
def admin_delete_question():
    data = request.get_json()
    subject = data.get("subject")
    qid = data.get("qid")
    questions = load(QUESTIONS_FILE, {})
    if subject in questions:
        questions[subject] = [q for q in questions[subject] if q["id"] != qid]
        save(QUESTIONS_FILE, questions)
    return jsonify({"success": True})

@app.route("/admin/books", methods=["GET", "POST"])
@admin_required
def admin_books():
    ctx = base_ctx()
    books = load(BOOKS_FILE, [])
    if request.method == "POST":
        title = request.form.get("title","").strip()
        subject = request.form.get("subject","").strip()
        desc = request.form.get("description","").strip()
        file = request.files.get("file")
        if title and file:
            filename = f"{secrets.token_hex(8)}_{file.filename}"
            filepath = os.path.join(DATA_DIR, "books", filename)
            file.save(filepath)
            books.append({
                "id": secrets.token_hex(6),
                "title": title,
                "subject": subject,
                "description": desc,
                "filename": filename,
                "size": os.path.getsize(filepath),
                "uploaded": datetime.now().isoformat()
            })
            save(BOOKS_FILE, books)
            ctx["success_msg"] = "Book uploaded."
    ctx["books"] = books
    ctx["subjects"] = JAMB_SUBJECTS
    return render_template("admin/books.html", **ctx)

@app.route("/admin/reports")
@admin_required
def admin_reports():
    ctx = base_ctx()
    reports = load(REPORTS_FILE, [])
    users = load(USERS_FILE, {})
    for r in reports:
        r["target_name"] = users.get(r["target_id"], {}).get("name", "Unknown")
    ctx["reports"] = sorted(reports, key=lambda x: x["date"], reverse=True)
    return render_template("admin/reports.html", **ctx)

@app.route("/admin/results")
@admin_required
def admin_results():
    ctx = base_ctx()
    results = load(RESULTS_FILE, {})
    ctx["results"] = sorted(results.values(), key=lambda x: x["date"], reverse=True)
    return render_template("admin/results.html", **ctx)

@app.route("/admin/support")
@admin_required
def admin_support():
    ctx = base_ctx()
    tickets = load(SUPPORT_FILE, [])
    ctx["tickets"] = sorted(tickets, key=lambda x: x["date"], reverse=True)
    return render_template("admin/support.html", **ctx)

@app.route("/admin/reply_support", methods=["POST"])
@admin_required
def admin_reply_support():
    data = request.get_json()
    ticket_id = data.get("ticket_id")
    reply = data.get("reply","").strip()
    tickets = load(SUPPORT_FILE, [])
    for tk in tickets:
        if tk["id"] == ticket_id:
            tk.setdefault("replies", []).append({
                "message": reply,
                "date": datetime.now().isoformat(),
                "by": get_user()["name"]
            })
            tk["status"] = "replied"
            break
    save(SUPPORT_FILE, tickets)
    return jsonify({"success": True})

@app.route("/admin/broadcast", methods=["GET", "POST"])
@admin_required
def admin_broadcast():
    ctx = base_ctx()
    broadcasts = load(BROADCAST_FILE, [])
    users = load(USERS_FILE, {})
    if request.method == "POST":
        msg = request.form.get("message","").strip()
        target_id = request.form.get("target_id","").strip()
        bc = {
            "id": secrets.token_hex(6),
            "message": msg,
            "target_id": target_id if target_id else None,
            "by": get_user()["name"],
            "date": datetime.now().isoformat()
        }
        broadcasts.append(bc)
        save(BROADCAST_FILE, broadcasts)
        ctx["success_msg"] = "Message broadcasted."
    students = [u for u in users.values() if u.get("role") == "student"]
    ctx["broadcasts"] = sorted(broadcasts, key=lambda x: x["date"], reverse=True)
    ctx["students"] = students
    return render_template("admin/broadcast.html", **ctx)

@app.route("/admin/admins")
@super_admin_required
def admin_manage_admins():
    ctx = base_ctx()
    users = load(USERS_FILE, {})
    admins = [u for u in users.values() if u.get("role") in ["admin","super_admin"]]
    students = [u for u in users.values() if u.get("role") == "student"]
    ctx["admins"] = admins
    ctx["students"] = students
    return render_template("admin/admins.html", **ctx)

@app.route("/admin/set_role", methods=["POST"])
@super_admin_required
def admin_set_role():
    data = request.get_json()
    uid = data.get("uid")
    role = data.get("role")
    users = load(USERS_FILE, {})
    user = users.get(uid)
    if not user or user.get("role") == "super_admin":
        return jsonify({"success": False, "message": "Cannot modify super admin."})
    if role in ["student", "admin"]:
        user["role"] = role
        save(USERS_FILE, users)
        return jsonify({"success": True, "message": f"Role updated to {role}."})
    return jsonify({"success": False})

# ============================================================
# BOOK DOWNLOAD
# ============================================================
@app.route("/download_book/<book_id>")
@login_required
def download_book(book_id):
    books = load(BOOKS_FILE, [])
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return redirect(url_for("library"))
    filepath = os.path.join(DATA_DIR, "books", book["filename"])
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath, as_attachment=True, download_name=book["title"] + ".pdf")

# ============================================================
# LEADERBOARD
# ============================================================
@app.route("/leaderboard")
@login_required
def leaderboard():
    ctx = base_ctx()
    results = load(RESULTS_FILE, {})
    users = load(USERS_FILE, {})
    # Best exam score per user
    best = {}
    for r in results.values():
        if r.get("mode") != "exam": continue
        uid = r["user_id"]
        if uid not in best or r["percentage"] > best[uid]["percentage"]:
            best[uid] = r
    board = sorted(best.values(), key=lambda x: x["percentage"], reverse=True)[:50]
    ctx["board"] = board
    ctx["current_uid"] = session["user_id"]
    return render_template("leaderboard.html", **ctx)

# ============================================================
# ADMIN - EDIT QUESTION
# ============================================================
@app.route("/admin/edit_question", methods=["POST"])
@admin_required
def admin_edit_question():
    data = request.get_json()
    subject = data.get("subject")
    qid = data.get("qid")
    questions = load(QUESTIONS_FILE, {})
    if subject in questions:
        for q in questions[subject]:
            if q["id"] == qid:
                q["question"] = data.get("question", q["question"])
                q["options"] = data.get("options", q["options"])
                q["answer"] = data.get("answer", q["answer"])
                q["explanation"] = data.get("explanation", q["explanation"])
                break
        save(QUESTIONS_FILE, questions)
    return jsonify({"success": True, "message": "Question updated."})

# ============================================================
# ADMIN - BULK IMPORT QUESTIONS (JSON)
# ============================================================
@app.route("/admin/bulk_import", methods=["POST"])
@admin_required
def admin_bulk_import():
    try:
        data = request.get_json()
        subject = data.get("subject")
        qs_raw = data.get("questions", [])
        if not subject or not qs_raw:
            return jsonify({"success": False, "message": "Missing data"})
        questions = load(QUESTIONS_FILE, {})
        if subject not in questions:
            questions[subject] = []
        added = 0
        for q in qs_raw:
            qid = f"Q{secrets.token_hex(4).upper()}"
            questions[subject].append({
                "id": qid,
                "question": q.get("question",""),
                "options": q.get("options", {}),
                "answer": q.get("answer","A"),
                "explanation": q.get("explanation",""),
                "subject": subject,
                "created": datetime.now().isoformat()
            })
            added += 1
        save(QUESTIONS_FILE, questions)
        return jsonify({"success": True, "message": f"{added} questions imported."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# ============================================================
# CERTIFICATE VERIFY (Public)
# ============================================================
@app.route("/verify")
@app.route("/verify/<verify_id>")
def verify_cert(verify_id=None):
    ctx = base_ctx()
    result = None
    if verify_id:
        results = load(RESULTS_FILE, {})
        for r in results.values():
            if r.get("verify_id") == verify_id.upper():
                result = r
                break
    ctx["result"] = result
    ctx["verify_id"] = verify_id or ""
    return render_template("verify.html", **ctx)

# ============================================================
# ADMIN - REPORT ACTION (warn/block via report)
# ============================================================
@app.route("/admin/resolve_report", methods=["POST"])
@admin_required
def admin_resolve_report():
    data = request.get_json()
    report_id = data.get("report_id")
    action = data.get("action")  # warn, block, ban, dismiss
    reports = load(REPORTS_FILE, [])
    target_id = None
    for r in reports:
        if r["id"] == report_id:
            r["status"] = "resolved"
            target_id = r["target_id"]
            break
    save(REPORTS_FILE, reports)
    if target_id and action in ["warn", "block", "ban"]:
        users = load(USERS_FILE, {})
        u = users.get(target_id)
        if u:
            if action == "warn": u["warned"] = True
            elif action == "block": u["blocked"] = True
            elif action == "ban": u["banned"] = True
            save(USERS_FILE, users)
    return jsonify({"success": True, "message": f"Report resolved. Action: {action}"})

# ============================================================
# ADMIN - SETTINGS
# ============================================================
@app.route("/admin/settings", methods=["GET","POST"])
@super_admin_required
def admin_settings():
    ctx = base_ctx()
    settings = load(SETTINGS_FILE, {
        "app_name": "Ahmerdee Exam Practice",
        "exam_duration_minutes": 40,
        "exam_questions": 40,
        "practice_questions": 20,
        "quiz_questions": 10,
        "allow_registration": True,
        "maintenance_mode": False,
    })
    if request.method == "POST":
        settings["app_name"] = request.form.get("app_name", settings["app_name"])
        settings["exam_duration_minutes"] = int(request.form.get("exam_duration", 40))
        settings["exam_questions"] = int(request.form.get("exam_questions", 40))
        settings["allow_registration"] = "allow_reg" in request.form
        settings["maintenance_mode"] = "maintenance" in request.form
        save(SETTINGS_FILE, settings)
        ctx["success_msg"] = "Settings saved."
    ctx["settings"] = settings
    return render_template("admin/settings.html", **ctx)

# ============================================================
# API
# ============================================================
@app.route("/api/verify_result/<verify_id>")
def verify_result(verify_id):
    results = load(RESULTS_FILE, {})
    for r in results.values():
        if r.get("verify_id") == verify_id:
            return jsonify({"valid": True, "result": {k: v for k, v in r.items() if k != "details"}})
    return jsonify({"valid": False})

@app.route("/api/leaderboard")
@login_required
def api_leaderboard():
    results = load(RESULTS_FILE, {})
    best = {}
    for r in results.values():
        if r.get("mode") != "exam": continue
        uid = r["user_id"]
        if uid not in best or r["percentage"] > best[uid]["percentage"]:
            best[uid] = r
    board = sorted(best.values(), key=lambda x: x["percentage"], reverse=True)[:20]
    return jsonify(board)

@app.route("/api/stats")
@login_required
def api_stats():
    results = load(RESULTS_FILE, {})
    uid = session["user_id"]
    my = [r for r in results.values() if r["user_id"] == uid]
    exam_results = [r for r in my if r.get("mode") == "exam"]
    avg = round(sum(r["percentage"] for r in exam_results) / len(exam_results)) if exam_results else 0
    best = max((r["percentage"] for r in exam_results), default=0)
    return jsonify({
        "total_exams": len(exam_results),
        "average_score": avg,
        "best_score": best,
        "total_practice": len([r for r in my if r.get("mode") == "practice"]),
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)

