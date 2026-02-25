const express = require('express');
const bcrypt = require('bcryptjs');
const { dbRun, dbGet } = require('../database/init');
const { generateToken } = require('../middleware/auth');

const router = express.Router();

// Register new user
router.post('/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;

    // Validation
    if (!name || !email || !password) {
      return res.status(400).json({ 
        error: true, 
        message: 'Name, email, and password are required' 
      });
    }

    // Check if user already exists
    const existingUser = await dbGet('SELECT id FROM users WHERE email = ?', [email]);
    if (existingUser) {
      return res.status(400).json({ 
        error: true, 
        message: 'Email already registered' 
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Insert user
    const result = await dbRun(
      'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
      [name, email, hashedPassword, 'user']
    );

    // Generate token
    const user = { id: result.lastID, email, role: 'user' };
    const token = generateToken(user);

    res.status(201).json({
      error: false,
      message: 'Registration successful',
      data: {
        user: { id: user.id, name, email, role: user.role },
        token
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: true, message: 'Registration failed' });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({ 
        error: true, 
        message: 'Email and password are required' 
      });
    }

    // Find user
    const user = await dbGet('SELECT * FROM users WHERE email = ?', [email]);
    if (!user) {
      return res.status(401).json({ 
        error: true, 
        message: 'Invalid email or password' 
      });
    }

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ 
        error: true, 
        message: 'Invalid email or password' 
      });
    }

    // Generate token
    const token = generateToken(user);

    res.json({
      error: false,
      message: 'Login successful',
      data: {
        user: { 
          id: user.id, 
          name: user.name, 
          email: user.email, 
          role: user.role 
        },
        token
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: true, message: 'Login failed' });
  }
});

module.exports = router;
