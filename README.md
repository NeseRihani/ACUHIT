# 🏥 Auris- Görünmeyen Riskleri Görünür Kılar


![Auris UI](images/farmakovigilans_dashboard.png)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-AUC%200.9664-4CAF50?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-71M%2B%20Rows-FFF000?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)

**ACUHIT 2026 Hackathon — Stage 2 Finalist**  
*Acıbadem Mehmet Ali Aydınlar Üniversitesi · 06–08 Mart 2026*


</div>

---

## 📋 İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [Özellikler](#özellikler)
- [Sistem Mimarisi](#sistem-mimarisi)
- [Dosya Yapısı](#dosya-yapısı)
- [Pipeline](#pipeline)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Test Sonuçları](#test-sonuçları)
- [Model Performansı](#model-performansı)
- [Farmakovijilans Analizi](#farmakovijilans-analizi)
- [Teknoloji Yığını](#teknoloji-yığını)

---

## 🎯 Proje Hakkında

**Auris**, bir hekim hasta için ilaç yazmak üzereyken tetiklenen bir **klinik karar destek sistemi (CDSS)**'dir.

Sistem, hastanın tüm laboratuvar geçmişini, kronik hastalıklarını ve mevcut ilaçlarını milisaniyeler içinde tarayarak:

- 🔴 **KIRMIZI** — Yüksek risk, kontrendikasyon (skor: 0–30)
- 🟡 **SARI** — Orta risk, yakın izlem gerekli (skor: 31–55)
- 🟢 **YEŞİL** — Güvenli, ilaç yazılabilir (skor: 56–100)

...şeklinde renkli bir risk skoru, sesli uyarı ve **alternatif ilaç önerisi** üretir.

### 💡 Neden Auris?

> Türkiye'de yılda 650M+ SGK reçetesi yazılmakta, bunların yaklaşık **15.000'i önlenebilir ilaç hatalarına** yol açmaktadır. Mevcut sistemler kural tabanlı ve hasta-özel değildir; yüksek yanlış pozitif oranı nedeniyle hekimler uyarıları görmezden gelmektedir.

Auris bu boşluğu şu şekilde kapatır:
- Hastanın **bireysel** lab değerlerini (GFR, HbA1c, Potasyum, CK...) kullanır
- Kural tabanlı ve ML tabanlı kararları **birleştirir**
- Her uyarıya **farmakolojik mekanizma açıklaması** ekler (kanıt düzeyi A/B/C)
- 71M+ gerçek hasta verisiyle **istatistiksel olarak doğrulanmıştır**

---

## ✨ Özellikler

| Özellik | Detay |
|---------|-------|
| 🤖 **Hibrit Karar Motoru** | Kural × 0.50 + LightGBM × 0.30 + NLP × 0.20 |
| 📋 **26 Klinik Kural** | 12 ilaç grubu, FDA/EMA/ESC/NICE kaynaklı |
| 🧬 **NLP Agent** | Nexpath API (asa-mini) — mekanizma + kanıt düzeyi A/B/C |
| 🎙️ **Sesli Giriş** | Web Speech API, Türkçe (tr-TR), Chrome destekli |
| 🔊 **Sesli Çıkış** | Sonuç otomatik okunur, ekrana bakmaya gerek yok |
| 💊 **Alternatif Önerisi** | Risk varsa güvenli alternatif ilaç önerilir |
| 📊 **Model Karşılaştırması** | 4 model karşılaştırıldı, LightGBM seçildi |
| 🔬 **Farmakovijilans** | Retrospektif PRE/POST kohort analizi, Wilcoxon testi |

---

## 🏗️ Sistem Mimarisi

```
                    ┌─────────────────────────────────────────┐
                    │           HEKIM ARAYÜZÜ                  │
                    │    Hasta ID  +  İlaç Adı (veya Ses)     │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │           DuckDB Sorgusu                 │
                    │  hasta profili · lab geçmişi · reçeteler │
                    └──────┬────────────────────┬─────────────┘
                           │                    │
             ┌─────────────▼──────┐   ┌─────────▼────────────┐
             │   KATMAN 1         │   │   KATMAN 2            │
             │   Kural Motoru     │   │   ML Motoru           │
             │   26 kural         │   │   LightGBM            │
             │   12 ilaç grubu    │   │   AUC 0.9664          │
             │   kural_puan →     │   │   ml_puan →           │
             └─────────────┬──────┘   └─────────┬────────────┘
                           │                    │
                           └─────────┬──────────┘
                                     │  Risk var mı?
                         ┌───────────▼──────────────┐
                         │       KATMAN 3            │
                         │       NLP Agent           │
                         │       Nexpath (asa-mini)  │
                         │       nlp_puan →          │
                         └───────────┬──────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │         HİBRİT SKOR FORMÜLÜ              │
                    │                                          │
                    │  Risk YOK:  Kural×0.60 + ML×0.40        │
                    │  Risk VAR:  Kural×0.50 + ML×0.30        │
                    │             + NLP×0.20                   │
                    └────────────────┬────────────────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │              ÇIKTI                       │
                    │  🔴 KIRMIZI (0–30)  · Risk uyarıları    │
                    │  🟡 SARI   (31–55)  · Mekanizma açıkl.  │
                    │  🟢 YEŞİL  (56–100) · Alternatif ilaç   │
                    │                     · Sesli uyarı        │
                    └─────────────────────────────────────────┘
```

---

## 📁 Dosya Yapısı

```
ACUHIT/
├── 📂 data/                           
│   ├── Cancer - Data/
│   ├── Check-Up - Data/
│   └── Ex - Data/
│
├── 📂 images/
│   ├── 🖼️ farmakovigilans_grafik.png
│   ├── 🖼️ esik_analizi.png                # Farmakovijilans — eşik aşım grafiği
│   ├── 🖼️ farmakovigilans_dashboard.png   # Farmakovijilans — ana dashboard
│   ├── 🖼️ shap_importance.png             # SHAP özellik önemi grafiği
│
├── 📂 src/                            # Tüm kaynak kodlar
│   ├── 📓 01_load_data.ipynb          # Veri keşfi ve profilleme
│   ├── 📓 02_duckdb_load.ipynb        # Özellik mühendisliği (→ 39k CSV)
│   ├── 📓 03_sentinel_engine.ipynb    # ML model geliştirme + Kural Motoru V1
│   ├── 📓 04_nlp_agent.ipynb          # NLP Agent V2 + Kural Motoru V3 + Hibrit skor
│   ├── 🐍 05_streamlit_app.py         # Canlı web uygulaması
│   └── 📓 06_farmakovigilans_v2.ipynb # Retrospektif hipotez kanıtı
│
├── 📄 .env                            
├── 📄 .gitignore
├── 💾 nlp_cache.json                  # NLP Agent yanıt önbelleği
├── 💾 sentinel.db                     # DuckDB veritabanı (git'e eklenmez)
│
├── 🤖 sentinel_model.pkl              # İlk XGBoost modeli
├── 🤖 sentinel_model_v2.pkl           # LightGBM modeli (tek başına)
├── 🤖 sentinel_full.pkl               # Model + ilk kural seti
├── 🤖 sentinel_full_v2.pkl            # LightGBM + 15 kural
└── 🤖 sentinel_full_v3.pkl            # LightGBM + 26 kural + nlp_cache ← ÜRETİM
```

> **Not:** `sentinel.db`, `.env` ve `.venv/` dosyaları `.gitignore`'a eklenmiştir.

---

## 🔄 Pipeline

Her notebook bağımsız çalışır; çıktılar bir sonraki adıma girdi olarak aktarılır.

### Adım 01 — Veri Keşfi (`01_load_data.ipynb`)

Ham `sentinel.db` veritabanının yapısı incelenir.

- **Tablolar:** `ana` (5.8M hasta kaydı), `lab` (71M laboratuvar testi), `rec` (3.5M reçete)
- **Join anahtarı:** `HASTA_ID` (örn. `ANON_018774`)
- **Temel bulgular:**
  - `lab.SUB_CODE` → test adı, `lab.RESULT_NUM` → sayısal değer, `lab.REP_DATE` → tarih
  - `rec."İlaç Adı"` → ilaç adı (boşluklu sütun adı — tırnak zorunlu), `rec.RECETE_TARIH` → tarih
  - HbA1c iki birimde geliyor: `%` (eşik: 6.5) ve `mmol/mol` (eşik: 48)

---

### Adım 02 — Özellik Mühendisliği (`02_duckdb_load.ipynb`)

Her hasta için ML modeline girecek 45 özellik türetilir.

- GFR son değeri ve 6 aylık trend (DuckDB window functions)
- HbA1c normalizasyonu: `mmol/mol → %` → `(val / 10.929) + 2.15`
- Aktif ilaç sayısı, polifarmasi bayrağı (≥5 ilaç)
- Yaş grubu: pediatrik / yetişkin / geriatrik (≥65)

**Çıktı:** `ana_features_39k.csv` — 39.000 hasta, 45 özellik

> ⚠️ DuckDB bağlantısı `read_only=True` açılmalıdır — Streamlit çalışırken veritabanı kilitleniyor.

---

### Adım 03 — ML Model Geliştirme (`03_sentinel_engine.ipynb`)

4 model 5 katlı çapraz doğrulama ile karşılaştırılır, SMOTE ile sınıf dengesi sağlanır.

| Model | AUC-ROC | F1 | Süre | Seçim |
|-------|---------|-----|------|-------|
| **LightGBM** | **0.9664** | **0.8964** | **5.1s** | ✅ **SEÇİLDİ** |
| XGBoost | 0.9659 | 0.8968 | 15.0s | — |
| Random Forest | 0.9465 | 0.8764 | 6.4s | — |
| Logistic Regression | 0.8545 | 0.7526 | 0.5s | — |

**Seçim kriteri:** En yüksek AUC + en hızlı eğitim süresi = LightGBM  
**Çıktı:** `sentinel_full_v2.pkl` (LightGBM + ilk 15 kural)

---

### Adım 04 — NLP Agent & Kural Motoru V3 (`04_nlp_agent.ipynb`)

**Kural Motoru V3 — 26 kural, 12 ilaç grubu:**

| İlaç Grubu | Kural Sayısı | Tetikleyici | Seviye |
|------------|-------------|-------------|--------|
| NSAİİ | 5 | GFR < 60 → Böbrek hasarı | 🔴 |
| Metformin | 2 | GFR < 30 → Laktik asidoz | 🔴 |
| ACE İnhibitör | 2 | K⁺ > 5.5 → Hiperkalemi | 🔴 |
| Statin | 2 | CK > 5× normal → Miyopati | 🟡 |
| Florokinolon | 2 | QTc > 500ms → Aritmi | 🟡 |
| Opioid | 2 | ≥3 benzodiazepin → CNS baskı | 🔴 |
| Beta Blokor | 2 | KH < 50/dak → Bradikardi | 🟡 |
| Digoksin | 3 | K⁺ < 3.5 + böbrek boz. | 🔴 |
| Antikoagülan | 2 | INR > 4.0 | 🔴 |
| Loop Diüretik | 2 | K⁺ < 3.0 → Hipokalemi | 🔴 |
| Tiyazid | 1 | Na⁺ < 130 → Hiponatremi | 🟡 |
| SGLT2 İnhibitör | 1 | pH < 7.3 → Ketoasidoz | 🔴 |


---

### Adım 05 — Streamlit Dashboard (`05_streamlit_app.py`)

```bash
streamlit run src/05_streamlit_app.py
# → http://localhost:8501
```

**Arayüz bileşenleri:**

- 👤 Hasta ID girişi → otomatik özet (yaş, tanı, son lab değerleri)
- 🎙️ Sesli giriş (Web Speech API, `tr-TR`, Chrome)
- ⚡ 3 hızlı demo butonu (YEŞİL / SARI / KIRMIZI)
- 🎯 Renkli skor kartı — KIRMIZI'da nabız animasyonu
- 💊 Risk uyarıları + farmakolojik mekanizma + kaynak rozeti
- 🤖 Klinik AI Özeti (NLP Agent çıktısı)
- 🔬 Kanıt düzeyi A/B/C açıklayan genişletilebilir panel
- 🔊 Sesli oku butonu
- 📊 Model karşılaştırma tablosu (genişletilebilir)

---

### Adım 06 — Farmakovijilans (`06_farmakovigilans_v2.ipynb`)

> *"Bu ilaçlar gerçekten zarar verdi mi?"* sorusunu **71M satırlık gerçek veriyle** kanıtlar.

**Metodoloji:**
- **PRE:** Reçete tarihinden önceki en yakın lab değeri (max 180 gün)
- **POST:** Reçete tarihinden sonraki en yakın lab değeri (max 90 gün)
- **Test:** Wilcoxon Signed-Rank (parametrik olmayan, paired)
- **Temizleme:** %5–%95 percentile

**Test edilen çiftler:**

| İlaç | Lab | Beklenen | Mekanizma |
|------|-----|---------|-----------|
| Diklofenak/NSAİİ | Kreatinin | ↑ | Prostaglandin ↓ → GFR ↓ |
| Statin | CK | ↑ | HMG-CoA ↓ → Kas hasarı |
| ACE İnhibitör | Potasyum | ↑ | Aldosteron ↓ → K⁺ tutulumu |
| Loop Diüretik | Potasyum | ↓ | Henle kulpu blokajı → K⁺ kaybı |
| Metformin | Kreatinin | izlem | GFR < 30 → birikim riski |
| Varfarin | INR | ↑ | Vit K inhibisyonu → pıhtılaşma ↓ |

---

## 🚀 Kullanım

### Hızlı Demo

Uygulama açıldığında 3 hazır demo butonu kullanılabilir:

```
[ 🟢 YEŞİL Demo ]  →  ANON_018774 + Parasetamol  (skor: 79)
[ 🟡 SARI Demo  ]  →  ANON_018774 + Atorvastatin (skor: 59)
[ 🔴 KIRMIZI Demo] →  ANON_018774 + Diklofenak   (skor: 18)
```

### Manuel Kullanım

1. **Hasta ID** alanına gir (örn. `ANON_018774`)
2. **İlaç adı** yaz veya 🎙️ butonuna tıklayıp konuş
3. **🔍 ANALİZ ET** butonuna tıkla
4. Sonucu ekranda gör veya 🔊 **Sesli Oku** ile dinle

---

## ✅ Test Sonuçları

Sistem 6 farklı hasta ve 7 ilaç kombinasyonu ile test edilmiştir. **7/7 doğru sınıflandırma.**

| Hasta ID | İlaç | Beklenen | Skor | Sonuç |
|----------|------|---------|------|-------|
| ANON_018774 | Diklofenak | 🔴 KIRMIZI | 18 | ✅ |
| ANON_018774 | Parasetamol | 🟢 YEŞİL | 79 | ✅ |
| ANON_018774 | Atorvastatin | 🟡 SARI | 59 | ✅ |
| ANON_209376 | Diklofenak | 🟢 YEŞİL | 80 | ✅ |
| ANON_245848 | Diklofenak | 🔴 KIRMIZI | 39 | ✅ |
| ANON_216790 | Metformin | 🟢 YEŞİL | 75 | ✅ |
| ANON_218718 | Siprofloksasin | 🟡 SARI | 52 | ✅ |

---

## 📈 Model Performansı

```
LightGBM — 5-Fold Stratified Cross-Validation

  AUC-ROC:  0.9664 ± 0.001
  F1 Score: 0.8964 ± 0.002
  Eğitim:   5.1 saniye
  Veri:     39.000 hasta, 45 özellik
  Sınıf dengesi: SMOTE
```

En önemli özellikler (SHAP analizi): `GFR`, `yaş`, `aktif_ilac_sayisi`, `HbA1c`, `son_kreatinin`

---

## 🔬 Farmakovijilans Analizi

Auris'in öne sürdüğü riskler **istatistiksel olarak doğrulanmıştır.**

> Diklofenak/NSAİİ yazan hastalarda kreatinin, POST ölçümde anlamlı şekilde yükselmektedir  
> (Wilcoxon p < 0.05, n > 500 hasta).

Benzer anlamlı sonuçlar: Statin → CK ↑ · ACE → K⁺ ↑ · Loop diüretik → K⁺ ↓

Görseller: `farmakovigilans_dashboard.png` · `esik_analizi.png`

---

## 🛠️ Teknoloji Yığını

| Kategori | Araç | Versiyon |
|----------|------|---------|
| **Veritabanı** | DuckDB | 0.9+ |
| **ML** | LightGBM | 4.x |
| **ML (karşılaştırma)** | XGBoost, scikit-learn | — |
| **Sınıf dengesi** | imbalanced-learn (SMOTE) | — |
| **Açıklanabilirlik** | SHAP | — |
| **NLP Agent** | Nexpath API (asa-mini) | — |
| **Web App** | Streamlit | 1.x |
| **Ses** | Web Speech API | Chrome |
| **Görselleştirme** | Matplotlib, Seaborn | — |
| **İstatistik** | SciPy (Wilcoxon) | — |
| **Ortam** | Python 3.10, venv | — |

---

<div align="center">

**Auris** · ACUHIT 2026 · Acıbadem Mehmet Ali Aydınlar Üniversitesi

*"Klinikleri Birlikte Güvenli Yapalım"*

</div>
