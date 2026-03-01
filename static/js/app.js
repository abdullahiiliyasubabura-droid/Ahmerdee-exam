// ═══════════════════════════════════════════════
// AEP v2.0 — app.js
// Socket.IO · Network Guard · Anti-Cheat
// Live Quiz Broadcast · Toast · Modal · Exam
// ═══════════════════════════════════════════════
'use strict';

// ── Socket.IO (lazily initialized) ────────────
let socket = null;
function getSocket() {
  if (!socket) {
    socket = io({ transports: ['websocket','polling'], reconnection: true, reconnectionDelay: 1000, reconnectionAttempts: 30 });
    socket.on('connect', () => console.log('[AEP] Socket connected'));
    socket.on('broadcast', data => showBroadcastTicker(data.message));
  }
  return socket;
}

// ═══════════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════════
function showToast(msg, type='info', duration=3400) {
  const icons = {success:'✅',error:'❌',info:'ℹ️',warning:'⚠️'};
  let c = document.getElementById('toast-container');
  if (!c) { c=document.createElement('div'); c.id='toast-container'; c.className='toast-container'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icons[type]||'•'}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => { t.style.cssText='opacity:0;transform:translateY(8px);transition:.3s'; setTimeout(()=>t.remove(),300); }, duration);
}

// ═══════════════════════════════════════════════
// MODAL
// ═══════════════════════════════════════════════
function openModal(id) { const e=document.getElementById(id); if(e){e.classList.add('active');document.body.style.overflow='hidden';} }
function closeModal(id) { const e=document.getElementById(id); if(e){e.classList.remove('active');document.body.style.overflow='';} }
document.addEventListener('click', e => { if(e.target.classList.contains('modal-overlay')){e.target.classList.remove('active');document.body.style.overflow='';} });

// ═══════════════════════════════════════════════
// AJAX
// ═══════════════════════════════════════════════
async function postJSON(url, data, btn) {
  const orig = btn ? btn.innerHTML : '';
  if (btn) { btn.disabled=true; btn.innerHTML='<span class="spinner"></span>'; }
  try {
    const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    const json = await res.json();
    if (json.success) { if(json.message)showToast(json.message,'success'); if(json.redirect)setTimeout(()=>location.href=json.redirect,600); }
    else showToast(json.message||'Error occurred','error');
    return json;
  } catch(e) { showToast('Network error','error'); return null; }
  finally { if(btn){btn.disabled=false;btn.innerHTML=orig;} }
}

function copyText(text, msg) {
  if (navigator.clipboard) navigator.clipboard.writeText(text).then(()=>showToast(msg||'Copied!','success'));
  else { const ta=document.createElement('textarea'); ta.value=text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); showToast(msg||'Copied!','success'); }
}

// ═══════════════════════════════════════════════
// NETWORK GUARD
// ═══════════════════════════════════════════════
function initNetworkGuard() {
  const overlay = document.getElementById('network-guard');
  if (!overlay) return;
  window.addEventListener('offline', ()=>overlay.classList.add('show'));
  window.addEventListener('online', ()=>{ overlay.classList.remove('show'); showToast('Connection restored! ✅','success'); });
  if (!navigator.onLine) overlay.classList.add('show');
}

// ═══════════════════════════════════════════════
// TAB DETECTION (anti-cheat)
// ═══════════════════════════════════════════════
let tabWarnings=0;
function initTabDetection(maxWarnings=3) {
  const el = document.getElementById('tab-warning');
  if (!el) return;
  function onHidden() {
    if (!document.hidden) return;
    tabWarnings++;
    const countEl = el.querySelector('.tab-warning-count');
    if (countEl) countEl.textContent = tabWarnings;
    el.classList.add('show');
    if (tabWarnings >= maxWarnings && window.examEngine) window.examEngine.forceFinish('Tab switch limit reached.');
  }
  document.addEventListener('visibilitychange', onHidden);
  window.addEventListener('blur', onHidden);
}
function dismissTabWarning() { const e=document.getElementById('tab-warning'); if(e)e.classList.remove('show'); }

// ═══════════════════════════════════════════════
// BROADCAST TICKER
// ═══════════════════════════════════════════════
function showBroadcastTicker(message) {
  let t = document.getElementById('broadcast-ticker');
  if (t) return;
  t = document.createElement('div'); t.id='broadcast-ticker'; t.className='broadcast-ticker';
  t.innerHTML = `<span class="broadcast-ticker-inner">📢 ${message} &nbsp;&nbsp;&nbsp; 📢 ${message}</span>`;
  document.body.insertBefore(t, document.body.firstChild);
  setTimeout(()=>{ if(t.parentNode)t.parentNode.removeChild(t); }, 15000);
}

// ═══════════════════════════════════════════════
// EXAM ENGINE
// ═══════════════════════════════════════════════
class ExamEngine {
  constructor(questions, mode, durationSec, subject) {
    this.questions=questions; this.mode=mode; this.durationSec=durationSec; this.subject=subject;
    this.current=0; this.answers={}; this.timeLeft=durationSec; this.timer=null; this.finished=false;
    window.examEngine=this;
  }
  start() { this.render(); if(this.durationSec>0)this.startTimer(); if(this.mode==='exam')initTabDetection(); }
  startTimer() {
    this.updateTimerDisplay();
    this.timer=setInterval(()=>{ this.timeLeft--; this.updateTimerDisplay(); if(this.timeLeft<=0){clearInterval(this.timer);showToast('⏰ Time up! Submitting...','warning');setTimeout(()=>this.finish(),1500);} },1000);
  }
  updateTimerDisplay() {
    const el=document.getElementById('exam-timer'); if(!el)return;
    const m=Math.floor(this.timeLeft/60), s=this.timeLeft%60;
    el.textContent=`${m}:${s.toString().padStart(2,'0')}`;
    el.className='timer-badge';
    if(this.timeLeft<=60)el.classList.add('danger');
    else if(this.timeLeft<=300)el.classList.add('warning');
  }
  render() {
    const q=this.questions[this.current], total=this.questions.length;
    const numEl=document.getElementById('q-num'); if(numEl)numEl.textContent=`Question ${this.current+1} of ${total}`;
    const textEl=document.getElementById('q-text'); if(textEl)textEl.textContent=q.question;
    const bar=document.getElementById('progress-fill'); if(bar)bar.style.width=`${((this.current+1)/total)*100}%`;
    const opts=document.getElementById('options-list'); if(!opts)return;
    opts.innerHTML='';
    ['A','B','C','D'].forEach((letter,i)=>{
      const text=[q.option_a,q.option_b,q.option_c,q.option_d][i];
      if(!text)return;
      const div=document.createElement('div');
      div.className='option-item'+(this.answers[q.id]===letter?' selected':'');
      div.innerHTML=`<div class="option-label">${letter}</div><div class="option-text">${text}</div>`;
      div.onclick=()=>this.select(letter,div,q.id);
      opts.appendChild(div);
    });
    this.updateQDots(); this.updateNavBtns();
  }
  select(letter,el,qid) {
    this.answers[qid]=letter;
    document.querySelectorAll('#options-list .option-item').forEach(d=>{d.classList.remove('selected');d.querySelector('.option-label').style.cssText='';});
    el.classList.add('selected');
    el.querySelector('.option-label').style.cssText='background:var(--accent);color:#fff';
    this.updateQDots();
  }
  updateQDots() {
    document.querySelectorAll('.q-dot').forEach((dot,i)=>{
      dot.classList.remove('answered','current');
      if(i===this.current)dot.classList.add('current');
      if(this.answers[this.questions[i]?.id])dot.classList.add('answered');
    });
  }
  updateNavBtns() {
    const prev=document.getElementById('prev-btn'); if(prev)prev.disabled=this.current===0;
    const next=document.getElementById('next-btn'); if(next)next.style.display=this.current===this.questions.length-1?'none':'flex';
    const fin=document.getElementById('finish-btn'); if(fin)fin.style.display=this.current===this.questions.length-1?'flex':'none';
  }
  go(i) { if(i>=0&&i<this.questions.length){this.current=i;this.render();} }
  prev() { this.go(this.current-1); }
  next() { this.go(this.current+1); }
  confirmFinish() {
    const unanswered=this.questions.length-Object.keys(this.answers).length;
    if(unanswered>0&&!confirm(`⚠️ ${unanswered} unanswered question(s). Submit anyway?`))return;
    this.finish();
  }
  forceFinish(reason) { showToast(`⚠️ ${reason} Auto-submitting...`,'warning',3000); setTimeout(()=>this.finish(),2000); }
  async finish() {
    if(this.finished)return; this.finished=true;
    if(this.timer)clearInterval(this.timer);
    const btn=document.getElementById('finish-btn'); if(btn){btn.disabled=true;btn.innerHTML='<span class="spinner"></span> Submitting...';}
    try {
      const res=await fetch('/submit_exam',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:this.mode,subject:this.subject,answers:this.answers,questions:this.questions})});
      const data=await res.json();
      if(data.success){
        if(this.mode==='practice'){showToast(`✅ Score: ${data.score}/${data.total} (${data.percentage}%)`,'success',5000);setTimeout(()=>location.href='/subjects',2500);}
        else location.href=`/result/${data.result_id}`;
      } else { showToast('Submission failed','error'); this.finished=false; }
    } catch(e) { showToast('Network error during submission!','error'); this.finished=false; }
  }
}

// ═══════════════════════════════════════════════
// GROUP CHAT
// ═══════════════════════════════════════════════
function initGroupChat(userId) {
  const sock=getSocket(); sock.emit('join_group');
  sock.on('group_message', msg=>appendGroupMessage(msg,userId));
  sock.on('group_typing',({name,uid})=>{
    if(uid===userId)return;
    const el=document.getElementById('typing-indicator');
    if(el){el.textContent=`${name} is typing...`;clearTimeout(el._t);el._t=setTimeout(()=>{el.textContent='';},3000);}
  });
  loadGroupMessages(userId);
  const input=document.getElementById('group-input');
  const sendBtn=document.getElementById('group-send');
  if(input){
    input.addEventListener('input',()=>{sock.emit('typing',{type:'group'});input.style.height='auto';input.style.height=Math.min(input.scrollHeight,100)+'px';});
    input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendGroupMessage();}});
  }
  if(sendBtn)sendBtn.addEventListener('click',sendGroupMessage);
}
async function loadGroupMessages(userId) {
  try { const res=await fetch('/api/group/messages'); const msgs=await res.json(); const c=document.getElementById('messages-area'); if(!c)return; c.innerHTML=''; msgs.forEach(m=>appendGroupMessage(m,userId,false)); c.scrollTop=c.scrollHeight; } catch(e){}
}
function appendGroupMessage(msg,currentUserId,scroll=true) {
  const c=document.getElementById('messages-area'); if(!c)return;
  const isMine=msg.from_id===currentUserId;
  const wrap=document.createElement('div'); wrap.className=`msg-wrap${isMine?' own':''}`;
  const av=msg.from_avatar?`<div class="msg-avatar"><img src="${msg.from_avatar}" alt=""></div>`:`<div class="msg-avatar">${(msg.from_name||'?')[0].toUpperCase()}</div>`;
  const time=new Date(msg.time).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  wrap.innerHTML=`${!isMine?av:''}<div class="msg-bubble ${isMine?'own':'other'}">${!isMine?`<div class="msg-name">${msg.from_name}${msg.from_role!=='student'?' 🛡️':''}</div>`:''}<span>${msg.message}</span><div class="msg-time">${time}</div></div>${isMine?av:''}`;
  c.appendChild(wrap);
  if(scroll)c.scrollTop=c.scrollHeight;
}
async function sendGroupMessage() {
  const input=document.getElementById('group-input'); if(!input)return;
  const msg=input.value.trim(); if(!msg)return; input.value=''; input.style.height='auto';
  await fetch('/api/group/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})}).catch(()=>showToast('Failed to send','error'));
}

// ═══════════════════════════════════════════════
// DM CHAT
// ═══════════════════════════════════════════════
function initDmChat(myId,targetId) {
  const sock=getSocket(); sock.emit('join_dm',{user_id:myId});
  sock.on('dm_message',msg=>{ if((msg.from_id===myId&&msg.to_id===targetId)||(msg.from_id===targetId&&msg.to_id===myId))appendDmMessage(msg,myId); });
  sock.on('typing',({from_id,target_id,type})=>{ if(type==='dm'&&from_id===targetId&&target_id===myId){const el=document.getElementById('typing-indicator');if(el){el.textContent='Typing...';clearTimeout(el._t);el._t=setTimeout(()=>{el.textContent='';},3000);}} });
  const input=document.getElementById('dm-input'), sendBtn=document.getElementById('dm-send');
  if(input){
    input.addEventListener('input',()=>{sock.emit('typing',{type:'dm',target_id:targetId});input.style.height='auto';input.style.height=Math.min(input.scrollHeight,100)+'px';});
    input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendDmMessage(myId,targetId);}});
  }
  if(sendBtn)sendBtn.addEventListener('click',()=>sendDmMessage(myId,targetId));
}
function appendDmMessage(msg,myId,scroll=true) {
  const c=document.getElementById('messages-area'); if(!c)return;
  const isMine=msg.from_id===myId;
  const wrap=document.createElement('div'); wrap.className=`msg-wrap${isMine?' own':''}`;
  const av=msg.from_avatar?`<div class="msg-avatar"><img src="${msg.from_avatar}" alt=""></div>`:`<div class="msg-avatar">${(msg.from_name||'?')[0].toUpperCase()}</div>`;
  const time=new Date(msg.time).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  wrap.innerHTML=`${!isMine?av:''}<div class="msg-bubble ${isMine?'own':'other'}"><span>${msg.message}</span><div class="msg-time">${time}</div></div>${isMine?av:''}`;
  c.appendChild(wrap); if(scroll)c.scrollTop=c.scrollHeight;
}
async function sendDmMessage(myId,targetId) {
  const input=document.getElementById('dm-input'); if(!input)return;
  const msg=input.value.trim(); if(!msg)return; input.value=''; input.style.height='auto';
  await fetch('/api/chat/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({to:targetId,message:msg})}).catch(()=>showToast('Failed to send','error'));
}

// ═══════════════════════════════════════════════
// LIVE QUIZ — STADIUM MODE
// ═══════════════════════════════════════════════
let liveTimerInterval=null;

function initLiveQuiz(quizId,userId,role) {
  const sock=getSocket();
  sock.emit('join_quiz',{quiz_id:quizId,user_id:userId});
  sock.on('next_question',data=>{updateLiveQuestion(data);startQuestionTimer(data.time_per_q);clearAnswerStates();});
  sock.on('live_answer',data=>{updateLiveScores(data.p1_score,data.p2_score);if(data.correct_answer)revealAnswers(data.correct_answer);});
  if(role==='spectator') sock.on('live_comment',comment=>appendLiveComment(comment));
  sock.on('quiz_finished',data=>showQuizResult(data));
  sock.on('quiz_cancelled',()=>{showToast('📺 Quiz cancelled by admin.','warning',5000);setTimeout(()=>location.href='/live',2500);});

  if(role==='spectator'){
    const ci=document.getElementById('comment-input'), cs=document.getElementById('comment-send');
    if(ci)ci.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();sendLiveComment(quizId);}});
    if(cs)cs.addEventListener('click',()=>sendLiveComment(quizId));
  }
  // Fallback poll
  setInterval(()=>{ fetch(`/api/live/state/${quizId}`).then(r=>r.json()).then(d=>{if(d.p1_score!==undefined)updateLiveScores(d.p1_score,d.p2_score);}).catch(()=>{}); },5000);
}

function updateLiveQuestion(data) {
  const qNum=document.getElementById('live-q-num'); if(qNum)qNum.textContent=`Q${data.index+1} of ${data.total}`;
  const qText=document.getElementById('live-q-text'); if(qText)qText.textContent=data.question;
  const opts=document.getElementById('live-options'); if(!opts||!data.options)return;
  opts.innerHTML='';
  ['A','B','C','D'].forEach((letter,i)=>{
    const div=document.createElement('div'); div.className='live-option-item'; div.dataset.letter=letter;
    div.innerHTML=`<div class="option-label">${letter}</div><div class="option-text">${data.options[i]||''}</div>`;
    div.onclick=()=>submitLiveAnswer(letter,data.q_id,div);
    opts.appendChild(div);
  });
}

function startQuestionTimer(seconds) {
  const el=document.getElementById('live-timer-val'); if(!el)return;
  if(liveTimerInterval)clearInterval(liveTimerInterval);
  let t=seconds;
  function tick(){
    el.textContent=t;
    const circle=document.getElementById('live-timer-circle');
    if(circle)circle.style.borderColor=t<=5?'#e17055':t<=10?'#f1c40f':'#a29bfe';
    if(t<=0){clearInterval(liveTimerInterval);return;} t--;
  }
  tick(); liveTimerInterval=setInterval(tick,1000);
}

function clearAnswerStates() {
  document.querySelectorAll('.live-option-item').forEach(el=>{el.classList.remove('selected','correct','wrong');el.style.pointerEvents='';});
  const pills=document.getElementById('answered-pills'); if(pills)pills.innerHTML='';
}

async function submitLiveAnswer(letter,qId,el) {
  document.querySelectorAll('.live-option-item').forEach(o=>o.style.pointerEvents='none');
  el.classList.add('selected');
  try {
    const res=await fetch('/api/live/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q_id:qId,answer:letter})});
    const data=await res.json();
    if(data.correct!==undefined){el.classList.remove('selected');el.classList.add(data.correct?'correct':'wrong');}
  } catch(e){showToast('Failed to submit answer','error');}
}

function revealAnswers(correctLetter) {
  document.querySelectorAll('.live-option-item').forEach(el=>{
    el.style.pointerEvents='none';
    if(el.dataset.letter===correctLetter)el.classList.add('correct');
    else if(el.classList.contains('selected'))el.classList.add('wrong');
  });
}

function updateLiveScores(p1,p2) {
  const s1=document.getElementById('p1-score'); if(s1)s1.textContent=p1;
  const s2=document.getElementById('p2-score'); if(s2)s2.textContent=p2;
}

function appendLiveComment(comment) {
  const feed=document.getElementById('comments-feed'); if(!feed)return;
  const div=document.createElement('div'); div.className='comment-item';
  const av=comment.from_avatar?`<div class="comment-avatar"><img src="${comment.from_avatar}" alt=""></div>`:`<div class="comment-avatar">${(comment.from_name||'?')[0].toUpperCase()}</div>`;
  div.innerHTML=`${av}<div class="comment-bubble"><div class="comment-name">${comment.from_name}</div><div class="comment-text">${comment.message}</div></div>`;
  feed.appendChild(div); feed.scrollTop=feed.scrollHeight;
}

async function sendLiveComment(quizId) {
  const input=document.getElementById('comment-input'); if(!input)return;
  const msg=input.value.trim(); if(!msg)return; input.value='';
  await fetch('/api/live/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({quiz_id:quizId,message:msg})}).catch(()=>{});
}

function showQuizResult(data) {
  const overlay=document.getElementById('quiz-result-overlay');
  if(overlay){
    const title=overlay.querySelector('.result-title'); if(title)title.textContent=data.winner?`🏆 ${data.winner_name} Wins!`:'🤝 It\'s a Tie!';
    const p1f=overlay.querySelector('.p1-final'); if(p1f)p1f.textContent=data.p1_score;
    const p2f=overlay.querySelector('.p2-final'); if(p2f)p2f.textContent=data.p2_score;
    overlay.classList.add('show');
  } else {
    showToast(`🏁 Quiz over! ${data.winner_name||'Tie'} — ${data.p1_score} vs ${data.p2_score}`,'info',8000);
  }
}

function initLiveLobby() {
  const sock=getSocket(); sock.emit('join_group');
  sock.on('new_live_quiz',()=>{showToast('🎮 New quiz scheduled!','info',5000);setTimeout(()=>location.reload(),2000);});
  sock.on('quiz_started',()=>{showToast('📺 Quiz is LIVE! Tap to watch 👇','success',5000);setTimeout(()=>location.reload(),1500);});
}

// ═══════════════════════════════════════════════
// ADMIN HELPERS
// ═══════════════════════════════════════════════
async function userAction(uid,action) { const r=await postJSON('/admin/user_action',{uid,action}); if(r?.success)setTimeout(()=>location.reload(),800); }
async function setRole(uid,role) { const r=await postJSON('/admin/set_role',{uid,role}); if(r?.success)setTimeout(()=>location.reload(),800); }
async function deleteQuestion(qid) {
  if(!confirm('Delete this question?'))return;
  const r=await postJSON('/admin/delete_question',{qid});
  if(r?.success){const row=document.getElementById(`q-row-${qid}`);if(row)row.remove();}
}
async function replyTicket(ticketId) {
  const input=document.getElementById(`reply-${ticketId}`); if(!input)return;
  const reply=input.value.trim(); if(!reply)return;
  const r=await postJSON('/admin/reply_support',{ticket_id:ticketId,reply}); if(r?.success)location.reload();
}
async function resolveReport(rId) { const r=await postJSON('/admin/resolve_report',{report_id:rId}); if(r?.success){const el=document.getElementById(`report-${rId}`);if(el)el.remove();} }
async function pinMessage(msgId) { const r=await postJSON('/api/group/pin',{msg_id:msgId}); if(r?.success)showToast('Message pinned 📌','success'); }
async function deleteMessage(msgId) { if(!confirm('Delete?'))return; const r=await postJSON('/api/group/delete',{msg_id:msgId}); if(r?.success){const el=document.getElementById(`msg-${msgId}`);if(el)el.remove();} }
async function startLiveQuiz(quizId) { const r=await postJSON('/admin/start_live_quiz',{quiz_id:quizId}); if(r?.success)setTimeout(()=>location.reload(),800); }
async function nextQuestion(quizId) { const btn=document.getElementById('next-q-btn'); const r=await postJSON('/admin/next_question',{quiz_id:quizId},btn); if(r?.success)showToast('▶️ Next question pushed!','success'); }
async function cancelLiveQuiz(quizId) { if(!confirm('Cancel this quiz?'))return; const r=await postJSON('/admin/cancel_live_quiz',{quiz_id:quizId}); if(r?.success)setTimeout(()=>location.href='/admin/live_quizzes',800); }

// ═══════════════════════════════════════════════
// AVATAR PREVIEW
// ═══════════════════════════════════════════════
function initAvatarPreview() {
  const fi=document.getElementById('avatar-input'), prev=document.getElementById('avatar-preview'), editBtn=document.querySelector('.avatar-edit-btn');
  if(editBtn)editBtn.onclick=()=>fi?.click();
  if(fi)fi.addEventListener('change',e=>{
    const file=e.target.files[0]; if(!file)return;
    if(file.size>10*1024*1024){showToast('Image too large (max 10MB)','error');return;}
    const reader=new FileReader();
    reader.onload=ev=>{if(prev){if(prev.tagName==='IMG')prev.src=ev.target.result;else prev.innerHTML=`<img src="${ev.target.result}" style="width:100%;height:100%;object-fit:cover">`;} };
    reader.readAsDataURL(file);
  });
}

// ═══════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Active nav
  const path=location.pathname;
  document.querySelectorAll('.nav-item').forEach(item=>{
    const href=item.getAttribute('href'); if(!href)return;
    item.classList.remove('active');
    if(href==='/'&&path==='/')item.classList.add('active');
    else if(href!=='/'&&path.startsWith(href))item.classList.add('active');
  });
  // Keepalive
  if(document.body.dataset.userId)setInterval(()=>fetch('/api/online_status',{method:'POST'}).catch(()=>{}),30000);
  // Auto-grow textareas
  document.querySelectorAll('textarea').forEach(ta=>{ta.addEventListener('input',()=>{ta.style.height='auto';ta.style.height=Math.min(ta.scrollHeight,120)+'px';});});
  initNetworkGuard();
  initAvatarPreview();
});
