const express = require('express');
const { dbRun, dbGet, dbAll } = require('../database/init');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get all subjects
router.get('/subjects', async (req, res) => {
  try {
    const subjects = await dbAll('SELECT * FROM subjects ORDER BY name');
    res.json({ error: false, data: subjects });
  } catch (error) {
    console.error('Error fetching subjects:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch subjects' });
  }
});

// Get questions by subject (offline practice - returns random 40 from 100)
router.get('/offline/:subjectId', async (req, res) => {
  try {
    const { subjectId } = req.params;
    const limit = parseInt(process.env.QUESTIONS_PER_EXAM) || 40;

    // Get all offline questions for this subject
    const questions = await dbAll(
      `SELECT id, subject_id, question_text, option_a, option_b, option_c, option_d 
       FROM questions 
       WHERE subject_id = ? AND is_online = 0 
       ORDER BY RANDOM() 
       LIMIT ?`,
      [subjectId, limit]
    );

    // Shuffle options for each question
    const shuffledQuestions = questions.map(q => ({
      ...q,
      options: shuffleArray([
        { key: 'A', text: q.option_a },
        { key: 'B', text: q.option_b },
        { key: 'C', text: q.option_c },
        { key: 'D', text: q.option_d }
      ])
    }));

    res.json({ 
      error: false, 
      data: shuffledQuestions,
      total: questions.length 
    });
  } catch (error) {
    console.error('Error fetching offline questions:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch questions' });
  }
});

// Get questions for online exam (requires authentication)
router.get('/online/:subjectId', authenticateToken, async (req, res) => {
  try {
    const { subjectId } = req.params;
    const limit = parseInt(process.env.QUESTIONS_PER_EXAM) || 40;

    // Get all online questions for this subject
    const questions = await dbAll(
      `SELECT id, subject_id, question_text, option_a, option_b, option_c, option_d 
       FROM questions 
       WHERE subject_id = ? AND is_online = 1 
       ORDER BY RANDOM() 
       LIMIT ?`,
      [subjectId, limit]
    );

    // Shuffle options for each question
    const shuffledQuestions = questions.map(q => ({
      ...q,
      options: shuffleArray([
        { key: 'A', text: q.option_a },
        { key: 'B', text: q.option_b },
        { key: 'C', text: q.option_c },
        { key: 'D', text: q.option_d }
      ])
    }));

    res.json({ 
      error: false, 
      data: shuffledQuestions,
      total: questions.length 
    });
  } catch (error) {
    console.error('Error fetching online questions:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch questions' });
  }
});

// Check answer for offline practice
router.post('/check-answer', async (req, res) => {
  try {
    const { questionId, userAnswer } = req.body;

    const question = await dbGet(
      'SELECT correct_answer, explanation FROM questions WHERE id = ?',
      [questionId]
    );

    if (!question) {
      return res.status(404).json({ error: true, message: 'Question not found' });
    }

    const isCorrect = question.correct_answer === userAnswer;

    res.json({
      error: false,
      data: {
        isCorrect,
        correctAnswer: question.correct_answer,
        explanation: question.explanation
      }
    });
  } catch (error) {
    console.error('Error checking answer:', error);
    res.status(500).json({ error: true, message: 'Failed to check answer' });
  }
});

// Helper function to shuffle array
function shuffleArray(array) {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

module.exports = router;
