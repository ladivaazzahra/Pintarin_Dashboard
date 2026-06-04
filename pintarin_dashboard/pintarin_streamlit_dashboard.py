import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PINTARIN · Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .block-container { padding: 2rem 2.5rem; }

    .section-header {
        border-left: 5px solid #4f8ef7;
        padding-left: 12px;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .section-header h3 { color: white; margin: 0; }

    .kpi-card {
        background: #1a1a2e;
        border: 1px solid #2d2d44;
        border-top: 3px solid #4f8ef7;
        padding: 20px 16px;
        border-radius: 10px;
        text-align: center;
    }
    .kpi-value { font-size: 1.9rem; font-weight: 800; color: #4f8ef7; }
    .kpi-value.red { color: #e76f51; }
    .kpi-label { font-size: 0.72rem; color: #8888aa; margin-top: 6px;
                 text-transform: uppercase; letter-spacing: 0.06em; }

    .insight-box {
        background: #1a1a2e;
        border-left: 4px solid #4f8ef7;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0 18px;
        font-size: 0.88rem;
        color: #c8d0e0;
        line-height: 1.6;
    }
    .finding-box {
        background: #0d2218;
        border-left: 4px solid #2a9d8f;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 0.88rem;
        color: #a8e6cf;
        line-height: 1.6;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600; font-size: 0.85rem;
        border-radius: 6px; padding: 8px 14px;
    }
</style>
""", unsafe_allow_html=True)

BG_MAIN  = "#0e1117"
BG_PANEL = "#1a1a2e"
PALETTE  = {"Rendah": "#4f8ef7", "Sedang": "#e9c46a", "Tinggi": "#e76f51"}
ORDER    = ["Rendah", "Sedang", "Tinggi"]
WHITE    = "white"
GRAY     = "#8888aa"

def dark_ax(fig, ax):
    fig.patch.set_facecolor(BG_MAIN)
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=WHITE)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.title.set_color(WHITE)
    for spine in ax.spines.values():
        spine.set_color("#444466")
    ax.grid(axis="y", alpha=0.15, color=WHITE)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("PINTARIN_MASTER_FINAL_5000.csv")
    df["Status_Resiko"] = pd.Categorical(
        df["Status_Resiko"], categories=ORDER, ordered=True
    )
    return df

df_master = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎓 PINTARIN")
    st.caption("Pemetaan Urgensi Pendidikan\nKota Bandung")
    st.divider()
    tahun_filter  = st.selectbox("📅 Tahun Analisis",
                                  sorted(df_master["Tahun"].unique(), reverse=True))
    risiko_filter = st.multiselect("🎯 Filter Status Risiko", ORDER, default=ORDER)
    st.divider()
    st.caption(f"Total data: {len(df_master):,} baris\n"
               f"{df_master['Kecamatan'].nunique()} kecamatan · "
               f"{df_master['Tahun'].nunique()} tahun")

df_t = df_master[
    (df_master["Tahun"] == tahun_filter) &
    (df_master["Status_Resiko"].isin(risiko_filter))
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎓 PINTARIN")
st.caption(f"Pemetaan Urgensi Pendidikan Kota Bandung · Tahun: {tahun_filter} · {len(df_t)} kecamatan")
st.markdown("---")

# ── KPI ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_rentan = int(df_t["Total_Warga_Rentan"].sum())
total_pip    = int(df_t["Total_Bantuan_PIP"].sum())
avg_rasio    = df_t["Rasio_Warga_Rentan"].mean()
n_tinggi     = int((df_t["Status_Resiko"] == "Tinggi").sum())

with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{total_rentan:,}</div>
        <div class="kpi-label">Total Warga Rentan</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{total_pip:,}</div>
        <div class="kpi-label">Total Penerima PIP</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value">{avg_rasio:.1f}%</div>
        <div class="kpi-label">Rata-rata Warga Rentan</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value red">{n_tinggi}</div>
        <div class="kpi-label">Kecamatan Risiko Tinggi</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📌 PB 1 · Infrastruktur SD vs Putus Sekolah",
    "📊 PB 2 · Faktor Risiko Pendidikan",
    "🎯 PB 3 · Prioritas Perluasan PIP",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""<div class="section-header"><h3>PB 1 · Infrastruktur SD vs Putus Sekolah</h3></div>
    <p style="color:#8888aa"><em>Apakah lebih banyak gedung SD berarti lebih sedikit anak putus sekolah?</em></p>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
    🔍 <b>Yang ingin kita ketahui:</b> Apakah kecamatan yang punya banyak sekolah dasar otomatis punya
    lebih sedikit warga yang tidak tamat sekolah? Ternyata jawabannya <b>tidak sesederhana itu.</b>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏫 Jumlah SD vs Warga Tidak Tamat Sekolah")
        fig, ax = plt.subplots(figsize=(7, 5))
        dark_ax(fig, ax)
        ax.grid(True, alpha=0.15, color=WHITE)

        for status in ORDER:
            grp = df_t[df_t["Status_Resiko"] == status]
            ax.scatter(grp["SD"], grp["Total_Warga_Rentan"],
                       color=PALETTE[status], s=70, alpha=0.82,
                       edgecolors="#222244", linewidths=0.5, label=f"Resiko {status}")
            for _, row in grp.iterrows():
                if row["Total_Warga_Rentan"] > df_t["Total_Warga_Rentan"].quantile(0.82) or \
                   row["SD"] > df_t["SD"].quantile(0.87):
                    ax.annotate(row["Kecamatan"].title(),
                                xy=(row["SD"], row["Total_Warga_Rentan"]),
                                xytext=(4, 4), textcoords="offset points",
                                fontsize=7, color=WHITE)

        m, b = np.polyfit(df_t["SD"], df_t["Total_Warga_Rentan"], 1)
        x_l = np.linspace(df_t["SD"].min(), df_t["SD"].max(), 100)
        ax.plot(x_l, m*x_l+b, "--", color="#aaaacc", lw=1.5, label="Tren")

        ax.set_xlabel("Jumlah Gedung SD", color=WHITE)
        ax.set_ylabel("Total Warga Tidak Tamat Sekolah", color=WHITE)
        ax.set_title("Scatter: SD vs Warga Rentan", color=WHITE, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.legend(facecolor=BG_PANEL, labelcolor=WHITE, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("📊 Rata-rata SD per Kelas Risiko")
        avg_sd = df_t.groupby("Status_Resiko", observed=True)["SD"].mean().reindex(ORDER)

        fig, ax = plt.subplots(figsize=(7, 5))
        dark_ax(fig, ax)

        bars = ax.bar(avg_sd.index, avg_sd.values,
                      color=[PALETTE[s] for s in ORDER],
                      width=0.5, edgecolor="#222244", linewidth=0.8)
        for bar, val in zip(bars, avg_sd.values):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    f"{val:.1f}", ha="center", va="bottom",
                    fontsize=13, fontweight="bold", color=WHITE)

        ax.set_title("Rata-rata Gedung SD per Kelas Risiko", color=WHITE, fontweight="bold")
        ax.set_ylabel("Rata-rata Gedung SD", color=WHITE)
        ax.set_ylim(0, avg_sd.max()*1.35)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.success("**Kesimpulan PB 1:** Rata-rata jumlah SD di kecamatan risiko tinggi (14.9) hampir sama "
               "dengan risiko rendah (18.2). Menambah gedung SD saja tidak cukup — faktor penentu utama "
               "adalah **kondisi ekonomi keluarga**, bukan kuantitas infrastruktur fisik.")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""<div class="section-header"><h3>PB 2 · Faktor Risiko Pendidikan</h3></div>
    <p style="color:#8888aa"><em>Apa yang paling menentukan risiko pendidikan suatu wilayah?</em></p>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
    🔍 <b>Yang ingin kita ketahui:</b> Di antara semua faktor — jumlah sekolah, bantuan PIP,
    jumlah penduduk, dan kondisi ekonomi — <b>faktor mana yang paling berpengaruh</b> terhadap
    tingginya risiko pendidikan di suatu kecamatan?
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 % Warga Tidak Tamat Sekolah per Kelas Risiko")
        stats = df_t.groupby("Status_Resiko", observed=True)["Rasio_Warga_Rentan"].mean().reindex(ORDER)

        fig, ax = plt.subplots(figsize=(7, 5))
        dark_ax(fig, ax)

        bars = ax.bar(stats.index, stats.values,
                      color=[PALETTE[s] for s in ORDER],
                      width=0.5, edgecolor="#222244")
        for bar, val in zip(bars, stats.values):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    f"{val:.1f}%", ha="center", va="bottom",
                    fontsize=13, fontweight="bold", color=WHITE)

        ax.set_title("Rata-rata % Warga Rentan per Kelas Risiko", color=WHITE, fontweight="bold")
        ax.set_xlabel("Tingkat Risiko", color=WHITE)
        ax.set_ylabel("% Warga Tidak Tamat Sekolah", color=WHITE)
        ax.set_ylim(0, stats.max()*1.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("🎯 Faktor yang Paling Berpengaruh terhadap Risiko")
        enc = {"Rendah": 0, "Sedang": 1, "Tinggi": 2}
        df_c = df_t[["Rasio_Warga_Rentan", "SD", "Total_Bantuan_PIP", "Total_Populasi"]].copy()
        df_c["Status_Resiko_Num"] = df_t["Status_Resiko"].map(enc)
        corr_vals = df_c.corr()["Status_Resiko_Num"].drop("Status_Resiko_Num")

        faktor_df = pd.DataFrame({
            "Faktor": ["Proporsi Warga\nTidak Tamat Sekolah",
                       "Total\nPenduduk",
                       "Jumlah\nGedung SD",
                       "Jumlah\nPenerima PIP"],
            "Nilai": [corr_vals["Rasio_Warga_Rentan"],
                      corr_vals["Total_Populasi"],
                      corr_vals["SD"],
                      corr_vals["Total_Bantuan_PIP"]],
        }).sort_values("Nilai")

        colors_bar = ["#e76f51" if v > 0.5 else "#e9c46a" if v > 0 else "#8888aa"
                      for v in faktor_df["Nilai"]]

        fig, ax = plt.subplots(figsize=(7, 5))
        dark_ax(fig, ax)
        ax.grid(axis="x", alpha=0.15, color=WHITE)
        ax.grid(axis="y", alpha=0)

        bars = ax.barh(faktor_df["Faktor"], faktor_df["Nilai"],
                       color=colors_bar, edgecolor="#222244", height=0.5)
        for bar, val in zip(bars, faktor_df["Nilai"]):
            ax.text(val + 0.02 if val >= 0 else val - 0.02,
                    bar.get_y() + bar.get_height()/2,
                    f"{val:.2f}", va="center",
                    fontsize=10, fontweight="bold", color=WHITE)

        ax.axvline(0, color="#aaaacc", lw=1, linestyle="--")
        ax.set_title("Tingkat Pengaruh Tiap Faktor\nterhadap Status Risiko", color=WHITE, fontweight="bold")
        ax.set_xlabel("Korelasi (-1 hingga +1)", color=WHITE)
        ax.set_xlim(-0.5, 1.3)
        ax.tick_params(colors=WHITE)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.success("**Kesimpulan PB 2:** Proporsi warga tidak tamat sekolah memiliki pengaruh sangat besar "
               "(0.92 dari skala 1.0) — jauh di atas faktor lainnya. "
               "**Kemiskinan dan kondisi ekonomi keluarga adalah akar utama masalah pendidikan.**")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""<div class="section-header"><h3>PB 3 · Prioritas Perluasan PIP</h3></div>
    <p style="color:#8888aa"><em>Kecamatan mana yang paling butuh tambahan bantuan PIP?</em></p>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
    🔍 <b>Cara menentukan prioritas:</b> Kecamatan diprioritaskan berdasarkan —
    (1) termasuk <b>risiko tinggi</b>, dan (2) memiliki <b>gap terbesar</b> antara jumlah warga
    yang tidak tamat sekolah dengan jumlah yang sudah menerima bantuan PIP.
    </div>""", unsafe_allow_html=True)

    df_p = df_t.copy()
    df_p["Cakupan_PIP_Pct"] = (df_p["Total_Bantuan_PIP"] / df_p["Total_Warga_Rentan"]) * 100
    df_p["Gap_Intervensi"]  = df_p["Total_Warga_Rentan"] - df_p["Total_Bantuan_PIP"]
    tinggi = df_p[df_p["Status_Resiko"] == "Tinggi"].sort_values("Gap_Intervensi", ascending=False)

    # ── Tabel prioritas ──────────────────────────────────────────────────────
    st.markdown("#### 🔴 Urutan Kecamatan Prioritas (Risiko Tinggi)")

    tabel = tinggi[["Kecamatan", "Total_Warga_Rentan", "Total_Bantuan_PIP",
                     "Gap_Intervensi", "Cakupan_PIP_Pct", "Rasio_Warga_Rentan"]].copy()
    tabel.columns = ["Kecamatan", "Warga Tidak Tamat Sekolah", "Sudah Dapat PIP",
                     "Belum Terjangkau PIP", "Cakupan PIP (%)", "% Warga Rentan"]
    tabel = tabel.reset_index(drop=True)
    tabel.index += 1

    def highlight_top3(row):
        # dark red highlight yang terbaca di dark theme
        if row.name <= 3:
            return ["background-color:#5c1a1a; color:#ff9999; font-weight:bold"] * len(row)
        return ["color: white"] * len(row)

    st.dataframe(
        tabel.style.apply(highlight_top3, axis=1)
             .format({
                 "Warga Tidak Tamat Sekolah": "{:,.0f}",
                 "Sudah Dapat PIP":           "{:,.0f}",
                 "Belum Terjangkau PIP":      "{:,.0f}",
                 "Cakupan PIP (%)":           "{:.1f}%",
                 "% Warga Rentan":            "{:.1f}%",
             }),
        use_container_width=True, height=340
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Warga yang Belum Terjangkau PIP")
        tinggi_s = tinggi.sort_values("Gap_Intervensi")
        colors_bar = ["#b71c1c" if i >= len(tinggi_s)-3 else "#ef9a9a"
                      for i in range(len(tinggi_s))]

        fig, ax = plt.subplots(figsize=(7, max(5, len(tinggi_s)*0.55)))
        dark_ax(fig, ax)
        ax.grid(axis="x", alpha=0.15, color=WHITE)
        ax.grid(axis="y", alpha=0)

        ax.barh(tinggi_s["Kecamatan"].str.title(),
                tinggi_s["Gap_Intervensi"],
                color=colors_bar, edgecolor="#222244", height=0.7)
        ax.invert_yaxis()
        ax.set_xlabel("Estimasi Warga Belum Terjangkau PIP", color=WHITE)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.tick_params(colors=WHITE)
        ax.set_title("Gap Intervensi PIP\n(Kecamatan Risiko Tinggi)", color=WHITE, fontweight="bold")

        p1 = mpatches.Patch(color="#b71c1c", label="Top 3 Prioritas Absolut")
        p2 = mpatches.Patch(color="#ef9a9a", label="Prioritas Lanjutan")
        ax.legend(handles=[p1, p2], facecolor=BG_PANEL, labelcolor=WHITE, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("🎯 Cakupan PIP vs % Warga Rentan")
        fig, ax = plt.subplots(figsize=(7, 5))
        dark_ax(fig, ax)
        ax.grid(True, alpha=0.15, color=WHITE)

        for status in ORDER:
            grp = df_p[df_p["Status_Resiko"] == status]
            ax.scatter(grp["Rasio_Warga_Rentan"], grp["Cakupan_PIP_Pct"],
                       color=PALETTE[status], s=70, alpha=0.85,
                       edgecolors="#222244", lw=0.5, label=f"Resiko {status}")

        ax.axhline(100, color="#aaaacc", linestyle="--", lw=1.5, label="Target Ideal 100%")

        for _, row in tinggi.head(3).iterrows():
            ax.annotate(row["Kecamatan"].title(),
                        xy=(row["Rasio_Warga_Rentan"], row["Cakupan_PIP_Pct"]),
                        xytext=(6, 6), textcoords="offset points",
                        fontsize=7.5, color="#ff9999",
                        arrowprops=dict(arrowstyle="->", color="#ff9999", lw=0.8))

        ax.set_xlabel("% Warga Tidak Tamat Sekolah", color=WHITE)
        ax.set_ylabel("Cakupan PIP (% dari warga rentan)", color=WHITE)
        ax.set_title("Cakupan PIP vs Rasio Warga Rentan\n(semua kecamatan)", color=WHITE, fontweight="bold")
        ax.legend(facecolor=BG_PANEL, labelcolor=WHITE, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.success("**Kesimpulan PB 3:** Tidak ada satu pun kecamatan yang cakupan PIP-nya mencapai 100%. "
               "**Babakan Ciparay, Bandung Kulon, dan Bojongloa Kaler** adalah tiga kecamatan paling "
               "mendesak untuk mendapat tambahan kuota PIP berdasarkan gap intervensi terbesar.")

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("PINTARIN © 2025 · Biar Bantuan Pendidikan Nggak Salah Sasaran! · Data Science Team")
