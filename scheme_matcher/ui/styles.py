"""Global stylesheet: "Aurora" palette (violet / magenta with emerald, orange and slate status colours)."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --v900:#2E1065; --v800:#4C1D95; --v700:#6D28D9; --v600:#7C3AED; --v500:#8B5CF6;
  --v200:#DDD6FE; --v100:#EDE9FE; --v50:#F5F3FF;
  --pink:#DB2777; --rose:#F43F5E;
  --ok:#047857; --ok-bg:#D1FAE5; --ok-line:#6EE7B7;
  --near:#C2410C; --near-bg:#FFEDD5; --near-line:#FDBA74;
  --no:#475569; --no-bg:#F1F5F9; --no-line:#CBD5E1;
  --ink:#24173B; --muted:#6B6480; --line:#E7E1F5; --card:#FFFFFF; --bg:#F7F5FB;
  --grad:linear-gradient(120deg,#4C1D95 0%,#7C3AED 52%,#DB2777 100%);
  --shadow:0 1px 2px rgba(36,23,59,.05),0 10px 28px rgba(36,23,59,.06);
}

html, body, .stApp, [class*="css"]{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;}
.stApp{background:var(--bg);color:var(--ink);}
#MainMenu, footer, .stDeployButton, [data-testid="stAppDeployButton"], [data-testid="stDecoration"]{display:none !important;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1240px;}
h1,h2,h3,h4{color:var(--ink);letter-spacing:-.015em;}

/* ---------------- Sidebar ---------------- */
section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line);}
section[data-testid="stSidebar"] > div{padding-top:0;}
[data-testid="stSidebarHeader"]{height:2.2rem;min-height:2.2rem;padding-top:.4rem;}
.sb-brand{display:flex;gap:.75rem;align-items:center;padding:.5rem .2rem 1rem;}
.sb-logo{width:42px;height:42px;border-radius:13px;background:var(--grad);display:grid;place-items:center;
  color:#fff;font-weight:800;font-size:1.1rem;box-shadow:0 10px 22px rgba(124,58,237,.35);}
.sb-name{font-weight:800;font-size:1.06rem;color:var(--ink);line-height:1.1;}
.sb-tag{font-size:.72rem;color:var(--muted);margin-top:2px;}
.sb-user{display:flex;gap:.7rem;align-items:center;padding:.7rem .8rem;border:1px solid var(--line);
  border-radius:14px;background:var(--v50);margin-bottom:.4rem;}
.sb-avatar{flex:0 0 36px;height:36px;border-radius:50%;background:var(--grad);color:#fff;display:grid;
  place-items:center;font-weight:700;font-size:.95rem;}
.sb-uname{font-weight:700;font-size:.88rem;color:var(--ink);line-height:1.2;}
.sb-mail{font-size:.72rem;color:var(--muted);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.sb-h{font-size:.68rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:1.2rem 0 .6rem;}
.step{position:relative;display:flex;gap:.7rem;padding-bottom:.9rem;}
.step:not(:last-child)::before{content:"";position:absolute;left:11px;top:25px;bottom:0;width:2px;background:var(--v200);}
.step .dot{flex:0 0 24px;height:24px;border-radius:50%;background:var(--v50);color:var(--v700);font-size:.7rem;
  font-weight:800;display:grid;place-items:center;border:2px solid var(--v200);}
.step.done .dot{background:var(--grad);color:#fff;border-color:transparent;}
.step .t{font-weight:700;font-size:.84rem;color:var(--ink);line-height:1.2;}
.step .r{font-size:.72rem;color:var(--muted);line-height:1.3;margin-top:1px;}

/* ---------------- Hero ---------------- */
.hero{position:relative;overflow:hidden;border-radius:24px;padding:2.1rem 2.3rem;color:#fff;background:var(--grad);
  box-shadow:0 22px 50px rgba(76,29,149,.28);margin-bottom:1.3rem;}
.hero::before{content:"";position:absolute;top:-45%;right:-6%;width:430px;height:430px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.30),transparent 64%);}
.hero::after{content:"";position:absolute;bottom:-60%;left:22%;width:380px;height:380px;border-radius:50%;
  background:radial-gradient(circle,rgba(244,63,94,.40),transparent 66%);}
.hero > *{position:relative;z-index:1;}
.hero .eyebrow{display:inline-block;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);
  padding:.28rem .8rem;border-radius:999px;font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.9rem;}
.hero h1{color:#fff !important;font-size:2.15rem;font-weight:800;letter-spacing:-.025em;margin:0 0 .45rem;line-height:1.15;padding:0;}
.hero p{color:rgba(255,255,255,.9) !important;font-size:1.02rem;margin:0;max-width:760px;line-height:1.55;}
.hero .chips{margin-top:1.15rem;display:flex;flex-wrap:wrap;gap:.5rem;}
.hero .chip{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.26);color:#fff;border-radius:999px;
  padding:.3rem .8rem;font-size:.78rem;font-weight:600;}

/* ---------------- KPI cards ---------------- */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.2rem;}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.1rem 1.2rem;display:flex;gap:.95rem;
  align-items:center;box-shadow:var(--shadow);}
.kpi .ico{flex:0 0 48px;height:48px;border-radius:14px;display:grid;place-items:center;}
.kpi .ico svg{width:23px;height:23px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}
.kpi.ok .ico{background:var(--ok-bg);color:var(--ok);}
.kpi.near .ico{background:var(--near-bg);color:var(--near);}
.kpi.no .ico{background:var(--no-bg);color:var(--no);}
.kpi.all .ico{background:var(--v100);color:var(--v700);}
.kpi .num{font-size:1.95rem;font-weight:800;line-height:1;color:var(--ink);}
.kpi .lbl{font-size:.78rem;color:var(--muted);font-weight:600;margin-top:.3rem;}

/* ---------------- Panels ---------------- */
.panel{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.25rem 1.35rem;box-shadow:var(--shadow);min-height:230px;box-sizing:border-box;}
.panel h4{margin:0 0 1rem;font-size:.95rem;font-weight:800;color:var(--ink);}
.panel .sub{font-size:.78rem;color:var(--muted);margin:-.6rem 0 1rem;}
.donut-wrap{display:flex;align-items:center;gap:1.4rem;flex-wrap:wrap;}
.donut{position:relative;width:148px;height:148px;border-radius:50%;flex:0 0 148px;display:grid;place-items:center;}
.donut::after{content:"";position:absolute;inset:21px;background:#fff;border-radius:50%;}
.donut .c{position:relative;z-index:1;text-align:center;line-height:1.1;}
.donut .c b{font-size:1.7rem;font-weight:800;color:var(--ink);display:block;}
.donut .c span{font-size:.68rem;color:var(--muted);font-weight:600;}
.legend{display:grid;gap:.55rem;font-size:.84rem;color:var(--ink);}
.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:.55rem;}
.legend b{font-weight:700;margin-left:.3rem;}
.bar-row{display:grid;grid-template-columns:132px 1fr 32px;gap:.75rem;align-items:center;margin:.6rem 0;font-size:.82rem;}
.bar-row .n{font-weight:700;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.bar{height:10px;border-radius:99px;background:var(--v100);overflow:hidden;}
.bar > i{display:block;height:100%;border-radius:99px;background:var(--grad);}
.bar-row .v{text-align:right;color:var(--muted);font-weight:600;}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:.7rem 1rem;}
.kv .k{font-size:.68rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:700;}
.kv .v{font-size:.88rem;color:var(--ink);font-weight:600;margin-top:2px;}
.empty{color:var(--muted);font-size:.86rem;}
.steps3{display:grid;gap:.85rem;}
.steps3 .s{display:flex;gap:.8rem;align-items:flex-start;}
.steps3 .n{flex:0 0 28px;height:28px;border-radius:9px;background:var(--v100);color:var(--v700);font-weight:800;font-size:.82rem;display:grid;place-items:center;}
.steps3 b{display:block;font-size:.88rem;color:var(--ink);}
.steps3 span{display:block;font-size:.78rem;color:var(--muted);line-height:1.4;margin-top:2px;}

/* ---------------- Scheme cards ---------------- */
div[class*="st-key-card-"]{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:1.3rem 1.4rem;
  box-shadow:var(--shadow);margin-bottom:.9rem;transition:box-shadow .2s ease,border-color .2s ease,transform .2s ease;}
div[class*="st-key-card-"]:hover{box-shadow:0 16px 40px rgba(109,40,217,.15);border-color:var(--v200);transform:translateY(-2px);}
.sc-head{display:flex;gap:1rem;align-items:flex-start;justify-content:space-between;}
.sc-title{display:flex;gap:.8rem;align-items:flex-start;}
.rank{flex:0 0 auto;min-width:38px;height:38px;border-radius:12px;background:var(--grad);color:#fff;font-weight:800;font-size:.9rem;
  display:grid;place-items:center;box-shadow:0 8px 18px rgba(124,58,237,.3);}
.sc-name{font-size:1.06rem;font-weight:800;color:var(--ink);line-height:1.3;}
.sc-min{font-size:.78rem;color:var(--muted);margin-top:2px;}
.status{flex:0 0 auto;font-size:.7rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;padding:.32rem .75rem;border-radius:999px;border:1px solid;}
.status.ok{background:var(--ok-bg);color:var(--ok);border-color:var(--ok-line);}
.status.near{background:var(--near-bg);color:var(--near);border-color:var(--near-line);}
.status.no{background:var(--no-bg);color:var(--no);border-color:var(--no-line);}
.pill{display:inline-block;background:var(--v50);color:var(--v700);border:1px solid var(--v200);border-radius:999px;padding:.18rem .7rem;font-size:.72rem;font-weight:600;margin:.7rem .4rem .2rem 0;}
.benefit{margin:.7rem 0 .2rem;font-size:.9rem;color:var(--ink);line-height:1.55;}
.benefit b{color:var(--v700);}
.callout{border-radius:14px;padding:.85rem 1rem;margin:.9rem 0 .4rem;font-size:.88rem;line-height:1.55;border-left:4px solid;}
.callout .ct{font-weight:800;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.25rem;}
.callout.ok{background:var(--ok-bg);border-color:var(--ok);color:#064E3B;}
.callout.near{background:var(--near-bg);border-color:var(--near);color:#7C2D12;}
.callout.tip{background:var(--v50);border-color:var(--v600);color:var(--v900);}
.meter{display:flex;align-items:center;gap:.7rem;margin:.6rem 0 .2rem;font-size:.75rem;color:var(--muted);font-weight:600;}
.meter .bar{flex:1;}
.apply{margin-top:.6rem;font-size:.86rem;color:var(--ink);line-height:1.5;}
.apply a{color:var(--v700) !important;font-weight:700;text-decoration:none;border-bottom:2px solid var(--v200);}
.apply a:hover{border-color:var(--v600);}
.src{margin-top:.5rem;font-size:.72rem;color:var(--muted);}
.rule{display:flex;gap:.6rem;align-items:flex-start;margin:.55rem 0;font-size:.85rem;line-height:1.45;}
.rule .b{flex:0 0 auto;font-size:.62rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;padding:.2rem .5rem;border-radius:6px;margin-top:2px;}
.rule .b.ok{background:var(--ok-bg);color:var(--ok);}
.rule .b.near{background:var(--near-bg);color:var(--near);}
.rule .b.no{background:var(--no-bg);color:var(--no);}
.rule small{display:block;color:var(--muted);font-size:.76rem;}

/* ---------------- Widgets ---------------- */
.stButton > button, .stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button{
  border-radius:12px;font-weight:600;border:1px solid var(--line);padding:.55rem 1.05rem;background:#fff;color:var(--ink);transition:all .15s ease;}
.stButton > button:hover, .stDownloadButton > button:hover{border-color:var(--v500);color:var(--v700);background:var(--v50);}
button[kind="primary"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--grad) !important;color:#fff !important;border:none !important;box-shadow:0 10px 22px rgba(124,58,237,.32);}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover{
  filter:brightness(1.07);color:#fff !important;transform:translateY(-1px);}
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="base-input"]{border-radius:12px !important;}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within{border-color:var(--v500) !important;box-shadow:0 0 0 3px rgba(139,92,246,.18) !important;}

div[data-baseweb="tab-list"]{gap:.35rem;background:var(--v50);padding:.3rem;border-radius:14px;border:1px solid var(--line);}
button[data-baseweb="tab"]{border-radius:10px;padding:.5rem 1.05rem;font-weight:600;color:var(--muted);height:auto;background:transparent;}
button[data-baseweb="tab"][aria-selected="true"]{background:#fff;color:var(--v700);box-shadow:0 2px 10px rgba(109,40,217,.16);}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"]{display:none;}

div[data-testid="stChatMessage"]{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:.9rem 1.05rem;margin-bottom:.55rem;}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){background:var(--v50);border-color:var(--v200);}
div[data-testid="stRadio"] div[role="radiogroup"]{gap:.45rem;}
div[data-testid="stRadio"] div[role="radiogroup"] label{background:#fff;border:1px solid var(--line);border-radius:12px;padding:.6rem .95rem;width:100%;transition:all .15s ease;}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover{border-color:var(--v500);background:var(--v50);}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:14px;background:#fff;}
div[data-testid="stExpander"] summary{font-weight:600;}
div[data-testid="stAlert"]{border-radius:14px;}
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden;}

/* ---------------- Auth gate ---------------- */
.brand-panel{position:relative;overflow:hidden;border-radius:26px;padding:2.4rem 2.3rem;color:#fff;background:var(--grad);
  min-height:560px;box-shadow:0 26px 60px rgba(76,29,149,.32);display:flex;flex-direction:column;justify-content:space-between;}
.brand-panel::before{content:"";position:absolute;top:-25%;right:-20%;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.28),transparent 65%);}
.brand-panel::after{content:"";position:absolute;bottom:-30%;left:-12%;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(244,63,94,.45),transparent 66%);}
.brand-panel > *{position:relative;z-index:1;}
.brand-panel .logo{width:48px;height:48px;border-radius:14px;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.32);display:grid;place-items:center;font-weight:800;font-size:1.2rem;color:#fff;}
.brand-panel h2{color:#fff !important;font-size:2.1rem;font-weight:800;line-height:1.15;letter-spacing:-.025em;margin:1.1rem 0 .6rem;padding:0;}
.brand-panel p{color:rgba(255,255,255,.88) !important;font-size:.98rem;line-height:1.55;margin:0;}
.brand-panel ul{list-style:none;padding:0 !important;margin:1.6rem 0 0 !important;display:grid;gap:.8rem;}
.brand-panel li{margin:0 !important;padding:0 !important;display:flex;gap:.7rem;align-items:center;font-size:.92rem;font-weight:600;color:#fff;}
.brand-panel li i{flex:0 0 24px;height:24px;border-radius:8px;background:rgba(255,255,255,.2);display:grid;place-items:center;font-style:normal;font-size:.75rem;}
.brand-panel .foot{font-size:.76rem;color:rgba(255,255,255,.75);margin-top:1.8rem;}
div[class*="st-key-auth-card"]{background:#fff;border:1px solid var(--line);border-radius:26px;padding:2rem 2rem 1.6rem;box-shadow:0 26px 60px rgba(36,23,59,.10);}
.auth-h{font-size:1.5rem;font-weight:800;color:var(--ink);letter-spacing:-.02em;margin:0;}
.auth-s{font-size:.88rem;color:var(--muted);margin:.25rem 0 1.1rem;}

/* ---------------- Splash ---------------- */
.stApp:has(.splash){background:radial-gradient(700px circle at 50% 30%,rgba(219,39,119,.38),transparent 65%),
  radial-gradient(760px circle at 12% 88%,rgba(124,58,237,.55),transparent 62%),
  radial-gradient(circle at 50% 30%,#4C1D95 0%,#24103F 55%,#160A2B 100%);}
.stApp:has(.splash) header[data-testid="stHeader"]{display:none;}
.splash{min-height:84vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;animation:fadeUp .6s ease;}
.orbit{position:relative;width:340px;height:340px;margin-bottom:.6rem;}
.orbit .core{position:absolute;inset:0;margin:auto;width:132px;height:132px;border-radius:50%;display:grid;place-items:center;font-size:66px;
  background:radial-gradient(circle at 30% 25%,rgba(255,255,255,.35),rgba(255,255,255,.08));border:1px solid rgba(255,255,255,.35);
  box-shadow:0 0 70px rgba(219,39,119,.55),0 24px 60px rgba(0,0,0,.4);animation:pulse 2.6s ease-in-out infinite;}
.orbit .e{position:absolute;width:56px;height:56px;border-radius:18px;display:grid;place-items:center;font-size:28px;
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);backdrop-filter:blur(6px);
  animation:floaty 3.2s ease-in-out infinite;box-shadow:0 12px 26px rgba(0,0,0,.28);}
.splash .s-name{font-size:2.5rem;font-weight:800;color:#fff !important;letter-spacing:-.03em;line-height:1.1;}
.splash .s-tag{font-size:1.02rem;color:rgba(255,255,255,.78) !important;margin-top:.55rem;}
.splash .s-bar{width:240px;height:5px;border-radius:99px;background:rgba(255,255,255,.18);margin-top:1.7rem;overflow:hidden;}
.splash .s-bar i{display:block;height:100%;width:0;border-radius:99px;background:linear-gradient(90deg,#C4B5FD,#F472B6);animation:load var(--dur,3.5s) ease-in-out forwards;}

@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
@keyframes floaty{0%,100%{transform:translateY(0) rotate(-3deg);}50%{transform:translateY(-14px) rotate(4deg);}}
@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.07);}}
@keyframes load{from{width:0;}to{width:100%;}}

@media (max-width:900px){
  .kpis{grid-template-columns:repeat(2,1fr);}
  .hero{padding:1.6rem 1.4rem;} .hero h1{font-size:1.65rem;}
  .brand-panel{min-height:auto;}
  .orbit{width:280px;height:280px;} .kv{grid-template-columns:1fr;}
}
</style>
"""
