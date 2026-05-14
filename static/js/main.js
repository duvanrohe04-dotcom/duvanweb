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
  const phrases=["Transformo negocios en marcas digitales poderosas","Paginas web que venden mientras duermes","Diseno que convierte visitantes en clientes","Tu negocio merece brillar en internet"];
  let pi=0,ci=0,del=false;
  function type(){
    const current=phrases[pi];
    if(!del){el.textContent=current.substring(0,ci+1);ci++;}
    else{el.textContent=current.substring(0,ci-1);ci--;}
    if(!del&&ci===current.length){del=true;setTimeout(type,2200);return;}
    if(del&&ci===0){del=false;pi=(pi+1)%phrases.length;}
    setTimeout(type,del?50:80);
  }
  setTimeout(type,800);
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
let adminPass = localStorage.getItem('dr_admin_pass') || 'DR2025admin';

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
}

// ══════════════════════════════════════
// DATA — localStorage
// ══════════════════════════════════════
function getData(key,def){try{return JSON.parse(localStorage.getItem(key))||def;}catch{return def;}}
function setData(key,val){localStorage.setItem(key,JSON.stringify(val));}

function initAdmin(){
  if(!getData('dr_clients',[]).length){
    setData('dr_clients',[
      {id:1,name:'Maria Camila Torres',biz:'Restaurante El Fogon',phone:'3001234567',service:'Profesional – Negocio Poderoso',status:'Entregado',date:'2025-02-15'},
      {id:2,name:'Juan Andres Mejia',biz:'Barberia Style',phone:'3119876543',service:'Basico – Presencia Digital',status:'En proceso',date:'2025-05-01'},
    ]);
  }
  if(!getData('dr_projects',[]).length){
    setData('dr_projects',[
      {id:1,client:'Restaurante El Fogon',type:'Restaurante',start:'2025-02-10',end:'2025-02-18',status:'Entregado',progress:100},
      {id:2,client:'Barberia Style',type:'Barberia',start:'2025-04-28',end:'2025-05-07',status:'Desarrollo',progress:60},
    ]);
  }
  if(!getData('dr_messages',[]).length){
    setData('dr_messages',[
      {id:1,name:'Carlos Hernandez',phone:'3209998877',msg:'Hola, quiero una pagina para mi ferreteria',status:'Nuevo'},
      {id:2,name:'Sandra Lopez',phone:'3155554433',msg:'Cuanto cuesta una tienda online?',status:'Contactado'},
      {id:3,name:'Roberto Diaz',phone:'3001112233',msg:'Me interesa el plan premium, tienen pago a cuotas?',status:'Nuevo'},
    ]);
  }
  if(!getData('dr_portfolio',[]).length){
    setData('dr_portfolio',[
      {id:1,title:'Restaurante El Fogon',desc:'Landing page con menu online y reservas',url:'',link:'#'},
      {id:2,title:'Barberia Style',desc:'Web de servicios con galeria y reservas',url:'',link:'#'},
    ]);
  }
  renderDashboard();
  document.getElementById('dashboard-date').textContent=new Date().toLocaleDateString('es-CO',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
  const income=localStorage.getItem('dr_income')||'0';
  document.getElementById('incomeInput').value=income;
  updateIncome(income);
}

// DASHBOARD
function renderDashboard(){
  const clients=getData('dr_clients',[]);
  const projects=getData('dr_projects',[]);
  const messages=getData('dr_messages',[]);
  const active=projects.filter(p=>p.status!=='Entregado').length;
  const newMsgs=messages.filter(m=>m.status==='Nuevo').length;
  document.getElementById('stat-active').textContent=active;
  document.getElementById('stat-clients').textContent=clients.length;
  document.getElementById('stat-messages').textContent=newMsgs;
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
function updateIncome(val){
  localStorage.setItem('dr_income',val||'0');
  const num=parseInt(val||0);
  document.getElementById('stat-income').textContent='$'+(isNaN(num)?0:num).toLocaleString('es-CO');
}

// CLIENTS
let clientFilter='',clientStatusFilter='';
function renderClients(){
  const clients=getData('dr_clients',[]);
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
function saveClient(){
  const clients=getData('dr_clients',[]);
  const editId=document.getElementById('cm-edit-id').value;
  const client={
    id:editId?+editId:Date.now(),
    name:document.getElementById('cm-name').value,
    biz:document.getElementById('cm-biz').value,
    phone:document.getElementById('cm-phone').value,
    service:document.getElementById('cm-service').value,
    status:document.getElementById('cm-status').value,
    date:document.getElementById('cm-date').value||new Date().toISOString().slice(0,10)
  };
  if(editId){const idx=clients.findIndex(c=>c.id===+editId);clients[idx]=client;}
  else clients.push(client);
  setData('dr_clients',clients);
  closeModal('client-modal');renderClients();renderDashboard();
  document.getElementById('cm-edit-id').value='';
}
function editClient(id){
  const c=getData('dr_clients',[]).find(c=>c.id===id);if(!c)return;
  document.getElementById('cm-name').value=c.name;
  document.getElementById('cm-biz').value=c.biz;
  document.getElementById('cm-phone').value=c.phone;
  document.getElementById('cm-service').value=c.service;
  document.getElementById('cm-status').value=c.status;
  document.getElementById('cm-date').value=c.date;
  document.getElementById('cm-edit-id').value=id;
  openModal('client-modal');
}
function deleteClient(id){
  if(!confirm('Eliminar este cliente?'))return;
  setData('dr_clients',getData('dr_clients',[]).filter(c=>c.id!==id));
  renderClients();renderDashboard();
}

// PROJECTS
function renderProjects(){
  const projects=getData('dr_projects',[]);
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
function saveProject(){
  const projects=getData('dr_projects',[]);
  const editId=document.getElementById('pm-edit-id').value;
  const proj={
    id:editId?+editId:Date.now(),
    client:document.getElementById('pm-client').value,
    type:document.getElementById('pm-type').value,
    start:document.getElementById('pm-start').value,
    end:document.getElementById('pm-end').value,
    status:document.getElementById('pm-status').value,
    progress:Math.min(100,Math.max(0,+document.getElementById('pm-progress').value||0))
  };
  if(editId){const idx=projects.findIndex(p=>p.id===+editId);projects[idx]=proj;}
  else projects.push(proj);
  setData('dr_projects',projects);
  closeModal('project-modal');renderProjects();renderDashboard();
  document.getElementById('pm-edit-id').value='';
}
function editProject(id){
  const p=getData('dr_projects',[]).find(p=>p.id===id);if(!p)return;
  document.getElementById('pm-client').value=p.client;
  document.getElementById('pm-type').value=p.type;
  document.getElementById('pm-start').value=p.start;
  document.getElementById('pm-end').value=p.end;
  document.getElementById('pm-status').value=p.status;
  document.getElementById('pm-progress').value=p.progress;
  document.getElementById('pm-edit-id').value=id;
  openModal('project-modal');
}
function deleteProject(id){
  if(!confirm('Eliminar este proyecto?'))return;
  setData('dr_projects',getData('dr_projects',[]).filter(p=>p.id!==id));
  renderProjects();renderDashboard();
}

// MESSAGES
function renderMessages(){
  const msgs=getData('dr_messages',[]);
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
function changeMessageStatus(id){
  const msgs=getData('dr_messages',[]);
  const m=msgs.find(m=>m.id===id);if(!m)return;
  const statuses=['Nuevo','Contactado','Cerrado'];
  m.status=statuses[(statuses.indexOf(m.status)+1)%statuses.length];
  setData('dr_messages',msgs);renderMessages();renderDashboard();
}
function deleteMessage(id){
  if(!confirm('Eliminar mensaje?'))return;
  setData('dr_messages',getData('dr_messages',[]).filter(m=>m.id!==id));
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
    '   WA: 3107480575',
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
  const items=getData('dr_portfolio',[]);
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
function savePortfolio(){
  const items=getData('dr_portfolio',[]);
  items.push({id:Date.now(),title:document.getElementById('pf-title').value,desc:document.getElementById('pf-desc').value,url:document.getElementById('pf-url').value,link:document.getElementById('pf-link').value});
  setData('dr_portfolio',items);closeModal('portfolio-modal');renderPortfolio();
}
function deletePortfolio(id){
  if(!confirm('Eliminar proyecto del portafolio?'))return;
  setData('dr_portfolio',getData('dr_portfolio',[]).filter(p=>p.id!==id));renderPortfolio();
}

// SETTINGS
function toggleSection(id){
  document.getElementById(id).classList.toggle('on');
}
function saveSettings(){
  const pass1=document.getElementById('cfg-pass1').value;
  const pass2=document.getElementById('cfg-pass2').value;
  if(pass1){
    if(pass1!==pass2){alert('Las contrasenas no coinciden');return;}
    adminPass=pass1;localStorage.setItem('dr_admin_pass',pass1);
  }
  localStorage.setItem('dr_wa',document.getElementById('cfg-wa').value);
  localStorage.setItem('dr_tagline',document.getElementById('cfg-tagline').value);
  document.getElementById('cfg-msg').style.display='block';
  document.getElementById('cfg-pass1').value='';document.getElementById('cfg-pass2').value='';
  setTimeout(()=>document.getElementById('cfg-msg').style.display='none',2500);
}

// MODALS
function openModal(id){document.getElementById(id).classList.add('open');}
function closeModal(id){document.getElementById(id).classList.remove('open');}
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('.modal-overlay').forEach(m=>m.addEventListener('click',function(e){if(e.target===this)this.classList.remove('open');}));
});

// KEYBOARD SECRET (Ctrl+Shift+A)
document.addEventListener('keydown',e=>{if(e.ctrlKey&&e.shiftKey&&e.key==='A'){showLogin();}});
