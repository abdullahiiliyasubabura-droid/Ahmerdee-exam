const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');

const DB_PATH = process.env.DB_PATH || './database/ahmerdee.db';

// Ensure database directory exists
const dbDir = path.dirname(DB_PATH);
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Error opening database:', err);
  } else {
    console.log('Connected to SQLite database');
  }
});

// Promisify database methods
const dbRun = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
};

const dbGet = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
};

const dbAll = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
};

async function initDatabase() {
  try {
    // Create Users table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create Subjects table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        emoji TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create Questions table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        explanation TEXT,
        difficulty TEXT DEFAULT 'medium',
        is_online BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
      )
    `);

    // Create Exams table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        exam_type TEXT NOT NULL,
        total_questions INTEGER NOT NULL,
        score INTEGER,
        percentage REAL,
        grade TEXT,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME,
        duration_seconds INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
      )
    `);

    // Create Exam Answers table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS exam_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        user_answer TEXT,
        is_correct BOOLEAN,
        time_spent_seconds INTEGER,
        FOREIGN KEY (exam_id) REFERENCES exams(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
      )
    `);

    // Create Certificates table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        certificate_number TEXT UNIQUE NOT NULL,
        file_path TEXT,
        issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exam_id) REFERENCES exams(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
      )
    `);

    // Create Settings table
    await dbRun(`
      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('✅ Database tables created successfully');

    // Insert default subjects if not exists
    const subjects = [
      { name: 'Mathematics', emoji: '🔢', description: 'JAMB Mathematics questions' },
      { name: 'Chemistry', emoji: '⚗️', description: 'JAMB Chemistry questions' },
      { name: 'Physics', emoji: '⚛️', description: 'JAMB Physics questions' },
      { name: 'Biology', emoji: '🧬', description: 'JAMB Biology questions' },
      { name: 'English', emoji: '📖', description: 'JAMB English questions' },
      { name: 'Geography', emoji: '🌍', description: 'JAMB Geography questions' }
    ];

    for (const subject of subjects) {
      const existing = await dbGet('SELECT id FROM subjects WHERE name = ?', [subject.name]);
      if (!existing) {
        await dbRun(
          'INSERT INTO subjects (name, emoji, description) VALUES (?, ?, ?)',
          [subject.name, subject.emoji, subject.description]
        );
      }
    }

    console.log('✅ Default subjects inserted');

    // Create default admin user if not exists
    const adminEmail = process.env.ADMIN_EMAIL || 'admin@ahmerdee.com';
    const adminPassword = process.env.ADMIN_PASSWORD || 'Admin@123';
    
    const existingAdmin = await dbGet('SELECT id FROM users WHERE email = ?', [adminEmail]);
    
    if (!existingAdmin) {
      const hashedPassword = await bcrypt.hash(adminPassword, 10);
      await dbRun(
        'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
        ['Admin', adminEmail, hashedPassword, 'admin']
      );
      console.log('✅ Default admin user created');
      console.log(`   Email: ${adminEmail}`);
      console.log(`   Password: ${adminPassword}`);
    }

    // Insert sample questions for offline practice
    await insertSampleQuestions();

    console.log('✅ Database initialization complete');
    
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  }
}

async function insertSampleQuestions() {
  // Check if sample questions already exist
  const existingQuestions = await dbGet('SELECT COUNT(*) as count FROM questions');
  
  if (existingQuestions.count > 0) {
    console.log('✅ Sample questions already exist');
    return;
  }

  // Get subject IDs
  const subjects = await dbAll('SELECT id, name FROM subjects');
  
  // Sample questions for Mathematics
  const mathSubject = subjects.find(s => s.name === 'Mathematics');
  if (mathSubject) {
    const mathQuestions = [
      {
        question: 'What is the quadratic formula?',
        a: 'x = (-b ± √(b² + 4ac)) / 2a',
        b: 'x = (-b ± √(b² - 4ac)) / 2a',
        c: 'x = (b ± √(b² - 4ac)) / 2a',
        d: 'x = (-b ± √(b² - 2ac)) / a',
        correct: 'B',
        explanation: 'The quadratic formula is x = (-b ± √(b² - 4ac)) / 2a'
      },
      {
        question: 'Simplify: 2x + 3x',
        a: '5x',
        b: '6x',
        c: '5x²',
        d: '2x²',
        correct: 'A',
        explanation: 'Like terms can be added: 2x + 3x = 5x'
      },
      {
        question: 'What is 15% of 200?',
        a: '20',
        b: '25',
        c: '30',
        d: '35',
        correct: 'C',
        explanation: '15% of 200 = (15/100) × 200 = 30'
      }
    ];

    for (const q of mathQuestions) {
      await dbRun(
        `INSERT INTO questions (subject_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, is_online) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)`,
        [mathSubject.id, q.question, q.a, q.b, q.c, q.d, q.correct, q.explanation]
      );
    }
  }

  // Sample questions for English
  const englishSubject = subjects.find(s => s.name === 'English');
  if (englishSubject) {
    const englishQuestions = [
      {
        question: 'Choose the correct synonym for "Happy"',
        a: 'Sad',
        b: 'Joyful',
        c: 'Angry',
        d: 'Tired',
        correct: 'B',
        explanation: 'Joyful is a synonym of happy'
      },
      {
        question: 'Which is the correct spelling?',
        a: 'Recieve',
        b: 'Receive',
        c: 'Recive',
        d: 'Receeve',
        correct: 'B',
        explanation: 'The correct spelling is "Receive" - i before e except after c'
      }
    ];

    for (const q of englishQuestions) {
      await dbRun(
        `INSERT INTO questions (subject_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, is_online) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)`,
        [englishSubject.id, q.question, q.a, q.b, q.c, q.d, q.correct, q.explanation]
      );
    }
  }

  console.log('✅ Sample questions inserted');
}

module.exports = {
  db,
  dbRun,
  dbGet,
  dbAll,
  initDatabase
};
