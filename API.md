# 📡 Ahmerdee Exam Practice - API Documentation

Base URL: `https://your-app.up.railway.app/api`

## Authentication

Most endpoints require JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "error": false,
  "message": "Registration successful",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "error": false,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

## 📚 Question Endpoints

### Get All Subjects
```http
GET /questions/subjects
```

**Response:**
```json
{
  "error": false,
  "data": [
    {
      "id": 1,
      "name": "Mathematics",
      "emoji": "🔢",
      "description": "JAMB Mathematics questions"
    }
  ]
}
```

### Get Offline Questions
```http
GET /questions/offline/:subjectId
```

**Example:** `GET /questions/offline/1`

**Response:**
```json
{
  "error": false,
  "data": [
    {
      "id": 1,
      "subject_id": 1,
      "question_text": "What is 2 + 2?",
      "options": [
        { "key": "A", "text": "3" },
        { "key": "B", "text": "4" },
        { "key": "C", "text": "5" },
        { "key": "D", "text": "6" }
      ]
    }
  ],
  "total": 40
}
```

### Get Online Questions (Auth Required)
```http
GET /questions/online/:subjectId
Authorization: Bearer <token>
```

### Check Answer (Offline Practice)
```http
POST /questions/check-answer
Content-Type: application/json

{
  "questionId": 1,
  "userAnswer": "B"
}
```

**Response:**
```json
{
  "error": false,
  "data": {
    "isCorrect": true,
    "correctAnswer": "B",
    "explanation": "2 + 2 equals 4"
  }
}
```

---

## 📝 Exam Endpoints (Auth Required)

### Start Exam
```http
POST /exams/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "subjectId": 1,
  "examType": "online"
}
```

**Response:**
```json
{
  "error": false,
  "message": "Exam started successfully",
  "data": {
    "examId": 42
  }
}
```

### Submit Exam
```http
POST /exams/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "examId": 42,
  "durationSeconds": 3600,
  "answers": [
    {
      "questionId": 1,
      "userAnswer": "B",
      "timeSpent": 30
    },
    {
      "questionId": 2,
      "userAnswer": "C",
      "timeSpent": 45
    }
  ]
}
```

**Response:**
```json
{
  "error": false,
  "message": "Exam submitted successfully",
  "data": {
    "examId": 42,
    "score": 35,
    "totalQuestions": 40,
    "percentage": "87.50",
    "grade": "A"
  }
}
```

### Get Exam Result
```http
GET /exams/result/:examId
Authorization: Bearer <token>
```

**Response:**
```json
{
  "error": false,
  "data": {
    "exam": {
      "id": 42,
      "score": 35,
      "percentage": 87.5,
      "grade": "A",
      "subject_name": "Mathematics",
      "completed_at": "2024-02-25T10:30:00Z"
    },
    "answers": [...],
    "summary": {
      "correct": 35,
      "wrong": 5,
      "total": 40,
      "percentage": 87.5,
      "grade": "A"
    }
  }
}
```

### Get Exam History
```http
GET /exams/history
Authorization: Bearer <token>
```

### Get User Statistics
```http
GET /exams/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "error": false,
  "data": {
    "totalExams": 15,
    "averageScore": "82.50",
    "bestScore": "95.00",
    "subjectPerformance": [
      {
        "name": "Mathematics",
        "emoji": "🔢",
        "avg_percentage": 85.5,
        "attempts": 5
      }
    ]
  }
}
```

---

## 🎓 Certificate Endpoints (Auth Required)

### Generate Certificate
```http
POST /certificates/generate/:examId
Authorization: Bearer <token>
```

**Response:**
```json
{
  "error": false,
  "message": "Certificate generated successfully",
  "data": {
    "certificateNumber": "AEP-1234567890-ABC123",
    "filePath": "/certificates/certificate-AEP-1234567890-ABC123.pdf"
  }
}
```

### Get Certificate
```http
GET /certificates/exam/:examId
Authorization: Bearer <token>
```

---

## 👤 User Endpoints (Auth Required)

### Get Profile
```http
GET /users/profile
Authorization: Bearer <token>
```

### Update Profile
```http
PUT /users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Updated",
  "email": "john.new@example.com"
}
```

### Change Password
```http
PUT /users/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "currentPassword": "oldpassword123",
  "newPassword": "newpassword456"
}
```

---

## 🔧 Admin Endpoints (Admin Auth Required)

### Get Dashboard Stats
```http
GET /admin/dashboard
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "error": false,
  "data": {
    "stats": {
      "totalUsers": 150,
      "totalQuestions": 600,
      "totalExams": 500,
      "averageScore": "75.50"
    },
    "recentExams": [...],
    "questionsBySubject": [...]
  }
}
```

### User Management

#### Get All Users
```http
GET /admin/users
Authorization: Bearer <admin-token>
```

#### Get User Details
```http
GET /admin/users/:userId
Authorization: Bearer <admin-token>
```

#### Delete User
```http
DELETE /admin/users/:userId
Authorization: Bearer <admin-token>
```

### Question Management

#### Get All Questions
```http
GET /admin/questions?subjectId=1&isOnline=true
Authorization: Bearer <admin-token>
```

#### Add Question
```http
POST /admin/questions
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "subjectId": 1,
  "questionText": "What is the capital of Nigeria?",
  "optionA": "Lagos",
  "optionB": "Abuja",
  "optionC": "Kano",
  "optionD": "Ibadan",
  "correctAnswer": "B",
  "explanation": "Abuja is the capital of Nigeria",
  "difficulty": "easy",
  "isOnline": true
}
```

#### Update Question
```http
PUT /admin/questions/:questionId
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "questionText": "Updated question text?",
  "optionA": "Updated A",
  "optionB": "Updated B",
  "optionC": "Updated C",
  "optionD": "Updated D",
  "correctAnswer": "A",
  "explanation": "Updated explanation",
  "difficulty": "medium",
  "isOnline": true
}
```

#### Delete Question
```http
DELETE /admin/questions/:questionId
Authorization: Bearer <admin-token>
```

#### Bulk Upload Questions
```http
POST /admin/questions/bulk-upload
Authorization: Bearer <admin-token>
Content-Type: multipart/form-data

file: <questions.json file>
```

### Subject Management

#### Add Subject
```http
POST /admin/subjects
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "name": "Economics",
  "emoji": "💰",
  "description": "JAMB Economics questions"
}
```

#### Update Subject
```http
PUT /admin/subjects/:subjectId
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "name": "Economics Updated",
  "emoji": "💵",
  "description": "Updated description"
}
```

#### Delete Subject
```http
DELETE /admin/subjects/:subjectId
Authorization: Bearer <admin-token>
```

### Results Management

#### Get All Results
```http
GET /admin/results?subjectId=1&userId=5&startDate=2024-01-01&endDate=2024-12-31
Authorization: Bearer <admin-token>
```

#### Delete Result
```http
DELETE /admin/results/:examId
Authorization: Bearer <admin-token>
```

---

## 🔢 Grade System

| Percentage | Grade |
|------------|-------|
| 90-100%    | A+    |
| 85-89%     | A     |
| 80-84%     | A-    |
| 75-79%     | B+    |
| 70-74%     | B     |
| 65-69%     | B-    |
| 60-64%     | C+    |
| 55-59%     | C     |
| 50-54%     | C-    |
| 45-49%     | D     |
| 0-44%      | F     |

---

## ⚠️ Error Responses

All errors follow this format:

```json
{
  "error": true,
  "message": "Error description"
}
```

### Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - No token or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 🧪 Testing with cURL

### Register and Login
```bash
# Register
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ahmerdee.com","password":"Admin@123"}'
```

### Use Token
```bash
# Get subjects
curl http://localhost:3000/api/questions/subjects

# Get profile (requires token)
curl http://localhost:3000/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📱 Android Integration Example

```java
// Retrofit interface
public interface AhmerdeeAPI {
    @POST("auth/login")
    Call<LoginResponse> login(@Body LoginRequest request);
    
    @GET("questions/offline/{subjectId}")
    Call<QuestionsResponse> getOfflineQuestions(@Path("subjectId") int subjectId);
    
    @POST("exams/start")
    Call<ExamResponse> startExam(
        @Header("Authorization") String token,
        @Body ExamStartRequest request
    );
}

// Usage
String token = "Bearer " + authToken;
api.startExam(token, new ExamStartRequest(subjectId, "online"));
```

---

## 🔐 Security Notes

1. Always use HTTPS in production
2. Store JWT tokens securely (not in localStorage)
3. Tokens expire after 7 days
4. Admin endpoints require admin role
5. Rate limiting may be applied

---

For more information, see [README.md](README.md)
