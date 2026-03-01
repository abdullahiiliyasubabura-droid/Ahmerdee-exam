"""
Ahmerdee Exam Practice (AEP) v2.0
- SQLAlchemy ORM (SQLite / PostgreSQL)
- Flask-SocketIO real-time Live Quiz Broadcast
- PalmPay/OPay aesthetic (White/Purple/Green/Gold)
- Profile picture auto-resize via Pillow
- Persistent sessions, network-guard, anti-cheat tab detection
- Multi-language: English, Hausa, Arabic (RTL)
- Stadium mode: spectators watch Ahmad vs Musa LIVE
"""

import os, json, hashlib, secrets, random, base64, io
from datetime import datetime, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, send_file)
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import Text, or_
from PIL import Image

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
VOLUME_DIR = "/data"
LOCAL_DIR  = os.path.join(BASE_DIR, "data")
DATA_DIR   = VOLUME_DIR if (os.path.exists(VOLUME_DIR) and os.access(VOLUME_DIR, os.W_OK)) else LOCAL_DIR

for d in [DATA_DIR, os.path.join(DATA_DIR,"logs"), os.path.join(DATA_DIR,"books"), os.path.join(DATA_DIR,"avatars")]:
    os.makedirs(d, exist_ok=True)

DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(DATA_DIR,'aep.db')}")
if DB_URL.startswith("postgres://"): DB_URL = DB_URL.replace("postgres://","postgresql://",1)

app = Flask(__name__, template_folder=os.path.join(BASE_DIR,"templates"), static_folder=os.path.join(BASE_DIR,"static"))
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY","aep_v2_purple_xk9z"),
                  SQLALCHEMY_DATABASE_URI=DB_URL, SQLALCHEMY_TRACK_MODIFICATIONS=False,
                  PERMANENT_SESSION_LIFETIME=timedelta(days=365), MAX_CONTENT_LENGTH=32*1024*1024)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", ping_timeout=120, ping_interval=25)

APP_SHORT = "AEP"
JAMB_SUBJECTS = ["English Language","Mathematics","Physics","Chemistry","Biology","Economics","Government",
    "History","Geography","Literature in English","Islamic Religious Studies","Christian Religious Studies",
    "Agricultural Science","Computer Studies","Technical Drawing","Commerce","Accounting","Business Studies",
    "Music","Fine Art","Home Economics","French","Yoruba","Igbo","Hausa","Further Mathematics"]
NIGERIAN_STATES = ["Abia","Adamawa","Akwa Ibom","Anambra","Bauchi","Bayelsa","Benue","Borno","Cross River",
    "Delta","Ebonyi","Edo","Ekiti","Enugu","FCT","Gombe","Imo","Jigawa","Kaduna","Kano","Katsina","Kebbi",
    "Kogi","Kwara","Lagos","Nasarawa","Niger","Ogun","Ondo","Osun","Oyo","Plateau","Rivers","Sokoto","Taraba","Yobe","Zamfara"]

TRANSLATIONS = {
    "en":{"app_name":"Ahmerdee Exam Practice","app_short":"AEP","tagline":"Nigeria's #1 JAMB CBT Platform",
          "login":"Login","register":"Register","email":"Email Address","password":"Password","full_name":"Full Name",
          "school":"School Attended","state":"State of Origin","address":"Home Address","dob":"Date of Birth",
          "phone":"Phone Number","confirm_password":"Confirm Password","create_account":"Create Account",
          "login_now":"Login Now","welcome_back":"Welcome back","dashboard":"Dashboard","subjects":"Subjects",
          "exam_mode":"Exam Mode","practice_mode":"Practice Mode","quiz_mode":"Quiz Mode","duel_mode":"Duel Mode",
          "library":"Book Library","chat":"Chat","group_chat":"Group Chat","profile":"Profile","support":"Support",
          "logout":"Logout","start_exam":"Start Exam","start_practice":"Start Practice","start_quiz":"Start Quiz",
          "submit":"Submit","next":"Next","previous":"Previous","score":"Score","grade":"Grade",
          "certificate":"Certificate","leaderboard":"Leaderboard","my_results":"My Results",
          "notifications":"Notifications","all_jamb_students":"All JAMB Students","live_quiz":"Live Quiz 📺"},
    "ha":{"app_name":"Ahmerdee Jarrabawar Jarabawa","app_short":"AEP","tagline":"Dandamalin #1 JAMB CBT na Najeriya",
          "login":"Shiga","register":"Yi Rajista","email":"Adireshin Email","password":"Kalmar Sirri",
          "full_name":"Cikakken Suna","school":"Makaranta","state":"Jiha","address":"Adireshi","dob":"Ranar Haihuwa",
          "phone":"Lambar Wayar","confirm_password":"Tabbatar Kalmar Sirri","create_account":"Ƙirƙiri Asusun",
          "login_now":"Shiga Yanzu","welcome_back":"Maraba da dawowa","dashboard":"Gida","subjects":"Darussa",
          "exam_mode":"Yanayin Jarrabawa","practice_mode":"Yanayin Aiki","quiz_mode":"Yanayin Quiz",
          "duel_mode":"Yanayin Duel","library":"Ɗakin Littattafai","chat":"Hira",
          "group_chat":"Tattaunawa Ta Ƙungiya","profile":"Bayani","support":"Taimako","logout":"Fita",
          "start_exam":"Fara Jarrabawa","start_practice":"Fara Aiki","start_quiz":"Fara Quiz","submit":"Aika",
          "next":"Na Gaba","previous":"Na Baya","score":"Maki","grade":"Daraja","certificate":"Takarda",
          "leaderboard":"Jerin Sakamako","my_results":"Sakamakon Na","notifications":"Sanarwa",
          "all_jamb_students":"Duk Ɗaliban JAMB","live_quiz":"Gasar Kai Tsaye 📺"},
    "ar":{"app_name":"ممارسة امتحانات أحمردي","app_short":"AEP","tagline":"المنصة الأولى للامتحانات في نيجيريا",
          "login":"تسجيل الدخول","register":"التسجيل","email":"البريد الإلكتروني","password":"كلمة المرور",
          "full_name":"الاسم الكامل","school":"المدرسة","state":"الولاية","address":"العنوان",
          "dob":"تاريخ الميلاد","phone":"رقم الهاتف","confirm_password":"تأكيد كلمة المرور",
          "create_account":"إنشاء حساب","login_now":"سجل الدخول الآن","welcome_back":"مرحباً بعودتك",
          "dashboard":"لوحة التحكم","subjects":"المواد","exam_mode":"وضع الامتحان","practice_mode":"وضع التدريب",
          "quiz_mode":"وضع الاختبار","duel_mode":"وضع المبارزة","library":"مكتبة الكتب","chat":"الدردشة",
          "group_chat":"دردشة جماعية","profile":"الملف الشخصي","support":"الدعم","logout":"تسجيل الخروج",
          "start_exam":"بدء الامتحان","start_practice":"بدء التدريب","start_quiz":"بدء الاختبار","submit":"إرسال",
          "next":"التالي","previous":"السابق","score":"النتيجة","grade":"الدرجة","certificate":"الشهادة",
          "leaderboard":"لوحة المتصدرين","my_results":"نتائجي","notifications":"الإشعارات",
          "all_jamb_students":"جميع طلاب JAMB","live_quiz":"مسابقة مباشرة 📺"},
}

def get_lang(): return session.get("lang","en")
def t(key):
    lang=get_lang()
    return TRANSLATIONS.get(lang,TRANSLATIONS["en"]).get(key,TRANSLATIONS["en"].get(key,key))

# ═══════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════
class User(db.Model):
    __tablename__="users"
    id=db.Column(db.String(32),primary_key=True)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(256),nullable=False)
    name=db.Column(db.String(120),nullable=False)
    reg_number=db.Column(db.String(20),unique=True)
    school=db.Column(db.String(200)); state=db.Column(db.String(80))
    address=db.Column(db.String(300)); dob=db.Column(db.String(20)); phone=db.Column(db.String(20))
    role=db.Column(db.String(20),default="student")
    avatar=db.Column(Text)
    lang_pref=db.Column(db.String(5),default="en")
    xp_points=db.Column(db.Integer,default=0)
    exam_count=db.Column(db.Integer,default=0); practice_count=db.Column(db.Integer,default=0)
    online=db.Column(db.Boolean,default=False); last_seen=db.Column(db.String(30))
    banned=db.Column(db.Boolean,default=False); blocked=db.Column(db.Boolean,default=False)
    warned=db.Column(db.Boolean,default=False); active=db.Column(db.Boolean,default=True)
    created=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    group_last_read=db.Column(db.String(30),default="2000-01-01")
    def to_dict(self):
        return {"id":self.id,"email":self.email,"name":self.name,"reg_number":self.reg_number,
                "school":self.school,"state":self.state,"address":self.address,"dob":self.dob,
                "phone":self.phone,"role":self.role,"avatar":self.avatar or "","lang_pref":self.lang_pref,
                "xp_points":self.xp_points or 0,"exam_count":self.exam_count or 0,
                "practice_count":self.practice_count or 0,"online":self.online,"banned":self.banned,
                "blocked":self.blocked,"warned":self.warned,"created":self.created}

class Question(db.Model):
    __tablename__="questions"
    id=db.Column(db.String(24),primary_key=True)
    subject=db.Column(db.String(100),nullable=False)
    question=db.Column(Text,nullable=False)
    option_a=db.Column(db.String(500)); option_b=db.Column(db.String(500))
    option_c=db.Column(db.String(500)); option_d=db.Column(db.String(500))
    answer=db.Column(db.String(1)); explanation=db.Column(Text)
    created=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    def to_dict(self):
        return {"id":self.id,"subject":self.subject,"question":self.question,
                "options":{"A":self.option_a,"B":self.option_b,"C":self.option_c,"D":self.option_d},
                "answer":self.answer,"explanation":self.explanation or ""}

class Result(db.Model):
    __tablename__="results"
    id=db.Column(db.String(30),primary_key=True)
    user_id=db.Column(db.String(32),db.ForeignKey("users.id"))
    user_name=db.Column(db.String(120)); reg_number=db.Column(db.String(20))
    subject=db.Column(db.String(100)); mode=db.Column(db.String(20))
    score=db.Column(db.Integer,default=0); total=db.Column(db.Integer,default=0)
    percentage=db.Column(db.Float,default=0); grade=db.Column(db.String(2))
    details=db.Column(Text); date=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    verify_id=db.Column(db.String(20),unique=True)
    user=db.relationship("User",backref="results",foreign_keys=[user_id])

class LiveQuiz(db.Model):
    __tablename__="live_quizzes"
    id=db.Column(db.String(20),primary_key=True)
    subject=db.Column(db.String(100)); subjects_list=db.Column(Text)
    player1_id=db.Column(db.String(32),db.ForeignKey("users.id"))
    player2_id=db.Column(db.String(32),db.ForeignKey("users.id"))
    status=db.Column(db.String(20),default="pending")
    current_q_index=db.Column(db.Integer,default=0)
    question_ids=db.Column(Text); player1_score=db.Column(db.Integer,default=0)
    player2_score=db.Column(db.Integer,default=0)
    answered_this_q=db.Column(Text,default="[]")
    time_per_q=db.Column(db.Integer,default=30); q_start_time=db.Column(db.String(30))
    created=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    started_at=db.Column(db.String(30)); finished_at=db.Column(db.String(30))
    scheduled_time=db.Column(db.String(30)); created_by=db.Column(db.String(32))
    player1=db.relationship("User",foreign_keys=[player1_id])
    player2=db.relationship("User",foreign_keys=[player2_id])
    def to_dict(self):
        p1=self.player1; p2=self.player2; qids=json.loads(self.question_ids or "[]")
        return {"id":self.id,"subject":self.subject,"subjects_list":json.loads(self.subjects_list or "[]"),
                "player1_id":self.player1_id,"player2_id":self.player2_id,
                "player1_name":p1.name if p1 else "","player2_name":p2.name if p2 else "",
                "player1_avatar":p1.avatar or "" if p1 else "","player2_avatar":p2.avatar or "" if p2 else "",
                "status":self.status,"current_q_index":self.current_q_index,"total_questions":len(qids),
                "player1_score":self.player1_score,"player2_score":self.player2_score,
                "answered_this_q":json.loads(self.answered_this_q or "[]"),
                "time_per_q":self.time_per_q,"q_start_time":self.q_start_time or "",
                "scheduled_time":self.scheduled_time or ""}

class GroupMessage(db.Model):
    __tablename__="group_messages"
    id=db.Column(db.String(20),primary_key=True)
    from_id=db.Column(db.String(32)); from_name=db.Column(db.String(120))
    from_role=db.Column(db.String(20)); from_avatar=db.Column(Text)
    message=db.Column(Text); time=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    pinned=db.Column(db.Boolean,default=False); reply_to_id=db.Column(db.String(20))
    def to_dict(self):
        return {"id":self.id,"from":self.from_id,"from_name":self.from_name,"from_role":self.from_role,
                "from_avatar":self.from_avatar or "","message":self.message,"time":self.time,
                "pinned":self.pinned,"reply_to":self.reply_to_id}

class LiveComment(db.Model):
    __tablename__="live_comments"
    id=db.Column(db.String(20),primary_key=True)
    quiz_id=db.Column(db.String(20),db.ForeignKey("live_quizzes.id"))
    from_id=db.Column(db.String(32)); from_name=db.Column(db.String(120))
    from_avatar=db.Column(Text); message=db.Column(Text)
    time=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    def to_dict(self):
        return {"id":self.id,"quiz_id":self.quiz_id,"from":self.from_id,"from_name":self.from_name,
                "from_avatar":self.from_avatar or "","message":self.message,"time":self.time}

class DmMessage(db.Model):
    __tablename__="dm_messages"
    id=db.Column(db.String(20),primary_key=True); from_id=db.Column(db.String(32))
    to_id=db.Column(db.String(32)); from_name=db.Column(db.String(120))
    message=db.Column(Text); time=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    read=db.Column(db.Boolean,default=False); room_key=db.Column(db.String(70))

class Broadcast(db.Model):
    __tablename__="broadcasts"
    id=db.Column(db.String(20),primary_key=True); message=db.Column(Text)
    target_id=db.Column(db.String(32)); by=db.Column(db.String(120))
    date=db.Column(db.String(30),default=lambda:datetime.now().isoformat())

class SupportTicket(db.Model):
    __tablename__="support_tickets"
    id=db.Column(db.String(20),primary_key=True); user_id=db.Column(db.String(32))
    user_name=db.Column(db.String(120)); reg_number=db.Column(db.String(20))
    message=db.Column(Text); date=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    status=db.Column(db.String(20),default="open"); replies=db.Column(Text,default="[]")

class Report(db.Model):
    __tablename__="reports"
    id=db.Column(db.String(20),primary_key=True)
    reporter_id=db.Column(db.String(32)); reporter_name=db.Column(db.String(120))
    target_id=db.Column(db.String(32)); target_name=db.Column(db.String(120))
    reason=db.Column(Text); date=db.Column(db.String(30),default=lambda:datetime.now().isoformat())
    status=db.Column(db.String(20),default="pending")

class Book(db.Model):
    __tablename__="books"
    id=db.Column(db.String(20),primary_key=True); title=db.Column(db.String(200))
    subject=db.Column(db.String(100)); description=db.Column(Text)
    filename=db.Column(db.String(200)); size=db.Column(db.Integer,default=0)
    uploaded=db.Column(db.String(30),default=lambda:datetime.now().isoformat())

class Settings(db.Model):
    __tablename__="settings"
    key=db.Column(db.String(80),primary_key=True); value=db.Column(Text)

# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def hash_pw(pw):
    s=secrets.token_hex(8); h=hashlib.sha256((s+pw).encode()).hexdigest(); return f"{s}:{h}"
def check_pw(pw,stored):
    try: s,h=stored.split(":",1); return hashlib.sha256((s+pw).encode()).hexdigest()==h
    except: return False
def gen_reg(): year=datetime.now().year; c=User.query.filter_by(role="student").count()+1; return f"AEP{year}{c:04d}"

def get_setting(k,default=None):
    row=Settings.query.get(k)
    if not row: return default
    try: return json.loads(row.value)
    except: return row.value

def set_setting(k,v):
    row=Settings.query.get(k)
    if not row: row=Settings(key=k); db.session.add(row)
    row.value=json.dumps(v); db.session.commit()

def all_settings():
    defs={"app_name":"Ahmerdee Exam Practice","exam_duration_minutes":40,"exam_questions":40,
          "practice_questions":20,"quiz_time_per_question":30,"allow_registration":True,
          "maintenance_mode":False,"group_only_admin":False,"group_name":"All JAMB Students"}
    return {k: (get_setting(k) if get_setting(k) is not None else v) for k,v in defs.items()}

def process_avatar(f):
    try:
        img=Image.open(f).convert("RGB").resize((500,500),Image.LANCZOS)
        buf=io.BytesIO(); img.save(buf,format="JPEG",quality=85,optimize=True)
        return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode()
    except: return None

def cu(): return User.query.get(session["user_id"]) if "user_id" in session else None

def bctx():
    lang=get_lang(); user=cu()
    return {"lang":lang,"t":t,"user":user,"app_name":t("app_name"),"app_short":APP_SHORT,
            "dir":"rtl" if lang=="ar" else "ltr"}

def login_req(f):
    @wraps(f)
    def d(*a,**k):
        if "user_id" not in session: return redirect(url_for("login"))
        return f(*a,**k)
    return d

def admin_req(f):
    @wraps(f)
    def d(*a,**k):
        if "user_id" not in session: return redirect(url_for("login"))
        u=User.query.get(session["user_id"])
        if not u or u.role not in ["admin","super_admin"]: return redirect(url_for("dashboard"))
        return f(*a,**k)
    return d

def super_req(f):
    @wraps(f)
    def d(*a,**k):
        if "user_id" not in session: return redirect(url_for("login"))
        u=User.query.get(session["user_id"])
        if not u or u.role!="super_admin": return redirect(url_for("dashboard"))
        return f(*a,**k)
    return d

# ═══════════════════════════════════════════════
# SEED
# ═══════════════════════════════════════════════
SEED_QS = {
  "English Language":[
    {"q":"Which of the following is a noun?","a":["Run","Beautiful","Happiness","Quickly"],"ans":"C","exp":"Happiness names a feeling — it is a noun."},
    {"q":"Identify the correct sentence:","a":["She go to school.","She goes to school.","She gone to school.","She going to school."],"ans":"B","exp":"Third-person singular requires 's': she goes."},
    {"q":"The plural of 'child' is:","a":["Childs","Childes","Children","Childrens"],"ans":"C","exp":"Child has an irregular plural: children."},
    {"q":"Synonym of 'benevolent':","a":["Cruel","Kind","Angry","Lazy"],"ans":"B","exp":"Benevolent means well-meaning and kind."},
    {"q":"A word opposite in meaning is called:","a":["Synonym","Homonym","Antonym","Acronym"],"ans":"C","exp":"Antonyms are words with opposite meanings."},
    {"q":"'The sun rises in the east.' Sentence type:","a":["Compound","Complex","Simple","Compound-complex"],"ans":"C","exp":"One independent clause = simple sentence."},
    {"q":"Figure of speech in: 'The wind whispered':","a":["Simile","Metaphor","Personification","Hyperbole"],"ans":"C","exp":"Giving human quality to wind = personification."},
    {"q":"Correct spelling:","a":["Recieve","Receive","Receeve","Receve"],"ans":"B","exp":"i before e except after c."},
    {"q":"'Quickly' is a(n):","a":["Adjective","Noun","Adverb","Verb"],"ans":"C","exp":"Adverbs modify verbs."},
    {"q":"'Laughter is the best medicine' is a:","a":["Metaphor","Proverb","Simile","Idiom"],"ans":"B","exp":"A widely known proverbial saying."},
    {"q":"Select correct article: '___ university is nearby.'","a":["A","An","The","No article"],"ans":"A","exp":"University starts with /j/ sound, use 'a'."},
    {"q":"'She had eaten before he arrived' tense:","a":["Simple past","Past continuous","Past perfect","Present perfect"],"ans":"C","exp":"Had + past participle = past perfect."},
    {"q":"Preposition in: 'She sat beside the window.'","a":["She","Sat","Beside","Window"],"ans":"C","exp":"Beside shows spatial relationship."},
    {"q":"Collective noun for lions:","a":["Pack","Herd","Pride","Flock"],"ans":"C","exp":"A group of lions = a pride."},
    {"q":"'She is the tallest.' Degree:","a":["Positive","Comparative","Superlative","Absolute"],"ans":"C","exp":"Tallest is superlative."},
  ],
  "Mathematics":[
    {"q":"15% of 200?","a":["20","25","30","35"],"ans":"C","exp":"15/100 × 200 = 30."},
    {"q":"Solve: 3x + 6 = 18","a":["x=2","x=3","x=4","x=6"],"ans":"C","exp":"3x=12, x=4."},
    {"q":"LCM of 4 and 6?","a":["24","12","8","6"],"ans":"B","exp":"LCM(4,6)=12."},
    {"q":"Simplify: (2³)²","a":["12","32","64","16"],"ans":"C","exp":"2^6=64."},
    {"q":"If a=3,b=4, √(a²+b²):","a":["5","7","25","12"],"ans":"A","exp":"√25=5."},
    {"q":"Gradient of y=3x+5:","a":["5","3","8","15"],"ans":"B","exp":"m=3 in y=mx+c."},
    {"q":"Factorize x²-9:","a":["(x-3)(x+3)","(x-9)(x+1)","(x+3)²","(x-3)²"],"ans":"A","exp":"Difference of squares."},
    {"q":"Sum of angles in triangle:","a":["90°","180°","270°","360°"],"ans":"B","exp":"Always 180°."},
    {"q":"Area of circle r=7,π=22/7:","a":["44","154","22","308"],"ans":"B","exp":"πr²=154."},
    {"q":"2^x=32, x=?","a":["4","5","6","3"],"ans":"B","exp":"2⁵=32."},
    {"q":"log₁₀ 1000:","a":["1","2","3","4"],"ans":"C","exp":"10³=1000."},
    {"q":"Speed: 120km in 2hrs:","a":["60 km/h","50 km/h","80 km/h","40 km/h"],"ans":"A","exp":"120÷2=60."},
    {"q":"Median of 3,7,1,9,5:","a":["5","7","4","3"],"ans":"A","exp":"Sorted: 1,3,5,7,9 → middle=5."},
    {"q":"Solve x²-5x+6=0:","a":["x=2,3","x=1,6","x=-2,-3","x=2,-3"],"ans":"A","exp":"(x-2)(x-3)=0."},
    {"q":"0.25 as fraction:","a":["1/2","1/4","1/5","2/5"],"ans":"B","exp":"25/100=1/4."},
  ],
  "Physics":[
    {"q":"SI unit of force:","a":["Joule","Newton","Watt","Pascal"],"ans":"B","exp":"Force in Newtons (N)."},
    {"q":"Speed of light in vacuum:","a":["3×10⁶ m/s","3×10⁸ m/s","3×10¹⁰ m/s","3×10⁵ m/s"],"ans":"B","exp":"c≈3×10⁸ m/s."},
    {"q":"Moving car possesses:","a":["Potential energy","Chemical energy","Kinetic energy","Nuclear energy"],"ans":"C","exp":"Moving objects have kinetic energy."},
    {"q":"Newton's 3rd Law:","a":["F=ma","v=u+at","Every action has equal opposite reaction","E=mc²"],"ans":"C","exp":"Newton's Third Law."},
    {"q":"Unit of resistance:","a":["Ampere","Volt","Ohm","Watt"],"ans":"C","exp":"Resistance in Ohms."},
    {"q":"NOT a vector:","a":["Velocity","Force","Speed","Displacement"],"ans":"C","exp":"Speed has magnitude only."},
    {"q":"Bending of light is:","a":["Reflection","Refraction","Diffraction","Dispersion"],"ans":"B","exp":"Refraction due to speed change."},
    {"q":"V=12V,R=4Ω, I=?","a":["3A","48A","0.33A","8A"],"ans":"A","exp":"I=V/R=3A."},
    {"q":"Energy in compressed spring:","a":["Kinetic","Electrical","Elastic potential","Gravitational potential"],"ans":"C","exp":"Elastic potential energy."},
    {"q":"Wave needing no medium:","a":["Sound","Water","Electromagnetic","Seismic"],"ans":"C","exp":"EM waves travel in vacuum."},
    {"q":"Unit of power:","a":["Newton","Joule","Watt","Pascal"],"ans":"C","exp":"Power in Watts."},
    {"q":"f=50Hz, Period=?","a":["50s","0.02s","5s","0.2s"],"ans":"B","exp":"T=1/f=0.02s."},
    {"q":"Atmospheric pressure measured by:","a":["Thermometer","Barometer","Ammeter","Voltmeter"],"ans":"B","exp":"Barometer measures air pressure."},
    {"q":"Highest frequency colour:","a":["Red","Green","Blue","Violet"],"ans":"D","exp":"Violet has highest frequency."},
    {"q":"Gravitational PE=:","a":["½mv²","mgh","mv","Fd"],"ans":"B","exp":"GPE=mgh."},
  ],
  "Chemistry":[
    {"q":"Symbol for Gold:","a":["Go","Gd","Au","Ag"],"ans":"C","exp":"Au from Latin Aurum."},
    {"q":"Formula for water:","a":["H₂O₂","HO","H₂O","H₃O"],"ans":"C","exp":"Two H, one O."},
    {"q":"Atomic number of Carbon:","a":["12","6","14","8"],"ans":"B","exp":"Carbon has 6 protons."},
    {"q":"Gas from HCl + Zinc:","a":["Oxygen","Carbon dioxide","Hydrogen","Chlorine"],"ans":"C","exp":"Zn+2HCl→ZnCl₂+H₂↑"},
    {"q":"pH of neutral solution:","a":["0","7","14","1"],"ans":"B","exp":"pH 7 is neutral."},
    {"q":"Noble gas:","a":["Nitrogen","Oxygen","Argon","Fluorine"],"ans":"C","exp":"Argon is Group 18."},
    {"q":"Bond in NaCl:","a":["Covalent","Ionic","Metallic","Hydrogen"],"ans":"B","exp":"Na⁺ and Cl⁻ = ionic."},
    {"q":"Formula of glucose:","a":["C₆H₁₂O₅","C₆H₁₂O₆","C₁₂H₂₂O₁₁","C₆H₁₀O₅"],"ans":"B","exp":"C₆H₁₂O₆."},
    {"q":"Rusting of iron is:","a":["Physical change","Combination","Oxidation","Reduction"],"ans":"C","exp":"Iron oxidises."},
    {"q":"Most electronegative element:","a":["Oxygen","Chlorine","Fluorine","Nitrogen"],"ans":"C","exp":"Fluorine most electronegative."},
  ],
  "Biology":[
    {"q":"Powerhouse of the cell:","a":["Nucleus","Ribosome","Mitochondria","Golgi body"],"ans":"C","exp":"Mitochondria produces ATP."},
    {"q":"Photosynthesis occurs in:","a":["Mitochondria","Chloroplast","Nucleus","Vacuole"],"ans":"B","exp":"Chloroplasts have chlorophyll."},
    {"q":"Universal blood donor:","a":["AB","A","B","O"],"ans":"D","exp":"Group O negative donates to all."},
    {"q":"DNA stands for:","a":["Dioxynucleic Acid","Deoxyribonucleic Acid","Diribonucleic Acid","Deoxyribose Nucleic Acid"],"ans":"B","exp":"Deoxyribonucleic Acid."},
    {"q":"Basic unit of life:","a":["Organ","Tissue","Cell","Organism"],"ans":"C","exp":"Cell is fundamental unit."},
    {"q":"Insulin produced by:","a":["Liver","Kidney","Pancreas","Stomach"],"ans":"C","exp":"Beta cells in pancreas."},
    {"q":"Osmosis: water moves from:","a":["Low to high conc","High to low water potential","Solute low to high","Low to high water potential"],"ans":"B","exp":"High to low water potential."},
    {"q":"Heart chambers:","a":["2","3","4","5"],"ans":"C","exp":"2 atria+2 ventricles=4."},
    {"q":"Vitamin from sunlight:","a":["A","B","C","D"],"ans":"D","exp":"Skin synthesises vitamin D."},
    {"q":"Bacteria are:","a":["Eukaryotes","Prokaryotes","Protists","Fungi"],"ans":"B","exp":"Bacteria lack membrane-bound nucleus."},
  ],
  "Economics":[
    {"q":"Basic economic problem:","a":["Inflation","Scarcity","Unemployment","Trade deficit"],"ans":"B","exp":"Unlimited wants vs limited resources."},
    {"q":"Demand curve slopes:","a":["Upward","Downward","Horizontally","Vertically"],"ans":"B","exp":"Higher price = lower demand."},
    {"q":"GDP stands for:","a":["Gross Domestic Product","Grand Development Plan","General Domestic Price","Gross Departmental Product"],"ans":"A","exp":"Total value of goods/services."},
    {"q":"Inflation means:","a":["Rising purchasing power","Falling prices","Sustained price rise","Money supply decrease"],"ans":"C","exp":"Continuous price level increase."},
    {"q":"Monopoly has ___ seller:","a":["Many","One","Two","Perfect"],"ans":"B","exp":"Single seller controls market."},
    {"q":"Opportunity cost is:","a":["Monetary cost","Next best alternative value","Total cost","Sunk cost"],"ans":"B","exp":"What you give up to choose."},
    {"q":"'Ceteris paribus' means:","a":["All else equal","Supply=demand","Price stability","Equilibrium"],"ans":"A","exp":"All other things equal."},
    {"q":"Direct tax example:","a":["VAT","Import duty","Income tax","Excise duty"],"ans":"C","exp":"Income tax paid directly to govt."},
    {"q":"Gini coefficient measures:","a":["Inflation","Income inequality","GDP","Trade"],"ans":"B","exp":"0=equality, 1=maximum inequality."},
    {"q":"CBN controls:","a":["Tax","Monetary policy","Roads","Trade"],"ans":"B","exp":"CBN controls money supply."},
  ],
  "Government":[
    {"q":"Democracy means:","a":["Rule by elite","Rule by people","Rule by law","Rule by force"],"ans":"B","exp":"Greek: demos+kratos."},
    {"q":"Nigeria's constitution adopted:","a":["1979","1989","1999","2009"],"ans":"C","exp":"1999 Constitution is current."},
    {"q":"Separation of powers by:","a":["John Locke","Rousseau","Montesquieu","Hobbes"],"ans":"C","exp":"Montesquieu proposed three branches."},
    {"q":"Nigeria's legislature:","a":["Cabinet","Supreme Court","National Assembly","Senate only"],"ans":"C","exp":"Senate+House of Reps."},
    {"q":"Nigeria independence year:","a":["1957","1960","1963","1966"],"ans":"B","exp":"October 1, 1960."},
    {"q":"INEC conducts:","a":["Tax","Elections","Foreign policy","Judicial review"],"ans":"B","exp":"INEC manages Nigerian elections."},
    {"q":"Rule of law means:","a":["Govt can do anything","Law applies equally","Military overrides","Law for citizens only"],"ans":"B","exp":"Everyone subject to law."},
    {"q":"ECOWAS founded:","a":["1960","1975","1963","1980"],"ans":"B","exp":"Lagos 1975."},
    {"q":"Franchise means:","a":["Right to trade","Right to vote","Freedom of movement","Right to education"],"ans":"B","exp":"Right to vote."},
    {"q":"Constitution is:","a":["Parliament laws","Fundamental law","Government policy","Executive order"],"ans":"B","exp":"Supreme law of land."},
  ],
  "Hausa":[
    {"q":"Sunayen a cikin: 'Ahmad ya karanta littafi':","a":["Ahmad","karanta","littafi","Ahmad da littafi"],"ans":"D","exp":"Ahmad da littafi sune sunaye."},
    {"q":"Jam'in 'doki':","a":["dokoki","dawakai","dokai","doki-doki"],"ans":"B","exp":"Jam'in doki = dawakai."},
    {"q":"'Fari' a nahawun Hausa shine:","a":["Suna","Aikatau","Sifa","Tawali'u"],"ans":"C","exp":"Fari sifa ce."},
    {"q":"Mataimakin aikatau a: 'Ya gudu da sauri':","a":["Ya","gudu","da","sauri"],"ans":"D","exp":"Sauri yana bayyana yadda aka gudu."},
    {"q":"Ma'anar 'gaskiya':","a":["Karya","Gaskiya/Truth","Gulma","Tsoro"],"ans":"B","exp":"Gaskiya=truth."},
  ],
  "Islamic Religious Studies":[
    {"q":"How many pillars of Islam?","a":["3","4","5","6"],"ans":"C","exp":"Five pillars: Shahada, Salah, Zakat, Sawm, Hajj."},
    {"q":"First revelation to Prophet Muhammad (SAW) was in:","a":["Cave Hira","Cave Thawr","Madinah","Makkah Mosque"],"ans":"A","exp":"First revelation in Cave Hira during Ramadan."},
    {"q":"The Quran has how many chapters (Surah)?","a":["99","100","114","120"],"ans":"C","exp":"The Quran has 114 Surahs."},
    {"q":"Zakat is obligatory for Muslims who:","a":["Are poor","Have nisab","Completed Hajj","Are elderly"],"ans":"B","exp":"Zakat due when wealth reaches nisab threshold."},
    {"q":"Salatul Fajr has how many rakats?","a":["1","2","3","4"],"ans":"B","exp":"Fajr prayer has 2 rakats."},
  ],
}

def seed_db():
    with app.app_context():
        db.create_all()
        _migrate_json()
        # Super admin
        if not User.query.filter_by(email="admin@ahmerdee.com").first():
            sa=User(id="super_admin_001",email="admin@ahmerdee.com",password=hash_pw("Ahmerdee@Admin2026"),
                    name="Ahmerdee (Founder)",reg_number="AEP-FOUNDER",role="super_admin",
                    school="Ahmerdee HQ",state="FCT",address="Abuja",dob="1990-01-01",phone="08000000000")
            db.session.add(sa); db.session.commit()
        # Questions
        for subj,qs in SEED_QS.items():
            if Question.query.filter_by(subject=subj).count()==0:
                for i,q in enumerate(qs):
                    obj=Question(id=f"Q{subj[:2].upper()}{i+1:03d}",subject=subj,question=q["q"],
                                 option_a=q["a"][0],option_b=q["a"][1],option_c=q["a"][2],option_d=q["a"][3],
                                 answer=q["ans"],explanation=q["exp"])
                    db.session.add(obj)
                db.session.commit()

def _migrate_json():
    for path in ["/data/users.json",os.path.join(BASE_DIR,"data","users.json")]:
        if not os.path.exists(path): continue
        try:
            with open(path) as f: users=json.load(f)
            for uid,u in users.items():
                if not User.query.get(uid):
                    obj=User(id=uid,email=u.get("email",""),password=u.get("password",""),
                             name=u.get("name","Unknown"),reg_number=u.get("reg_number",""),
                             school=u.get("school",""),state=u.get("state",""),
                             address=u.get("address",""),dob=u.get("dob",""),phone=u.get("phone",""),
                             role=u.get("role","student"),avatar=u.get("avatar",""),
                             exam_count=u.get("exam_count",0),practice_count=u.get("practice_count",0),
                             banned=u.get("banned",False),blocked=u.get("blocked",False),
                             warned=u.get("warned",False),active=u.get("active",True),
                             created=u.get("created",datetime.now().isoformat()))
                    db.session.add(obj)
            db.session.commit()
        except: pass
    for path in ["/data/questions.json",os.path.join(BASE_DIR,"data","questions.json")]:
        if not os.path.exists(path): continue
        try:
            with open(path) as f: qs=json.load(f)
            for subj,items in qs.items():
                for q in items:
                    if not Question.query.get(q["id"]):
                        opts=q.get("options",{})
                        obj=Question(id=q["id"],subject=subj,question=q["question"],
                                     option_a=opts.get("A",""),option_b=opts.get("B",""),
                                     option_c=opts.get("C",""),option_d=opts.get("D",""),
                                     answer=q["answer"],explanation=q.get("explanation",""))
                        db.session.add(obj)
            db.session.commit()
        except: pass

# ═══════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════
@app.route("/")
def index(): return redirect(url_for("login") if "user_id" not in session else url_for("dashboard"))

@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in ["en","ha","ar"]:
        session["lang"]=lang
        if "user_id" in session:
            u=User.query.get(session["user_id"])
            if u: u.lang_pref=lang; db.session.commit()
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/login",methods=["GET","POST"])
def login():
    if "user_id" in session: return redirect(url_for("dashboard"))
    ctx=bctx()
    if request.method=="POST":
        ident=request.form.get("identifier","").strip(); pw=request.form.get("password","").strip()
        u=User.query.filter(or_(User.email==ident.lower(),User.reg_number==ident.upper())).first()
        if u and check_pw(pw,u.password):
            if u.banned: ctx["error"]="Account banned. Contact support."; return render_template("login.html",**ctx)
            session["user_id"]=u.id; session.permanent=True
            u.online=True; u.last_seen=datetime.now().isoformat(); db.session.commit()
            return redirect(url_for("admin_dashboard") if u.role in ["admin","super_admin"] else url_for("dashboard"))
        ctx["error"]="Invalid credentials. Check email/reg number and password."
    return render_template("login.html",**ctx)

@app.route("/register",methods=["GET","POST"])
def register():
    ctx=bctx(); ctx["states"]=NIGERIAN_STATES
    if not get_setting("allow_registration",True): ctx["error"]="Registration closed."; return render_template("register.html",**ctx)
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower()
        school=request.form.get("school","").strip(); state=request.form.get("state","").strip()
        address=request.form.get("address","").strip(); dob=request.form.get("dob","").strip()
        phone=request.form.get("phone","").strip(); pw=request.form.get("password","").strip()
        confirm=request.form.get("confirm","").strip()
        if not all([name,email,school,state,address,dob,phone,pw]): ctx["error"]="All fields required."; return render_template("register.html",**ctx)
        if pw!=confirm: ctx["error"]="Passwords don't match."; return render_template("register.html",**ctx)
        if len(pw)<6: ctx["error"]="Password must be 6+ characters."; return render_template("register.html",**ctx)
        if User.query.filter_by(email=email).first(): ctx["error"]="Email already registered."; return render_template("register.html",**ctx)
        reg=gen_reg(); uid=secrets.token_hex(12)
        u=User(id=uid,email=email,password=hash_pw(pw),name=name,reg_number=reg,school=school,
               state=state,address=address,dob=dob,phone=phone,role="student")
        db.session.add(u); db.session.commit()
        ctx["success"]=True; ctx["reg_number"]=reg; ctx["student_name"]=name
    return render_template("register.html",**ctx)

@app.route("/logout")
def logout():
    if "user_id" in session:
        u=User.query.get(session["user_id"])
        if u: u.online=False; db.session.commit()
    session.clear(); return redirect(url_for("login"))

# ═══════════════════════════════════════════════
# STUDENT ROUTES
# ═══════════════════════════════════════════════
@app.route("/dashboard")
@login_req
def dashboard():
    user=cu()
    if user.role in ["admin","super_admin"]: return redirect(url_for("admin_dashboard"))
    ctx=bctx()
    rc=Result.query.filter_by(user_id=user.id,mode="exam").count()
    last_bc=Broadcast.query.filter(or_(Broadcast.target_id==None,Broadcast.target_id==user.id)).order_by(Broadcast.date.desc()).first()
    ug=GroupMessage.query.filter(GroupMessage.time>user.group_last_read,GroupMessage.from_id!=user.id).count()
    live=LiveQuiz.query.filter_by(status="active").first()
    ctx.update({"results_count":rc,"recent_bc":last_bc,"unread_group":ug,"live_quiz":live.to_dict() if live else None})
    return render_template("dashboard.html",**ctx)

@app.route("/profile",methods=["GET","POST"])
@login_req
def profile():
    ctx=bctx(); user=cu()
    if request.method=="POST":
        user.name=request.form.get("name",user.name).strip()
        user.phone=request.form.get("phone",user.phone or "").strip()
        user.address=request.form.get("address",user.address or "").strip()
        af=request.files.get("avatar")
        if af and af.filename:
            b64=process_avatar(af)
            if b64: user.avatar=b64; ctx["success_msg"]="Profile picture updated! ✅"
            else: ctx["error"]="Could not process image."
        np=request.form.get("new_password","").strip()
        if np:
            if len(np)<6: ctx["error"]="Password must be 6+ chars."
            else: user.password=hash_pw(np); ctx["success_msg"]="Password updated."
        db.session.commit()
        if "success_msg" not in ctx: ctx["success_msg"]="Profile updated. ✅"
    ctx["user"]=user
    return render_template("profile.html",**ctx)

@app.route("/api/online_status",methods=["POST"])
@login_req
def online_status():
    u=cu()
    if u: u.online=True; u.last_seen=datetime.now().isoformat(); db.session.commit()
    return jsonify({"ok":True})

@app.route("/subjects")
@login_req
def subjects():
    ctx=bctx()
    counts={s:Question.query.filter_by(subject=s).count() for s in JAMB_SUBJECTS}
    ctx["subjects"]=JAMB_SUBJECTS; ctx["subject_counts"]=counts
    return render_template("subjects.html",**ctx)

@app.route("/exam/<subject>")
@login_req
def exam(subject):
    if subject not in JAMB_SUBJECTS: return redirect(url_for("subjects"))
    ctx=bctx(); n=get_setting("exam_questions",40); dur=get_setting("exam_duration_minutes",40)*60
    qs=random.sample(Question.query.filter_by(subject=subject).all(),min(n,Question.query.filter_by(subject=subject).count()))
    ctx.update({"subject":subject,"questions":[q.to_dict() for q in qs],"mode":"exam","duration":dur})
    return render_template("exam.html",**ctx)

@app.route("/practice/<subject>")
@login_req
def practice(subject):
    ctx=bctx(); n=get_setting("practice_questions",20)
    all_qs=Question.query.filter_by(subject=subject).all()
    qs=random.sample(all_qs,min(n,len(all_qs))) if all_qs else []
    ctx.update({"subject":subject,"questions":[q.to_dict() for q in qs],"mode":"practice","duration":0})
    return render_template("practice.html",**ctx)

@app.route("/submit_exam",methods=["POST"])
@login_req
def submit_exam():
    data=request.get_json(); mode=data.get("mode"); subject=data.get("subject")
    answers=data.get("answers",{}); qs=data.get("questions",[])
    score=0; total=len(qs); details=[]
    for q in qs:
        ua=answers.get(q["id"],""); correct=q["answer"]; ic=ua==correct
        if ic: score+=1
        details.append({**q,"user_answer":ua,"is_correct":ic})
    pct=round((score/total)*100) if total else 0
    grade="A" if pct>=70 else "B" if pct>=60 else "C" if pct>=50 else "F"
    user=cu(); rid=f"RES{secrets.token_hex(6).upper()}"
    r=Result(id=rid,user_id=user.id,user_name=user.name,reg_number=user.reg_number,
             subject=subject,mode=mode,score=score,total=total,percentage=pct,grade=grade,
             details=json.dumps(details),verify_id=secrets.token_hex(8).upper())
    db.session.add(r)
    xp=score*10; user.xp_points=(user.xp_points or 0)+xp
    if mode=="exam": user.exam_count=(user.exam_count or 0)+1
    else: user.practice_count=(user.practice_count or 0)+1
    db.session.commit()
    return jsonify({"success":True,"result_id":rid,"score":score,"total":total,"percentage":pct,"grade":grade,"mode":mode,"xp":xp})

@app.route("/result/<rid>")
@login_req
def result(rid):
    ctx=bctx(); r=Result.query.get(rid); user=cu()
    if not r or (r.user_id!=user.id and user.role not in ["admin","super_admin"]): return redirect(url_for("dashboard"))
    ctx["result"]={"id":r.id,"user_id":r.user_id,"user_name":r.user_name,"reg_number":r.reg_number,
                   "subject":r.subject,"mode":r.mode,"score":r.score,"total":r.total,
                   "percentage":r.percentage,"grade":r.grade,"date":r.date,"verify_id":r.verify_id,
                   "details":json.loads(r.details or "[]")}
    return render_template("result.html",**ctx)

@app.route("/my_results")
@login_req
def my_results():
    ctx=bctx()
    ress=Result.query.filter_by(user_id=session["user_id"]).order_by(Result.date.desc()).all()
    ctx["results"]=[{"id":r.id,"subject":r.subject,"mode":r.mode,"score":r.score,"total":r.total,
                     "percentage":r.percentage,"grade":r.grade,"date":r.date} for r in ress]
    return render_template("my_results.html",**ctx)

@app.route("/leaderboard")
@app.route("/leaderboard/<subject>")
@login_req
def leaderboard(subject=None):
    ctx=bctx()
    avail=[s for s in JAMB_SUBJECTS if Question.query.filter_by(subject=s).count()>0]
    if subject and subject not in JAMB_SUBJECTS: subject=None
    sel=subject or (avail[0] if avail else None)
    q=Result.query.filter_by(mode="exam")
    if sel: q=q.filter_by(subject=sel)
    best={}
    for r in q.all():
        k=f"{r.user_id}_{r.subject}"
        if k not in best or r.percentage>best[k]["percentage"]:
            u=User.query.get(r.user_id)
            best[k]={"user_id":r.user_id,"user_name":r.user_name,"reg_number":r.reg_number,
                     "subject":r.subject,"percentage":r.percentage,"grade":r.grade,
                     "date":r.date[:10],"avatar":u.avatar if u else ""}
    board=sorted(best.values(),key=lambda x:x["percentage"],reverse=True)[:50]
    ctx.update({"board":board,"current_uid":session["user_id"],"selected_subject":sel,"available_subjects":avail})
    return render_template("leaderboard.html",**ctx)

@app.route("/group")
@login_req
def group_chat():
    ctx=bctx(); s=all_settings()
    msgs=[m.to_dict() for m in GroupMessage.query.order_by(GroupMessage.time.asc()).limit(100).all()]
    pinned=[p.to_dict() for p in GroupMessage.query.filter_by(pinned=True).order_by(GroupMessage.time.desc()).limit(3).all()]
    u=cu(); u.group_last_read=datetime.now().isoformat(); db.session.commit()
    ctx.update({"messages":msgs,"pinned":pinned,"group_name":s.get("group_name","All JAMB Students"),
                "only_admin_can_talk":s.get("group_only_admin",False)})
    return render_template("group_chat.html",**ctx)

@app.route("/api/group/messages")
@login_req
def group_messages():
    since=request.args.get("since","")
    q=GroupMessage.query.order_by(GroupMessage.time.asc())
    if since: q=q.filter(GroupMessage.time>since)
    else: q=q.limit(50)
    msgs=[m.to_dict() for m in q.all()]
    pinned=[p.to_dict() for p in GroupMessage.query.filter_by(pinned=True).limit(3).all()]
    return jsonify({"messages":msgs,"pinned":pinned})

@app.route("/api/group/send",methods=["POST"])
@login_req
def group_send():
    s=all_settings(); user=cu()
    if s.get("group_only_admin") and user.role not in ["admin","super_admin"]:
        return jsonify({"success":False,"message":"Only admin can send messages now."})
    data=request.get_json(); msg_text=data.get("message","").strip()
    if not msg_text: return jsonify({"success":False})
    msg=GroupMessage(id=secrets.token_hex(8),from_id=user.id,from_name=user.name,from_role=user.role,
                     from_avatar=user.avatar or "",message=msg_text,reply_to_id=data.get("reply_to"))
    db.session.add(msg); db.session.commit()
    d=msg.to_dict(); socketio.emit("group_message",d,room="group")
    return jsonify({"success":True,"msg":d})

@app.route("/api/group/pin",methods=["POST"])
@admin_req
def group_pin():
    data=request.get_json(); m=GroupMessage.query.get(data.get("msg_id"))
    if m: m.pinned=(data.get("action","pin")=="pin"); db.session.commit()
    return jsonify({"success":True})

@app.route("/api/group/delete",methods=["POST"])
@admin_req
def group_delete():
    m=GroupMessage.query.get(request.get_json().get("msg_id"))
    if m: db.session.delete(m); db.session.commit()
    return jsonify({"success":True})

@app.route("/chat")
@login_req
def chat():
    ctx=bctx(); ctx["students"]=[u.to_dict() for u in User.query.filter(User.id!=session["user_id"],User.banned==False).all()]
    return render_template("chat.html",**ctx)

@app.route("/api/chat/messages/<target_id>")
@login_req
def chat_messages(target_id):
    rk="_".join(sorted([session["user_id"],target_id]))
    msgs=DmMessage.query.filter_by(room_key=rk).order_by(DmMessage.time.asc()).all()
    for m in msgs:
        if m.to_id==session["user_id"] and not m.read: m.read=True
    db.session.commit()
    return jsonify([{"id":m.id,"from":m.from_id,"from_name":m.from_name,"to":m.to_id,"message":m.message,"time":m.time,"read":m.read} for m in msgs])

@app.route("/api/chat/send",methods=["POST"])
@login_req
def chat_send():
    data=request.get_json(); tid=data.get("to"); msg_text=data.get("message","").strip()
    if not tid or not msg_text: return jsonify({"success":False})
    user=cu(); rk="_".join(sorted([session["user_id"],tid]))
    msg=DmMessage(id=secrets.token_hex(8),from_id=user.id,from_name=user.name,to_id=tid,message=msg_text,room_key=rk)
    db.session.add(msg); db.session.commit()
    socketio.emit("dm_message",{"from":user.id,"from_name":user.name,"to":tid,"message":msg_text,"time":msg.time},room=f"dm_{tid}")
    return jsonify({"success":True})

@app.route("/support",methods=["GET","POST"])
@login_req
def support():
    ctx=bctx(); uid=session["user_id"]; user=cu()
    if request.method=="POST":
        msg=request.form.get("message","").strip()
        if msg:
            tk=SupportTicket(id=secrets.token_hex(8),user_id=uid,user_name=user.name,reg_number=user.reg_number,message=msg)
            db.session.add(tk); db.session.commit(); ctx["success_msg"]="Message sent to admin."
    ctx["tickets"]=[{"id":t.id,"message":t.message,"date":t.date,"status":t.status,"replies":json.loads(t.replies or "[]")}
                    for t in SupportTicket.query.filter_by(user_id=uid).order_by(SupportTicket.date.desc()).all()]
    return render_template("support.html",**ctx)

@app.route("/notifications")
@login_req
def notifications():
    ctx=bctx()
    ctx["broadcasts"]=[{"id":b.id,"message":b.message,"by":b.by,"date":b.date}
                       for b in Broadcast.query.filter(or_(Broadcast.target_id==None,Broadcast.target_id==session["user_id"])).order_by(Broadcast.date.desc()).all()]
    return render_template("notifications.html",**ctx)

@app.route("/library")
@login_req
def library():
    ctx=bctx(); ctx["books"]=[{"id":b.id,"title":b.title,"subject":b.subject,"description":b.description,"size":b.size} for b in Book.query.all()]
    return render_template("library.html",**ctx)

@app.route("/download_book/<bid>")
@login_req
def download_book(bid):
    b=Book.query.get(bid)
    if not b: return redirect(url_for("library"))
    fp=os.path.join(DATA_DIR,"books",b.filename)
    if not os.path.exists(fp): return "File not found",404
    return send_file(fp,as_attachment=True,download_name=b.title+".pdf")

@app.route("/verify")
@app.route("/verify/<vid>")
def verify_cert(vid=None):
    ctx=bctx(); result=None
    if vid:
        r=Result.query.filter_by(verify_id=vid.upper()).first()
        if r: result={"user_name":r.user_name,"subject":r.subject,"score":r.score,"total":r.total,"percentage":r.percentage,"grade":r.grade,"date":r.date}
    ctx["result"]=result; ctx["verify_id"]=vid or ""
    return render_template("verify.html",**ctx)

@app.route("/report_user",methods=["POST"])
@login_req
def report_user():
    data=request.get_json(); tid=data.get("user_id"); reason=data.get("reason","").strip()
    if not tid or not reason: return jsonify({"success":False})
    user=cu(); target=User.query.get(tid)
    r=Report(id=secrets.token_hex(8),reporter_id=user.id,reporter_name=user.name,
             target_id=tid,target_name=target.name if target else "Unknown",reason=reason)
    db.session.add(r); db.session.commit()
    return jsonify({"success":True,"message":"Report submitted."})

# ═══════════════════════════════════════════════
# LIVE QUIZ ROUTES
# ═══════════════════════════════════════════════
@app.route("/live")
@login_req
def live_quiz_lobby():
    ctx=bctx()
    quizzes=LiveQuiz.query.filter(LiveQuiz.status.in_(["pending","active"])).all()
    ctx["quizzes"]=[q.to_dict() for q in quizzes]
    return render_template("live_quiz_lobby.html",**ctx)

@app.route("/live/<qid>")
@login_req
def live_quiz(qid):
    ctx=bctx(); quiz=LiveQuiz.query.get(qid)
    if not quiz: return redirect(url_for("live_quiz_lobby"))
    user=cu(); is_player=user.id in [quiz.player1_id,quiz.player2_id]
    qids=json.loads(quiz.question_ids or "[]")
    current_q=None
    if quiz.status=="active" and qids and quiz.current_q_index<len(qids):
        q=Question.query.get(qids[quiz.current_q_index])
        if q:
            d=q.to_dict()
            if is_player: d.pop("answer",None); d.pop("explanation",None)  # hide answer from players
            current_q=d
    comments=[c.to_dict() for c in LiveComment.query.filter_by(quiz_id=qid).order_by(LiveComment.time.asc()).limit(100).all()]
    ctx.update({"quiz":quiz.to_dict(),"is_player":is_player,"current_q":current_q,"comments":comments,"quiz_id":qid})
    return render_template("live_quiz.html",**ctx)

@app.route("/api/live/comment",methods=["POST"])
@login_req
def live_comment():
    data=request.get_json(); qid=data.get("quiz_id"); msg_text=data.get("message","").strip()
    if not qid or not msg_text: return jsonify({"success":False})
    quiz=LiveQuiz.query.get(qid)
    if not quiz: return jsonify({"success":False})
    user=cu()
    if quiz.status=="active" and user.id in [quiz.player1_id,quiz.player2_id]:
        return jsonify({"success":False,"message":"Players cannot comment during quiz!"})
    c=LiveComment(id=secrets.token_hex(8),quiz_id=qid,from_id=user.id,from_name=user.name,from_avatar=user.avatar or "",message=msg_text)
    db.session.add(c); db.session.commit()
    cd=c.to_dict(); socketio.emit("live_comment",cd,room=f"spectators_{qid}")
    return jsonify({"success":True,"comment":cd})

@app.route("/api/live/answer",methods=["POST"])
@login_req
def live_answer():
    data=request.get_json(); qid=data.get("quiz_id"); answer=data.get("answer","").upper()
    quiz=LiveQuiz.query.get(qid)
    if not quiz or quiz.status!="active": return jsonify({"success":False,"message":"Quiz not active"})
    user=cu()
    if user.id not in [quiz.player1_id,quiz.player2_id]: return jsonify({"success":False,"message":"Not a player"})
    answered=json.loads(quiz.answered_this_q or "[]")
    if user.id in answered: return jsonify({"success":False,"message":"Already answered"})
    qids=json.loads(quiz.question_ids or "[]")
    q=Question.query.get(qids[quiz.current_q_index]) if qids else None
    correct=q.answer if q else None; is_correct=answer==correct
    if is_correct:
        if user.id==quiz.player1_id: quiz.player1_score+=1
        else: quiz.player2_score+=1
    answered.append(user.id); quiz.answered_this_q=json.dumps(answered); db.session.commit()
    payload={"player_id":user.id,"player_name":user.name,"answer":answer,"correct":is_correct,
             "correct_answer":correct,"p1_score":quiz.player1_score,"p2_score":quiz.player2_score}
    socketio.emit("live_answer",payload,room=f"quiz_{qid}")
    return jsonify({"success":True,"correct":is_correct,"correct_answer":correct,"explanation":q.explanation if q else ""})

@app.route("/api/live/state/<qid>")
@login_req
def live_state(qid):
    quiz=LiveQuiz.query.get(qid)
    if not quiz: return jsonify({"error":"not found"}),404
    user=cu(); is_player=user.id in [quiz.player1_id,quiz.player2_id]
    d=quiz.to_dict(); qids=json.loads(quiz.question_ids or "[]")
    if quiz.status=="active" and qids and quiz.current_q_index<len(qids):
        q=Question.query.get(qids[quiz.current_q_index])
        if q:
            qd=q.to_dict()
            if is_player: qd.pop("answer",None); qd.pop("explanation",None)
            d["current_question"]=qd
    return jsonify(d)

# ═══════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════
@app.route("/admin")
@admin_req
def admin_dashboard():
    ctx=bctx()
    ctx.update({"total_users":User.query.filter_by(role="student").count(),
                "total_questions":Question.query.count(),"total_results":Result.query.count(),
                "pending_reports":Report.query.filter_by(status="pending").count(),
                "total_books":Book.query.count(),"open_tickets":SupportTicket.query.filter_by(status="open").count(),
                "active_quizzes":LiveQuiz.query.filter(LiveQuiz.status.in_(["pending","active"])).count(),
                "online_students":User.query.filter_by(online=True,role="student").count()})
    return render_template("admin/dashboard.html",**ctx)

@app.route("/admin/users")
@admin_req
def admin_users():
    ctx=bctx(); q=request.args.get("q","").strip().lower()
    query=User.query.filter_by(role="student")
    if q: query=query.filter(or_(User.name.ilike(f"%{q}%"),User.reg_number.ilike(f"%{q}%"),User.email.ilike(f"%{q}%")))
    ctx["students"]=[u.to_dict() for u in query.order_by(User.created.desc()).all()]; ctx["q"]=q
    return render_template("admin/users.html",**ctx)

@app.route("/admin/user/<uid>")
@admin_req
def admin_user_detail(uid):
    ctx=bctx(); u=User.query.get(uid)
    if not u: return redirect(url_for("admin_users"))
    ctx["target"]=u.to_dict()
    ctx["user_results"]=[{"id":r.id,"subject":r.subject,"mode":r.mode,"score":r.score,"total":r.total,"percentage":r.percentage,"grade":r.grade,"date":r.date}
                         for r in Result.query.filter_by(user_id=uid).all()]
    return render_template("admin/user_detail.html",**ctx)

@app.route("/admin/user_action",methods=["POST"])
@admin_req
def admin_user_action():
    data=request.get_json(); uid=data.get("uid"); action=data.get("action")
    u=User.query.get(uid)
    if not u: return jsonify({"success":False,"message":"User not found"})
    if action=="warn": u.warned=True
    elif action=="block": u.blocked=not u.blocked
    elif action=="ban": u.banned=not u.banned
    elif action=="unblock": u.blocked=False
    elif action=="unban": u.banned=False
    db.session.commit()
    return jsonify({"success":True,"message":f"Action '{action}' applied."})

@app.route("/admin/questions")
@admin_req
def admin_questions():
    ctx=bctx(); subj=request.args.get("subject",JAMB_SUBJECTS[0])
    ctx["questions"]=[q.to_dict() for q in Question.query.filter_by(subject=subj).all()]
    ctx["subjects"]=JAMB_SUBJECTS; ctx["selected_subject"]=subj
    return render_template("admin/questions.html",**ctx)

@app.route("/admin/add_question",methods=["POST"])
@admin_req
def admin_add_question():
    data=request.get_json(); subj=data.get("subject"); qt=data.get("question","").strip()
    opts=data.get("options",{}); ans=data.get("answer","").strip().upper()
    if not all([subj,qt,opts,ans]): return jsonify({"success":False,"message":"Missing fields"})
    qobj=Question(id=f"Q{secrets.token_hex(5).upper()}",subject=subj,question=qt,
                  option_a=opts.get("A",""),option_b=opts.get("B",""),option_c=opts.get("C",""),option_d=opts.get("D",""),
                  answer=ans,explanation=data.get("explanation",""))
    db.session.add(qobj); db.session.commit()
    return jsonify({"success":True,"message":"Question added."})

@app.route("/admin/edit_question",methods=["POST"])
@admin_req
def admin_edit_question():
    data=request.get_json(); qid=data.get("qid"); q=Question.query.get(qid)
    if q:
        opts=data.get("options",{})
        q.question=data.get("question",q.question); q.option_a=opts.get("A",q.option_a)
        q.option_b=opts.get("B",q.option_b); q.option_c=opts.get("C",q.option_c); q.option_d=opts.get("D",q.option_d)
        q.answer=data.get("answer",q.answer); q.explanation=data.get("explanation",q.explanation)
        db.session.commit()
    return jsonify({"success":True,"message":"Question updated."})

@app.route("/admin/delete_question",methods=["POST"])
@admin_req
def admin_delete_question():
    q=Question.query.get(request.get_json().get("qid"))
    if q: db.session.delete(q); db.session.commit()
    return jsonify({"success":True})

@app.route("/admin/bulk_import",methods=["POST"])
@admin_req
def admin_bulk_import():
    try:
        data=request.get_json(); subj=data.get("subject"); qs_raw=data.get("questions",[]); added=0
        for q in qs_raw:
            opts=q.get("options",{})
            obj=Question(id=f"Q{secrets.token_hex(5).upper()}",subject=subj,question=q.get("question",""),
                         option_a=opts.get("A",""),option_b=opts.get("B",""),option_c=opts.get("C",""),option_d=opts.get("D",""),
                         answer=q.get("answer","A"),explanation=q.get("explanation",""))
            db.session.add(obj); added+=1
        db.session.commit()
        return jsonify({"success":True,"message":f"{added} questions imported."})
    except Exception as e: return jsonify({"success":False,"message":str(e)})

@app.route("/admin/live_quizzes")
@admin_req
def admin_live_quizzes():
    ctx=bctx()
    ctx["quizzes"]=[q.to_dict() for q in LiveQuiz.query.order_by(LiveQuiz.created.desc()).all()]
    ctx["students"]=[u.to_dict() for u in User.query.filter_by(role="student",banned=False).order_by(User.name.asc()).all()]
    ctx["subjects"]=JAMB_SUBJECTS
    return render_template("admin/live_quizzes.html",**ctx)

@app.route("/admin/create_live_quiz",methods=["POST"])
@admin_req
def admin_create_live_quiz():
    data=request.get_json()
    p1=data.get("player1_id"); p2=data.get("player2_id")
    subjects_list=data.get("subjects",[data.get("subject",JAMB_SUBJECTS[0])])
    tpq=int(data.get("time_per_q",30)); sched=data.get("scheduled_time","")
    nq=int(data.get("n_questions",10))
    if not p1 or not p2: return jsonify({"success":False,"message":"Need 2 players"})
    all_qids=[]
    for subj in subjects_list:
        qs=Question.query.filter_by(subject=subj).all()
        all_qids.extend([q.id for q in random.sample(qs,min(nq,len(qs)))])
    random.shuffle(all_qids)
    quiz=LiveQuiz(id=f"LQ{secrets.token_hex(5).upper()}",subject=subjects_list[0],
                  subjects_list=json.dumps(subjects_list),player1_id=p1,player2_id=p2,
                  status="pending",question_ids=json.dumps(all_qids),time_per_q=tpq,
                  scheduled_time=sched,created_by=session["user_id"])
    db.session.add(quiz); db.session.commit()
    p1u=User.query.get(p1); p2u=User.query.get(p2)
    ann=(f"🏟️ LIVE QUIZ SCHEDULED!\n\n🥊 {p1u.name} VS {p2u.name}\n"
         f"📚 {', '.join(subjects_list)}\n⏱️ {tpq}s/question\n"
         f"⏰ {sched or 'Starting soon!'}\n\n"
         f"📺 Watch LIVE: /live/{quiz.id}\n👀 Duk dalibai zasu iya kallo!\n\nGood luck! 🔥")
    gm=GroupMessage(id=secrets.token_hex(8),from_id="system",from_name="🏆 Admin",from_role="admin",message=ann,pinned=True)
    db.session.add(gm); db.session.commit()
    socketio.emit("group_message",gm.to_dict(),room="group")
    socketio.emit("new_live_quiz",quiz.to_dict(),room="global")
    return jsonify({"success":True,"message":"Live Quiz created!","id":quiz.id})

@app.route("/admin/start_live_quiz",methods=["POST"])
@admin_req
def admin_start_live_quiz():
    qid=request.get_json().get("quiz_id"); quiz=LiveQuiz.query.get(qid)
    if not quiz: return jsonify({"success":False})
    quiz.status="active"; quiz.started_at=datetime.now().isoformat()
    quiz.q_start_time=datetime.now().isoformat(); quiz.current_q_index=0
    quiz.player1_score=0; quiz.player2_score=0; quiz.answered_this_q=json.dumps([])
    db.session.commit()
    qids=json.loads(quiz.question_ids or "[]")
    q=Question.query.get(qids[0]) if qids else None
    socketio.emit("quiz_started",{"quiz_id":qid,"status":"active","current_q_index":0,
                                   "p1_score":0,"p2_score":0,"q_start_time":quiz.q_start_time,
                                   "time_per_q":quiz.time_per_q,"total_questions":len(qids),
                                   "question":{} if not q else q.to_dict()},room=f"quiz_{qid}")
    return jsonify({"success":True})

@app.route("/admin/next_question",methods=["POST"])
@admin_req
def admin_next_question():
    qid=request.get_json().get("quiz_id"); quiz=LiveQuiz.query.get(qid)
    if not quiz or quiz.status!="active": return jsonify({"success":False})
    nxt=quiz.current_q_index+1; qids=json.loads(quiz.question_ids or "[]")
    if nxt>=len(qids):
        quiz.status="finished"; quiz.finished_at=datetime.now().isoformat(); db.session.commit()
        p1=User.query.get(quiz.player1_id); p2=User.query.get(quiz.player2_id)
        total=len(qids)
        winner=p1.name if quiz.player1_score>quiz.player2_score else (p2.name if quiz.player2_score>quiz.player1_score else "Zaman lafiya (Tie)!")
        rt=(f"🏆 LIVE QUIZ RESULTS!\n\n🥊 {p1.name}: {quiz.player1_score}/{total} ⭐\n"
            f"🥊 {p2.name}: {quiz.player2_score}/{total} ⭐\n\n🎉 Winner: {winner}\n\nGreat match! 👏 Tafi!")
        gm=GroupMessage(id=secrets.token_hex(8),from_id="system",from_name="🏆 Quiz Results",from_role="admin",message=rt,pinned=True)
        db.session.add(gm); db.session.commit()
        socketio.emit("group_message",gm.to_dict(),room="group")
        socketio.emit("quiz_finished",{"quiz_id":qid,"p1_name":p1.name,"p1_score":quiz.player1_score,
                                        "p2_name":p2.name,"p2_score":quiz.player2_score,"total":total,"winner":winner},room=f"quiz_{qid}")
        # XP
        if quiz.player1_score>quiz.player2_score: p1.xp_points=(p1.xp_points or 0)+100; p2.xp_points=(p2.xp_points or 0)+30
        elif quiz.player2_score>quiz.player1_score: p2.xp_points=(p2.xp_points or 0)+100; p1.xp_points=(p1.xp_points or 0)+30
        else: p1.xp_points=(p1.xp_points or 0)+60; p2.xp_points=(p2.xp_points or 0)+60
        db.session.commit()
    else:
        quiz.current_q_index=nxt; quiz.answered_this_q=json.dumps([]); quiz.q_start_time=datetime.now().isoformat()
        db.session.commit()
        q=Question.query.get(qids[nxt])
        socketio.emit("next_question",{"quiz_id":qid,"current_q_index":nxt,"q_start_time":quiz.q_start_time,
                                        "time_per_q":quiz.time_per_q,"p1_score":quiz.player1_score,"p2_score":quiz.player2_score,
                                        "question":{} if not q else q.to_dict()},room=f"quiz_{qid}")
    return jsonify({"success":True})

@app.route("/admin/cancel_live_quiz",methods=["POST"])
@admin_req
def admin_cancel_live_quiz():
    qid=request.get_json().get("quiz_id"); quiz=LiveQuiz.query.get(qid)
    if quiz: quiz.status="cancelled"; db.session.commit(); socketio.emit("quiz_cancelled",{"quiz_id":qid},room=f"quiz_{qid}")
    return jsonify({"success":True})

@app.route("/admin/broadcast",methods=["GET","POST"])
@admin_req
def admin_broadcast():
    ctx=bctx()
    if request.method=="POST":
        msg=request.form.get("message","").strip(); tid=request.form.get("target_id","").strip() or None
        user=cu(); bc=Broadcast(id=secrets.token_hex(8),message=msg,target_id=tid,by=user.name)
        db.session.add(bc); db.session.commit()
        if not tid:
            gm=GroupMessage(id=secrets.token_hex(8),from_id="system",from_name="📢 Admin Broadcast",from_role="admin",message=msg)
            db.session.add(gm); db.session.commit()
            socketio.emit("group_message",gm.to_dict(),room="group")
            socketio.emit("broadcast",{"message":msg,"by":user.name},room="global")
        ctx["success_msg"]="Broadcast sent."
    ctx["broadcasts"]=[{"id":b.id,"message":b.message,"by":b.by,"date":b.date} for b in Broadcast.query.order_by(Broadcast.date.desc()).all()]
    ctx["students"]=[u.to_dict() for u in User.query.filter_by(role="student").all()]
    return render_template("admin/broadcast.html",**ctx)

@app.route("/admin/books",methods=["GET","POST"])
@admin_req
def admin_books():
    ctx=bctx()
    if request.method=="POST":
        title=request.form.get("title","").strip(); subject=request.form.get("subject","").strip()
        desc=request.form.get("description","").strip(); file=request.files.get("file")
        if title and file:
            fn=f"{secrets.token_hex(8)}_{file.filename}"; fp=os.path.join(DATA_DIR,"books",fn); file.save(fp)
            b=Book(id=secrets.token_hex(8),title=title,subject=subject,description=desc,filename=fn,size=os.path.getsize(fp))
            db.session.add(b); db.session.commit(); ctx["success_msg"]="Book uploaded."
    ctx["books"]=[{"id":b.id,"title":b.title,"subject":b.subject,"size":b.size} for b in Book.query.all()]
    ctx["subjects"]=JAMB_SUBJECTS
    return render_template("admin/books.html",**ctx)

@app.route("/admin/reports")
@admin_req
def admin_reports():
    ctx=bctx()
    ctx["reports"]=[{"id":r.id,"reporter_name":r.reporter_name,"target_name":r.target_name,"target_id":r.target_id,"reason":r.reason,"date":r.date,"status":r.status}
                    for r in Report.query.order_by(Report.date.desc()).all()]
    return render_template("admin/reports.html",**ctx)

@app.route("/admin/resolve_report",methods=["POST"])
@admin_req
def admin_resolve_report():
    data=request.get_json(); r=Report.query.get(data.get("report_id")); action=data.get("action")
    if r:
        r.status="resolved"
        u=User.query.get(r.target_id)
        if u and action in ["warn","block","ban"]:
            if action=="warn": u.warned=True
            elif action=="block": u.blocked=True
            elif action=="ban": u.banned=True
        db.session.commit()
    return jsonify({"success":True})

@app.route("/admin/results")
@admin_req
def admin_results():
    ctx=bctx(); subj=request.args.get("subject","")
    q=Result.query.order_by(Result.date.desc())
    if subj: q=q.filter_by(subject=subj)
    ctx["results"]=[{"id":r.id,"user_name":r.user_name,"reg_number":r.reg_number,"subject":r.subject,"mode":r.mode,"score":r.score,"total":r.total,"percentage":r.percentage,"grade":r.grade,"date":r.date} for r in q.all()]
    ctx["subjects"]=JAMB_SUBJECTS; ctx["selected_subject"]=subj
    return render_template("admin/results.html",**ctx)

@app.route("/admin/support")
@admin_req
def admin_support():
    ctx=bctx()
    ctx["tickets"]=[{"id":t.id,"user_name":t.user_name,"reg_number":t.reg_number,"message":t.message,"date":t.date,"status":t.status,"replies":json.loads(t.replies or "[]")}
                    for t in SupportTicket.query.order_by(SupportTicket.date.desc()).all()]
    return render_template("admin/support.html",**ctx)

@app.route("/admin/reply_support",methods=["POST"])
@admin_req
def admin_reply_support():
    data=request.get_json(); t=SupportTicket.query.get(data.get("ticket_id"))
    if t:
        reps=json.loads(t.replies or "[]")
        reps.append({"message":data.get("reply",""),"date":datetime.now().isoformat(),"by":cu().name})
        t.replies=json.dumps(reps); t.status="replied"; db.session.commit()
    return jsonify({"success":True})

@app.route("/admin/admins")
@super_req
def admin_manage_admins():
    ctx=bctx()
    ctx["admins"]=[u.to_dict() for u in User.query.filter(User.role.in_(["admin","super_admin"])).all()]
    ctx["students"]=[u.to_dict() for u in User.query.filter_by(role="student").all()]
    return render_template("admin/admins.html",**ctx)

@app.route("/admin/set_role",methods=["POST"])
@super_req
def admin_set_role():
    data=request.get_json(); uid=data.get("uid"); role=data.get("role")
    u=User.query.get(uid)
    if not u or u.role=="super_admin": return jsonify({"success":False,"message":"Cannot modify super admin."})
    if role in ["student","admin"]: u.role=role; db.session.commit(); return jsonify({"success":True,"message":f"Role updated to {role}."})
    return jsonify({"success":False})

@app.route("/admin/settings",methods=["GET","POST"])
@super_req
def admin_settings():
    ctx=bctx(); settings=all_settings()
    if request.method=="POST":
        for k in ["app_name","group_name"]: set_setting(k,request.form.get(k,settings[k]))
        for k in ["exam_duration_minutes","exam_questions","quiz_time_per_question"]:
            try: set_setting(k,int(request.form.get(k,settings[k])))
            except: pass
        set_setting("allow_registration","allow_reg" in request.form)
        set_setting("maintenance_mode","maintenance" in request.form)
        set_setting("group_only_admin","group_only_admin" in request.form)
        ctx["success_msg"]="Settings saved."; settings=all_settings()
    ctx["settings"]=settings
    return render_template("admin/settings.html",**ctx)

@app.route("/admin/group")
@admin_req
def admin_group():
    ctx=bctx(); s=all_settings()
    msgs=[m.to_dict() for m in GroupMessage.query.order_by(GroupMessage.time.asc()).limit(200).all()]
    ctx.update({"messages":msgs,"group_name":s.get("group_name","All JAMB Students"),"only_admin":s.get("group_only_admin",False)})
    return render_template("admin/group.html",**ctx)

# ═══════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════
@app.route("/api/stats")
@login_req
def api_stats():
    uid=session["user_id"]; ress=Result.query.filter_by(user_id=uid,mode="exam").all()
    avg=round(sum(r.percentage for r in ress)/len(ress)) if ress else 0
    return jsonify({"total_exams":len(ress),"average_score":avg,
                    "best_score":max((r.percentage for r in ress),default=0),
                    "total_practice":Result.query.filter_by(user_id=uid,mode="practice").count()})

@app.route("/api/verify_result/<vid>")
def verify_result(vid):
    r=Result.query.filter_by(verify_id=vid).first()
    if r: return jsonify({"valid":True,"result":{"user_name":r.user_name,"subject":r.subject,"score":r.score,"total":r.total,"percentage":r.percentage,"grade":r.grade}})
    return jsonify({"valid":False})

# ═══════════════════════════════════════════════
# SOCKET.IO
# ═══════════════════════════════════════════════
@socketio.on("connect")
def on_connect():
    join_room("global")
    if "user_id" in session:
        u=User.query.get(session["user_id"])
        if u: u.online=True; u.last_seen=datetime.now().isoformat(); db.session.commit()

@socketio.on("disconnect")
def on_disconnect():
    if "user_id" in session:
        u=User.query.get(session["user_id"])
        if u: u.online=False; u.last_seen=datetime.now().isoformat(); db.session.commit()

@socketio.on("join_group")
def on_join_group():
    join_room("group")
    if "user_id" in session:
        u=User.query.get(session["user_id"])
        if u: u.group_last_read=datetime.now().isoformat(); db.session.commit()

@socketio.on("join_quiz")
def on_join_quiz(data):
    qid=data.get("quiz_id",""); join_room(f"quiz_{qid}")
    uid=session.get("user_id","")
    quiz=LiveQuiz.query.get(qid)
    u=User.query.get(uid) if uid else None
    is_player=u and quiz and u.id in [quiz.player1_id,quiz.player2_id]
    if not is_player: join_room(f"spectators_{qid}")
    emit("joined_quiz",{"quiz_id":qid,"is_player":bool(is_player)})

@socketio.on("join_dm")
def on_join_dm():
    if "user_id" in session: join_room(f"dm_{session['user_id']}")

@socketio.on("typing")
def on_typing(data):
    u=User.query.get(session.get("user_id","")) if "user_id" in session else None
    if u: emit("user_typing",{"from":u.id,"name":u.name},room=f"dm_{data.get('target_id')}")

@socketio.on("group_typing")
def on_group_typing():
    u=User.query.get(session.get("user_id","")) if "user_id" in session else None
    if u: emit("group_user_typing",{"name":u.name},room="group",include_self=False)

# ═══════════════════════════════════════════════
seed_db()
if __name__=="__main__":
    socketio.run(app,debug=True,port=5000,use_reloader=False)
