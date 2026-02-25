const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { dbRun, dbGet, dbAll } = require('../database/init');
const { authenticateToken, requireAdmin } = require('../middleware/auth');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = './uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ 
  storage,
  limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10485760 } // 10MB default
});

// Middleware: All admin routes require authentication and admin role
router.use(authenticateToken);
router.use(requireAdmin);

// ==================== DASHBOARD STATS ====================

router.get('/dashboard', async (req, res) => {
  try {
    // Total users
    const totalUsers = await dbGet('SELECT COUNT(*) as count FROM users WHERE role = "user"');
    
    // Total questions
    const totalQuestions = await dbGet('SELECT COUNT(*) as count FROM questions');
    
    // Total exams
    const totalExams = await dbGet('SELECT COUNT(*) as count FROM exams WHERE completed_at IS NOT NULL');
    
    // Average score
    const avgScore = await dbGet('SELECT AVG(percentage) as average FROM exams WHERE completed_at IS NOT NULL');
    
    // Recent exams
    const recentExams = await dbAll(
      `SELECT e.*, u.name as user_name, s.name as subject_name
       FROM exams e
       JOIN users u ON e.user_id = u.id
       JOIN subjects s ON e.subject_id = s.id
       WHERE e.completed_at IS NOT NULL
       ORDER BY e.completed_at DESC
       LIMIT 10`
    );

    // Questions by subject
    const questionsBySubject = await dbAll(
      `SELECT s.name, s.emoji, 
              COUNT(CASE WHEN q.is_online = 0 THEN 1 END) as offline_count,
              COUNT(CASE WHEN q.is_online = 1 THEN 1 END) as online_count,
              COUNT(*) as total_count
       FROM subjects s
       LEFT JOIN questions q ON s.id = q.subject_id
       GROUP BY s.id, s.name, s.emoji`
    );

    res.json({
      error: false,
      data: {
        stats: {
          totalUsers: totalUsers.count || 0,
          totalQuestions: totalQuestions.count || 0,
          totalExams: totalExams.count || 0,
          averageScore: avgScore.average?.toFixed(2) || 0
        },
        recentExams,
        questionsBySubject
      }
    });
  } catch (error) {
    console.error('Error fetching dashboard:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch dashboard data' });
  }
});

// ==================== USER MANAGEMENT ====================

// Get all users
router.get('/users', async (req, res) => {
  try {
    const users = await dbAll(
      `SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC`
    );
    res.json({ error: false, data: users });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch users' });
  }
});

// Get user details with exam history
router.get('/users/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    const user = await dbGet(
      'SELECT id, name, email, role, created_at FROM users WHERE id = ?',
      [userId]
    );

    if (!user) {
      return res.status(404).json({ error: true, message: 'User not found' });
    }

    const exams = await dbAll(
      `SELECT e.*, s.name as subject_name, s.emoji as subject_emoji
       FROM exams e
       JOIN subjects s ON e.subject_id = s.id
       WHERE e.user_id = ? AND e.completed_at IS NOT NULL
       ORDER BY e.completed_at DESC`,
      [userId]
    );

    res.json({ error: false, data: { user, exams } });
  } catch (error) {
    console.error('Error fetching user details:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch user details' });
  }
});

// Delete user
router.delete('/users/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    // Don't allow deleting admin users
    const user = await dbGet('SELECT role FROM users WHERE id = ?', [userId]);
    if (user && user.role === 'admin') {
      return res.status(403).json({ error: true, message: 'Cannot delete admin users' });
    }

    // Delete user's exams and related data
    await dbRun('DELETE FROM exam_answers WHERE exam_id IN (SELECT id FROM exams WHERE user_id = ?)', [userId]);
    await dbRun('DELETE FROM certificates WHERE user_id = ?', [userId]);
    await dbRun('DELETE FROM exams WHERE user_id = ?', [userId]);
    await dbRun('DELETE FROM users WHERE id = ?', [userId]);

    res.json({ error: false, message: 'User deleted successfully' });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({ error: true, message: 'Failed to delete user' });
  }
});

// ==================== QUESTION MANAGEMENT ====================

// Get all questions
router.get('/questions', async (req, res) => {
  try {
    const { subjectId, isOnline } = req.query;
    
    let query = `
      SELECT q.*, s.name as subject_name, s.emoji as subject_emoji
      FROM questions q
      JOIN subjects s ON q.subject_id = s.id
      WHERE 1=1
    `;
    const params = [];

    if (subjectId) {
      query += ' AND q.subject_id = ?';
      params.push(subjectId);
    }

    if (isOnline !== undefined) {
      query += ' AND q.is_online = ?';
      params.push(isOnline === 'true' ? 1 : 0);
    }

    query += ' ORDER BY q.created_at DESC';

    const questions = await dbAll(query, params);
    res.json({ error: false, data: questions });
  } catch (error) {
    console.error('Error fetching questions:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch questions' });
  }
});

// Add single question
router.post('/questions', async (req, res) => {
  try {
    const { 
      subjectId, 
      questionText, 
      optionA, 
      optionB, 
      optionC, 
      optionD, 
      correctAnswer, 
      explanation,
      difficulty,
      isOnline 
    } = req.body;

    // Validation
    if (!subjectId || !questionText || !optionA || !optionB || !optionC || !optionD || !correctAnswer) {
      return res.status(400).json({ 
        error: true, 
        message: 'All question fields are required' 
      });
    }

    const result = await dbRun(
      `INSERT INTO questions 
       (subject_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty, is_online) 
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [subjectId, questionText, optionA, optionB, optionC, optionD, correctAnswer, explanation || '', difficulty || 'medium', isOnline ? 1 : 0]
    );

    res.status(201).json({
      error: false,
      message: 'Question added successfully',
      data: { questionId: result.lastID }
    });
  } catch (error) {
    console.error('Error adding question:', error);
    res.status(500).json({ error: true, message: 'Failed to add question' });
  }
});

// Update question
router.put('/questions/:questionId', async (req, res) => {
  try {
    const { questionId } = req.params;
    const { 
      questionText, 
      optionA, 
      optionB, 
      optionC, 
      optionD, 
      correctAnswer, 
      explanation,
      difficulty,
      isOnline 
    } = req.body;

    await dbRun(
      `UPDATE questions 
       SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, 
           correct_answer = ?, explanation = ?, difficulty = ?, is_online = ?
       WHERE id = ?`,
      [questionText, optionA, optionB, optionC, optionD, correctAnswer, explanation, difficulty, isOnline ? 1 : 0, questionId]
    );

    res.json({ error: false, message: 'Question updated successfully' });
  } catch (error) {
    console.error('Error updating question:', error);
    res.status(500).json({ error: true, message: 'Failed to update question' });
  }
});

// Delete question
router.delete('/questions/:questionId', async (req, res) => {
  try {
    const { questionId } = req.params;

    // Check if question is used in any exams
    const usedInExams = await dbGet(
      'SELECT COUNT(*) as count FROM exam_answers WHERE question_id = ?',
      [questionId]
    );

    if (usedInExams.count > 0) {
      return res.status(400).json({ 
        error: true, 
        message: 'Cannot delete question that has been used in exams' 
      });
    }

    await dbRun('DELETE FROM questions WHERE id = ?', [questionId]);

    res.json({ error: false, message: 'Question deleted successfully' });
  } catch (error) {
    console.error('Error deleting question:', error);
    res.status(500).json({ error: true, message: 'Failed to delete question' });
  }
});

// Bulk upload questions from JSON
router.post('/questions/bulk-upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: true, message: 'No file uploaded' });
    }

    const filePath = req.file.path;
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const questions = JSON.parse(fileContent);

    let successCount = 0;
    let errorCount = 0;

    for (const q of questions) {
      try {
        await dbRun(
          `INSERT INTO questions 
           (subject_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty, is_online) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            q.subjectId, 
            q.questionText, 
            q.optionA, 
            q.optionB, 
            q.optionC, 
            q.optionD, 
            q.correctAnswer, 
            q.explanation || '', 
            q.difficulty || 'medium', 
            q.isOnline ? 1 : 0
          ]
        );
        successCount++;
      } catch (error) {
        console.error('Error inserting question:', error);
        errorCount++;
      }
    }

    // Delete uploaded file
    fs.unlinkSync(filePath);

    res.json({
      error: false,
      message: `Bulk upload completed: ${successCount} questions added, ${errorCount} errors`,
      data: { successCount, errorCount }
    });
  } catch (error) {
    console.error('Error in bulk upload:', error);
    res.status(500).json({ error: true, message: 'Failed to upload questions' });
  }
});

// ==================== EXAM RESULTS MANAGEMENT ====================

// Get all exam results
router.get('/results', async (req, res) => {
  try {
    const { subjectId, userId, startDate, endDate } = req.query;
    
    let query = `
      SELECT e.*, u.name as user_name, u.email as user_email, s.name as subject_name, s.emoji as subject_emoji
      FROM exams e
      JOIN users u ON e.user_id = u.id
      JOIN subjects s ON e.subject_id = s.id
      WHERE e.completed_at IS NOT NULL
    `;
    const params = [];

    if (subjectId) {
      query += ' AND e.subject_id = ?';
      params.push(subjectId);
    }

    if (userId) {
      query += ' AND e.user_id = ?';
      params.push(userId);
    }

    if (startDate) {
      query += ' AND e.completed_at >= ?';
      params.push(startDate);
    }

    if (endDate) {
      query += ' AND e.completed_at <= ?';
      params.push(endDate);
    }

    query += ' ORDER BY e.completed_at DESC LIMIT 100';

    const results = await dbAll(query, params);
    res.json({ error: false, data: results });
  } catch (error) {
    console.error('Error fetching results:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch results' });
  }
});

// Delete exam result
router.delete('/results/:examId', async (req, res) => {
  try {
    const { examId } = req.params;

    await dbRun('DELETE FROM exam_answers WHERE exam_id = ?', [examId]);
    await dbRun('DELETE FROM certificates WHERE exam_id = ?', [examId]);
    await dbRun('DELETE FROM exams WHERE id = ?', [examId]);

    res.json({ error: false, message: 'Exam result deleted successfully' });
  } catch (error) {
    console.error('Error deleting result:', error);
    res.status(500).json({ error: true, message: 'Failed to delete result' });
  }
});

// ==================== SUBJECTS MANAGEMENT ====================

// Add new subject
router.post('/subjects', async (req, res) => {
  try {
    const { name, emoji, description } = req.body;

    if (!name) {
      return res.status(400).json({ error: true, message: 'Subject name is required' });
    }

    const result = await dbRun(
      'INSERT INTO subjects (name, emoji, description) VALUES (?, ?, ?)',
      [name, emoji || '📚', description || '']
    );

    res.status(201).json({
      error: false,
      message: 'Subject added successfully',
      data: { subjectId: result.lastID }
    });
  } catch (error) {
    console.error('Error adding subject:', error);
    res.status(500).json({ error: true, message: 'Failed to add subject' });
  }
});

// Update subject
router.put('/subjects/:subjectId', async (req, res) => {
  try {
    const { subjectId } = req.params;
    const { name, emoji, description } = req.body;

    await dbRun(
      'UPDATE subjects SET name = ?, emoji = ?, description = ? WHERE id = ?',
      [name, emoji, description, subjectId]
    );

    res.json({ error: false, message: 'Subject updated successfully' });
  } catch (error) {
    console.error('Error updating subject:', error);
    res.status(500).json({ error: true, message: 'Failed to update subject' });
  }
});

// Delete subject
router.delete('/subjects/:subjectId', async (req, res) => {
  try {
    const { subjectId } = req.params;

    // Check if subject has questions
    const hasQuestions = await dbGet(
      'SELECT COUNT(*) as count FROM questions WHERE subject_id = ?',
      [subjectId]
    );

    if (hasQuestions.count > 0) {
      return res.status(400).json({ 
        error: true, 
        message: 'Cannot delete subject with existing questions' 
      });
    }

    await dbRun('DELETE FROM subjects WHERE id = ?', [subjectId]);

    res.json({ error: false, message: 'Subject deleted successfully' });
  } catch (error) {
    console.error('Error deleting subject:', error);
    res.status(500).json({ error: true, message: 'Failed to delete subject' });
  }
});

// ==================== SETTINGS MANAGEMENT ====================

// Get all settings
router.get('/settings', async (req, res) => {
  try {
    const settings = await dbAll('SELECT * FROM settings');
    res.json({ error: false, data: settings });
  } catch (error) {
    console.error('Error fetching settings:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch settings' });
  }
});

// Update setting
router.put('/settings/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const { value } = req.body;

    await dbRun(
      `INSERT INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))
       ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')`,
      [key, value, value]
    );

    res.json({ error: false, message: 'Setting updated successfully' });
  } catch (error) {
    console.error('Error updating setting:', error);
    res.status(500).json({ error: true, message: 'Failed to update setting' });
  }
});

module.exports = router;
