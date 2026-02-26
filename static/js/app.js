// AEP v1.0 - app.js

// ===== TOAST =====
function showToast(msg, type = 'info') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  let c = document.getElementById('toast-container');
  if (!c) { c = document.createElement('div'); c.id = 'toast-container'; c.className = 'toast-container'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icons[type]||'•'}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3400);
}

// ===== MODAL =====
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('active'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('active'); document.body.style.overflow = ''; }
}
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// ===== AJAX =====
async function postJSON(url, data, btn) {
  const orig = btn ? btn.innerHTML : '';
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>'; }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    if (json.success) {
      if (json.message) showToast(json.message, 'success');
      if (json.redirect) setTimeout(() => location.href = json.redirect, 600);
    } else {
      showToast(json.message || 'Error occurred', 'error');
    }
    return json;
  } catch (e) {
    showToast('Network error', 'error');
    return null;
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = orig; }
  }
}

// ===== COPY =====
function copyText(text, msg) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => showToast(msg || 'Copied!', 'success'));
  } else {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta);
    ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
    showToast(msg || 'Copied!', 'success');
  }
}

// ===== ACTIVE NAV =====
document.addEventListener('DOMContentLoaded', () => {
  const path = location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && path === href) item.classList.add('active');
    else if (href && href !== '/' && path.startsWith(href)) item.classList.add('active');
  });
  // Keep online status
  setInterval(() => {
    fetch('/api/online_status', { method: 'POST' }).catch(() => {});
  }, 30000);
});

// ===== EXAM ENGINE =====
class ExamEngine {
  constructor(questions, mode, duration, subject) {
    this.questions = questions;
    this.mode = mode;
    this.duration = duration;
    this.subject = subject;
    this.current = 0;
    this.answers = {};
    this.timeLeft = duration;
    this.timer = null;
    this.finished = false;
  }

  start() {
    this.render();
    if (this.duration > 0) this.startTimer();
  }

  startTimer() {
    this.timer = setInterval(() => {
      this.timeLeft--;
      this.updateTimer();
      if (this.timeLeft <= 0) {
        clearInterval(this.timer);
        this.finish();
      }
    }, 1000);
  }

  updateTimer() {
    const el = document.getElementById('exam-timer');
    if (!el) return;
    const m = Math.floor(this.timeLeft / 60);
    const s = this.timeLeft % 60;
    el.textContent = `⏱ ${m}:${s.toString().padStart(2,'0')}`;
    el.className = 'exam-timer';
    if (this.timeLeft <= 60) el.classList.add('danger');
    else if (this.timeLeft <= 300) el.classList.add('warning');
  }

  render() {
    const q = this.questions[this.current];
    const total = this.questions.length;
    
    document.getElementById('q-number').textContent = `Question ${this.current + 1} of ${total}`;
    document.getElementById('q-text').textContent = q.question;
    
    const optContainer = document.getElementById('options-container');
    optContainer.innerHTML = '';
    const letters = ['A','B','C','D'];
    Object.entries(q.options).forEach(([letter, text]) => {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      if (this.answers[q.id] === letter) btn.classList.add('selected');
      btn.innerHTML = `<span class="option-letter">${letter}</span>${text}`;
      btn.onclick = () => this.selectAnswer(letter);
      optContainer.appendChild(btn);
    });

    // Progress
    const progress = ((this.current + 1) / total) * 100;
    const bar = document.getElementById('progress-fill');
    if (bar) bar.style.width = progress + '%';

    // Nav buttons
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    if (prevBtn) prevBtn.disabled = this.current === 0;
    if (nextBtn) {
      if (this.current === total - 1) {
        nextBtn.textContent = '✅ Finish';
        nextBtn.onclick = () => this.finish();
      } else {
        nextBtn.textContent = 'Next ›';
        nextBtn.onclick = () => this.next();
      }
    }
  }

  selectAnswer(letter) {
    const q = this.questions[this.current];
    this.answers[q.id] = letter;
    this.render();
  }

  next() {
    if (this.current < this.questions.length - 1) {
      this.current++;
      this.render();
    }
  }

  prev() {
    if (this.current > 0) {
      this.current--;
      this.render();
    }
  }

  async finish() {
    if (this.finished) return;
    this.finished = true;
    if (this.timer) clearInterval(this.timer);
    
    const submitBtn = document.getElementById('finish-btn');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = '<span class="spinner"></span>'; }

    const res = await fetch('/submit_exam', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: this.mode,
        subject: this.subject,
        answers: this.answers,
        questions: this.questions
      })
    });
    const data = await res.json();
    if (data.success) {
      if (this.mode === 'practice') {
        showToast(`Score: ${data.score}/${data.total} (${data.percentage}%)`, 'success');
        setTimeout(() => location.href = '/subjects', 2000);
      } else {
        location.href = `/result/${data.result_id}`;
      }
    }
  }
}

// ===== QUIZ ENGINE =====
class QuizEngine {
  constructor(questions, subject) {
    this.questions = questions;
    this.subject = subject;
    this.current = 0;
    this.score = 0;
    this.answered = false;
  }

  start() { this.render(); }

  render() {
    if (this.current >= this.questions.length) {
      this.showFinalScore();
      return;
    }
    const q = this.questions[this.current];
    document.getElementById('q-number').textContent = `Question ${this.current + 1} of ${this.questions.length}`;
    document.getElementById('q-text').textContent = q.question;
    
    const optContainer = document.getElementById('options-container');
    optContainer.innerHTML = '';
    this.answered = false;
    document.getElementById('quiz-feedback').innerHTML = '';

    Object.entries(q.options).forEach(([letter, text]) => {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML = `<span class="option-letter">${letter}</span>${text}`;
      btn.onclick = () => this.answer(letter, btn, q);
      optContainer.appendChild(btn);
    });
  }

  answer(letter, btn, q) {
    if (this.answered) return;
    this.answered = true;
    const correct = q.answer === letter;
    if (correct) { this.score++; btn.classList.add('correct'); }
    else {
      btn.classList.add('wrong');
      // Highlight correct
      document.querySelectorAll('.option-btn').forEach(b => {
        if (b.textContent.trim().startsWith(q.answer)) b.classList.add('correct');
      });
    }
    const fb = document.getElementById('quiz-feedback');
    fb.innerHTML = `
      <div class="quiz-result-badge ${correct ? 'quiz-correct' : 'quiz-wrong'}">
        ${correct ? '✅ Correct!' : '❌ Wrong!'}<br>
        <small style="font-size:12px;font-weight:600;margin-top:6px;display:block">💡 ${q.explanation || 'No explanation available.'}</small>
      </div>
      <button class="btn btn-primary" onclick="window.quizEngine.next()" style="margin-top:8px">
        ${this.current < this.questions.length - 1 ? 'Next Question ›' : '🏁 See Score'}
      </button>
    `;
  }

  next() {
    this.current++;
    this.render();
  }

  showFinalScore() {
    const pct = Math.round((this.score / this.questions.length) * 100);
    document.getElementById('exam-body').innerHTML = `
      <div style="text-align:center;padding:40px 24px">
        <div style="font-size:60px;margin-bottom:16px">🎉</div>
        <div style="font-size:36px;font-weight:900;color:var(--accent)">${pct}%</div>
        <div style="font-size:16px;font-weight:700;margin-bottom:8px">${this.score}/${this.questions.length} Correct</div>
        <div style="font-size:13px;color:var(--muted);margin-bottom:24px">${this.subject} - Quiz Mode</div>
        <a href="/subjects" class="btn btn-primary" style="text-decoration:none">Back to Subjects</a>
      </div>
    `;
  }
}

// ===== CHAT =====
let chatTarget = null;
let chatPollInterval = null;

async function openChat(uid, name) {
  chatTarget = uid;
  document.getElementById('chat-target-name').textContent = name;
  document.getElementById('chat-list').style.display = 'none';
  document.getElementById('chat-window').style.display = 'flex';
  await loadMessages();
  if (chatPollInterval) clearInterval(chatPollInterval);
  chatPollInterval = setInterval(loadMessages, 3000);
}

function closeChat() {
  chatTarget = null;
  if (chatPollInterval) clearInterval(chatPollInterval);
  document.getElementById('chat-list').style.display = 'block';
  document.getElementById('chat-window').style.display = 'none';
}

async function loadMessages() {
  if (!chatTarget) return;
  const res = await fetch(`/api/chat/messages/${chatTarget}`);
  const msgs = await res.json();
  const container = document.getElementById('chat-messages');
  const currentUserId = document.getElementById('current-user-id').value;
  container.innerHTML = '';
  msgs.forEach(m => {
    const isMine = m.from === currentUserId;
    const d = document.createElement('div');
    d.innerHTML = `
      <div class="msg-bubble ${isMine ? 'msg-mine' : 'msg-theirs'}">
        ${m.message}
        <div class="msg-time">${new Date(m.time).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</div>
      </div>
    `;
    container.appendChild(d);
  });
  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg || !chatTarget) return;
  input.value = '';
  await fetch('/api/chat/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to: chatTarget, message: msg })
  });
  await loadMessages();
}

// ===== ADMIN =====
async function userAction(uid, action) {
  const res = await postJSON('/admin/user_action', { uid, action });
  if (res?.success) setTimeout(() => location.reload(), 800);
}

async function setRole(uid, role) {
  const res = await postJSON('/admin/set_role', { uid, role });
  if (res?.success) setTimeout(() => location.reload(), 800);
}

async function deleteQuestion(subject, qid) {
  if (!confirm('Delete this question?')) return;
  const res = await postJSON('/admin/delete_question', { subject, qid });
  if (res?.success) location.reload();
}

async function replyTicket(ticketId) {
  const reply = document.getElementById(`reply-${ticketId}`).value.trim();
  if (!reply) return;
  const res = await postJSON('/admin/reply_support', { ticket_id: ticketId, reply });
  if (res?.success) location.reload();
}
