const express = require('express');
const bcrypt = require('bcryptjs');
const { dbRun, dbGet } = require('../database/init');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// All routes require authentication
router.use(authenticateToken);

// Get current user profile
router.get('/profile', async (req, res) => {
  try {
    const userId = req.user.id;

    const user = await dbGet(
      'SELECT id, name, email, role, created_at FROM users WHERE id = ?',
      [userId]
    );

    if (!user) {
      return res.status(404).json({ error: true, message: 'User not found' });
    }

    res.json({ error: false, data: user });
  } catch (error) {
    console.error('Error fetching profile:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch profile' });
  }
});

// Update user profile
router.put('/profile', async (req, res) => {
  try {
    const userId = req.user.id;
    const { name, email } = req.body;

    if (!name || !email) {
      return res.status(400).json({ error: true, message: 'Name and email are required' });
    }

    // Check if email is already used by another user
    const existingUser = await dbGet(
      'SELECT id FROM users WHERE email = ? AND id != ?',
      [email, userId]
    );

    if (existingUser) {
      return res.status(400).json({ error: true, message: 'Email already in use' });
    }

    await dbRun(
      'UPDATE users SET name = ?, email = ?, updated_at = datetime("now") WHERE id = ?',
      [name, email, userId]
    );

    res.json({ error: false, message: 'Profile updated successfully' });
  } catch (error) {
    console.error('Error updating profile:', error);
    res.status(500).json({ error: true, message: 'Failed to update profile' });
  }
});

// Change password
router.put('/change-password', async (req, res) => {
  try {
    const userId = req.user.id;
    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({ 
        error: true, 
        message: 'Current password and new password are required' 
      });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ 
        error: true, 
        message: 'New password must be at least 6 characters long' 
      });
    }

    // Get current user
    const user = await dbGet('SELECT password FROM users WHERE id = ?', [userId]);

    // Verify current password
    const validPassword = await bcrypt.compare(currentPassword, user.password);
    if (!validPassword) {
      return res.status(401).json({ error: true, message: 'Current password is incorrect' });
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);

    // Update password
    await dbRun(
      'UPDATE users SET password = ?, updated_at = datetime("now") WHERE id = ?',
      [hashedPassword, userId]
    );

    res.json({ error: false, message: 'Password changed successfully' });
  } catch (error) {
    console.error('Error changing password:', error);
    res.status(500).json({ error: true, message: 'Failed to change password' });
  }
});

module.exports = router;
