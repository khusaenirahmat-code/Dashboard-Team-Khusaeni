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

# Custom CSS styling
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
# 2. HELPER & GENERATOR DATA DUMMY
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
    st.session_state.selected_modules = ["FeedGuard (Feedstock & Supply)", "Operational Shield"]

# ==========================================
# 3. SIDEBAR NAVIGATION
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
# 4. HALAMAN DASHBOARD
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
    Proyek Waste-to-Energy (WtE) memiliki risiko kompleksitas tinggi yang mencakup 5 fase utama. Solusi asuransi eksisting saat ini masih **parsial** (sebatas CAR, PAR, dan MB). **Tugu CircularShield 360** hadir sebagai jawaban holistik dengan unggulan **FeedGuard** — produk *Parametric Insurance* berbasis data real-time untuk mitigasi risiko pasokan sampah.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Target Proyek WtE Nasional", "12 Lokasi", "Perpres 35/2018")
    with col2:
        st.metric("Gap Asuransi Eksisting", "Parsial (CAR/PAR)", "Belum cover Feedstock/Carbon")
    with col3:
        st.metric("Potensi GWP (3 Tahun)", "Rp 148,5 Miliar", "Base Case Scenario")
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
            st.caption("Klaim parametrik otomatis tanpa perselisihan.")
    with c5:
        with st.container(border=True):
            st.markdown("**ENABLE**")
            st.caption("Meningkatkan Bankability & ESG rating.")

    st.markdown("---")
    st.subheader("Perbandingan: Asuransi Eksisting vs Tugu CircularShield 360")
    comp_df = pd.DataFrame({
        "Aspek": ["Cakupan Risiko", "Risiko Pasokan Sampah (Feedstock)", "Proses Klaim", "Monetisasi Karbon", "Dukungan Bankability"],
        "Asuransi Konvensional (Eksisting)": ["Parsial (Konstruksi & Mesin Fisik)", "Tidak Ditanggung (Dianggap risiko operasional)", "Membutuhkan Loss Adjuster & waktu lama", "Tidak Ada", "Terbatas pada Aset Fisik"],
        "Tugu CircularShield 360": ["End-to-End (5 Fase Lengkap)", "Ditanggung via FeedGuard Parametric", "Otomatis cair via Trigger Parameter Data", "Di-cover dalam Carbon Credit Shield", "Tinggi (Menjamin kepastian pendapatan)"]
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
    
    # Sankey diagram dengan kontras visual memadai
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
    
    risk_data = pd.DataFrame([
        {"Fase": "1. Pengumpulan & Feedstock", "Jenis Risiko": "Defisit Pasokan Sampah", "Severity": 5, "Likelihood": 4, "Status Eksisting": "Uninsured", "Solusi Tugu": "FeedGuard Parametric"},
        {"Fase": "1. Pengumpulan & Feedstock", "Jenis Risiko": "Kadar Air & Kalori Rendah", "Severity": 4, "Likelihood": 4, "Status Eksisting": "Uninsured", "Solusi Tugu": "FeedGuard Parametric"},
        {"Fase": "2. Konstruksi & EPC", "Jenis Risiko": "Keterlambatan Pembangunan", "Severity": 4, "Likelihood": 3, "Status Eksisting": "CAR Covered", "Solusi Tugu": "Development Shield"},
        {"Fase": "3. Operasional Pembangkit", "Jenis Risiko": "Boiler Explosion / Machinery Failure", "Severity": 5, "Likelihood": 2, "Status Eksisting": "MB Covered", "Solusi Tugu": "Operational Shield"},
        {"Fase": "3. Operasional Pembangkit", "Jenis Risiko": "Kebakaran Fasilitas", "Severity": 5, "Likelihood": 2, "Status Eksisting": "PAR Covered", "Solusi Tugu": "Operational Shield"},
        {"Fase": "4. Distribusi Listrik (PLN)", "Jenis Risiko": "Kegagalan Interkoneksi Grid", "Severity": 3, "Likelihood": 2, "Status Eksisting": "Uninsured", "Solusi Tugu": "Offtake Shield"},
        {"Fase": "5. Monetisasi Karbon", "Jenis Risiko": "Volatilitas Harga & Kegagalan Sertifikasi", "Severity": 3, "Likelihood": 3, "Status Eksisting": "Uninsured", "Solusi Tugu": "Carbon Credit Shield"}
    ])
    
    filtered_risk = risk_data[risk_data["Fase"].isin(fase_filter)]
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.dataframe(filtered_risk, use_container_width=True)
    with col2:
        fig_heat = px.scatter(
            filtered_risk, x="Likelihood", y="Severity", color="Fase",
            size=[20]*len(filtered_risk), hover_name="Jenis Risiko",
            title="Risk Heatmap (Severity vs Likelihood)",
            labels={"Likelihood": "Frekuensi (1-5)", "Severity": "Dampak Kerugian (1-5)"}
        )
        fig_heat.update_xaxes(range=[0.5, 5.5])
        fig_heat.update_yaxes(range=[0.5, 5.5])
        st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------
# PAGE 3: FEEDGUARD SIMULATOR (PARAMETRIC)
# ------------------------------------------
elif menu == "3. FeedGuard Simulator (Parametric)":
    st.title("⚡ FeedGuard Simulator")
    st.markdown("##### *Data-Driven Parametric Insurance Engine untuk Risiko Feedstock Sampah*")
    st.info("💡 **Fitur Utama:** Mensimulasikan deteksi otomatis, forecasting, dan pencairan klaim otomatis (*automatic payout trigger*) berdasarkan batas ambang pasokan harian.")
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
    
    fig_line = px.line(df_feed, x="Tanggal", y=["Volume_Ton", "Forecast_Trend"], 
                       labels={"value": "Volume Sampah (Ton/Hari)"},
                       title="Grafik Pasokan Sampah Harian Pembangkit WtE (365 Hari)",
                       color_discrete_map={"Volume_Ton": "#0056b3", "Forecast_Trend": "#ff7f0e"})
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Tahap 3 & 4: Parametric Trigger & Backtesting Simulator")
    
    col_param, col_res = st.columns([1, 2])
    
    with col_param:
        st.markdown("### 🎛️ Parameter Polis")
        target_capacity = st.number_input("Kebutuhan Operasional Normal (Ton/Hari):", value=1000, step=50)
        trigger_percent = st.slider("Trigger Threshold (% dari Kebutuhan):", min_value=50, max_value=90, value=70, step=5)
        trigger_val = target_capacity * (trigger_percent / 100.0)
        
        payout_per_day = st.number_input("Klaim per Hari Defisit (Rp Juta):", value=150, step=10)
        max_policy_limit = st.number_input("Maksimum Limit Polis per Tahun (Rp Miliar):", value=5.0, step=0.5) * 1e9
        annual_premium = st.number_input("Premi Tahunan (Rp Juta):", value=600, step=50) * 1e6
        
        st.caption(f"📌 **Penjelasan Trigger:** Jika pasokan harian < **{trigger_val:.0f} Ton** (< {trigger_percent}%), klaim otomatis cair sebesar **Rp {payout_per_day} Juta/hari** tanpa verifikasi kerugian fisik.")

    df_feed["Trigger_Active"] = df_feed["Volume_Ton"] < trigger_val
    df_feed["Deficit_Ton"] = np.where(df_feed["Trigger_Active"], trigger_val - df_feed["Volume_Ton"], 0)
    df_feed["Payout_IDR"] = np.where(df_feed["Trigger_Active"], payout_per_day * 1e6, 0)
    
    total_trigger_days = df_feed["Trigger_Active"].sum()
    raw_payout = df_feed["Payout_IDR"].sum()
    actual_payout = min(raw_payout, max_policy_limit)
    loss_ratio = (actual_payout / annual_premium) * 100 if annual_premium > 0 else 0

    with col_res:
        st.markdown("### 📊 Hasil Simulasi (Backtesting 1 Tahun)")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Hari Terjadi Defisit", f"{total_trigger_days} Hari", f"{(total_trigger_days/365)*100:.1f}% dari setahun")
        m2.metric("Total Pencairan Klaim", f"Rp {actual_payout/1e9:.2f} Miliar", "Otomatis Cair")
        m3.metric("Loss Ratio FeedGuard", f"{loss_ratio:.1f}%", "Sehat" if loss_ratio < 70 else "Tinggi")
        
        df_trigger_only = df_feed[df_feed["Trigger_Active"]]
        fig_payout = px.bar(df_trigger_only, x="Tanggal", y="Payout_IDR", 
                            title="Kejadian Aktivasi Trigger Klaim Otomatis",
                            labels={"Payout_IDR": "Nilai Klaim (Rp)"}, color_discrete_sequence=["#dc3545"])
        st.plotly_chart(fig_payout, use_container_width=True)

# ------------------------------------------
# PAGE 4: PRODUCT ARCHITECTURE MODULAR
# ------------------------------------------
elif menu == "4. Product Architecture Modular":
    st.title("🧩 Arsitektur Produk Modular (5 Modul)")
    st.markdown("Fleksibilitas pemilihan perlindungan berbasis kebutuhan spesifik pengembang proyek WtE.")
    st.markdown("---")
    
    st.markdown("### Pilih Kombinasi Modul Asuransi:")
    
    modules = {
        "Development Shield": {"fase": "Konstruksi & EPC", "base_premium": 800, "desc": "Perlindungan keterlambatan proyek, kegagalan uji coba (commissioning), & CAR."},
        "FeedGuard (Feedstock & Supply)": {"fase": "Pasokan Sampah", "base_premium": 600, "desc": "Parametric insurance terhadap risiko penurunan volume pasokan sampah & kalori."},
        "Operational Shield": {"fase": "Operasional Pembangkit", "base_premium": 1200, "desc": "Perlindungan PAR (kebakaran), MB (kerusakan mesin boiler/turbin), & kerugian bisnis."},
        "Offtake Shield": {"fase": "Distribusi & Grid", "base_premium": 400, "desc": "Penjaminan interferensi jaringan listrik PLN & risiko ketidakmampuan penyerapan daya."},
        "Carbon Credit Shield": {"fase": "Monetisasi Karbon", "base_premium": 300, "desc": "Perlindungan penurunan nilai pasar karbon & kegagalan verifikasi kredit karbon."}
    }
    
    selected = []
    total_est_premium = 0
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        for mod, details in modules.items():
            is_checked = st.checkbox(
                f"**{mod}** — Rp {details['base_premium']} Juta/tahun",
                value=(mod in st.session_state.selected_modules)
            )
            st.caption(f"📍 *Fase:* {details['fase']} | {details['desc']}")
            if is_checked:
                selected.append(mod)
                total_est_premium += details["base_premium"]
            st.markdown("---")
        st.session_state.selected_modules = selected

    with col_b:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 🛍️ Ringkasan Paketan Polis")
        st.markdown(f"**Modul Dipilih:** {len(selected)} dari 5 Modul")
        for s in selected:
            st.markdown(f"- ✅ {s}")
        
        st.markdown("---")
        st.markdown(f"### Total Estimasi Premi:\n# Rp {total_est_premium} Juta /thn")
        
        if len(selected) >= 4:
            st.success("🎉 **Diskon Bundling 10%** diterapkan karena memilih ≥ 4 Modul!")
            st.markdown(f"**Premi Final:** **Rp {total_est_premium * 0.9:.1f} Juta/thn**")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# PAGE 5: BUSINESS MODEL & NETWORK
# ------------------------------------------
elif menu == "5. Business Model & Network":
    st.title("🌐 Model Bisnis & Ekosistem Kolaborasi")
    st.markdown("Menghubungkan Tugu Insurance sebagai *Hub Utama* dalam ekosistem multi-pihak WtE.")
    st.markdown("---")
    
    st.subheader("Jaringan Kemitraan Tugu WtE Risk Hub")
    
    nodes_df = pd.DataFrame({
        "Entitas": ["Tugu Insurance (Hub)", "Pemerintah Daerah (Pemda)", "Kontraktor EPC", "PLN (Offtaker)", "Lembaga Pembiayaan / Investor", "Reasuransi Global"],
        "Peran": ["Underwriter & Pengelola Platform Risk Hub", "Penyedia Pasokan Sampah & Penanggung Tip Fee", "Pembangkit & Pengelola Fasilitas WtE", "Pembeli Listrik Pembangkit WtE", "Penyedia Modal Proyek (Project Financing)", "Penjamin Proteksi Risiko Katastropik"],
        "Alur Nilai (Value Flow)": ["Premi & Data Analytics", "Retribusi & Kebijakan", "Jaminan EPC & Operasional", "Power Purchase Agreement (PPA)", "Bankability Guarantee", "Kapasitas Reasuransi"]
    })
    
    st.table(nodes_df)
    
    st.markdown("---")
    st.subheader("Business Model Canvas (9-Box Summary)")
    
    bmc_c1, bmc_c2, bmc_c3 = st.columns(3)
    with bmc_c1:
        st.write("**Key Partners:** Pemda, PLN, Reasuransi, IoT Data Vendors")
        st.write("**Key Activities:** Underwriting, Parametric Data Analytics, Risk Inspection")
    with bmc_c2:
        st.write("**Value Proposition:** Proteksi End-to-End, Klaim Parametrik Otomatis, Peningkatan Bankability Proyek")
        st.write("**Customer Relationships:** Long-term Partnership, Automated Trigger Payouts")
    with bmc_c3:
        st.write("**Customer Segments:** Pengembang Proyek WtE, Investor EBT, Kontraktor EPC")
        st.write("**Revenue Streams:** Premi Asuransi Modular, Fee-based Risk Analytics")

# ------------------------------------------
# PAGE 6: FINANCIAL PROJECTION DYNAMIC
# ------------------------------------------
elif menu == "6. Financial Projection Dynamic":
    st.title("📈 Proyeksi Keuangan 3 Tahun (What-If Simulation)")
    st.markdown("Simulasi fleksibel untuk menguji kelayakan bisnis dan potensi pendapatan Tugu Insurance.")
    st.markdown("---")
    
    st.subheader("🎛️ Asumsi Skenario Proyeksi")
    scenario = st.radio("Pilih Skenario Otomatis:", ["Conservative", "Base Case", "Optimistic"], index=1, horizontal=True)
    
    if scenario == "Conservative":
        default_proj = [2, 4, 6]
        default_avg_prem = 3.5
        default_loss_ratio = 55.0
    elif scenario == "Base Case":
        default_proj = [3, 7, 12]
        default_avg_prem = 4.5
        default_loss_ratio = 48.0
    else: 
        default_proj = [5, 10, 18]
        default_avg_prem = 5.0
        default_loss_ratio = 40.0
        
    c1, c2, c3 = st.columns(3)
    with c1:
        avg_premium = st.number_input("Rata-rata Premi per Proyek (Rp Miliar/Tahun):", value=default_avg_prem, step=0.5)
    with c2:
        target_loss_ratio = st.slider("Target Loss Ratio (%):", min_value=30.0, max_value=80.0, value=default_loss_ratio, step=1.0)
    with c3:
        opex_ratio = st.slider("Rasio Operasional & Komisi (%):", min_value=10.0, max_value=30.0, value=15.0, step=1.0)
        
    years = ["Tahun 1 (2026)", "Tahun 2 (2027)", "Tahun 3 (2028)"]
    num_projects = default_proj
    
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
    st.dataframe(fin_df, use_container_width=True)
    
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

    with col_esg2:
        st.markdown("### 🤝 Social")
        st.markdown("- **Kesehatan Masyarakat:** Mengurangi risiko penyakit akibat TPA liar / *open dumping*.")
        st.markdown("- **Pemberdayaan Lokal:** Menciptakan lapangan kerja hijau di sektor pengelolaan sampah.")
        st.metric("Peningkatan Ketahanan Energi Local", "+150 MW", "Clean Power")

    with col_esg3:
        st.markdown("### 🏛️ Governance")
        st.markdown("- **Transparansi Data:** Penggunaan data sensor IoT real-time untuk penetapan klaim.")
        st.markdown("- **Standardisasi Risiko:** Menyusun benchmark manajemen risiko WtE pertama di Indonesia.")
        st.metric("ESG Alignment Score", "94 / 100", "Certified")

    st.markdown("---")
    st.subheader("Daftar Periksa Keselarasan Regulasi (Regulatory Checklist)")
    
    reg_df = pd.DataFrame([
        {"Regulasi": "UU No. 18 Tahun 2008", "Fokus": "Pengelolaan Sampah Nasional", "Kesesuaian Solusi Tugu": "Sesuai (Mendorong pengolahan sampah berbasis teknologi)"},
        {"Regulasi": "Perpres No. 35 Tahun 2018", "Fokus": "Percepatan Pembangunan Instalasi WtE", "Kesesuaian Solusi Tugu": "Sesuai (Memberikan proteksi finansial pada 12 kota prioritas)"},
        {"Regulasi": "Taksonomi Hijau Indonesia 2.0 (OJK)", "Fokus": "Kategori Hijau (Sektor Energi Terbarukan)", "Kesesuaian Solusi Tugu": "Sesuai (Memenuhi kriteria pembiayaan berkelanjutan/bankable)"},
        {"Regulasi": "Target Net Zero Emission (NZE) 2060", "Fokus": "Transisi Energi & Dekarbonisasi", "Kesesuaian Solusi Tugu": "Sesuai (Mendukung porsi EBT dalam bauran energi nasional)"}
    ])
    st.table(reg_df)
    st.success("✅ Solusi **Tugu CircularShield 360** secara penuh mematuhi seluruh koridor hukum dan regulasi EBT di Indonesia.")

# Footer
st.markdown("---")
st.caption("© 2026 Tim Khusaeni — Business Case Competition IDEANATION 2026 | Universitas Gunadarma")
