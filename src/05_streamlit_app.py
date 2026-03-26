import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import pickle
import json
import os
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv(r"C:\Users\Mutlu\Desktop\ACUHIT\.env")

st.set_page_config(
    page_title="Acıbadem Auris",          # DEĞİŞTİ
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH      = os.getenv("DB_PATH", r"C:\Users\Mutlu\Desktop\ACUHIT\sentinel.db")
SENTINEL_PKL = r"C:\Users\Mutlu\Desktop\ACUHIT\sentinel_full_v3.pkl"
CACHE_PATH   = os.getenv("CACHE_PATH", r"C:\Users\Mutlu\Desktop\ACUHIT\nlp_cache.json")
DEMO_HASTA   = "ANON_018774"
BASE_URL     = os.getenv("NEXPATH_BASE_URL")
API_KEY      = os.getenv("NEXPATH_API_KEY")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.sentinel-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.5rem; color: white;
}
.sentinel-header h1 { font-size: 2rem; font-weight: 700; margin: 0; }
.sentinel-header p  { font-size: 0.9rem; opacity: 0.7; margin: 0.3rem 0 0 0; }
.score-card-YESIL {
    background: linear-gradient(135deg, #0a3d1f, #1a5c2e);
    border: 2px solid #2ecc71; border-radius: 20px; padding: 2rem; text-align: center; color: white;
}
.score-card-SARI {
    background: linear-gradient(135deg, #3d2e00, #5c4500);
    border: 2px solid #f39c12; border-radius: 20px; padding: 2rem; text-align: center; color: white;
}
.score-card-KIRMIZI {
    background: linear-gradient(135deg, #3d0a0a, #5c1a1a);
    border: 2px solid #e74c3c; border-radius: 20px; padding: 2rem; text-align: center; color: white;
    animation: pulse-red 2s infinite;
}
@keyframes pulse-red {
    0%   { box-shadow: 0 0 0 0 rgba(231,76,60,0.4); }
    70%  { box-shadow: 0 0 0 15px rgba(231,76,60,0); }
    100% { box-shadow: 0 0 0 0 rgba(231,76,60,0); }
}

/* DEĞİŞTİ — uyarı kartları okunabilir renk */
.uyari-KIRMIZI {
    background: rgba(231,76,60,0.18); border-left: 4px solid #e74c3c;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0;
}
.uyari-KIRMIZI b   { color: #ff8080; }
.uyari-KIRMIZI,
.uyari-KIRMIZI span { color: #f5d0d0; }
.uyari-SARI {
    background: rgba(243,156,18,0.15); border-left: 4px solid #f39c12;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0;
}
.uyari-SARI b   { color: #ffd166; }
.uyari-SARI,
.uyari-SARI span { color: #ffe8b0; }

.mekanizma-box {
    background: rgba(88,166,255,0.08); border-left: 3px solid #58a6ff;
    border-radius: 6px; padding: 0.6rem 0.9rem; margin-top: 0.4rem;
    font-size: 0.83rem; color: #c0d8f0; line-height: 1.5;
}
.kaynak-badge {
    display: inline-block; background: rgba(88,166,255,0.15);
    color: #90c8ff; border-radius: 4px; padding: 2px 8px;
    font-size: 0.75rem; margin-top: 0.3rem;
}
.alternatif-box {
    background: rgba(46,204,113,0.12); border: 1px solid #2ecc71;
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.8rem; color: #2ecc71;
}
.agent-box {
    background: rgba(52,152,219,0.08); border: 1px solid rgba(52,152,219,0.3);
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.8rem;
    color: #7fb3d3; font-size: 0.88rem; line-height: 1.6;
}
.farmakoloji-box {
    background: rgba(155,89,182,0.1); border: 1px solid rgba(155,89,182,0.4);
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.5rem;
    color: #c39bd3; font-size: 0.88rem; line-height: 1.6;
}
.hasta-bilgi {
    background: rgba(255,255,255,0.06); border-radius: 10px;
    padding: 1rem; margin: 0.3rem 0; border: 1px solid rgba(255,255,255,0.18);
    color: #e2e8f0;
}
.hasta-bilgi b { color: #58a6ff !important; }
.hasta-bilgi span { color: #ffffff !important; }
.model-badge {
    display: inline-block; background: rgba(46,204,113,0.15);
    color: #2ecc71; border-radius: 20px; padding: 3px 12px;
    font-size: 0.78rem; font-weight: 600;
}
.stApp { background: #0d1117; }

/* Başlıklar net beyaz */
h4 { color: #ffffff !important; font-size: 1.1rem !important; font-weight: 700 !important; }

/* Input alanı */
.stTextInput > div > div > input {
    background: #1e2535 !important; color: #ffffff !important;
    border: 1px solid #4a5568 !important; border-radius: 10px !important;
    font-size: 1.05rem !important; padding: 0.65rem 1rem !important;
}
.stTextInput > div > div > input::placeholder { color: #a0aec0 !important; }

/* Butonlar */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb, #0969da) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    width: 100% !important;
}

/* Metric kutucukları */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06); border-radius: 10px;
    padding: 0.5rem; border: 1px solid rgba(255,255,255,0.15);
}
/* Metric — tüm yazılar beyaz */
div[data-testid="stMetricLabel"] p { color: #d0d8e8 !important; font-size: 0.85rem !important; font-weight: 600 !important; }
div[data-testid="stMetricValue"]  { color: #ffffff !important; font-weight: 700 !important; }
div[data-testid="stMetricDelta"]  { color: #ffffff !important; }

/* Genel gri metin override — tüm p ve label */
[data-testid="stVerticalBlock"] p  { color: #e2e8f0 !important; }
label { color: #e2e8f0 !important; }
small { color: #cbd5e0 !important; }

/* Metric değer kesilmesin */
div[data-testid="stMetricValue"] { overflow: visible !important; white-space: nowrap !important; font-size: 1.4rem !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_resources():
    with open(SENTINEL_PKL, "rb") as f:
        saved = pickle.load(f)
    con = duckdb.connect(DB_PATH, read_only=True)
    cache = {}
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
    return saved, con, cache

saved, con, nlp_cache = load_resources()
model         = saved["model"]
FEATURE_COLS  = saved["features"]
medians       = saved["medians"]
KURAL_TABLOSU = saved["kural_tablosu"]
MODEL_ADI     = saved.get("model_adi", "LightGBM")
KARSILASTIRMA = saved.get("karsilastirma", [])

def get_hasta_profili(hasta_id):
    lab = con.execute(f"""
        SELECT
            AVG(CASE WHEN SUB_CODE='Hemoglobin' THEN RESULT_NUM END) AS hb_ort,
            MIN(CASE WHEN SUB_CODE='Hemoglobin' THEN RESULT_NUM END) AS hb_min,
            AVG(CASE WHEN SUB_CODE LIKE '%Glukoz%' THEN RESULT_NUM END) AS glukoz_ort,
            MAX(CASE WHEN SUB_CODE LIKE '%Kreatinin%' THEN RESULT_NUM END) AS kreatinin_max,
            MAX(CASE WHEN SUB_CODE LIKE '%HBA1c%' OR SUB_CODE LIKE '%HbA1c%' THEN RESULT_NUM END) AS hba1c_max,
            MIN(CASE WHEN SUB_CODE LIKE '%Potasyum%' THEN RESULT_NUM END) AS potasyum_min,
            MAX(CASE WHEN SUB_CODE LIKE '%Potasyum%' THEN RESULT_NUM END) AS potasyum_max,
            MIN(CASE WHEN SUB_CODE LIKE '%Albumin%' THEN RESULT_NUM END) AS albumin_min,
            COUNT(*) AS lab_toplam,
            SUM(CASE WHEN is_abnormal THEN 1 ELSE 0 END) AS anormal_toplam
        FROM lab WHERE HASTA_ID = '{hasta_id}'
    """).fetchdf().iloc[0].to_dict()
    ana = con.execute(f"""
        SELECT MAX(TANI_YASI) AS yas, MAX(CINSIYET) AS cinsiyet,
               COUNT(DISTINCT SQ_EPISODE) AS n_ziyaret,
               COUNT(DISTINCT SERVISADI) AS n_bolum,
               MAX(TOPLAM_GELIS_SAYISI) AS toplam_gelis,
               MAX(ILK_TANI_SON_TANI_GUN_FARKI) AS kronik_gun,
               MAX(TANIKODU) AS tanikodu, MAX(TUM_EPS_TANILAR) AS tum_tanilar
        FROM ana WHERE HASTA_ID = '{hasta_id}'
    """).fetchdf().iloc[0].to_dict()
    rec = con.execute(f"""
        SELECT COUNT(DISTINCT "İlaç Adı") AS ilac_cesit,
               MAX(CASE WHEN LOWER("İlaç Adı") LIKE '%clexane%' OR LOWER("İlaç Adı") LIKE '%warfarin%'
                   THEN 1 ELSE 0 END) AS antikoagulan,
               MAX(CASE WHEN LOWER("İlaç Adı") LIKE '%metformin%' OR LOWER("İlaç Adı") LIKE '%janumet%'
                   THEN 1 ELSE 0 END) AS diyabet_ilac
        FROM rec WHERE HASTA_ID = '{hasta_id}'
    """).fetchdf().iloc[0].to_dict()
    profil = {**lab, **ana, **rec}
    kre = profil.get("kreatinin_max"); yas = profil.get("yas", 60)
    profil["gfr_tahmini"] = (141*min(kre/0.9,1)**(-0.411)*max(kre/0.9,1)**(-1.209)*(0.993**yas)
                              if kre and kre > 0 else None)
    profil["bobrek_risk"]  = 1 if (profil.get("gfr_tahmini") or 100) < 60 else 0
    profil["diyabet_risk"] = 1 if ((profil.get("hba1c_max") or 0)>6.5 or (profil.get("glukoz_ort") or 0)>126) else 0
    profil["anemi_risk"]   = 1 if (profil.get("hb_min") or 15) < 11.5 else 0
    profil["albumin_risk"] = 1 if (profil.get("albumin_min") or 4) < 3.5 else 0
    profil["polifarmasi"]  = 1 if (profil.get("ilac_cesit") or 0) >= 5 else 0
    profil["yasli"]        = 1 if (yas or 0) >= 75 else 0
    profil["cinsiyet_e"]   = 1 if profil.get("cinsiyet") == "E" else 0
    profil["kanser_gecmis"]= 1 if "C" in str(profil.get("tum_tanilar","")) else 0
    return profil

def hasta_notlari_cek(hasta_id):
    df = con.execute(f"""
        SELECT CAST(EPISODE_TARIH AS DATE) AS tarih, SERVISADI,
               YAKINMA, "Muayene Notu", "Tedavi Notu", "Özgeçmiş Notu",
               "Sürekli Kullandığı İlaçlar"
        FROM ana WHERE HASTA_ID = '{hasta_id}'
          AND (YAKINMA IS NOT NULL OR "Muayene Notu" IS NOT NULL)
        ORDER BY EPISODE_TARIH DESC LIMIT 20
    """).fetchdf()
    if len(df) == 0: return ""
    parcalar = []
    for _, row in df.iterrows():
        p = f"[{row['tarih']} - {row['SERVISADI']}]\n"
        for col in df.columns[2:]:
            val = row.get(col)
            if pd.notna(val) and str(val).strip() not in ["", "nan", "None"]:
                p += f"{col}: {str(val)[:200]}\n"
        parcalar.append(p)
    return "\n".join(parcalar)

def nexpath_api_cagir(sistem, kullanici):
    payload = {"id":"sentinel","messages":[{"role":"system","content":sistem},
               {"role":"user","content":kullanici}],
               "outputStyle":"normal","model":"asa-mini","email":""}
    resp = requests.post(f"{BASE_URL}/api/search",
                         headers={"X-API-Key":API_KEY,"Content-Type":"application/json"},
                         json=payload, stream=True, timeout=60)
    resp.raise_for_status()
    yanit = ""
    for line in resp.iter_lines(decode_unicode=True):
        line = line.decode("utf-8") if isinstance(line, bytes) else line
        if not line: continue
        if line.startswith("error:500"): raise RuntimeError("Server error")
        if line.startswith("0:"): yanit += line[3:].rstrip()[:-1]
    return yanit.strip()

def parse_api_json(yanit):
    yanit = yanit.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
    yanit = yanit.replace("\\'", "'")
    if '```' in yanit:
        parcalar = yanit.split('```')
        for p in parcalar:
            p = p.strip().lstrip('json').strip()
            if p.startswith('{'): yanit = p; break
    if not yanit.strip().startswith('{'):
        s = yanit.find('{'); e = yanit.rfind('}')+1
        if s != -1 and e > s: yanit = yanit[s:e]
    return json.loads(yanit)

SYSTEM_PROMPT_V2 = """Klinik NLP ve farmakoloji motorusun. Sadece JSON don:
{
  "risk_faktorleri": [{"kategori":"","bulgu":"","aktif":true,"ciddiyet":""}],
  "kontrendikasyon_uyarilari": [{"ilac_grubu":"","neden":"","mekanizma":"","kanit_duzeyi":"A","ciddiyet":""}],
  "klinik_ozet": "ozet",
  "nlp_risk_skoru": 75,
  "acil_bayraklar": [],
  "farmakolojik_not": "ilac-hasta etkilesim ozeti"
}"""

def nlp_analiz_v2(hasta_id, nota, ilac_adi):
    cache_key = hashlib.md5(f"v2:{hasta_id}:{ilac_adi}:{nota[:200]}".encode()).hexdigest()
    if cache_key in nlp_cache: return nlp_cache[cache_key]
    if not nota or len(nota.strip()) < 50: return None
    kullanici = f"Hasta notlari:\n{nota[:3000]}\n\nSorgulanan ilac: {ilac_adi}\n\nBu ilacin bu hastaya ozgu risklerini ve farmakolojik mekanizmayi acikla."
    try:
        yanit = nexpath_api_cagir(SYSTEM_PROMPT_V2, kullanici)
        sonuc = parse_api_json(yanit)
        nlp_cache[cache_key] = sonuc
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(nlp_cache, f, ensure_ascii=False, indent=2)
        return sonuc
    except: return None

def sentinel_skor(hasta_id, ilac_adi):
    profil     = get_hasta_profili(hasta_id)
    ilac_lower = ilac_adi.lower()
    uyarilar   = []; puan_kesinti = 0; en_siddetli = "YESIL"; alternatif = None
    for kural in KURAL_TABLOSU:
        anahtarlar = kural.get("ilaclar", kural.get("ilac_grubu", []))
        if isinstance(anahtarlar, str): anahtarlar = [anahtarlar.lower()]
        if not any(k in ilac_lower for k in anahtarlar): continue
        deger = profil.get(kural["kontrol"])
        if deger is None: continue
        op = kural["operator"]
        tetik = (op=="<" and deger<kural["esik"]) or \
                (op==">" and deger>kural["esik"]) or \
                (op=="==" and deger==kural["esik"])
        if tetik:
            uyarilar.append({
                "siddet"   : kural["siddet"],
                "mesaj"    : kural["mesaj"],
                "kesinti"  : kural["puan_kesinti"],
                "mekanizma": kural.get("mekanizma",""),
                "kaynak"   : kural.get("kaynak",""),
                "alternatif": kural.get("alternatif","")
            })
            puan_kesinti += kural["puan_kesinti"]
            if kural["siddet"]=="KIRMIZI": en_siddetli="KIRMIZI"; alternatif=kural["alternatif"]
            elif kural["siddet"]=="SARI" and en_siddetli=="YESIL": en_siddetli="SARI"; alternatif=kural["alternatif"]
    kural_puan = max(0, 100 - puan_kesinti)
    x = pd.DataFrame([profil])
    for col in FEATURE_COLS:
        if col not in x.columns: x[col] = medians.get(col, 0)
    x = x[FEATURE_COLS].fillna(pd.Series(medians))
    ml_risk = model.predict_proba(x)[0][1]; ml_puan = (1-ml_risk)*100
    nlp_puan = 50; nlp_sonuc = None
    nota = hasta_notlari_cek(hasta_id)
    if nota:
        nlp_sonuc = nlp_analiz_v2(hasta_id, nota, ilac_adi)
        if nlp_sonuc: nlp_puan = 100 - nlp_sonuc.get("nlp_risk_skoru", 50)
    if kural_puan == 100:
        final = max(0, min(100, round(kural_puan*0.60 + ml_puan*0.40)))
    else:
        final = max(0, min(100, round(kural_puan*0.50 + ml_puan*0.30 + nlp_puan*0.20)))
    durum = "YESIL" if final>=75 else ("SARI" if final>=40 else "KIRMIZI")
    if en_siddetli=="KIRMIZI": durum="KIRMIZI"
    return {"skor":final,"durum":durum,"uyarilar":uyarilar,"alternatif":alternatif,
            "ml_risk":round(ml_risk*100,1),"kural_puan":kural_puan,"nlp_puan":round(nlp_puan),
            "klinik_ozet":nlp_sonuc.get("klinik_ozet") if nlp_sonuc else None,
            "farmakolojik_not":nlp_sonuc.get("farmakolojik_not") if nlp_sonuc else None,
            "nlp_kontrendikasyonlar":nlp_sonuc.get("kontrendikasyon_uyarilari",[]) if nlp_sonuc else [],
            "acil_bayraklar":nlp_sonuc.get("acil_bayraklar",[]) if nlp_sonuc else [],
            "profil":profil}

def sesli_metin(sonuc, ilac):
    s=sonuc["skor"]; d=sonuc["durum"]
    if d=="YESIL":
        return f"{ilac.title()} bu hasta icin uygundur. Risk skoru {s} uzerinden yuz. Guvenle yazabilirsiniz."
    elif d=="SARI":
        u = ". ".join([x["mesaj"].split("-")[-1].strip() for x in sonuc["uyarilar"][:2]])
        return f"Dikkat! {ilac.title()} icin risk skoru {s}. {u}. Alternatif: {sonuc.get('alternatif','')}"
    else:
        u = ". ".join([x["mesaj"].split("-")[-1].strip() for x in sonuc["uyarilar"][:2]])
        return f"UYARI! {ilac.title()} bu hastaya kontrendikedir! Skor {s}. {u}. Onerilen: {sonuc.get('alternatif','')}"

# ── SESSION STATE ────────────────────────────────────────────
if "sonuc"    not in st.session_state: st.session_state.sonuc    = None
if "ilac_adi" not in st.session_state: st.session_state.ilac_adi = ""
if "hasta_id" not in st.session_state: st.session_state.hasta_id = DEMO_HASTA

# ── HEADER — DEĞİŞTİ: isim + slogan ────────────────────────
st.markdown(f"""
<div class="sentinel-header">
    <h1>🏥 Acıbadem Auris <span class="model-badge">v2.0 · {MODEL_ADI}</span></h1>
    <p>Görünmeyen Risklerin Görünen Kalkanı. &nbsp;·&nbsp; Klinik Güvenlikte Hata Payını Sıfıra, Güveni Zirveye Taşır.</p>
</div>
""", unsafe_allow_html=True)

# ── ÜST BÖLÜM ───────────────────────────────────────────────
col_sol, col_sag = st.columns([1, 1], gap="large")

with col_sol:
    st.markdown("<h4 style='color:#ffffff;font-weight:700;margin-bottom:8px'>👤 Hasta</h4>", unsafe_allow_html=True)
    hasta_id = st.text_input("Hasta ID", value=st.session_state.hasta_id,
                              label_visibility="collapsed",
                              placeholder="Hasta ID (örn: ANON_018774)",
                              key="hasta_input")
    st.session_state.hasta_id = hasta_id

    if hasta_id:
        try:
            ozet = con.execute(f"""
                SELECT MAX(TANI_YASI) AS yas, MAX(CINSIYET) AS cins,
                       COUNT(DISTINCT SQ_EPISODE) AS n_ep,
                       COUNT(DISTINCT SERVISADI) AS n_bol,
                       MIN(CAST(EPISODE_TARIH AS DATE)) AS ilk,
                       MAX(CAST(EPISODE_TARIH AS DATE)) AS son
                FROM ana WHERE HASTA_ID = '{hasta_id}'
            """).fetchdf().iloc[0]
            st.markdown(f"""
            <div class="hasta-bilgi">
                <b style="color:#58a6ff">Yaş:</b> <span style="color:white">{int(ozet.yas) if pd.notna(ozet.yas) else "-"}</span> &nbsp;|&nbsp;
                <b style="color:#58a6ff">Cinsiyet:</b> <span style="color:white">{ozet.cins}</span><br>
                <b style="color:#58a6ff">Ziyaret:</b> <span style="color:white">{int(ozet.n_ep)}</span> &nbsp;|&nbsp;
                <b style="color:#58a6ff">Bölüm:</b> <span style="color:white">{int(ozet.n_bol)}</span><br>
                <b style="color:#58a6ff">Takip:</b> <span style="color:white">{ozet.ilk} → {ozet.son}</span>
            </div>
            """, unsafe_allow_html=True)
        except: pass

    if KARSILASTIRMA:
        with st.expander("📊 Model Karşılaştırma", expanded=False):
            df_k = pd.DataFrame(KARSILASTIRMA)[['Model','AUC','F1']].round(4)
            df_k['AUC'] = df_k['AUC'].apply(lambda x: f"{x:.4f}")
            df_k['F1']  = df_k['F1'].apply(lambda x: f"{x:.4f}")
            st.dataframe(df_k, hide_index=True, use_container_width=True)

with col_sag:
    st.markdown("<h4 style='color:#ffffff;font-weight:700;margin-bottom:8px'>💊 İlaç Kontrolü</h4>", unsafe_allow_html=True)

    # DEĞİŞTİ: 3 demo butonu kaldırıldı — sadece metin girişi
    ilac_input = st.text_input(
        "İlaç adı yazın veya konuşun",
        value="",
        placeholder="İlaç adı yazın (örn: diklofenak, metformin...)",
        label_visibility="collapsed",
        key="ilac_yazma"
    )

    st.components.v1.html("""
    <div style="margin-top:4px">
    <button id="micBtn" onclick="startListening()"
        style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:white;
               border:none;border-radius:8px;padding:10px 20px;font-size:0.9rem;
               font-weight:600;cursor:pointer;width:100%">
        🎙️ Sesli Giriş
    </button>
    <p id="micStatus" style="color:#8b949e;font-size:0.78rem;margin-top:5px;text-align:center;min-height:18px"></p>
    </div>
    <script>
    function startListening() {
        var btn=document.getElementById("micBtn");
        var st=document.getElementById("micStatus");
        if(!("webkitSpeechRecognition" in window)&&!("SpeechRecognition" in window)){
            st.innerText="Chrome kullanın."; return;
        }
        var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
        var rec=new SR(); rec.lang="tr-TR"; rec.interimResults=false; rec.maxAlternatives=1;
        btn.innerText="🔴 Dinleniyor..."; st.innerText="İlaç adını söyleyin...";
        rec.start();
        rec.onresult=function(e){
            var text=e.results[0][0].transcript;
            st.innerText="Duyulan: "+text;
            var inputs=window.parent.document.querySelectorAll("input[type=text]");
            inputs.forEach(function(inp){
                if(inp.placeholder&&inp.placeholder.includes("diklofenak")){
                    var setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set;
                    setter.call(inp,text);
                    inp.dispatchEvent(new Event("input",{bubbles:true}));
                }
            });
            btn.innerText="🎙️ Sesli Giriş";
        };
        rec.onerror=function(e){st.innerText="Hata: "+e.error; btn.innerText="🎙️ Sesli Giriş";};
        rec.onend=function(){btn.innerText="🎙️ Sesli Giriş";};
    }
    </script>
    """, height=70)

    if st.button("🔍 ANALİZ ET", type="primary", use_container_width=True):
        ilac_kullan = ilac_input.strip()
        if ilac_kullan:
            st.session_state.ilac_adi = ilac_kullan
            with st.spinner("Auris analiz ediyor..."):
                st.session_state.sonuc = sentinel_skor(hasta_id, ilac_kullan)
        elif st.session_state.ilac_adi:
            with st.spinner("Auris analiz ediyor..."):
                st.session_state.sonuc = sentinel_skor(hasta_id, st.session_state.ilac_adi)

st.markdown("---")

# ── SONUÇ ───────────────────────────────────────────────────
if st.session_state.sonuc:
    sonuc = st.session_state.sonuc
    ilac  = st.session_state.ilac_adi
    durum = sonuc["durum"]
    skor  = sonuc["skor"]
    emoji    = {"YESIL":"✅","SARI":"⚠️","KIRMIZI":"🔴"}[durum]
    durum_tr = {"YESIL":"YEŞİL","SARI":"SARI","KIRMIZI":"KIRMIZI"}[durum]

    res_sol, res_sag = st.columns([1, 2], gap="large")

    with res_sol:
        st.markdown(f"""
        <div class="score-card-{durum}">
            <div style="font-size:3rem">{emoji}</div>
            <div style="font-size:4rem;font-weight:700;line-height:1">{skor}</div>
            <div style="font-size:0.85rem;opacity:0.7">/ 100</div>
            <div style="font-size:1.4rem;font-weight:600;margin-top:0.5rem;letter-spacing:2px">{durum_tr}</div>
            <div style="margin-top:1rem;font-size:0.85rem;opacity:0.8">💊 {ilac.upper()}</div>
        </div>
        """, unsafe_allow_html=True)



        metin = sesli_metin(sonuc, ilac)
        metin_js = metin.replace("'"," ").replace("\n"," ").replace('"',' ')
        st.components.v1.html(f"""
        <button onclick="oku()" style="background:linear-gradient(135deg,#6f42c1,#5a32a3);
            color:white;border:none;border-radius:8px;padding:10px;
            font-size:0.88rem;font-weight:600;cursor:pointer;width:100%;margin-top:8px">
            🔊 Sesli Oku
        </button>
        <script>
        function oku(){{
            var u=new SpeechSynthesisUtterance("{metin_js}");
            u.lang="tr-TR"; u.rate=0.9; u.pitch=1.0;
            var v=speechSynthesis.getVoices().find(function(x){{return x.lang.startsWith("tr")}});
            if(v) u.voice=v;
            speechSynthesis.cancel(); speechSynthesis.speak(u);
        }}
        </script>
        """, height=55)

    with res_sag:
        # DEĞİŞTİ: uyarı metinleri okunabilir renkte
        if sonuc["uyarilar"]:
            st.markdown("#### 🚨 Tespit Edilen Riskler")
            for u in sonuc["uyarilar"]:
                ikon = "🔴" if u["siddet"]=="KIRMIZI" else "⚠️"
                st.markdown(f"""
                <div class="uyari-{u['siddet']}">
                    {ikon} <b>[{u["siddet"]}]</b> <span>{u["mesaj"]}</span><br>
                    <small style="opacity:0.6">Puan etkisi: -{u["kesinti"]}</small>
                    {"<div class='mekanizma-box'>🔬 " + u["mekanizma"] + "</div>" if u.get("mekanizma") else ""}
                    {"<span class='kaynak-badge'>📚 " + u["kaynak"] + "</span>" if u.get("kaynak") else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Bu ilaç için kontrendikasyon tespit edilmedi.")

        if sonuc.get("alternatif"):
            st.markdown(f"""
            <div class="alternatif-box">
                💊 <b>Önerilen Alternatif:</b><br>{sonuc["alternatif"]}
            </div>
            """, unsafe_allow_html=True)

        if sonuc.get("klinik_ozet"):
            st.markdown(f"""
            <div class="agent-box">
                🤖 <b>Klinik AI Özeti:</b><br>{sonuc["klinik_ozet"]}
            </div>
            """, unsafe_allow_html=True)

        if sonuc.get("farmakolojik_not"):
            st.markdown(f"""
            <div class="farmakoloji-box">
                🔬 <b>Farmakolojik Değerlendirme:</b><br>{sonuc["farmakolojik_not"]}
            </div>
            """, unsafe_allow_html=True)

        if sonuc.get("nlp_kontrendikasyonlar"):
            with st.expander("🧬 NLP Agent Kontrendikasyon Detayları", expanded=False):
                for ku in sonuc["nlp_kontrendikasyonlar"]:
                    st.markdown(f"""
<span style="color:#ffffff;font-weight:700;font-size:1rem">[{ku.get("ciddiyet","").upper()}] {ku.get("ilac_grubu","")}</span>

<span style="color:#e2e8f0">• **Neden:** {ku.get("neden","")}</span>

<span style="color:#e2e8f0">• **Mekanizma:** {ku.get("mekanizma","")}</span>

<span style="color:#e2e8f0">• **Kanıt düzeyi:** {ku.get("kanit_duzeyi","")}</span>

---
                    """, unsafe_allow_html=True)

        if sonuc.get("acil_bayraklar"):
            st.error("🚨 " + " | ".join(sonuc["acil_bayraklar"]))

        st.markdown("#### 📊 Kritik Lab Değerleri")
        p = sonuc["profil"]
        gfr = p.get("gfr_tahmini"); hba = p.get("hba1c_max"); hb = p.get("hb_min")
        lc1,lc2,lc3 = st.columns(3)
        lc1.metric("GFR", f"{round(gfr,0):.0f}" if gfr else "-",
                   delta="⚠️ Düşük" if gfr and gfr<60 else "Normal",
                   delta_color="inverse" if gfr and gfr<60 else "off")
        lc2.metric("HbA1c", f"{hba}" if hba else "-",
                   delta="⚠️ Yüksek" if hba and hba>6.5 else "Normal",
                   delta_color="inverse" if hba and hba>6.5 else "off")
        lc3.metric("Hb Min", f"{hb}" if hb else "-",
                   delta="⚠️ Düşük" if hb and hb<11.5 else "Normal",
                   delta_color="inverse" if hb and hb<11.5 else "off")
        lc4,lc5,lc6 = st.columns(3)
        lc4.metric("Glukoz Ort", f"{round(p.get('glukoz_ort') or 0,0):.0f}")
        lc5.metric("Albumin", f"{p.get('albumin_min') or '-'}")
        lc6.metric("Antikoag.", "EVET" if p.get("antikoagulan") else "Hayır")

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#8b949e">
        <div style="font-size:4rem">🏥</div>
        <h3 style="color:#58a6ff;margin-top:1rem">Acıbadem Auris v2.0 Hazır</h3>
        <p>Görünmeyen Risklerin Görünen Kalkanı.</p>
        <br>
        <p style="font-size:0.85rem">Hasta ID girin, ilaç adı yazın veya sesli giriş yapın.</p>
    </div>
    """, unsafe_allow_html=True)