// ══════════════════════════════════════
// GLOBAL STATE & API
// ══════════════════════════════════════
let appData = {
  clients: [],
  projects: [],
  messages: [],
  portfolio: [],
  reviews: [],
  settings: {}
};

async function api(url, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(url, options);
  return res.json();
}

async function refreshData() {
  const data = await api('/api/init');
  appData = data;
  return data;
}

// ══════════════════════════════════════
// ══════════════════════════════════════
// PARTICLES CANVAS (HERO)
// ══════════════════════════════════════
(function(){
  const canvas = document.getElementById('particles-canvas');
  if(!canvas)return;
  const ctx = canvas.getContext('2d');
  let particles = [];
  function resize(){canvas.width=window.innerWidth;canvas.height=window.innerHeight;}
  resize();
  window.addEventListener('resize',resize);
  class Particle{
    constructor(){this.reset();}
    reset(){
      this.x=Math.random()*canvas.width;
      this.y=Math.random()*canvas.height;
      this.size=Math.random()*2+.5;
      this.speedX=(Math.random()-.5)*.6;
      this.speedY=-Math.random()*.8-.2;
      this.opacity=Math.random()*.7+.1;
      this.char=Math.random()>.5?(Math.random()>.5?'<':'>'):String.fromCharCode(Math.floor(Math.random()*26)+65);
      this.isChar=Math.random()>.6;
    }
    update(){
      this.x+=this.speedX;this.y+=this.speedY;
      if(this.y<-20||this.x<-20||this.x>canvas.width+20)this.reset();
    }
    draw(){
      ctx.globalAlpha=this.opacity;
      if(this.isChar){
        ctx.fillStyle='#00cfff';ctx.font=`${this.size*6}px 'Orbitron',monospace`;
        ctx.fillText(this.char,this.x,this.y);
      } else {
        ctx.fillStyle='rgba(0,207,255,0.8)';ctx.beginPath();
        ctx.arc(this.x,this.y,this.size,0,Math.PI*2);ctx.fill();
      }
    }
  }
  for(let i=0;i<90;i++)particles.push(new Particle());
  function animate(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.globalAlpha=0.03;ctx.strokeStyle='#00cfff';ctx.lineWidth=1;
    for(let x=0;x<canvas.width;x+=60){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,canvas.height);ctx.stroke();}
    for(let y=0;y<canvas.height;y+=60){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(canvas.width,y);ctx.stroke();}
    particles.forEach(p=>{p.update();p.draw();});
    requestAnimationFrame(animate);
  }
  animate();
})();

// CTA CANVAS
(function(){
  const canvas = document.getElementById('cta-canvas');
  if(!canvas)return;
  const ctx = canvas.getContext('2d');
  let drops=[];
  function resize(){canvas.width=canvas.parentElement.offsetWidth;canvas.height=canvas.parentElement.offsetHeight;}
  resize();
  window.addEventListener('resize',resize);
  for(let i=0;i<40;i++)drops.push({x:Math.random()*1400,y:Math.random()*-600,speed:Math.random()*2+.5,char:String.fromCharCode(Math.floor(Math.random()*94)+33),opacity:Math.random()*.4+.05});
  function animate(){
    ctx.fillStyle='rgba(10,10,15,0.15)';ctx.fillRect(0,0,canvas.width,canvas.height);
    drops.forEach(d=>{
      ctx.globalAlpha=d.opacity;ctx.fillStyle='#1a6fff';ctx.font='14px monospace';
      ctx.fillText(d.char,d.x,d.y);d.y+=d.speed;
      if(d.y>canvas.height+20){d.y=-20;d.x=Math.random()*canvas.width;}
    });
    requestAnimationFrame(animate);
  }
  animate();
})();

// ══════════════════════════════════════
// TYPEWRITER
// ══════════════════════════════════════
(function(){
  const el=document.getElementById('typewriter');
  if(!el)return;
  function startTypewriter(){
    const saved = appData.settings.dr_tagline || '';
    const phrases=[saved.trim()||'Tu pagina web profesional lista en solo dias','Clientes nuevos buscandote en Google 24/7','Diseno a medida para tu negocio colombiano','Dominio y hosting incluidos sin tecnicismos'];
    let pi=0,ci=0,del=false;
    function type(){
      const current=phrases[pi];
      if(!del){el.textContent=current.substring(0,ci+1);ci++;}
      else{el.textContent=current.substring(0,ci-1);ci--;}
      if(!del&&ci===current.length){del=true;setTimeout(type,2200);return;}
      if(del&&ci===0){del=false;pi=(pi+1)%phrases.length;}
      setTimeout(type,del?50:80);
    }
    type();
  }
  // Wait for data
  const check = setInterval(()=>{
    if(appData.settings.dr_tagline !== undefined){ clearInterval(check); startTypewriter(); }
  }, 100);
})();

// ══════════════════════════════════════
// COUNTERS
// ══════════════════════════════════════
function animateCounters(){
  document.querySelectorAll('.stat-num[data-target]').forEach(el=>{
    const target=+el.dataset.target;let curr=0;
    const inc=target/60;
    const timer=setInterval(()=>{curr+=inc;if(curr>=target){curr=target;clearInterval(timer);}el.textContent=Math.floor(curr)+(target>=10?'+':'');},30);
  });
}
(function(){
  let counted=false;
  const checkScroll=()=>{
    if(!counted&&window.scrollY<200){animateCounters();counted=true;}
  };
  window.addEventListener('scroll',checkScroll);
  checkScroll();
})();

// ══════════════════════════════════════
// NAVBAR
// ══════════════════════════════════════
window.addEventListener('scroll',()=>{
  const navbar=document.getElementById('navbar');
  if(navbar)navbar.classList.toggle('scrolled',window.scrollY>50);
});

function toggleMobile(){
  const menu=document.getElementById('mobileMenu');
  if(menu)menu.classList.toggle('open');
}

// ══════════════════════════════════════
// SCROLL ANIMATIONS
// ══════════════════════════════════════
(function(){
  if(!window.IntersectionObserver)return;
  const observer=new IntersectionObserver(entries=>{
    entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible');});
  },{threshold:.12});
  document.querySelectorAll('.fade-in-up').forEach(el=>observer.observe(el));
})();

// ══════════════════════════════════════
// FAQ
// ══════════════════════════════════════
function toggleFaq(btn){
  const item=btn.parentElement;
  document.querySelectorAll('.faq-item').forEach(i=>{if(i!==item)i.classList.remove('open');});
  item.classList.toggle('open');
}

// ══════════════════════════════════════
// ADMIN AUTH
// ══════════════════════════════════════
function showLogin(){
  document.getElementById('login-screen').classList.add('active');
}
function hideLogin(){
  document.getElementById('login-screen').classList.remove('active');
  document.getElementById('loginErr').style.display='none';
}
function doLogin(){
  const u=document.getElementById('loginUser').value.trim();
  const p=document.getElementById('loginPass').value.trim();
  const adminPass = appData.settings.dr_admin_pass || 'DR2026admin';
  if(u==='duvan'&&p===adminPass){
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('admin-panel').classList.add('active');
    document.getElementById('public-page').style.display='none';
    document.getElementById('navbar').style.display='none';
    initAdmin();
  } else {
    document.getElementById('loginErr').style.display='block';
  }
}
document.addEventListener('DOMContentLoaded',()=>{
  const lp=document.getElementById('loginPass');
  if(lp)lp.addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
});
function doLogout(){
  document.getElementById('admin-panel').classList.remove('active');
  document.getElementById('public-page').style.display='block';
  document.getElementById('navbar').style.display='flex';
  applyWhatsAppPhone();
  applySocialAndFooter();
  renderPublicTestimonials();
}

// ══════════════════════════════════════
// ADMIN NAV
// ══════════════════════════════════════
function showAdminSection(name,el){
  document.querySelectorAll('.admin-section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.admin-nav-item').forEach(i=>i.classList.remove('active'));
  document.getElementById('section-'+name).classList.add('active');
  el.classList.add('active');
  renderSection(name);
}
function renderSection(name){
  if(name==='clients')renderClients();
  if(name==='projects')renderProjects();
  if(name==='messages')renderMessages();
  if(name==='portfolio')renderPortfolio();
  if(name==='dashboard')renderDashboard();
  if(name==='visitors')renderVisitors();
  if(name==='reviews')renderReviewsAdmin();
}

// ══════════════════════════════════════
// PUBLIC RENDERING
// ══════════════════════════════════════

function renderPublicTestimonials(){
  const grid=document.getElementById('testimonials-grid');
  if(!grid)return;
  const esc=s=>String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  const reviews=appData.reviews;
  if(!reviews.length){
    grid.innerHTML='<p style="text-align:center;color:var(--text-secondary);grid-column:1/-1;padding:32px 16px;">Pronto publicaremos nuevas reseñas de clientes.</p>';
    return;
  }
  const starRow=n=>{const s=Math.min(5,Math.max(1,+n||5));return'★'.repeat(s);};
  grid.innerHTML=reviews.map(r=>{
    const ini=esc((r.initials||'CL').slice(0,3));
    const s=Math.min(5,Math.max(1,+r.stars||5));
    return'<div class="testi-card fade-in-up visible">'+
      '<div class="testi-avatar">'+ini+'</div>'+
      '<div class="testi-stars">'+starRow(s)+'</div>'+
      '<p class="testi-text">"'+esc(r.text)+'"</p>'+
      '<div class="testi-name">'+esc(r.name)+'</div>'+
      '<div class="testi-biz">'+esc(r.biz)+'</div>'+
    '</div>';
  }).join('');
}

function applyWhatsAppPhone(){
  const phone=(appData.settings.dr_wa || '3107480575').replace(/\D/g,'');
  document.querySelectorAll('a[href*="wa.me"]').forEach(a=>{
    try{
      const u=new URL(a.href);
      if(u.hostname!=='wa.me')return;
      const path='/57'+phone;
      a.href='https://wa.me'+path+u.search+u.hash;
    }catch(e){a.href='https://wa.me/57'+phone;}
  });
  const fp=document.getElementById('footer-phone-display');
  if(fp)fp.textContent=phone.length>=10?phone.replace(/(\d{3})(\d{3})(\d+)/,'$1 $2 $3'):phone;
}

function applySocialAndFooter(){
  function normalizeInstagramUrl(raw){
    const t=(raw||'').trim();
    if(!t)return'';
    if(/^https?:\/\//i.test(t))return t;
    const u=t.replace(/^@/,'').replace(/^\//,'').replace(/^instagram\.com\/?/i,'');
    if(!u)return'';
    return'https://www.instagram.com/'+u.trim();
  }
  function normalizeTikTokUrl(raw){
    const t=(raw||'').trim();
    if(!t)return'';
    if(/^https?:\/\//i.test(t))return t;
    let u=t.replace(/^@/,'').replace(/^\//,'');
    if(/^tiktok\.com\//i.test(u))return'https://www.'+u;
    u=u.replace(/^@/,'');
    return'https://www.tiktok.com/@'+u;
  }
  const ig=normalizeInstagramUrl(appData.settings.dr_social_ig || '');
  const tt=normalizeTikTokUrl(appData.settings.dr_social_tt || '');
  const aig=document.getElementById('footer-social-ig');
  const att=document.getElementById('footer-social-tt');
  if(aig){aig.href=ig||'#';aig.setAttribute('rel','noopener noreferrer');if(ig)aig.removeAttribute('aria-disabled');else aig.setAttribute('aria-disabled','true');}
  if(att){att.href=tt||'#';if(tt)att.removeAttribute('aria-disabled');else att.setAttribute('aria-disabled','true');}
  const def1='Tu página web lista en días: dominio y hosting incluidos, diseño profesional adaptado a tu negocio, y una tienda o catálogo digital abierto 24/7 para que tus clientes te encuentren desde cualquier lugar. Sin complicaciones técnicas y con soporte directo por WhatsApp cuando lo necesites.';
  const def2='Página web lista en 3–10 días · Dominio y hosting incluidos · Soporte por WhatsApp · Sin conocimiento técnico necesario';
  const p1=appData.settings.dr_footer_1;
  const p2=appData.settings.dr_footer_2;
  const el1=document.getElementById('footer-brand-text');
  const el2=document.getElementById('footer-tagline');
  if(el1)el1.textContent=(p1!==null&&p1!==undefined&&p1!=='')?p1:def1;
  if(el2)el2.textContent=(p2!==null&&p2!==undefined&&p2!=='')?p2:def2;
}

function initServiceCardFlip(){
  document.querySelectorAll('.service-card').forEach(card=>{
    card.setAttribute('role','button');
    card.setAttribute('tabindex','0');
    card.setAttribute('aria-expanded','false');
    function doFlip(el){
      const isFlipped = el.classList.toggle('is-flipped');
      el.setAttribute('aria-expanded', isFlipped ? 'true' : 'false');
    }
    card.addEventListener('click',function(e){
      if(e.target.closest('a'))return;
      doFlip(this);
    });
    card.addEventListener('keydown',function(e){
      if((e.key==='Enter'||e.key===' ')&&!e.target.closest('a')){
        e.preventDefault();
        doFlip(this);
      }
    });
  });
}

// ══════════════════════════════════════
// ADMIN LOGIC
// ══════════════════════════════════════

function initAdmin(){
  renderDashboard();
  document.getElementById('dashboard-date').textContent=new Date().toLocaleDateString('es-CO',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
  const income=appData.settings.dr_income || '0';
  document.getElementById('incomeInput').value=income;
  updateIncome(income, false); // false to not save back to server immediately
  loadAdminSettingsForm();
}

function loadAdminSettingsForm(){
  const w=document.getElementById('cfg-wa');if(!w)return;
  w.value=appData.settings.dr_wa || '3107480575';
  document.getElementById('cfg-tagline').value=appData.settings.dr_tagline || 'Tu pagina web profesional lista en solo dias';
  const ig=document.getElementById('cfg-ig');
  if(ig)ig.value=appData.settings.dr_social_ig || '';
  const tt=document.getElementById('cfg-tt');
  if(tt)tt.value=appData.settings.dr_social_tt || '';
  const f1=document.getElementById('cfg-footer-1');
  if(f1)f1.value=appData.settings.dr_footer_1 || '';
  const f2=document.getElementById('cfg-footer-2');
  if(f2)f2.value=appData.settings.dr_footer_2 || '';
}

// DASHBOARD
function renderDashboard(){
  const clients=appData.clients;
  const projects=appData.projects;
  const messages=appData.messages;
  const active=projects.filter(p=>p.status!=='Entregado').length;
  const todayVisits=appData.stats ? appData.stats.today_visits : 0;
  document.getElementById('stat-active').textContent=active;
  document.getElementById('stat-clients').textContent=clients.length;
  document.getElementById('stat-visits').textContent=todayVisits;
  const el=document.getElementById('dashboard-projects-list');
  el.innerHTML=projects.slice(-4).reverse().map(p=>`
    <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05);">
      <div>
        <div style="font-weight:600;color:var(--text-primary);">${p.client}</div>
        <div style="color:var(--text-secondary);font-size:.85rem;">${p.type} — ${p.status}</div>
      </div>
      <div style="width:120px;">
        <div style="color:var(--accent-cyan);font-size:.8rem;margin-bottom:4px;text-align:right;">${p.progress}%</div>
        <div class="progress-bar"><div class="progress-fill" style="width:${p.progress}%"></div></div>
      </div>
    </div>`).join('');
}

// VISITORS
function renderVisitors(){
  const stats = appData.stats || { total_visits: 0, today_visits: 0 };
  document.getElementById('vis-total').textContent = stats.total_visits;
  document.getElementById('vis-today').textContent = stats.today_visits;
}

async function resetVisits(){
  if(!confirm('¿Estás seguro de que deseas reiniciar todas las estadísticas de visitas? Esta acción no se puede deshacer.')) return;
  const res = await api('/api/visits', 'DELETE');
  if(res.success){
    await refreshData();
    renderVisitors();
    if(document.getElementById('section-dashboard').classList.contains('active')) renderDashboard();
  } else {
    alert('Error al reiniciar visitas: ' + (res.error || 'Error desconocido'));
  }
}

async function updateIncome(val, save = true){
  const num=parseInt(val||0);
  document.getElementById('stat-income').textContent='$'+(isNaN(num)?0:num).toLocaleString('es-CO');
  if(save) {
    await api('/api/settings', 'POST', { dr_income: val });
    appData.settings.dr_income = val;
  }
}

// CLIENTS
let clientFilter='',clientStatusFilter='';
function renderClients(){
  const clients=appData.clients;
  const filtered=clients.filter(c=>{
    const matchText=(c.name+c.biz+c.phone+c.service).toLowerCase().includes(clientFilter.toLowerCase());
    const matchStatus=!clientStatusFilter||c.status===clientStatusFilter;
    return matchText&&matchStatus;
  });
  document.getElementById('clients-tbody').innerHTML=filtered.map(c=>`
    <tr>
      <td style="font-weight:600;">${c.name}</td>
      <td style="color:var(--text-secondary);">${c.biz}</td>
      <td><a href="https://wa.me/57${c.phone}" target="_blank" style="color:var(--success);">${c.phone}</a></td>
      <td style="color:var(--text-secondary);font-size:.85rem;">${c.service}</td>
      <td><span class="badge ${c.status==='Entregado'?'badge-done':c.status==='En proceso'?'badge-process':'badge-pending'}">${c.status}</span></td>
      <td style="color:var(--text-secondary);">${c.date}</td>
      <td style="display:flex;gap:6px;">
        <button class="btn-sm" onclick="editClient(${c.id})" style="padding:6px 12px;font-size:.8rem;">Editar</button>
        <button class="btn-sm btn-danger" onclick="deleteClient(${c.id})" style="padding:6px 12px;font-size:.8rem;">Eliminar</button>
      </td>
    </tr>`).join('')||'<tr><td colspan="7" style="text-align:center;color:var(--text-secondary);padding:32px;">Sin clientes</td></tr>';
}
function filterClients(v){clientFilter=v;renderClients();}
function filterClientsByStatus(v){clientStatusFilter=v;renderClients();}

async function saveClient(){
  const editId=document.getElementById('cm-edit-id').value;
  const client={
    name:document.getElementById('cm-name').value,
    biz:document.getElementById('cm-biz').value,
    phone:document.getElementById('cm-phone').value,
    service:document.getElementById('cm-service').value,
    status:document.getElementById('cm-status').value,
    date:document.getElementById('cm-date').value||new Date().toISOString().slice(0,10)
  };
  if(editId) client.id = +editId;
  
  await api('/api/clients', 'POST', client);
  await refreshData();
  closeModal('client-modal');renderClients();renderDashboard();
  document.getElementById('cm-edit-id').value='';
}
function editClient(id){
  const c=appData.clients.find(c=>c.id===id);if(!c)return;
  document.getElementById('cm-name').value=c.name;
  document.getElementById('cm-biz').value=c.biz;
  document.getElementById('cm-phone').value=c.phone;
  document.getElementById('cm-service').value=c.service;
  document.getElementById('cm-status').value=c.status;
  document.getElementById('cm-date').value=c.date;
  document.getElementById('cm-edit-id').value=id;
  openModal('client-modal');
}
async function deleteClient(id){
  if(!confirm('Eliminar este cliente?'))return;
  await api(`/api/clients/${id}`, 'DELETE');
  await refreshData();
  renderClients();renderDashboard();
}

// PROJECTS
function renderProjects(){
  const projects=appData.projects;
  const statusColors={Diseno:['var(--accent-blue)',25],Desarrollo:['var(--warning)',55],Revision:['var(--accent-cyan)',80],Entregado:['var(--success)',100]};
  document.getElementById('projects-grid').innerHTML=projects.map(p=>{
    const[color]=statusColors[p.status]||['var(--text-secondary)',0];
    return`<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px;transition:.3s;" onmouseover="this.style.borderColor='rgba(0,207,255,.3)'" onmouseout="this.style.borderColor='var(--border)'">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
        <div>
          <div style="font-family:'Orbitron',sans-serif;font-size:.95rem;font-weight:700;color:var(--text-primary);">${p.client}</div>
          <div style="color:var(--text-secondary);font-size:.8rem;">${p.type}</div>
        </div>
        <span class="badge" style="background:rgba(0,0,0,.3);color:${color};border:1px solid ${color};">${p.status}</span>
      </div>
      <div style="color:var(--text-secondary);font-size:.8rem;margin-bottom:4px;">📅 ${p.start} → ${p.end}</div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;margin-top:12px;">
        <span style="color:var(--text-secondary);font-size:.8rem;">Progreso</span>
        <span style="color:${color};font-size:.85rem;font-weight:700;">${p.progress}%</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:${p.progress}%;background:${color};"></div></div>
      <div style="display:flex;gap:8px;margin-top:14px;">
        <button class="btn-sm" onclick="editProject(${p.id})" style="padding:6px 12px;font-size:.8rem;">Editar</button>
        <button class="btn-sm btn-danger" onclick="deleteProject(${p.id})" style="padding:6px 12px;font-size:.8rem;">Eliminar</button>
      </div>
    </div>`;
  }).join('')||'<div style="color:var(--text-secondary);grid-column:1/-1;text-align:center;padding:40px;">Sin proyectos aun</div>';
}
async function saveProject(){
  const editId=document.getElementById('pm-edit-id').value;
  const proj={
    client:document.getElementById('pm-client').value,
    type:document.getElementById('pm-type').value,
    start:document.getElementById('pm-start').value,
    end:document.getElementById('pm-end').value,
    status:document.getElementById('pm-status').value,
    progress:Math.min(100,Math.max(0,+document.getElementById('pm-progress').value||0))
  };
  if(editId) proj.id = +editId;
  
  await api('/api/projects', 'POST', proj);
  await refreshData();
  closeModal('project-modal');renderProjects();renderDashboard();
  document.getElementById('pm-edit-id').value='';
}
function editProject(id){
  const p=appData.projects.find(p=>p.id===id);if(!p)return;
  document.getElementById('pm-client').value=p.client;
  document.getElementById('pm-type').value=p.type;
  document.getElementById('pm-start').value=p.start;
  document.getElementById('pm-end').value=p.end;
  document.getElementById('pm-status').value=p.status;
  document.getElementById('pm-progress').value=p.progress;
  document.getElementById('pm-edit-id').value=id;
  openModal('project-modal');
}
async function deleteProject(id){
  if(!confirm('Eliminar este proyecto?'))return;
  await api(`/api/projects/${id}`, 'DELETE');
  await refreshData();
  renderProjects();renderDashboard();
}

// MESSAGES
function renderMessages(){
  const msgs=appData.messages;
  document.getElementById('messages-tbody').innerHTML=msgs.map(m=>`
    <tr>
      <td style="font-weight:600;">${m.name}</td>
      <td><a href="https://wa.me/57${m.phone}" target="_blank" style="color:var(--success);">${m.phone}</a></td>
      <td style="color:var(--text-secondary);max-width:240px;font-size:.9rem;">${m.msg}</td>
      <td><span class="badge ${m.status==='Nuevo'?'badge-new':m.status==='Contactado'?'badge-process':'badge-done'}">${m.status}</span></td>
      <td style="display:flex;gap:6px;flex-wrap:wrap;">
        <a href="https://wa.me/57${m.phone}?text=Hola%20${encodeURIComponent(m.name)}%2C%20te%20contacto%20de%20parte%20de%20Duvan%20Rodriguez%20Diseno%20Web%20🌐" target="_blank" class="btn-sm btn-success" style="padding:6px 10px;font-size:.8rem;text-decoration:none;">WA</a>
        <button class="btn-sm" onclick="changeMessageStatus(${m.id})" style="padding:6px 10px;font-size:.8rem;">Estado</button>
        <button class="btn-sm btn-danger" onclick="deleteMessage(${m.id})" style="padding:6px 10px;font-size:.8rem;">✕</button>
      </td>
    </tr>`).join('')||'<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:32px;">Sin mensajes</td></tr>';
}
async function changeMessageStatus(id){
  const m=appData.messages.find(m=>m.id===id);if(!m)return;
  const statuses=['Nuevo','Contactado','Cerrado'];
  m.status=statuses[(statuses.indexOf(m.status)+1)%statuses.length];
  await api('/api/messages', 'POST', m);
  await refreshData();
  renderMessages();renderDashboard();
}
async function deleteMessage(id){
  if(!confirm('Eliminar mensaje?'))return;
  await api(`/api/messages/${id}`, 'DELETE');
  await refreshData();
  renderMessages();
}

// QUOTES
function generateQuote(){
  const name=document.getElementById('q-name').value;
  const biz=document.getElementById('q-business').value;
  const plan=document.getElementById('q-plan').value;
  const extras=document.getElementById('q-extras').value;
  const price=document.getElementById('q-price').value;
  const phone=document.getElementById('q-phone').value;
  if(!name){alert('Ingresa el nombre del cliente');return;}
  const date=new Date().toLocaleDateString('es-CO');
  const text=[
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '🌐 COTIZACION PROFESIONAL',
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '📋 Cliente: '+name,
    '🏢 Negocio: '+(biz||'—'),
    '📱 WhatsApp: '+(phone||'—'),
    '📅 Fecha: '+date,
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '💼 PLAN SELECCIONADO:',
    '   '+plan,
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '➕ ADICIONALES:',
    '   '+(extras||'Sin adicionales'),
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '💰 INVERSION TOTAL:',
    '   $'+(price?parseInt(price).toLocaleString('es-CO'):' Por definir')+' COP',
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '✅ Incluye:',
    '• Diseno personalizado',
    '• Responsive (movil + desktop)',
    '• Soporte post-entrega',
    '• Asesoria incluida',
    '━━━━━━━━━━━━━━━━━━━━━━━━',
    '📲 Duvan Rodriguez',
    '   Creador de Paginas Web',
    '   WA: '+(appData.settings.dr_wa || '3107480575'),
    '━━━━━━━━━━━━━━━━━━━━━━━━'
  ].join('\n');
  const out=document.getElementById('quote-output');
  out.textContent=text;out.style.display='block';
  document.getElementById('quote-actions').style.display='flex';
}
function copyQuote(){
  navigator.clipboard.writeText(document.getElementById('quote-output').textContent).then(()=>alert('Cotizacion copiada al portapapeles'));
}
function shareQuoteWA(){
  const text=encodeURIComponent(document.getElementById('quote-output').textContent);
  const phone=document.getElementById('q-phone').value;
  window.open('https://wa.me/57'+phone+'?text='+text,'_blank');
}

// PORTFOLIO
function renderPortfolio(){
  const items=appData.portfolio;
  document.getElementById('portfolio-grid').innerHTML=items.map(p=>`
    <div class="portfolio-card">
      <div class="portfolio-img">${p.url?'<img src="'+p.url+'" onerror="this.parentElement.textContent=\'🖼️ Sin imagen\'">':' 🖼️ Sin imagen'}</div>
      <div class="portfolio-info">
        <h4>${p.title}</h4>
        <p>${p.desc}</p>
        ${p.link&&p.link!='#'?'<a href="'+p.link+'" target="_blank" style="color:var(--accent-cyan);font-size:.8rem;margin-top:6px;display:block;">Ver sitio →</a>':''}
        <div style="display:flex;gap:8px;margin-top:10px;">
          <button class="btn-sm btn-danger" onclick="deletePortfolio(${p.id})" style="padding:4px 10px;font-size:.75rem;">Eliminar</button>
        </div>
      </div>
    </div>`).join('')||'<div style="color:var(--text-secondary);padding:40px;grid-column:1/-1;text-align:center;">Sin proyectos en el portafolio</div>';
}
async function savePortfolio(){
  const item = {title:document.getElementById('pf-title').value,desc:document.getElementById('pf-desc').value,url:document.getElementById('pf-url').value,link:document.getElementById('pf-link').value};
  await api('/api/portfolio', 'POST', item);
  await refreshData();
  closeModal('portfolio-modal');renderPortfolio();
}
async function deletePortfolio(id){
  if(!confirm('Eliminar proyecto del portafolio?'))return;
  await api(`/api/portfolio/${id}`, 'DELETE');
  await refreshData();
  renderPortfolio();
}

// RESEÑAS (página pública + admin)
function renderReviewsAdmin(){
  const tb=document.getElementById('reviews-tbody');
  if(!tb)return;
  const esc=s=>String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const reviews=appData.reviews;
  tb.innerHTML=reviews.map(r=>`
    <tr>
      <td style="font-weight:600;">${esc(r.name)}</td>
      <td style="color:var(--text-secondary);font-size:.85rem;max-width:200px;">${esc(r.biz)}</td>
      <td style="color:var(--text-secondary);font-size:.85rem;max-width:280px;">${esc((r.text||'').slice(0,120))}${(r.text||'').length>120?'…':''}</td>
      <td>${+r.stars||5}★</td>
      <td><button class="btn-sm btn-danger" onclick="deletePublicReview(${r.id})" style="padding:6px 12px;font-size:.8rem;">Eliminar de la web</button></td>
    </tr>`).join('')||'<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:32px;">No hay reseñas. Agrega una con el botón superior.</td></tr>';
}
async function deletePublicReview(id){
  if(!confirm('Esta reseña dejará de mostrarse en la página pública. ¿Continuar?'))return;
  await api(`/api/reviews/${id}`, 'DELETE');
  await refreshData();
  renderReviewsAdmin();
  renderPublicTestimonials();
}
async function savePublicReview(){
  const name=document.getElementById('rv-name').value.trim();
  const text=document.getElementById('rv-text').value.trim();
  if(!name||!text){alert('Nombre y texto de la reseña son obligatorios');return;}
  const review = {
    initials:(document.getElementById('rv-ini').value.trim()||name.split(/\s+/).map(w=>w[0]).join('').slice(0,3)).toUpperCase(),
    stars:Math.min(5,Math.max(1,+document.getElementById('rv-stars').value||5)),
    name,
    biz:document.getElementById('rv-biz').value.trim(),
    text
  };
  await api('/api/reviews', 'POST', review);
  await refreshData();
  closeModal('review-modal');
  document.getElementById('rv-name').value='';
  document.getElementById('rv-biz').value='';
  document.getElementById('rv-ini').value='';
  document.getElementById('rv-text').value='';
  document.getElementById('rv-stars').value='5';
  renderReviewsAdmin();
  renderPublicTestimonials();
}

async function submitPublicReview(){
  const name = document.getElementById('pub-rv-name').value.trim();
  const biz = document.getElementById('pub-rv-biz').value.trim();
  const text = document.getElementById('pub-rv-text').value.trim();
  const stars = document.getElementById('pub-rv-stars').value;
  const msgEl = document.getElementById('pub-rv-msg');

  if(!name || !text){
    msgEl.textContent = 'Por favor ingresa tu nombre y comentario.';
    msgEl.style.color = 'var(--danger)';
    msgEl.style.display = 'block';
    return;
  }

  const newReview = {
    initials: name.split(/\s+/).map(w=>w[0]).join('').slice(0,3).toUpperCase() || 'CL',
    stars: parseInt(stars),
    name: name,
    biz: biz || 'Cliente Satisfecho',
    text: text
  };

  await api('/api/reviews', 'POST', newReview);
  await refreshData();

  msgEl.textContent = '¡Gracias! Tu reseña ha sido enviada con éxito.';
  msgEl.style.color = 'var(--success)';
  msgEl.style.display = 'block';

  document.getElementById('pub-rv-name').value = '';
  document.getElementById('pub-rv-biz').value = '';
  document.getElementById('pub-rv-text').value = '';

  renderPublicTestimonials();
}

// SETTINGS
function toggleSection(id){
  document.getElementById(id).classList.toggle('on');
}
async function saveSettings(){
  const settingsUpdate = {};
  const pass1=document.getElementById('cfg-pass1').value;
  const pass2=document.getElementById('cfg-pass2').value;
  if(pass1){
    if(pass1!==pass2){alert('Las contrasenas no coinciden');return;}
    settingsUpdate.dr_admin_pass = pass1;
  }
  settingsUpdate.dr_wa = document.getElementById('cfg-wa').value.replace(/\D/g,'');
  settingsUpdate.dr_tagline = document.getElementById('cfg-tagline').value;
  
  const cig=document.getElementById('cfg-ig');
  const ctt=document.getElementById('cfg-tt');
  function normIg(v){
    const t=(v||'').trim();if(!t)return'';
    if(/^https?:\/\//i.test(t))return t;
    const u=t.replace(/^@/,'').replace(/^\//,'').replace(/^instagram\.com\/?/i,'');
    return u?'https://www.instagram.com/'+u:'';
  }
  function normTt(v){
    const t=(v||'').trim();if(!t)return'';
    if(/^https?:\/\//i.test(t))return t;
    let u=t.replace(/^@/,'').replace(/^\//,'');
    if(/^tiktok\.com\//i.test(u))return'https://www.'+u;
    u=u.replace(/^@/,'');
    return'https://www.tiktok.com/@'+u;
  }
  if(cig) settingsUpdate.dr_social_ig = normIg(cig.value);
  if(ctt) settingsUpdate.dr_social_tt = normTt(ctt.value);
  
  const cf1=document.getElementById('cfg-footer-1');
  const cf2=document.getElementById('cfg-footer-2');
  if(cf1) settingsUpdate.dr_footer_1 = cf1.value;
  if(cf2) settingsUpdate.dr_footer_2 = cf2.value;
  
  await api('/api/settings', 'POST', settingsUpdate);
  await refreshData();
  
  document.getElementById('cfg-msg').style.display='block';
  document.getElementById('cfg-pass1').value='';document.getElementById('cfg-pass2').value='';
  setTimeout(()=>document.getElementById('cfg-msg').style.display='none',2500);
  applyWhatsAppPhone();
  applySocialAndFooter();
  loadAdminSettingsForm();
}

// MODALS
function openModal(id){document.getElementById(id).classList.add('open');}
function closeModal(id){document.getElementById(id).classList.remove('open');}

document.addEventListener('DOMContentLoaded', async ()=>{
  document.querySelectorAll('.modal-overlay').forEach(m=>m.addEventListener('click',function(e){if(e.target===this)this.classList.remove('open');}));
  
  // INITIAL DATA FETCH
  await refreshData();
  
  initServiceCardFlip();
  renderPublicTestimonials();
  applyWhatsAppPhone();
  applySocialAndFooter();
});

// KEYBOARD SECRET (Ctrl+Shift+A)
document.addEventListener('keydown',e=>{if(e.ctrlKey&&e.shiftKey&&e.key==='A'){showLogin();}});
