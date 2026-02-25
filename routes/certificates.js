const express = require('express');
const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { dbRun, dbGet } = require('../database/init');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Ensure certificates directory exists
const certificatesDir = './certificates';
if (!fs.existsSync(certificatesDir)) {
  fs.mkdirSync(certificatesDir, { recursive: true });
}

// Generate certificate for an exam
router.post('/generate/:examId', authenticateToken, async (req, res) => {
  try {
    const { examId } = req.params;
    const userId = req.user.id;

    // Get exam details
    const exam = await dbGet(
      `SELECT e.*, u.name as user_name, s.name as subject_name
       FROM exams e
       JOIN users u ON e.user_id = u.id
       JOIN subjects s ON e.subject_id = s.id
       WHERE e.id = ? AND e.user_id = ? AND e.completed_at IS NOT NULL`,
      [examId, userId]
    );

    if (!exam) {
      return res.status(404).json({ error: true, message: 'Exam not found or not completed' });
    }

    // Check if certificate already exists
    const existingCert = await dbGet(
      'SELECT * FROM certificates WHERE exam_id = ?',
      [examId]
    );

    if (existingCert) {
      return res.json({
        error: false,
        message: 'Certificate already exists',
        data: {
          certificateNumber: existingCert.certificate_number,
          filePath: `/certificates/${path.basename(existingCert.file_path)}`
        }
      });
    }

    // Generate certificate number
    const certificateNumber = `AEP-${Date.now()}-${uuidv4().substring(0, 8).toUpperCase()}`;
    const fileName = `certificate-${certificateNumber}.pdf`;
    const filePath = path.join(certificatesDir, fileName);

    // Create PDF certificate
    await generateCertificatePDF(exam, certificateNumber, filePath);

    // Save certificate record
    await dbRun(
      `INSERT INTO certificates (exam_id, user_id, certificate_number, file_path) 
       VALUES (?, ?, ?, ?)`,
      [examId, userId, certificateNumber, filePath]
    );

    res.json({
      error: false,
      message: 'Certificate generated successfully',
      data: {
        certificateNumber,
        filePath: `/certificates/${fileName}`
      }
    });
  } catch (error) {
    console.error('Error generating certificate:', error);
    res.status(500).json({ error: true, message: 'Failed to generate certificate' });
  }
});

// Get certificate by exam ID
router.get('/exam/:examId', authenticateToken, async (req, res) => {
  try {
    const { examId } = req.params;
    const userId = req.user.id;

    const certificate = await dbGet(
      'SELECT * FROM certificates WHERE exam_id = ? AND user_id = ?',
      [examId, userId]
    );

    if (!certificate) {
      return res.status(404).json({ error: true, message: 'Certificate not found' });
    }

    res.json({
      error: false,
      data: {
        certificateNumber: certificate.certificate_number,
        filePath: `/certificates/${path.basename(certificate.file_path)}`,
        issuedAt: certificate.issued_at
      }
    });
  } catch (error) {
    console.error('Error fetching certificate:', error);
    res.status(500).json({ error: true, message: 'Failed to fetch certificate' });
  }
});

// Helper function to generate PDF certificate
function generateCertificatePDF(exam, certificateNumber, filePath) {
  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument({ size: 'A4', layout: 'landscape' });
      const stream = fs.createWriteStream(filePath);

      doc.pipe(stream);

      // Background color
      doc.rect(0, 0, 842, 595).fill('#f8f9fa');

      // Border
      doc.rect(30, 30, 782, 535)
         .lineWidth(3)
         .strokeColor('#00C853')
         .stroke();

      // Inner border
      doc.rect(40, 40, 762, 515)
         .lineWidth(1)
         .strokeColor('#00C853')
         .stroke();

      // Logo/Header
      doc.fontSize(36)
         .fillColor('#00C853')
         .font('Helvetica-Bold')
         .text('AHMERDEE EXAM PRACTICE', 0, 80, { align: 'center' });

      // Certificate title
      doc.fontSize(28)
         .fillColor('#333')
         .text('CERTIFICATE OF ACHIEVEMENT', 0, 140, { align: 'center' });

      // Decorative line
      doc.moveTo(250, 190)
         .lineTo(592, 190)
         .lineWidth(2)
         .strokeColor('#00C853')
         .stroke();

      // "This is to certify that"
      doc.fontSize(14)
         .fillColor('#666')
         .font('Helvetica')
         .text('This is to certify that', 0, 220, { align: 'center' });

      // User name
      doc.fontSize(28)
         .fillColor('#000')
         .font('Helvetica-Bold')
         .text(exam.user_name.toUpperCase(), 0, 250, { align: 'center' });

      // Achievement text
      doc.fontSize(14)
         .fillColor('#666')
         .font('Helvetica')
         .text('has successfully completed the', 0, 300, { align: 'center' });

      // Subject name
      doc.fontSize(22)
         .fillColor('#00C853')
         .font('Helvetica-Bold')
         .text(exam.subject_name + ' Examination', 0, 330, { align: 'center' });

      // Score details
      doc.fontSize(16)
         .fillColor('#333')
         .font('Helvetica')
         .text(`Score: ${exam.score}/${exam.total_questions} (${exam.percentage.toFixed(1)}%) | Grade: ${exam.grade}`, 0, 375, { align: 'center' });

      // Date and certificate number
      const completedDate = new Date(exam.completed_at).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });

      doc.fontSize(12)
         .fillColor('#666')
         .text(`Date: ${completedDate}`, 100, 450);

      doc.text(`Certificate No: ${certificateNumber}`, 500, 450);

      // Signature section
      doc.fontSize(10)
         .fillColor('#333')
         .text('_____________________', 150, 500, { width: 200, align: 'center' });
      
      doc.text('Authorized Signature', 150, 520, { width: 200, align: 'center' });

      doc.text('_____________________', 500, 500, { width: 200, align: 'center' });
      
      doc.text('Date of Issue', 500, 520, { width: 200, align: 'center' });

      // Footer
      doc.fontSize(8)
         .fillColor('#999')
         .text('Ahmerdee Exam Practice - Excellence in Education', 0, 550, { align: 'center' });

      doc.end();

      stream.on('finish', () => {
        resolve();
      });

      stream.on('error', (error) => {
        reject(error);
      });
    } catch (error) {
      reject(error);
    }
  });
}

module.exports = router;
