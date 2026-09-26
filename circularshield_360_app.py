import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME
# ==========================================
st.set_page_config(
    page_title="Tugu CircularShield 360",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #0E2F56;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #0056b3;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KONSTANTA GLOBAL & DATA MODUL PRODUK
#    Sumber tunggal (single source of truth) agar Page 4 (Product Architecture)
#    dan Page 6 (Financial Projection) selalu konsisten — fix Image 12 poin (c).
# ==========================================
NATIONAL_WTE_TARGET = 12  # Target regulasi Perpres 35/2018 — BUKAN proyeksi capture rate Tugu (fix Image 3)

MODULES = {
    "Development Shield": {
        "fase": "Konstruksi & EPC",
        "base_premium": 800,  # Rp Juta/tahun
        "desc": "Perlindungan keterlambatan proyek, kegagalan uji coba (commissioning), & CAR.",
        "default_loss_ratio": 35.0,
        "risk_covered": "Keterlambatan konstruksi, kegagalan commissioning, kerusakan fisik selama pembangunan (CAR).",
        "trigger_event": "Delay melewati milestone kontrak EPC; kegagalan performance test saat commissioning.",
        "insured_party": "Kontraktor EPC & Project Owner (joint insured; bank sebagai loss payee bila ada financing).",
        "coverage_period": "Sejak mulai konstruksi s.d. serah terima operasional (Provisional Acceptance Certificate).",
        "sum_insured": "Sesuai nilai kontrak EPC (project cost).",
        "deductible": "5% dari klaim, minimum Rp250 juta per kejadian.",
        "exclusion": "Kesalahan desain yang sudah diketahui sebelum konstruksi; keterlambatan akibat force majeure regulasi."
    },
    "FeedGuard (Feedstock & Supply)": {
        "fase": "Pasokan Sampah",
        "base_premium": 600,  # Rp Juta/tahun — baseline manual; akan digantikan angka otomatis dari simulator
        "desc": "Parametric insurance terhadap defisit pasokan sampah & kalori yang bersifat struktural (bukan fluktuasi harian normal).",
        "default_loss_ratio": 60.0,
        "risk_covered": "Defisit pasokan sampah struktural (berlangsung beberapa hari berturut-turut di bawah threshold operasional).",
        "trigger_event": "Volume harian < threshold selama ≥N hari berturut-turut, diverifikasi data IoT/timbangan TPA.",
        "insured_party": "Operator pembangkit WtE.",
        "coverage_period": "Tahunan, sejak Commercial Operation Date (COD).",
        "sum_insured": "Maksimum limit polis per tahun (default Rp5 miliar).",
        "deductible": "Waiting period dalam bentuk hari (default 3 hari pertama defisit tidak dibayar).",
        "exclusion": "Fluktuasi harian normal (di bawah ambang hari berturut-turut); defisit akibat wanprestasi kontraktual operator sendiri."
    },
    "Operational Shield": {
        "fase": "Operasional Pembangkit",
        "base_premium": 1200,
        "desc": "Perlindungan PAR (kebakaran), MB (kerusakan mesin boiler/turbin), & kerugian bisnis (business interruption).",
        "default_loss_ratio": 58.0,
        "risk_covered": "Kebakaran fasilitas (PAR), kerusakan mesin boiler/turbin (MB), gangguan bisnis akibat keduanya.",
        "trigger_event": "Kejadian fisik terverifikasi loss adjuster (kebakaran, ledakan, kerusakan mekanis).",
        "insured_party": "Operator pembangkit WtE.",
        "coverage_period": "Tahunan, sejak COD, renewable.",
        "sum_insured": "Nilai reinstatement (replacement value) aset pembangkit.",
        "deductible": "10% dari klaim, minimum Rp500 juta per kejadian.",
        "exclusion": "Keausan wajar (wear & tear); kelalaian pemeliharaan terjadwal yang terdokumentasi."
    },
    "Offtake Shield": {
        "fase": "Distribusi & Grid",
        "base_premium": 400,
        "desc": "Penjaminan interferensi jaringan listrik PLN & risiko ketidakmampuan penyerapan daya.",
        "default_loss_ratio": 30.0,
        "risk_covered": "Kegagalan interkoneksi grid, curtailment berkepanjangan akibat kegagalan teknis jaringan PLN.",
        "trigger_event": "Grid curtailment atau kegagalan interkoneksi terdokumentasi melebihi periode tertentu.",
        "insured_party": "Operator pembangkit WtE (revenue protection terhadap PPA).",
        "coverage_period": "Tahunan, mengikuti masa Power Purchase Agreement (PPA).",
        "sum_insured": "Estimasi revenue loss maksimum per tahun.",
        "deductible": "Waiting period 7 hari kalender.",
        "exclusion": "Curtailment akibat kegagalan teknis di sisi pembangkit sendiri."
    },
    "Carbon Credit Shield": {
        "fase": "Monetisasi Karbon",
        "base_premium": 300,
        "desc": "Perlindungan penurunan nilai pasar karbon & kegagalan verifikasi kredit karbon.",
        "default_loss_ratio": 45.0,
        "risk_covered": "Volatilitas harga kredit karbon & kegagalan sertifikasi/verifikasi proyek.",
        "trigger_event": "Harga karbon jatuh di bawah floor price acuan; penolakan sertifikasi oleh verifier resmi.",
        "insured_party": "Project owner / carbon project developer.",
        "coverage_period": "Tahunan, sinkron dengan siklus verifikasi karbon.",
        "sum_insured": "Estimasi nilai kredit karbon tahunan proyek.",
        "deductible": "15% dari klaim.",
        "exclusion": "Kegagalan verifikasi akibat data proyek yang tidak lengkap dari pihak tertanggung."
    }
}


def bundling_discount(n_modules):
    return 0.9 if n_modules >= 4 else 1.0


# ==========================================
# 3. HELPER & GENERATOR DATA DUMMY
# ==========================================
@st.cache_data
def generate_feedstock_data():
    """Generates realistic daily feedstock supply data with seasonal variations."""
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=365, freq="D")
    base_supply = 1000  # ton/hari
    seasonality = np.sin(np.linspace(0, 2 * np.pi, 365)) * 150
    noise = np.random.normal(0, 80, 365)

    # Skenario ekstrim: Cuaca/Banjir TPA
    extreme_events = np.zeros(365)
    extreme_events[40:48] = -350
    extreme_events[300:305] = -400

    volume = base_supply + seasonality + noise + extreme_events
    volume = np.clip(volume, 300, 1500)

    df = pd.DataFrame({"Tanggal": dates, "Volume_Ton": volume})
    return df


if "selected_modules" not in st.session_state:
    st.session_state.selected_modules = list(MODULES.keys())  # default: arsitektur penuh 5 modul

if "feedguard_loss_ratio" not in st.session_state:
    st.session_state.feedguard_loss_ratio = MODULES["FeedGuard (Feedstock & Supply)"]["default_loss_ratio"]

if "feedguard_premium_juta" not in st.session_state:
    st.session_state.feedguard_premium_juta = float(MODULES["FeedGuard (Feedstock & Supply)"]["base_premium"])

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=60)
st.sidebar.title("CircularShield 360")
st.sidebar.caption("Risk Intelligence Dashboard - Tim Khusaeni")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigasi Modul Dashboard:",
    [
        "1. Executive Summary",
        "2. Risk Mapping Ecosystem",
        "3. FeedGuard Simulator (Parametric)",
        "4. Product Architecture Modular",
        "5. Business Model & Network",
        "6. Financial Projection Dynamic",
        "7. ESG & Regulatory Compliance"
    ]
)

# ==========================================
# 5. HALAMAN DASHBOARD
# ==========================================

# ------------------------------------------
# PAGE 1: EXECUTIVE SUMMARY
# ------------------------------------------
if menu == "1. Executive Summary":
    st.title("🛡️ Tugu CircularShield 360")
    st.markdown("##### *End-to-End Parametric & Holistic Insurance for Waste-to-Energy (WtE) Ecosystem in Indonesia*")
    st.markdown("---")

    st.markdown("### Executive Overview")
    st.write("""
    Proyek Waste-to-Energy (WtE) memiliki risiko kompleksitas tinggi yang mencakup 5 fase utama. Solusi asuransi eksisting saat ini masih **parsial** (sebatas CAR, PAR, dan MB). **Tugu CircularShield 360** hadir sebagai jawaban holistik dengan unggulan **FeedGuard** — produk *Parametric Insurance* berbasis data real-time untuk mitigasi risiko pasokan sampah yang bersifat struktural.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Target Proyek WtE Nasional", f"{NATIONAL_WTE_TARGET} Lokasi", "Perpres 35/2018")
        st.caption("⚠️ Target regulasi nasional, **bukan** proyeksi capture rate Tugu — lihat asumsi capture rate di modul Financial Projection.")
    with col2:
        st.metric("Gap Asuransi Eksisting", "Parsial (CAR/PAR)", "Belum cover Feedstock/Carbon")
    with col3:
        st.metric("Potensi GWP (3 Tahun)", "Lihat Financial Projection →", "Base Case Scenario")
    with col4:
        st.metric("Integrasi Modul", "5 Modul End-to-End", "PREDICT - ENABLE")

    st.markdown("---")
    st.subheader("Pendekatan Strategis: PREDICT → ASSESS → PREVENT → PROTECT → ENABLE")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        with st.container(border=True):
            st.markdown("**PREDICT**")
            st.caption("AI Forecasting pasokan feedstock & emisi.")
    with c2:
        with st.container(border=True):
            st.markdown("**ASSESS**")
            st.caption("Risk Scoring otomatis 5 fase proyek WtE.")
    with c3:
        with st.container(border=True):
            st.markdown("**PREVENT**")
            st.caption("Early warning system saat pasokan kritis.")
    with c4:
        with st.container(border=True):
            st.markdown("**PROTECT**")
            st.caption("Klaim parametrik otomatis untuk defisit struktural, tanpa perselisihan.")
    with c5:
        with st.container(border=True):
            st.markdown("**ENABLE**")
            st.caption("Meningkatkan Bankability & ESG rating.")

    st.markdown("---")
    st.subheader("Perbandingan: Asuransi Eksisting vs Tugu CircularShield 360")
    comp_df = pd.DataFrame({
        "Aspek": ["Cakupan Risiko", "Risiko Pasokan Sampah (Feedstock)", "Proses Klaim", "Monetisasi Karbon", "Dukungan Bankability"],
        "Asuransi Konvensional (Eksisting)": ["Parsial (Konstruksi & Mesin Fisik)", "Tidak Ditanggung (Dianggap risiko operasional)", "Membutuhkan Loss Adjuster & waktu lama", "Tidak Ada", "Terbatas pada Aset Fisik"],
        "Tugu CircularShield 360": ["End-to-End (5 Fase Lengkap)", "Ditanggung via FeedGuard Parametric (defisit struktural)", "Otomatis cair via Trigger Parameter Data", "Di-cover dalam Carbon Credit Shield", "Tinggi (Menjamin kepastian pendapatan)"]
    })
    st.table(comp_df)

# ------------------------------------------
# PAGE 2: RISK MAPPING ECOSYSTEM
# ------------------------------------------
elif menu == "2. Risk Mapping Ecosystem":
    st.title("🗺️ Pemetaan Risiko Ekosistem Waste-to-Energy")
    st.markdown("Visualisasi kompleksitas risiko sepanjang siklus rantai nilai WtE di Indonesia.")
    st.markdown("---")

    st.subheader("Alur Rantai Nilai & Paparan Risiko WtE")

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
          pad=20,
          thickness=20,
          line=dict(color="black", width=0.5),
          label=[
              "1. Pengumpulan Sampah", "2. Konstruksi Fasilitas", "3. Operasional Pembangkit", "4. Offtake Listrik PLN", "5. Kredit Karbon",
              "Risiko Pasokan (Feedstock)", "Risiko Keterlambatan EPC", "Risiko Kerusakan Mesin (MB)", "Risiko Penalti Grid", "Risiko Volatilitas Harga Karbon"
          ],
          color=["#0056b3", "#0056b3", "#0056b3", "#0056b3", "#0056b3", "#dc3545", "#dc3545", "#dc3545", "#dc3545", "#dc3545"]
        ),
        link=dict(
          source=[0, 1, 2, 3, 4],
          target=[5, 6, 7, 8, 9],
          value=[40, 25, 30, 20, 15],
          color=["#cbd5e1", "#cbd5e1", "#cbd5e1", "#cbd5e1", "#cbd5e1"]
        )
    )])

    fig_sankey.update_layout(
        title_text="Pergerakan Rantai Nilai ke Titik Risiko Utamanya",
        font_size=12,
        height=450,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    st.markdown("---")
    st.subheader("Matriks & Heatmap Risiko Interaktif")

    fase_filter = st.multiselect(
        "Filter Berdasarkan Fase Proyek:",
        ["1. Pengumpulan & Feedstock", "2. Konstruksi & EPC", "3. Operasional Pembangkit", "4. Distribusi Listrik (PLN)", "5. Monetisasi Karbon"],
        default=["1. Pengumpulan & Feedstock", "2. Konstruksi & EPC", "3. Operasional Pembangkit"]
    )

    # Kolom "Risk Treatment" ditambahkan (fix Image 6) — menunjukkan tidak semua risiko
    # ditransfer lewat asuransi; ada yang lebih tepat ditangani via kontrak atau mitigasi operasional.
    risk_data = pd.DataFrame([
        {"Fase": "1. Pengumpulan & Feedstock", "Jenis Risiko": "Defisit Pasokan Sampah (struktural, berturut-turut)", "Severity": 5, "Likelihood": 4, "Risk Treatment": "Insurance Transfer (FeedGuard)"},
        {"Fase": "1. Pengumpulan & Feedstock", "Jenis Risiko": "Kadar Air & Kalori Rendah", "Severity": 4, "Likelihood": 4, "Risk Treatment": "Contractual Risk-Sharing (penalti spesifikasi ke Pemda)"},
        {"Fase": "1. Pengumpulan & Feedstock", "Jenis Risiko": "Fluktuasi harian normal pasokan (noise)", "Severity": 2, "Likelihood": 5, "Risk Treatment": "Operational Mitigation (buffer stok, bukan asuransi)"},
        {"Fase": "2. Konstruksi & EPC", "Jenis Risiko": "Keterlambatan Pembangunan", "Severity": 4, "Likelihood": 3, "Risk Treatment": "Insurance Transfer (Development Shield / CAR)"},
        {"Fase": "3. Operasional Pembangkit", "Jenis Risiko": "Boiler Explosion / Machinery Failure", "Severity": 5, "Likelihood": 2, "Risk Treatment": "Insurance Transfer (Operational Shield / MB)"},
        {"Fase": "3. Operasional Pembangkit", "Jenis Risiko": "Kebakaran Fasilitas", "Severity": 5, "Likelihood": 2, "Risk Treatment": "Insurance Transfer (Operational Shield / PAR)"},
        {"Fase": "4. Distribusi Listrik (PLN)", "Jenis Risiko": "Kegagalan Interkoneksi Grid", "Severity": 3, "Likelihood": 2, "Risk Treatment": "Insurance Transfer (Offtake Shield)"},
        {"Fase": "5. Monetisasi Karbon", "Jenis Risiko": "Volatilitas Harga & Kegagalan Sertifikasi", "Severity": 3, "Likelihood": 3, "Risk Treatment": "Insurance Transfer (Carbon Credit Shield)"}
    ])

    filtered_risk = risk_data[risk_data["Fase"].isin(fase_filter)]

    col1, col2 = st.columns([3, 2])
    with col1:
        st.dataframe(filtered_risk, use_container_width=True, hide_index=True)
        st.caption("Kolom 'Risk Treatment' menunjukkan diferensiasi: mis. kualitas sampah lebih tepat ditangani via kontrak spesifikasi dengan Pemda, bukan transfer asuransi.")
    with col2:
        fig_heat = px.scatter(
            filtered_risk, x="Likelihood", y="Severity", color="Fase",
            size=[20] * len(filtered_risk), hover_name="Jenis Risiko",
            title="Risk Heatmap (Severity vs Likelihood)",
            labels={"Likelihood": "Frekuensi (1-5)", "Severity": "Dampak Kerugian (1-5)"}
        )
        fig_heat.update_xaxes(range=[0.5, 5.5])
        fig_heat.update_yaxes(range=[0.5, 5.5])
        st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------
# PAGE 3: FEEDGUARD SIMULATOR (PARAMETRIC) — REVISI PRIORITAS #1
# ------------------------------------------
elif menu == "3. FeedGuard Simulator (Parametric)":
    st.title("⚡ FeedGuard Simulator")
    st.markdown("##### *Data-Driven Parametric Insurance Engine untuk Risiko Feedstock Sampah Struktural*")
    st.info("💡 **Revisi:** Trigger diubah dari single-day menjadi consecutive-day + waiting period, dan premi kini di-*reprice* otomatis dari expected loss — bukan angka tetap yang menghasilkan loss ratio 225%.")
    st.markdown("---")

    df_feed = generate_feedstock_data()

    st.subheader("Tahap 1 & 2: Data Historis & Forecasting Engine")

    preset = st.selectbox("Pilih Skenario Data Pasokan:", ["Normal Operational", "Skenario Musim Hujan / Ekstrem (Februari & November)"])
    if preset == "Skenario Musim Hujan / Ekstrem (Februari & November)":
        st.warning("⚠️ Mengaktifkan efek penurunan pasokan akibat cuaca buruk dan jalan TPA terganggu.")

    df_feed["Day_Index"] = np.arange(len(df_feed))
    X = df_feed[["Day_Index"]]
    y = df_feed["Volume_Ton"]
    model = LinearRegression().fit(X, y)
    df_feed["Forecast_Trend"] = model.predict(X)

    st.markdown("---")
    st.subheader("Tahap 3 & 4: Parametric Trigger & Backtesting Simulator")

    col_param, col_res = st.columns([1, 2])

    with col_param:
        st.markdown("### 🎛️ Parameter Polis")
        target_capacity = st.number_input("Kebutuhan Operasional Normal (Ton/Hari):", value=1000, step=50)
        trigger_percent = st.slider("Trigger Threshold (% dari Kebutuhan):", min_value=50, max_value=90, value=70, step=5)
        trigger_val = target_capacity * (trigger_percent / 100.0)

        min_run_days = st.slider(
            "Minimum Hari Berturut-turut (baru — anti-noise):",
            min_value=1, max_value=10, value=5,
            help="1 = perilaku lama (single-day). Nilai ≥5 memfilter fluktuasi harian normal agar hanya defisit struktural yang di-trigger."
        )
        waiting_period = st.slider("Waiting Period sebelum klaim cair (hari, baru):", min_value=0, max_value=7, value=3)

        payout_per_day = st.number_input("Klaim per Hari Defisit (Rp Juta):", value=150, step=10)
        max_policy_limit = st.number_input("Maksimum Limit Polis per Tahun (Rp Miliar):", value=5.0, step=0.5) * 1e9
        margin_loading = st.slider(
            "Margin Loading untuk Repricing Premi Otomatis (%):",
            min_value=20, max_value=150, value=60,
            help="Premi = Total Klaim Historis × (1 + Margin). Mendemonstrasikan prinsip price-to-expected-loss."
        )
        manual_premium_ref = st.number_input("Premi Lama (referensi manual, Rp Juta):", value=600, step=50)

        st.caption(
            f"📌 **Penjelasan Trigger Baru:** Klaim otomatis cair sebesar **Rp {payout_per_day} Juta/hari** hanya jika pasokan "
            f"harian < **{trigger_val:.0f} Ton** ({trigger_percent}%) selama **≥{min_run_days} hari berturut-turut**, dengan "
            f"**{waiting_period} hari pertama** sebagai waiting period (deductible waktu)."
        )

    # --- Skema LAMA: single-day, tanpa syarat berturut-turut, premi tetap ---
    df_feed["Trigger_Active"] = df_feed["Volume_Ton"] < trigger_val
    old_trigger_days = int(df_feed["Trigger_Active"].sum())
    old_payout = min(old_trigger_days * payout_per_day * 1e6, max_policy_limit)
    old_premium = manual_premium_ref * 1e6
    old_loss_ratio = (old_payout / old_premium) * 100 if old_premium > 0 else 0

    # --- Skema BARU: consecutive-day + waiting period + premi otomatis ---
    df_feed["grp"] = (df_feed["Trigger_Active"] != df_feed["Trigger_Active"].shift()).cumsum()
    run_lengths = df_feed[df_feed["Trigger_Active"]].groupby("grp").size()
    structural_runs = run_lengths[run_lengths >= min_run_days]
    num_structural_events = int(len(structural_runs))
    payable_days_new = int((structural_runs - waiting_period).clip(lower=0).sum())
    new_payout = min(payable_days_new * payout_per_day * 1e6, max_policy_limit)
    new_premium = new_payout * (1 + margin_loading / 100.0)
    new_loss_ratio = (new_payout / new_premium) * 100 if new_premium > 0 else 0

    # Simpan ke session_state agar Page 4 & Page 6 ikut sinkron (fix reconciliation Image 9 & 12)
    st.session_state.feedguard_loss_ratio = new_loss_ratio
    st.session_state.feedguard_premium_juta = new_premium / 1e6

    with col_res:
        st.markdown("### 📊 Perbandingan Skema Lama vs Baru (Backtesting 1 Tahun)")

        oc1, oc2 = st.columns(2)
        with oc1:
            st.markdown("**Skema Lama (single-day)**")
            st.metric("Hari Trigger", f"{old_trigger_days} Hari")
            st.metric("Total Klaim", f"Rp {old_payout / 1e9:.2f} Miliar")
            st.metric("Premi", f"Rp {manual_premium_ref} Juta")
            st.metric("Loss Ratio", f"{old_loss_ratio:.1f}%", "Sehat" if old_loss_ratio < 70 else "Tinggi", delta_color="inverse")
        with oc2:
            st.markdown("**Skema Baru (consecutive-day)**")
            st.metric("Event Struktural", f"{num_structural_events}")
            st.metric("Total Klaim", f"Rp {new_payout / 1e9:.2f} Miliar")
            st.metric("Premi (Otomatis)", f"Rp {new_premium / 1e6:.0f} Juta")
            if 55 <= new_loss_ratio <= 65:
                st.metric("Loss Ratio", f"{new_loss_ratio:.1f}%", "Dalam Target Sehat")
            elif new_loss_ratio > 65:
                st.metric("Loss Ratio", f"{new_loss_ratio:.1f}%", "Masih Tinggi", delta_color="inverse")
            else:
                st.metric("Loss Ratio", f"{new_loss_ratio:.1f}%", "Kurang Kompetitif")

        st.success(
            "🛡️ **Reinsurance Layer: Aggregate Stop-Loss** — karena data historis masih terbatas (1 tahun), tail risk "
            "FeedGuard ditransfer ke reasuransi sampai data credibility cukup untuk repricing mandiri di tahun ke-3."
        )

        # Grafik dengan anotasi threshold (fix Image 7)
        fig_line = px.line(
            df_feed, x="Tanggal", y=["Volume_Ton", "Forecast_Trend"],
            labels={"value": "Volume Sampah (Ton/Hari)"},
            title="Grafik Pasokan Sampah Harian Pembangkit WtE (365 Hari)",
            color_discrete_map={"Volume_Ton": "#0056b3", "Forecast_Trend": "#ff7f0e"}
        )
        fig_line.add_hline(
            y=trigger_val, line_dash="dot", line_color="#dc3545",
            annotation_text=f"Threshold {trigger_percent}% ({trigger_val:.0f} ton)", annotation_position="top left"
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.caption(
            "⚠️ Fluktuasi harian ≠ risiko struktural — trigger baru mensyaratkan minimal beberapa hari berturut-turut "
            "di bawah threshold sebelum dianggap defisit struktural (lihat parameter 'Minimum Hari Berturut-turut')."
        )

        df_feed["Payout_IDR_OldRule"] = np.where(df_feed["Trigger_Active"], payout_per_day * 1e6, 0)
        df_trigger_only = df_feed[df_feed["Trigger_Active"]]
        fig_payout = px.bar(
            df_trigger_only, x="Tanggal", y="Payout_IDR_OldRule",
            title="Hari dengan Pasokan di Bawah Threshold (sebelum filter consecutive-day)",
            labels={"Payout_IDR_OldRule": "Nilai Klaim per Hari jika Skema Lama (Rp)"},
            color_discrete_sequence=["#dc3545"]
        )
        st.plotly_chart(fig_payout, use_container_width=True)

# ------------------------------------------
# PAGE 4: PRODUCT ARCHITECTURE MODULAR
# ------------------------------------------
elif menu == "4. Product Architecture Modular":
    st.title("🧩 Arsitektur Produk Modular (5 Modul)")
    st.markdown(
        "Fleksibilitas pemilihan perlindungan berbasis kebutuhan spesifik pengembang proyek WtE. "
        "Klik **'Lihat Detail Polis'** tiap modul untuk rincian risk covered, trigger, insured party, sum insured, deductible, dan exclusion."
    )
    st.markdown("---")

    st.markdown("### Pilih Kombinasi Modul Asuransi:")

    selected = []
    total_est_premium = 0.0

    col_a, col_b = st.columns([2, 1])

    with col_a:
        for mod, details in MODULES.items():
            display_premium = float(details["base_premium"])
            if mod == "FeedGuard (Feedstock & Supply)":
                display_premium = st.session_state.feedguard_premium_juta

            is_checked = st.checkbox(
                f"**{mod}** — Rp {display_premium:.0f} Juta/tahun",
                value=(mod in st.session_state.selected_modules)
            )
            st.caption(f"📍 *Fase:* {details['fase']} | {details['desc']}")
            if mod == "FeedGuard (Feedstock & Supply)":
                st.caption(f"🔗 Rp{display_premium:.0f} juta premi ini = bagian dari total premi per proyek di Financial Projection (dihitung otomatis dari FeedGuard Simulator). →")

            with st.expander(f"ℹ️ Lihat Detail Polis — {mod}"):
                st.markdown(f"""
| Aspek | Ketentuan |
|---|---|
| Risk Covered | {details['risk_covered']} |
| Trigger / Event | {details['trigger_event']} |
| Insured Party | {details['insured_party']} |
| Coverage Period | {details['coverage_period']} |
| Sum Insured | {details['sum_insured']} |
| Deductible | {details['deductible']} |
| Exclusion Utama | {details['exclusion']} |
                """)

            if is_checked:
                selected.append(mod)
                total_est_premium += display_premium
            st.markdown("---")
        st.session_state.selected_modules = selected

    with col_b:
        with st.container(border=True):
            st.markdown("### 🛍️ Ringkasan Paketan Polis")
            st.markdown(f"**Modul Dipilih:** {len(selected)} dari {len(MODULES)} Modul")
            for s in selected:
                st.markdown(f"- ✅ {s}")

            st.markdown("---")
            discount = bundling_discount(len(selected))
            final_premium = total_est_premium * discount
            st.metric("Total Estimasi Premi", f"Rp {total_est_premium:.0f} Juta/thn")
            if discount < 1.0:
                st.success("🎉 Diskon Bundling 10% diterapkan (≥4 modul)")
                st.metric("Premi Final (setelah diskon)", f"Rp {final_premium:.0f} Juta/thn")

# ------------------------------------------
# PAGE 5: BUSINESS MODEL & NETWORK
# ------------------------------------------
elif menu == "5. Business Model & Network":
    st.title("🌐 Model Bisnis & Ekosistem Kolaborasi")
    st.markdown("Menghubungkan Tugu Insurance sebagai *Hub Utama* dalam ekosistem multi-pihak WtE.")
    st.markdown("---")

    st.subheader("Jaringan Kemitraan Tugu WtE Risk Hub")
    st.caption("Ditampilkan sebagai kartu per-stakeholder (bukan tabel lebar) agar tidak ada kolom yang terpotong di layar (fix Image 10).")

    stakeholders = [
        {"entitas": "Tugu Insurance (Hub)", "peran": "Underwriter & Pengelola Platform Risk Hub",
         "bayar_ke": "Reasuransi (kapasitas), IoT data vendor", "terima_dari": "Premi seluruh modul",
         "data_mengalir": "Data underwriting, klaim, & analytics ke seluruh partner"},
        {"entitas": "Pemerintah Daerah (Pemda)", "peran": "Penyedia Pasokan Sampah & Penanggung Tip Fee",
         "bayar_ke": "Tugu (co-payment klaim jika wanprestasi kontrak spesifikasi)", "terima_dari": "Retribusi & kepastian kebijakan pengelolaan sampah",
         "data_mengalir": "Data volume & kualitas sampah harian — basis trigger FeedGuard"},
        {"entitas": "Kontraktor EPC", "peran": "Membangun & Mengelola Fasilitas WtE",
         "bayar_ke": "Tugu (premi Development Shield)", "terima_dari": "Jaminan EPC & perlindungan commissioning",
         "data_mengalir": "Milestone konstruksi & hasil performance test"},
        {"entitas": "PLN (Offtaker)", "peran": "Pembeli Listrik Pembangkit WtE",
         "bayar_ke": "Operator (sesuai PPA)", "terima_dari": "Kepastian pasokan listrik terjamin",
         "data_mengalir": "Data interkoneksi grid & curtailment"},
        {"entitas": "Lembaga Pembiayaan / Investor", "peran": "Penyedia Modal Proyek (Project Financing)",
         "bayar_ke": "Operator (pencairan bertahap)", "terima_dari": "Bankability guarantee dari paket asuransi Tugu",
         "data_mengalir": "Laporan risiko proyek untuk covenant pembiayaan"},
        {"entitas": "Reasuransi Global", "peran": "Penjamin Proteksi Risiko Katastropik & Tail Risk FeedGuard",
         "bayar_ke": "-", "terima_dari": "Premi reasuransi dari Tugu",
         "data_mengalir": "Data agregat portofolio untuk pricing treaty"},
    ]

    cols = st.columns(2)
    for i, s in enumerate(stakeholders):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{s['entitas']}**")
                st.caption(f"**Peran:** {s['peran']}")
                st.caption(f"**Bayar ke:** {s['bayar_ke']}")
                st.caption(f"**Terima Value:** {s['terima_dari']}")
                st.caption(f"**Data Mengalir:** {s['data_mengalir']}")

    st.markdown("---")
    st.subheader("Business Model Canvas (9-Box Summary)")

    bmc_c1, bmc_c2, bmc_c3 = st.columns(3)
    with bmc_c1:
        st.markdown("**Key Partners**")
        st.caption("Pemda, PLN, Reasuransi, IoT Data Vendors")
        st.markdown("**Key Activities**")
        st.caption("Underwriting, Parametric Data Analytics, Risk Inspection")
    with bmc_c2:
        st.markdown("**Value Proposition**")
        st.caption("Proteksi End-to-End, Klaim Parametrik Otomatis untuk defisit struktural, Peningkatan Bankability Proyek")
        st.markdown("**Customer Relationships**")
        st.caption("Long-term Partnership, Automated Trigger Payouts")
    with bmc_c3:
        st.markdown("**Customer Segments**")
        st.caption("Pengembang Proyek WtE, Investor EBT, Kontraktor EPC")
        st.markdown("**Revenue Streams**")
        st.caption("Premi Asuransi Modular, Fee-based Risk Analytics")

# ------------------------------------------
# PAGE 6: FINANCIAL PROJECTION DYNAMIC
# ------------------------------------------
elif menu == "6. Financial Projection Dynamic":
    st.title("📈 Proyeksi Keuangan 3 Tahun (What-If Simulation)")
    st.markdown("Simulasi fleksibel untuk menguji kelayakan bisnis dan potensi pendapatan Tugu Insurance.")
    st.markdown("---")

    # ---- Rekonsiliasi Loss Ratio per Modul (fix Image 12 poin a) ----
    st.subheader("🔍 Rekonsiliasi Loss Ratio per Modul")
    st.caption("Blended loss ratio sekarang dihitung dari premi & loss ratio tiap modul — bukan angka 48% yang berdiri sendiri.")

    module_loss_ratios = {}
    lr_cols = st.columns(len(MODULES))
    for i, (mod, details) in enumerate(MODULES.items()):
        with lr_cols[i]:
            short_label = mod.split(" (")[0]
            if mod == "FeedGuard (Feedstock & Supply)":
                lr_val = st.session_state.feedguard_loss_ratio
                st.metric(short_label, f"{lr_val:.1f}%", "dari Simulator")
                module_loss_ratios[mod] = lr_val
            else:
                lr_val = st.slider(
                    short_label, min_value=10, max_value=90,
                    value=int(details["default_loss_ratio"]), key=f"lr_{mod}"
                )
                module_loss_ratios[mod] = lr_val

    weights = {
        mod: (st.session_state.feedguard_premium_juta if mod == "FeedGuard (Feedstock & Supply)" else MODULES[mod]["base_premium"])
        for mod in MODULES
    }
    total_weight = sum(weights.values())
    blended_loss_ratio = sum(weights[m] * module_loss_ratios[m] for m in MODULES) / total_weight if total_weight else 0

    rc1, rc2 = st.columns(2)
    rc1.metric("Loss Ratio Direkonsiliasi (dari arsitektur produk)", f"{blended_loss_ratio:.1f}%")
    rc2.metric("Klaim Lama (tidak tereferensi ke modul)", "48.0%", "Digantikan angka di kiri", delta_color="off")

    st.markdown("---")

    st.subheader("🎛️ Asumsi Skenario Proyeksi")
    scenario = st.radio("Pilih Skenario Otomatis:", ["Conservative", "Base Case", "Optimistic"], index=1, horizontal=True)

    # Rata-rata premi per proyek sekarang DITURUNKAN dari arsitektur produk (fix Image 12 poin c),
    # bukan angka independen Rp4,5 Miliar yang tidak bisa dijumlahkan dari Product Architecture.
    full_bundle_premium = sum(weights.values())  # Rp Juta, memakai FeedGuard premium otomatis
    discounted_bundle = full_bundle_premium * bundling_discount(5)

    if scenario == "Conservative":
        default_proj = [2, 4, 6]
        core3 = MODULES["Development Shield"]["base_premium"] + weights["FeedGuard (Feedstock & Supply)"] + MODULES["Operational Shield"]["base_premium"]
        default_avg_prem = round(core3 / 1000, 2)  # 3 modul inti, tanpa Offtake & Carbon
        capture_rate_note = "30–50%"
    elif scenario == "Base Case":
        default_proj = [3, 7, 10]
        default_avg_prem = round(discounted_bundle / 1000, 2)  # 5 modul dengan diskon bundling
        capture_rate_note = "40–60%"
    else:
        default_proj = [5, 10, 18]
        default_avg_prem = round(discounted_bundle / 1000 * 1.1, 2)  # 5 modul + asumsi premium growth optimistis
        capture_rate_note = "55–75% (agresif — perlu skema panel/reasuransi multi-carrier di atas ~10 proyek)"

    c1, c2, c3 = st.columns(3)
    with c1:
        avg_premium = st.number_input("Rata-rata Premi per Proyek (Rp Miliar/Tahun):", value=default_avg_prem, step=0.1)
        st.caption(f"= dijumlahkan dari kombinasi modul di Product Architecture (bundle penuh 5 modul Rp{full_bundle_premium:.0f} jt, setelah diskon Rp{discounted_bundle:.0f} jt).")
    with c2:
        target_loss_ratio = st.slider("Target Loss Ratio (%):", min_value=30.0, max_value=80.0, value=round(blended_loss_ratio, 1), step=1.0)
    with c3:
        opex_ratio = st.slider("Rasio Operasional & Komisi (%):", min_value=10.0, max_value=30.0, value=15.0, step=1.0)

    years = ["Tahun 1 (2026)", "Tahun 2 (2027)", "Tahun 3 (2028)"]
    num_projects = default_proj
    capture_pct = round(num_projects[-1] / NATIONAL_WTE_TARGET * 100)

    st.caption(
        f"📌 **Asumsi capture rate:** {num_projects[0]} → {num_projects[1]} → {num_projects[2]} proyek dalam 3 tahun ≈ "
        f"**{capture_pct}%** dari {NATIONAL_WTE_TARGET} lokasi target nasional (asumsi {capture_rate_note} proyek yang benar-benar "
        f"commissioning). Tugu berperan sebagai **lead insurer** dengan porsi risiko 40–60%, sisanya melalui skema panel/reasuransi "
        f"— bukan asumsi memenangkan 100% target nasional."
    )

    gwp_list = [p * avg_premium for p in num_projects]
    claims_list = [g * (target_loss_ratio / 100.0) for g in gwp_list]
    opex_list = [g * (opex_ratio / 100.0) for g in gwp_list]
    underwriting_result = [gwp_list[i] - claims_list[i] - opex_list[i] for i in range(3)]
    combined_ratio = [target_loss_ratio + opex_ratio for _ in range(3)]

    fin_df = pd.DataFrame({
        "Tahun": years,
        "Jumlah Proyek WtE": num_projects,
        "Gross Written Premium (Rp Miliar)": gwp_list,
        "Estimasi Klaim (Rp Miliar)": claims_list,
        "Biaya Operasional (Rp Miliar)": opex_list,
        "Hasil Underwriting (Rp Miliar)": underwriting_result,
        "Combined Ratio (%)": combined_ratio
    })

    st.markdown("---")
    st.subheader(f"📊 Ringkasan Keuangan Skenario: **{scenario}**")
    st.dataframe(fin_df, use_container_width=True, hide_index=True)

    fig_fin = go.Figure()
    fig_fin.add_trace(go.Bar(x=years, y=gwp_list, name="Gross Written Premium (GWP)", marker_color="#0056b3"))
    fig_fin.add_trace(go.Bar(x=years, y=underwriting_result, name="Hasil Underwriting (Profit)", marker_color="#28a745"))
    fig_fin.update_layout(title="Pertumbuhan Pendapatan Premi vs Keuntungan Underwriting", barmode="group")
    st.plotly_chart(fig_fin, use_container_width=True)

# ------------------------------------------
# PAGE 7: ESG & REGULATORY COMPLIANCE
# ------------------------------------------
elif menu == "7. ESG & Regulatory Compliance":
    st.title("🌱 Dampak ESG & Kepatuhan Regulasi")
    st.markdown("Menyiapkan ekosistem WtE yang berkelanjutan dan selaras dengan regulasi nasional.")
    st.markdown("---")

    col_esg1, col_esg2, col_esg3 = st.columns(3)

    with col_esg1:
        st.markdown("### 🍃 Environmental")
        st.markdown("- **Pengurangan Sampah:** Menargetkan pengurangan hingga 3,5 juta ton sampah TPA.")
        st.markdown("- **Reduksi Emisi:** Mendukung eliminasi emisi Methane (CH4) via konversi energi terbarukan.")
        st.metric("Estimasi Reduksi Emisi Carbon", "1.2 Mt CO2e /thn")
        st.caption("Asumsi internal berdasarkan kapasitas portofolio 12 lokasi target — belum diverifikasi pihak ketiga.")

    with col_esg2:
        st.markdown("### 🤝 Social")
        st.markdown("- **Kesehatan Masyarakat:** Mengurangi risiko penyakit akibat TPA liar / *open dumping*.")
        st.markdown("- **Pemberdayaan Lokal:** Menciptakan lapangan kerja hijau di sektor pengelolaan sampah.")
        st.metric("Peningkatan Ketahanan Energi Lokal", "+150 MW", "Clean Power")

    with col_esg3:
        st.markdown("### 🏛️ Governance")
        st.markdown("- **Transparansi Data:** Penggunaan data sensor IoT real-time untuk penetapan klaim.")
        st.markdown("- **Standardisasi Risiko:** Menyusun benchmark manajemen risiko WtE pertama di Indonesia.")
        st.metric("ESG Alignment Score", "94 / 100")
        st.caption("🔖 **Self-Assessed ESG Alignment Score** — metodologi: skoring internal berdasarkan kriteria Taksonomi Hijau Indonesia 2.0 (OJK), bukan sertifikasi pihak ketiga.")

    st.markdown("---")
    st.subheader("Daftar Periksa Keselarasan Regulasi (Regulatory Checklist)")

    reg_df = pd.DataFrame([
        {"Regulasi": "UU No. 18 Tahun 2008", "Fokus": "Pengelolaan Sampah Nasional", "Kesesuaian Solusi Tugu": "Sesuai (Mendorong pengolahan sampah berbasis teknologi)"},
        {"Regulasi": "Perpres No. 35 Tahun 2018", "Fokus": "Percepatan Pembangunan Instalasi WtE", "Kesesuaian Solusi Tugu": "Sesuai (Memberikan proteksi finansial pada 12 kota prioritas)"},
        {"Regulasi": "Taksonomi Hijau Indonesia 2.0 (OJK)", "Fokus": "Kategori Hijau (Sektor Energi Terbarukan)", "Kesesuaian Solusi Tugu": "Sesuai (Basis metodologi ESG Score di atas; memenuhi kriteria pembiayaan berkelanjutan/bankable)"},
        {"Regulasi": "Target Net Zero Emission (NZE) 2060", "Fokus": "Transisi Energi & Dekarbonisasi", "Kesesuaian Solusi Tugu": "Sesuai (Mendukung porsi EBT dalam bauran energi nasional)"}
    ])
    st.table(reg_df)
    st.success("✅ Solusi **Tugu CircularShield 360** secara penuh mematuhi seluruh koridor hukum dan regulasi EBT di Indonesia.")

# Footer
st.markdown("---")
st.caption("© 2026 Tim Khusaeni — Business Case Competition IDEANATION 2026 | Universitas Gunadarma")
