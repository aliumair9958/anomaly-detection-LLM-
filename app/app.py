from flask import Flask, render_template_string, jsonify
import random
from datetime import datetime
from model import detect_anomaly

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Anomaly Detection | Umair Ali</title>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        .wrap{background:#f9f8f6;color:#2a2a2a;font-family:'IBM Plex Mono',monospace;min-height:100vh;}
        .header{display:flex;justify-content:space-between;align-items:center;padding:1.4rem 2rem;border-bottom:2px solid #d0cdc8;}
        .title-block h1{font-size:0.8rem;font-weight:500;letter-spacing:3px;color:#2a2a2a;}
        .title-block p{font-size:0.6rem;color:#aaa;letter-spacing:2px;margin-top:3px;}
        .header-right a{font-size:0.7rem;color:#aaa;text-decoration:none;letter-spacing:1px;}
        .header-right a:hover{color:#2a2a2a;}
        .container{max-width:860px;margin:0 auto;padding:2rem;}
        .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:#d0cdc8;border:2px solid #d0cdc8;margin-bottom:2px;}
        .metric-card{background:#f9f8f6;padding:1.5rem;}
        .metric-label{font-size:0.58rem;letter-spacing:3px;color:#aaa;margin-bottom:0.8rem;}
        .metric-value{font-size:2.2rem;font-weight:300;color:#2a2a2a;line-height:1;}
        .metric-unit{font-size:0.6rem;color:#bbb;margin-top:0.3rem;}
        .status-row{display:flex;align-items:center;gap:6px;margin-top:0.8rem;}
        .status-dot{width:5px;height:5px;border-radius:50%;background:#aaa;}
        .status-dot.anomaly{background:#c0392b;}
        .status-text{font-size:0.58rem;letter-spacing:2px;color:#aaa;}
        .status-text.anomaly{color:#c0392b;}
        .log-section{background:#f9f8f6;border:2px solid #d0cdc8;border-top:none;padding:1.5rem;}
        .log-label{font-size:0.58rem;letter-spacing:3px;color:#aaa;margin-bottom:1rem;}
        .log-area{font-size:0.68rem;line-height:2;min-height:80px;color:#aaa;}
        .log-normal{color:#888;}
        .log-anomaly{color:#c0392b;}
        .btn-row{display:flex;justify-content:space-between;align-items:center;padding:1.2rem 0 0;}
        .btn{background:#2a2a2a;color:#f9f8f6;border:2px solid #2a2a2a;padding:0.65rem 1.8rem;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;letter-spacing:2px;cursor:pointer;}
        .btn:hover{background:#444;border-color:#444;}
        .footer{padding:1.2rem 2rem;border-top:2px solid #d0cdc8;display:flex;justify-content:space-between;align-items:center;margin-top:1rem;}
        .footer a{font-size:0.6rem;color:#bbb;text-decoration:none;letter-spacing:1px;}
        .footer a:hover{color:#2a2a2a;}
        .footer-right{font-size:0.58rem;color:#ccc;letter-spacing:1px;}
    </style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="title-block">
      <h1>ANOMALY DETECTION SYSTEM</h1>
      <p>REAL-TIME INFRASTRUCTURE MONITORING</p>
    </div>
    <div class="header-right">
      <a href="https://iumairali.vercel.app" target="_blank">Built by Umair Ali ↗</a>
    </div>
  </div>
  <div class="container">
    <div class="grid">
      <div class="metric-card">
        <div class="metric-label">CPU USAGE</div>
        <div class="metric-value" id="cpu">--</div>
        <div class="metric-unit">percent</div>
        <div class="status-row"><div class="status-dot" id="cpu-dot"></div><span class="status-text" id="cpu-st">CHECKING</span></div>
      </div>
      <div class="metric-card">
        <div class="metric-label">MEMORY USAGE</div>
        <div class="metric-value" id="mem">--</div>
        <div class="metric-unit">percent</div>
        <div class="status-row"><div class="status-dot" id="mem-dot"></div><span class="status-text" id="mem-st">CHECKING</span></div>
      </div>
      <div class="metric-card">
        <div class="metric-label">RESPONSE TIME</div>
        <div class="metric-value" id="rt">--</div>
        <div class="metric-unit">milliseconds</div>
        <div class="status-row"><div class="status-dot" id="rt-dot"></div><span class="status-text" id="rt-st">CHECKING</span></div>
      </div>
    </div>
    <div class="log-section">
      <div class="log-label">DETECTION LOG</div>
      <div class="log-area" id="log">Initializing...</div>
    </div>
    <div class="btn-row">
      <button class="btn" onclick="runDetection()">RUN DETECTION →</button>
      <span style="font-size:0.58rem;color:#ccc;letter-spacing:1px;">AUTO-REFRESH 5s</span>
    </div>
  </div>
  <div class="footer">
    <a href="https://arxiv.org/abs/1802.04431" target="_blank">Research paper — LSTM-based Anomaly Detection ↗</a>
    <div class="footer-right">Umair Ali · 2026</div>
  </div>
</div>
<script>
function runDetection(){
  fetch('/detect').then(r=>r.json()).then(data=>{
    document.getElementById('cpu').textContent=data.cpu;
    document.getElementById('mem').textContent=data.memory;
    document.getElementById('rt').textContent=data.response_time;
    setStatus('cpu-dot','cpu-st',data.cpu_anomaly);
    setStatus('mem-dot','mem-st',data.memory_anomaly);
    setStatus('rt-dot','rt-st',data.rt_anomaly);
    addLog(data);
  });
}
function setStatus(dotId,stId,isAnomaly){
  const dot=document.getElementById(dotId);
  const st=document.getElementById(stId);
  dot.className='status-dot'+(isAnomaly?' anomaly':'');
  st.textContent=isAnomaly?'ANOMALY':'NORMAL';
  st.className='status-text'+(isAnomaly?' anomaly':'');
}
function addLog(data){
  const log=document.getElementById('log');
  const t=new Date().toLocaleTimeString();
  const anomalies=[];
  if(data.cpu_anomaly)anomalies.push('CPU('+data.cpu+'%)');
  if(data.memory_anomaly)anomalies.push('MEM('+data.memory+'%)');
  if(data.rt_anomaly)anomalies.push('RT('+data.response_time+'ms)');
  const cls=anomalies.length?'log-anomaly':'log-normal';
  const msg=anomalies.length?'[ANOMALY] '+anomalies.join(' '):'[NORMAL] All metrics within threshold';
  const prev=log.innerHTML==='Initializing...'?'':log.innerHTML;
  log.innerHTML='<span class="'+cls+'">['+t+'] '+msg+'</span><br>'+prev;
}
setInterval(runDetection,5000);
runDetection();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/detect')
def detect():
    cpu = round(random.uniform(20, 95), 1)
    memory = round(random.uniform(30, 90), 1)
    response_time = round(random.uniform(50, 500), 1)
    return jsonify({
        'cpu': cpu,
        'memory': memory,
        'response_time': response_time,
        'cpu_anomaly': detect_anomaly(cpu, threshold=80),
        'memory_anomaly': detect_anomaly(memory, threshold=85),
        'rt_anomaly': detect_anomaly(response_time, threshold=400),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/metrics')
def metrics():
    return """# HELP anomaly_detection_requests Total requests
# TYPE anomaly_detection_requests counter
anomaly_detection_requests_total 1
""", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
