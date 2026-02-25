const express = require('express');
const { dbRun, dbGet, dbAll } = require('../database/init');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Start a new exam
router.post('/start', authenticateToken, async (req, res) => {
  try {
    const { subjectId, examType } = req.body;
    const userId = req.user.id;

    // Validate
    if (!subjectId || !examType) {
      return res.status(400).json({ 
        error: true, 
        message: 'Subject ID and exam type are required' 
      });
    }

    // Create exam record
    const result = await dbRun(
      `INSERT INTO exams (user_id, subject_id, exam_type, total_questions, started_at) 
       VALUES (?, ?, ?, ?, datetime('now'))`,
      [userId, subjectId, examType, parseInt(process.env.QUESTIONS_PER_EXAM) || 40]
    );

    res.json({
      error: false,
      message: 'Exam started successfully',
      data: { examId: result.lastID }
    });
  } catch (error) {
    console.error('Error starting exam:', error);
    res.status(500).json({ error: true, message: 'Failed to start exam' });
  }
});

// Submit exam answers
router.post('/submit', authenticateToken, async (req, res) => {
  try {
    const { examId, answers, durationSeconds } = req.body;
    const userId = req.user.id;

    // Validate exam belongs to user
    const exam = await dbGet(
      'SELECT * FROM exams WHERE id = ? AND user_id = ?',
      [examId, userId]
    );

    if (!exam) {
      return res.status(404).json({ error: true, message: 'Exam not found' });
    }

    if (exam.completed_at) {
      return res.status(400).json({ error: true, message: 'Exam already submitted' });
    }

    // Calculate score
    let correctCount = 0;
    const totalQuestions = answers.length;

    // Save answers and calculate score
    for (const answer of answers) {
      const question = await dbGet(
        'SELECT correct_answer FROM questions WHERE id = ?',
        [answer.questionId]
      );

      const isCorrect = question && question.correct_answer === answer.userAnswer;
      if (isCorrect) correctCount++;

      await dbRun(
        `INSERT INTO exam_answers (exam_id, question_id, user_answer, is_correct, time_spent_seconds) 
         VALUES (?, ?, ?, ?, ?)`,
        [examId, answer.questionId, answer.userAnswer, isCorrect ? 1 : 0, answer.timeSpent || 0]
      );
    }

    // Calculate percentage and grade
    const percentage = (correctCount / totalQuestions) * 100;
    const grade = calculateGrade(percentage);

    // Update exam record
    await dbRun(
      `UPDATE exams 
       SET score = ?, percentage = ?, grade = ?, completed_at = datetime('now'), duration_seconds = ? 
       WHERE id = ?`,
      [correctCount, percentage, grade, durationSeconds, examId]
    );

    res.json({
      error: false,
      message: 'Exam submitted successfully',
      data: {
        examId,
        score: correctCount,
        totalQuestions,
        percentage: percentage.toFixed(2),
        grade
      }
    });
  } catch (error) {
    console.error('Error submitting exam:', error);
    res.status(500).json({ error: true, message: 'Failed to submit exam' });
  }
});

// Get exam result
router.get('/result/:examId', authenticateToken, async (req, res) => {
  try {
    const { examId } = req.params;
    const userId = req.user.id;

    const exam = await dbGet(
      `SELECT e.*, s.name as subject_name, s.emoji as subject_emoji, u.name as user_name
       FROM exams e
       JOIN subjects s ON e.subject_id = s.id
       JOIN users u ON e.user_id = u.id
       WHERE e.id = ? AND e.user_id = ?`,
      [examId, userId]
    );

    if (!exam) {
      return res.status(404).json({ error: true, message: 'Exam not found' });
    }

    // Get detailed answers
    const answers = await dbAll(
      `SELECT ea.*, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d, 
              q.correct_answer, q.explanation
       FROM exam_answers ea
       JOIN questions q ON ea.question_id = q.id
       WHERE ea.exam_id = ?`,
      [examId]
    );

    res.json({
      error: false,
      data: {
        exam,
        answers,
        summary: {
          correct: exam.score,
          wrong: exam.total_questions - exam.score,
          total: exam.total_questions,
          percentage: exam.percentage,
          grade: exam.grade
        }
      }
    });
  } catch (error) {
    console.error('Error fetching result:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch result' });
  }
});

// Get user's exam history
router.get('/history', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;

    const exams = await dbAll(
      `SELECT e.*, s.name as subject_name, s.emoji as subject_emoji
       FROM exams e
       JOIN subjects s ON e.subject_id = s.id
       WHERE e.user_id = ? AND e.completed_at IS NOT NULL
       ORDER BY e.completed_at DESC
       LIMIT 50`,
      [userId]
    );

    res.json({ error: false, data: exams });
  } catch (error) {
    console.error('Error fetching history:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch history' });
  }
});

// Get user statistics
router.get('/stats', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;

    // Total exams taken
    const totalExams = await dbGet(
      'SELECT COUNT(*) as count FROM exams WHERE user_id = ? AND completed_at IS NOT NULL',
      [userId]
    );

    // Average score
    const avgScore = await dbGet(
      'SELECT AVG(percentage) as average FROM exams WHERE user_id = ? AND completed_at IS NOT NULL',
      [userId]
    );

    // Best score
    const bestScore = await dbGet(
      'SELECT MAX(percentage) as best FROM exams WHERE user_id = ? AND completed_at IS NOT NULL',
      [userId]
    );

    // Performance by subject
    const subjectPerformance = await dbAll(
      `SELECT s.name, s.emoji, AVG(e.percentage) as avg_percentage, COUNT(*) as attempts
       FROM exams e
       JOIN subjects s ON e.subject_id = s.id
       WHERE e.user_id = ? AND e.completed_at IS NOT NULL
       GROUP BY s.id, s.name, s.emoji`,
      [userId]
    );

    res.json({
      error: false,
      data: {
        totalExams: totalExams.count || 0,
        averageScore: avgScore.average?.toFixed(2) || 0,
        bestScore: bestScore.best?.toFixed(2) || 0,
        subjectPerformance
      }
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch statistics' });
  }
});

// Helper function to calculate grade
function calculateGrade(percentage) {
  if (percentage >= 90) return 'A+';
  if (percentage >= 85) return 'A';
  if (percentage >= 80) return 'A-';
  if (percentage >= 75) return 'B+';
  if (percentage >= 70) return 'B';
  if (percentage >= 65) return 'B-';
  if (percentage >= 60) return 'C+';
  if (percentage >= 55) return 'C';
  if (percentage >= 50) return 'C-';
  if (percentage >= 45) return 'D';
  return 'F';
}

module.exports = router;
