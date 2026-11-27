/* Offline navigation, source excerpts and two step-by-step teaching labs. */
(function () {
"use strict";
const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=(x,d=6)=>Number(x).toLocaleString("en-US",{minimumFractionDigits:0,maximumFractionDigits:d,useGrouping:false});
const M=window.GuideMath, S=window.GUIDE_SOURCES;

// Render exact source, keeping line numbers outside the copy payload.
function highlight(line) {
  const re=/(#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:def|return|for|in|if|else|while|break|import|from|as|with|True|False|None|lambda)\b|\b\d+(?:\.\d+)?\b)/g;
  let html="",last=0;
  for(const match of line.matchAll(re)){
    html+=esc(line.slice(last,match.index));
    const t=match[0],cl=t[0]==="#"?"tok-comment":/^["']/.test(t)?"tok-string":/^\d/.test(t)?"tok-number":"tok-key";
    html+='<span class="'+cl+'">'+esc(t)+'</span>';last=match.index+t.length;
  }
  return html+esc(line.slice(last));
}
function numbered(code,start=1){
  return '<pre class="source-pre" tabindex="0" aria-label="Mã Python; cuộn ngang nếu dòng dài"><code>'+
    code.split("\n").map((l,i)=>'<span class="code-line"><span class="line-num" aria-hidden="true">'+(start+i)+'</span>'+highlight(l)+'</span>').join("")+'</code></pre>';
}
async function copyCode(code,status) {
  try {
    if(navigator.clipboard&&window.isSecureContext) await navigator.clipboard.writeText(code);
    else{
      const t=document.createElement("textarea");t.value=code;t.style.position="fixed";t.style.left="-10000px";document.body.append(t);t.select();
      const ok=document.execCommand("copy");t.remove();if(!ok)throw new Error("Clipboard unavailable");
    }
    status.textContent="Đã sao chép nội dung, không kèm số dòng.";
  }catch{status.textContent="Trình duyệt không cho sao chép tự động. Bạn có thể chọn và sao chép code trực tiếp.";}
}
// Commands are documentation: copy them for a terminal, never execute them here.
$$("pre.command").forEach((pre,i)=>{
  const block=document.createElement("div");block.className="command-block";
  pre.before(block);
  const toolbar=document.createElement("div");toolbar.className="command-tools";
  const label=document.createElement("span");label.textContent="Lệnh PowerShell";
  const button=document.createElement("button");button.type="button";button.textContent="Sao chép lệnh";
  const status=document.createElement("p");status.className="copy-status";status.id="command-copy-"+i;status.setAttribute("role","status");
  button.setAttribute("aria-describedby",status.id);
  toolbar.append(label,button);block.append(toolbar,pre,status);
  button.addEventListener("click",()=>copyCode(pre.textContent,status));
});
$$("[data-snippet]").forEach(host=>{
  const key=host.dataset.snippet, sn=S.snippets[key];
  if(!sn){host.textContent="Không tìm thấy trích đoạn. Chạy tools/sync_sources.py.";return;}
  host.className="snippet";
  const f=S.files[sn.file];
  host.innerHTML='<div class="code-heading"><div>Trích code gốc<strong>'+esc(f.name)+'</strong>Dòng '+sn.start+'–'+sn.end+'</div><div class="code-actions"><button class="copy-code" type="button">Sao chép</button><button class="open-source" type="button">Xem cả tệp</button></div></div>'+numbered(sn.code,sn.start)+'<p class="copy-status" role="status"></p>';
  host.querySelector(".copy-code").addEventListener("click",()=>copyCode(sn.code,host.querySelector(".copy-status")));
  host.querySelector(".open-source").addEventListener("click",()=>{
    $("#source-select").value=sn.file;renderSource();$("#full-source").open=true;
    location.hash="sources";$("#source-select").focus({preventScroll:true});
  });
});
Object.entries(S.files).forEach(([key,f])=>$("#source-select").add(new Option(f.name,key)));
function renderSource(){
  const f=S.files[$("#source-select").value];
  $("#source-code").innerHTML=numbered(f.text.trimEnd());
  $("#source-meta").textContent=f.name+" · "+f.lines+" dòng · Đồng bộ "+S.synced+" · SHA-256: "+f.sha256;
}
$("#source-select").addEventListener("change",renderSource);renderSource();
$("#download-source").addEventListener("click",()=>{
  const f=S.files[$("#source-select").value],url=URL.createObjectURL(new Blob([f.text],{type:"text/x-python;charset=utf-8"}));
  const a=document.createElement("a");a.href=url;a.download=f.name;document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),2000);
});

// Navigation: search only filters the table of contents, never hides lessons.
const norm=s=>s.normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/đ/g,"d").replace(/Đ/g,"D").toLowerCase();
$("#nav-search").addEventListener("input",e=>{
  const q=norm(e.target.value.trim());let found=0;
  $$("nav a").forEach(a=>{a.hidden=!norm(a.textContent).includes(q);if(!a.hidden)found++;});
  $("#nav-empty").hidden=found>0;
});
$("#menu-toggle").addEventListener("click",()=>{
  const open=$("#sidebar").classList.toggle("open");$("#menu-toggle").setAttribute("aria-expanded",String(open));
});
$$("nav a, .brand").forEach(a=>a.addEventListener("click",()=>{
  $("#sidebar").classList.remove("open");$("#menu-toggle").setAttribute("aria-expanded","false");
}));
document.addEventListener("keydown",e=>{if(e.key==="Escape"){$("#sidebar").classList.remove("open");$("#menu-toggle").setAttribute("aria-expanded","false");}});
let ticking=false;
function currentSection(){
  let current="start";for(const s of $$("main>section")){if(s.getBoundingClientRect().top<150)current=s.id;}
  $$("nav a").forEach(a=>{if(a.hash==="#"+current)a.setAttribute("aria-current","location");else a.removeAttribute("aria-current");});ticking=false;
}
window.addEventListener("scroll",()=>{if(!ticking){requestAnimationFrame(currentSection);ticking=true;}},{passive:true});currentSection();

// Explicitly self-marked reading progress, stored only in this browser.
const validMarks=new Set($$(".mark-read").map(b=>b.dataset.mark));
$$(".mark-read").forEach(b=>{if(!b.dataset.readLabel)b.dataset.readLabel=b.textContent;});
let completed=[];
try{const v=JSON.parse(localStorage.getItem("first-order-guide-read")||"[]");if(Array.isArray(v))completed=[...new Set(v.map(String).filter(x=>validMarks.has(x)))];}catch{}
function progress(){
  $$(".mark-read").forEach(b=>{const done=completed.includes(b.dataset.mark);b.classList.toggle("done",done);b.setAttribute("aria-pressed",String(done));b.textContent=done?"Đã đánh dấu hiểu · Bấm để bỏ đánh dấu":b.dataset.readLabel;});
  $("#read-progress").max=validMarks.size;
  $("#read-progress").value=completed.length;$("#read-count").textContent=completed.length+" / "+validMarks.size+" mục";
}
$$(".mark-read").forEach(b=>b.addEventListener("click",()=>{const id=b.dataset.mark;completed=completed.includes(id)?completed.filter(x=>x!==id):[...completed,id];try{localStorage.setItem("first-order-guide-read",JSON.stringify(completed));}catch{}progress();}));progress();
let detailsBefore=[];
window.addEventListener("beforeprint",()=>{detailsBefore=$$("details").map(d=>[d,d.open]);$$("details:not(#full-source)").forEach(d=>d.open=true);});
window.addEventListener("afterprint",()=>detailsBefore.forEach(([d,open])=>d.open=open));
$("#print-guide").addEventListener("click",async()=>{
  // Decode lazy figures before invoking the print dialog so PDF includes them.
  await Promise.all($$("img").map(async img=>{img.loading="eager";try{await img.decode();}catch{}}));
  window.print();
});

// SVG helper: labeled axes and a fixed viewBox, no external chart library.
function chartBase(title,xmin,xmax,ymin,ymax,xlabel,ylabel){
  const W=520,H=300,L=60,R=22,T=40,B=48;
  const X=v=>L+(v-xmin)/(xmax-xmin)*(W-L-R),Y=v=>H-B-(v-ymin)/(ymax-ymin)*(H-T-B);
  let svg='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(title)+'"><title>'+esc(title)+'</title><text x="'+L+'" y="18" font-weight="600">'+esc(title)+'</text>';
  for(let i=0;i<=4;i++){
    const xv=xmin+(xmax-xmin)*i/4,yv=ymin+(ymax-ymin)*i/4;
    svg+='<line x1="'+L+'" y1="'+Y(yv)+'" x2="'+(W-R)+'" y2="'+Y(yv)+'" stroke="#dce5eb"/><text x="'+(L-8)+'" y="'+(Y(yv)+4)+'" text-anchor="end">'+esc(fmt(yv,2))+'</text>';
    svg+='<text x="'+X(xv)+'" y="'+(H-B+20)+'" text-anchor="middle">'+esc(fmt(xv,2))+'</text>';
  }
  svg+='<line x1="'+L+'" y1="'+(H-B)+'" x2="'+(W-R)+'" y2="'+(H-B)+'" stroke="#708597"/><text x="'+(W/2)+'" y="'+(H-5)+'" text-anchor="middle">'+esc(xlabel)+'</text><text transform="translate(13 '+(H/2)+') rotate(-90)" text-anchor="middle">'+esc(ylabel)+'</text>';
  return {svg,X,Y};
}

// Lab 1: scalar quadratic with a bounded number of clicks.
let zs=[2];
function renderQuad(){
  const eta=Number($("#quad-rate").value), k=zs.length-1,z=zs[k];
  let message=k===0?"Xuất phát z₀=2, f(z₀)=4.":"z mới = "+fmt(zs[k-1])+" − "+fmt(eta)+" × (2 × "+fmt(zs[k-1])+") = "+fmt(z)+".";
  const outcome=eta<1?"Độ lớn tiến về 0.":eta===1?"Dao động giữa 2 và −2; không hội tụ.":"Độ lớn tăng: bước quá lớn cho f(z)=z².";
  $("#quad-status").innerHTML='<strong>Bước '+k+' · z = '+fmt(z)+' · f(z) = '+fmt(z*z)+'</strong><br>'+esc(message)+'<br>'+outcome;
  const lim=Math.max(2.5,...zs.map(x=>Math.abs(x)*1.15)),c=chartBase("Tham số z theo bước cập nhật",0,Math.max(4,k),-lim,lim,"Bước k","Tham số z");
  c.svg+='<line x1="'+c.X(0)+'" y1="'+c.Y(0)+'" x2="'+c.X(Math.max(4,k))+'" y2="'+c.Y(0)+'" stroke="#8195a3" stroke-dasharray="4 3"/>';
  c.svg+='<polyline fill="none" stroke="#196b9e" stroke-width="2.5" points="'+zs.map((v,i)=>c.X(i)+","+c.Y(v)).join(" ")+'"/>';
  zs.forEach((v,i)=>c.svg+='<circle cx="'+c.X(i)+'" cy="'+c.Y(v)+'" r="4" fill="#196b9e"/>');
  $("#quad-plot").innerHTML=c.svg+"</svg>";$("#quad-step").disabled=k>=12;
}
$("#quad-step").addEventListener("click",()=>{if(zs.length<=12)zs.push(M.quadratic(zs[zs.length-1],Number($("#quad-rate").value)));renderQuad();});
function resetQuad(){zs=[2];renderQuad();}
$("#quad-reset").addEventListener("click",resetQuad);$("#quad-rate").addEventListener("change",resetQuad);renderQuad();

// Lab 2: exact three-step schedule from script 01; no hidden training.
let history=[];
const colors={gd:"#196b9e",sgd:"#b52c39",mb:"#237643"};
function renderSim(){
  const method=$("#method").value,rate=Number($("#rate").value),k=history.length,w=k?history[k-1].next:0;
  const used=history.reduce((sum,r)=>sum+r.batch.length,0);
  const nextIndices=k<3?M.schedules[method][k].map(i=>i+1).join(", "):"đã xong";
  $("#sim-status").dataset.w=String(w);
  $("#sim-status").innerHTML='<strong>Sau '+k+' / 3 bước: w = '+fmt(w)+' · J(w) = '+fmt(M.loss(w))+'</strong><br>Đã tính '+used+' gradient thành phần. '+(k<3?"Bước tiếp dùng mẫu: "+nextIndices+".":"Hoàn thành ví dụ. Chọn phương pháp khác để so sánh.");
  const row=k?history[k-1]:M.step(0,method,0,rate);
  $("#contributions").innerHTML='<p class="caption">'+(k?"Tính tại w trước = "+fmt(row.before):"Xem trước bước 1, chưa cập nhật")+'. Ô tô màu là mẫu được dùng.</p><div class="table-wrap"><table><thead><tr><th>Mẫu</th><th>ŷ=wx</th><th>r=ŷ−y</th><th>gᵢ=r×x</th><th>Dùng?</th></tr></thead><tbody>'+row.terms.map(p=>'<tr class="'+(p.used?"chosen":"")+'"><td>'+ (p.i+1)+'</td><td>'+fmt(p.prediction,4)+'</td><td>'+fmt(p.residual,4)+'</td><td>'+fmt(p.gradient,4)+'</td><td>'+(p.used?"Có":"Không")+'</td></tr>').join("")+'</tbody></table></div>';
  $("#substitution").innerHTML='g = ('+row.terms.filter(p=>p.used).map(p=>fmt(p.gradient)).join(" + ")+') / '+row.batch.length+' = '+fmt(row.g)+'<br>w mới = '+fmt(row.before)+' − '+fmt(row.rate)+' × ('+fmt(row.g)+') = <strong>'+fmt(row.next)+'</strong>'+(k?"":"<br><small>Giá trị dự kiến khi bấm Đi 1 bước.</small>");
  $("#history").innerHTML=history.length?history.map(r=>'<tr><td>'+r.k+'</td><td>{'+r.batch.map(i=>i+1).join(", ")+'}</td><td>'+fmt(r.before)+'</td><td>'+fmt(r.g)+'</td><td>'+fmt(r.next)+'</td><td>'+fmt(r.loss)+'</td></tr>').join(""):'<tr><td colspan="6">Chưa cập nhật. Bấm Đi 1 bước để bắt đầu.</td></tr>';
  const ws=[0,...history.map(r=>r.next)],min=Math.min(-.25,...ws)-.08,max=Math.max(1.65,...ws)+.08;
  const ymax=Math.max(M.loss(min),M.loss(max))*1.12,c=chartBase("Loss toàn tập theo tham số w",min,max,0,ymax,"Tham số w","J(w)");
  const curve=Array.from({length:121},(_,i)=>min+(max-min)*i/120);
  c.svg+='<polyline fill="none" stroke="#8195a3" stroke-width="2" points="'+curve.map(v=>c.X(v)+","+c.Y(M.loss(v))).join(" ")+'"/>';
  c.svg+='<polyline fill="none" stroke="'+colors[method]+'" stroke-width="1.5" stroke-dasharray="4 3" points="'+ws.map(v=>c.X(v)+","+c.Y(M.loss(v))).join(" ")+'"/>';
  ws.forEach((v,i)=>{c.svg+='<circle cx="'+c.X(v)+'" cy="'+c.Y(M.loss(v))+'" r="5" fill="'+colors[method]+'"/><text x="'+(c.X(v)+5)+'" y="'+(c.Y(M.loss(v))-9-i*3)+'" font-weight="600">'+i+'</text>';});
  c.svg+='<text x="'+c.X(M.wStar)+'" y="'+(c.Y(M.jStar)+4)+'" text-anchor="middle">★</text><text x="'+(c.X(M.wStar)+12)+'" y="'+(c.Y(M.jStar)-9)+'">w*</text>';
  $("#loss-plot").innerHTML=c.svg+"</svg>";$("#step").disabled=k>=3;
}
$("#step").addEventListener("click",()=>{if(history.length>=3)return;const w=history.length?history[history.length-1].next:0;history.push(M.step(w,$("#method").value,history.length,Number($("#rate").value)));renderSim();});
function resetSim(){history=[];renderSim();}
$("#reset").addEventListener("click",resetSim);$("#method").addEventListener("change",resetSim);$("#rate").addEventListener("change",resetSim);renderSim();

// Quiz: each explanation teaches the specific distinction being checked.
const questions=[
{q:"Tại w=0, J′(w)=−13/3, η=0.1. GD cho w mới bằng bao nhiêu?",options:["−0.433333","0.433333","4.333333"],answer:1,why:"w mới = 0 − 0.1×(−13/3) = 0.433333. Trừ một số âm làm tham số tăng."},
{q:"N=5, batch_size=2, giữ lô cuối. Một epoch có mấy cập nhật?",options:["2","5","3"],answer:2,why:"Các lô có 2,2,1 mẫu: cần 3 lần cập nhật. Công thức là ⌈N/b⌉."},
{q:"Lô cuối chỉ còn 1 mẫu, batch_size dự kiến là 32. Chia gradient cho số nào?",options:["32","1","N toàn tập"],answer:1,why:"Gradient trung bình lô phải chia số mẫu thực tế, tức len(lo)=1."},
{q:"Trong PyTorch, dòng nào thực sự đổi trọng số?",options:["loss.backward()","optimizer.zero_grad()","optimizer.step()"],answer:2,why:"backward tính gradient; zero_grad xóa gradient cũ; step dùng gradient để cập nhật trọng số."},
{q:"partial_fit của SGDClassifier nhận một khối 32 mẫu. Điều gì đúng?",options:["Luôn là một cập nhật gradient trung bình lô 32","Nó vẫn cập nhật theo mẫu bên trong","Nó chỉ dự đoán, không học"],answer:1,why:"Kích thước khối truyền vào không đồng nghĩa kích thước lô gradient. SGDClassifier thực hiện SGD theo mẫu."},
{q:"R²=0.326 có nghĩa gì?",options:["Chính xác 32.6% số nhãn","Chỉ số hồi quy so với mốc dự đoán trung bình, không phải accuracy","Loss bằng 0.326"],answer:1,why:"R²=1−SSE/SST. Nó không đếm tỷ lệ dự đoán nhãn đúng và còn có thể âm."},
{q:"Tại sao chỉ fit StandardScaler trên train?",options:["Để giảm số dòng code","Để test góp thông tin vào huấn luyện","Để tránh dùng thông tin test trong tiền xử lý"],answer:2,why:"μ và σ là thống kê được học. Fit trên toàn tập làm rò rỉ thông tin test; dùng thống kê train để transform cả hai."},
{q:"Mini-batch thắng ở một thí nghiệm có đủ chứng minh luôn tốt nhất?",options:["Không; còn dữ liệu, lr, seed, ngân sách và phần cứng","Có, vì dùng nhiều mẫu hơn SGD","Có, vì tên thuật toán có batch"],answer:0,why:"Thí nghiệm minh họa chỉ hỗ trợ kết luận trong cấu hình đã đo. Cần thiết kế đánh giá rộng và công bằng hơn để suy rộng."}
];
$("#quiz-questions").innerHTML=questions.map((q,i)=>'<fieldset><legend>'+(i+1)+'. '+esc(q.q)+'</legend>'+q.options.map((o,j)=>'<label><input type="radio" name="q'+i+'" value="'+j+'">'+esc(o)+'</label>').join("")+'<p class="feedback" id="feedback-'+i+'" aria-live="polite"></p></fieldset>').join("");
$("#quiz-form").addEventListener("submit",e=>{
  e.preventDefault();let score=0,answered=0;
  questions.forEach((q,i)=>{const v=$('input[name="q'+i+'"]:checked'),f=$("#feedback-"+i);const good=v&&Number(v.value)===q.answer;if(v)answered++;if(good)score++;
    f.className="feedback "+(good?"correct":"wrong");f.textContent=(good?"Đúng. ":v?"Chưa đúng. ":"Chưa chọn đáp án. ")+q.why;});
  $("#quiz-score").textContent="Bạn trả lời đúng "+score+" / "+questions.length+" câu; đã chọn "+answered+" / "+questions.length+". Đọc giải thích dưới mỗi câu để ôn lại.";
});
$("#quiz-form").addEventListener("reset",()=>{$$(".feedback").forEach(f=>{f.textContent="";f.className="feedback";});$("#quiz-score").textContent="";});
})();
