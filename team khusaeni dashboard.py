import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Tugu Insurance WtE Risk & Financial Dashboard",
    page_icon="♻️",
    layout="wide"
)

# Custom Styling CSS untuk Tampilan Profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigasi
st.sidebar.title("📌 Navigasi Proposal Semifinal")
st.sidebar.image("https://images.unsplash.com/photo-1532996122724-e3c3fa4a0d5d?q=80&w=400&auto=format&fit=crop", use_container_width=True)
menu = st.sidebar.radio("Pilih Modul Analisis:", [
    "1. Overview & Ecosystem Risk Mapping",
    "2. End-to-End Insurance Solution & Pricing",
    "3. Carbon Credit & ESG Impact Calculator",
    "4. Financial Projection (3 Years)"
])

st.sidebar.markdown("---")
st.sidebar.info("💡 **IDEANATION 2026 - Semi-Final Business Case**\nTim Strategi Korporasi Tugu Insurance (TUGU)")

# ==========================================
# MODUL 1: OVERVIEW & RISK MAPPING
# ==========================================
if menu == "1. Overview & Ecosystem Risk Mapping":
    st.title("♻️ Tugu Insurance: Waste-to-Energy (WtE) Strategic Dashboard")
    st.markdown("Dashboard interaktif pemetaan risiko *end-to-end* dan solusi asuransi strategis untuk mendukung proyeksi Energi Baru Terbarukan (EBT) dan Net Zero Emission (NZE) 2060[cite: 2].")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Premi Tugu (Q4 2025)", "Rp 6,3 Triliun", "Peringkat ke-4 AAUI[cite: 2]")
    col2.metric("Target Reduksi Sampah", "30%", "Jakstranas[cite: 2]")
    col3.metric("Target Penanganan Sampah", "70%", "Jakstranas[cite: 2]")
    col4.metric("Rating Kekuatan Finansial", "A- / aaa.ID", "AM Best (Excellent)[cite: 2]")
    
    st.markdown("---")
    st.subheader("🗺️ End-to-End Project Lifecycle & Risk Exposure Mapping")
    
    lifecycle_data = pd.DataFrame({
        "Tahapan Siklus Proyek": [
            "1. Pengumpulan & Transportasi Sampah",
            "2. Konstruksi & EPC",
            "3. Commissioning & Boiler Testing",
            "4. Operasional Pembangkit (WtE)",
            "5. Distribusi Listrik (PLN Offtaker)",
            "6. Monetisasi Carbon Credit"
        ],
        "Risiko Utama": [
            "Feedstock Risk, Kecelakaan Logistik, Gangguan Rute[cite: 2]",
            "Keterlambatan Proyek, Over Budget, Force Majeure",
            "Kegagalan Mesin, Ledakan Boiler, Risiko Teknis[cite: 2]",
            "Pencemaran Lingkungan, Cyber Risk, Boiler Breakdown[cite: 2]",
            "Kegagalan Offtake, Fluktuasi Tarif, Regulatory Shift[cite: 2]",
            "Volatilitas Pasar Karbon, Perubahan Regulasi MRV[cite: 2]"
        ],
        "Solusi Produk Tugu": [
            "Marine & Logistics Liability Insurance",
            "Contractors All Risks (CAR)[cite: 2] + Delay in Start-Up (DSU)",
            "Machinery Breakdown (MB)[cite: 2] & Testing Cover",
            "Property All Risks (PAR)[cite: 2] + Environmental Liability",
            "Business Interruption & Credit Insurance",
            "Carbon Credit Guarantee & Price Volatility Cover"
        ]
    })
    
    st.dataframe(lifecycle_data, use_container_width=True)

# ==========================================
# MODUL 2: END-TO-END INSURANCE SOLUTION & PRICING
# ==========================================
elif menu == "2. End-to-End Insurance Solution & Pricing":
    st.title("🛡️ Simulasi Underwriting & Kapasitas Premi WtE")
    st.markdown("Simulasikan nilai proyek konstruksi dan operasional fasilitas *Waste-to-Energy* untuk melihat estimasi premi asuransi dan struktur reasuransi berlapis.")
    
    col1, col2 = st.columns(2)
    with col1:
        project_val = st.number_input("Nilai Total Proyek (dalam Rupiah)", min_value=10000000000, max_value=5000000000000, value=500000000000, step=50000000000)
        risk_profile = st.selectbox("Tingkat Risiko Proyek (Risk Grading)", ["Low (Standard Tech)", "Medium (Standard WtE)", "High (Complex Integration & Novel Tech)"])
    
    with col2:
        retention_pct = st.slider("Retensi Sendiri (Retention Tugu %)", min_value=5, max_value=25, value=10, step=5)
        co_insurance = st.checkbox("Gunakan Konsorsium Asuransi / Ko-asuransi", value=True)

    # Kalkulasi Otomatis
    base_rate = {"Low (Standard Tech)": 0.0035, "Medium (Standard WtE)": 0.0055, "High (Complex Integration & Novel Tech)": 0.0085}[risk_profile]
    total_premium = project_val * base_rate
    tugu_retention_amt = total_premium * (retention_pct / 100)
    reinsurance_amt = total_premium - tugu_retention_amt

    st.markdown("### 📊 Hasil Simulasi Finansial Underwriting")
    m1, m2, m3 = st.columns(3)
    m1.metric("Estimasi Premi Bruto", f"Rp {total_premium:,.0f}")
    m2.metric(f"Bagian Ditahan Tugu ({retention_pct}%)", f"Rp {tugu_retention_amt:,.0f}")
    m3.metric("Bagian Reasuransi Internasional", f"Rp {reinsurance_amt:,.0f}")

    # Grafik Alokasi Risiko
    fig = px.pie(
        names=["Retensi Tugu Insurance", "Reasuransi Berlapis (Treaty/Facultative)"],
        values=[tugu_retention_amt, reinsurance_amt],
        title="Struktur Kapasitas & Penempatan Risiko (Layered Reinsurance)"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODUL 3: CARBON CREDIT & ESG CALCULATOR
# ==========================================
elif menu == "3. Carbon Credit & ESG Impact Calculator":
    st.title("🌱 Kalkulator Dampak ESG & Reduksi Emisi Karbon WtE")
    st.markdown("Menghitung estimasi kapasitas reduksi emisi gas rumah kaca dari pengolahan sampah tonase harian dan potensi nilai ekonomi dari *carbon credit*.")

    col1, col2 = st.columns(2)
    with col1:
        daily_waste = st.slider("Volume Sampah Masuk (Ton / Hari)", min_value=500, max_value=5000, value=2000, step=100)
        operating_days = st.slider("Hari Operasional per Tahun", min_value=300, max_value=365, value=350, step=5)
    
    with col2:
        emission_factor = st.number_input("Faktor Reduksi Emisi (Ton CO2e / Ton Sampah)", value=0.5, step=0.1)
        carbon_price_usd = st.number_input("Harga Karbon per Ton CO2e (USD)", value=15.0, step=1.0)
        exchange_rate = st.number_input("Kurs USD ke IDR", value=16000.0, step=500.0)

    annual_waste = daily_waste * operating_days
    total_carbon_credits = annual_waste * emission_factor
    total_revenue_idr = total_carbon_credits * carbon_price_usd * exchange_rate

    st.markdown("### 📈 Proyeksi Hasil Pengelolaan Karbon Tahunan")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sampah Diolah / Tahun", f"{annual_waste:,.0f} Ton")
    c2.metric("Potensi Carbon Credit", f"{total_carbon_credits:,.0f} Ton CO2e")
    c3.metric("Estimasi Valuasi Pendapatan Karbon", f"Rp {total_revenue_idr:,.0f}")

# ==========================================
# MODUL 4: FINANCIAL PROJECTION (3 YEARS)
# ==========================================
elif menu == "4. Financial Projection (3 Years)":
    st.title("📈 Proyeksi Keuangan 3 Tahun (Tugu WtE Insurance Line)")
    st.markdown("Proyeksi pertumbuhan bisnis lini produk asuransi ekosistem *Waste-to-Energy* Tugu Insurance untuk 3 tahun ke depan.")

    years = ["Tahun 1 (Eksplorasi & Pilot)", "Tahun 2 (Scale-Up & Ekspansi)", "Tahun 3 (Market Leadership)"]
    premi_proyeksi = [75000000000, 210000000000, 480000000000]
    klaim_proyeksi = [30000000000, 84000000000, 182400000000]
    laba_proyeksi = [15000000000, 45000000000, 110000000000]

    df_proj = pd.DataFrame({
        "Tahun": years,
        "Pendapatan Premi (Rp)": premi_proyeksi,
        "Estimasi Klaim (Rp)": klaim_proyeksi,
        "Laba Underwriting (Rp)": laba_proyeksi
    })

    st.dataframe(df_proj, use_container_width=True)

    fig_bar = px.bar(
        df_proj, x="Tahun", y=["Pendapatan Premi (Rp)", "Laba Underwriting (Rp)"],
        barmode="group", title="Grafik Pertumbuhan Proyeksi Finansial 3 Tahun WtE"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.markdown("© 2026 Tim Semifinal Business Case Competition IDEANATION | Tugu Insurance Strategy")