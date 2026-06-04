"""
PINTARIN – Explanatory Analysis (Data Asli)
Menjawab 3 Pertanyaan Bisnis Utama

Jalankan:
    python pintarin_explanatory.py

Pastikan file PINTARIN_MASTER_FINAL.csv berada di folder yang sama,
atau sesuaikan path DATA_PATH di bawah.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.gridspec import GridSpec

# ── Konfigurasi ─────────────────────────────────────────────────────────────
DATA_PATH  = "PINTARIN_MASTER_FINAL_5000.csv"
OUTPUT_DIR = "."          # folder simpan gambar
EXPORT_DPI = 180

PALETTE    = {"Rendah": "#2196F3", "Sedang": "#FF9800", "Tinggi": "#F44336"}
BG_COLOR   = "#F8F9FA"
TITLE_FONT = {"fontsize": 14, "fontweight": "bold", "color": "#1A237E"}
NOTE_FONT  = {"fontsize": 9,  "color": "#546E7A", "style": "italic"}

plt.rcParams.update({
    "figure.facecolor":  BG_COLOR,
    "axes.facecolor":    BG_COLOR,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ── Load data ────────────────────────────────────────────────────────────────
df_master = pd.read_csv(DATA_PATH)
df_master["Status_Resiko"] = pd.Categorical(
    df_master["Status_Resiko"], categories=["Rendah","Sedang","Tinggi"], ordered=True
)
df_2025 = df_master[df_master["Tahun"] == 2025].copy()

print(f"✔ Data loaded: {df_master.shape[0]} baris, {df_master['Kecamatan'].nunique()} kecamatan")
print(f"  Tahun: {sorted(df_master['Tahun'].unique())}")
print(f"  Kolom: {list(df_master.columns)}\n")


# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN BISNIS 1
# Apakah ketersediaan gedung SD berbanding lurus dengan rendahnya angka putus sekolah?
# ══════════════════════════════════════════════════════════════════════════════
def plot_pb1(df_2025):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(
        "PB 1 · Infrastruktur SD vs Angka Putus Sekolah (2025)",
        **TITLE_FONT, y=1.02
    )

    # ── Panel kiri: bubble scatter ──────────────────────────────────────────
    ax = axes[0]
    for status, grp in df_2025.groupby("Status_Resiko", observed=True):
        ax.scatter(
            grp["SD"], grp["Total_Warga_Rentan"],
            s=grp["Total_Populasi"] / 600,
            color=PALETTE[status], alpha=0.78,
            edgecolors="#37474F", linewidths=0.6,
            label=f"Resiko {status}"
        )
        # Label nama kecamatan untuk outlier ekstrem
        for _, row in grp.iterrows():
            if row["Total_Warga_Rentan"] > df_2025["Total_Warga_Rentan"].quantile(0.85) or \
               row["SD"] > df_2025["SD"].quantile(0.85):
                ax.annotate(
                    row["Kecamatan"].title(),
                    xy=(row["SD"], row["Total_Warga_Rentan"]),
                    xytext=(4, 4), textcoords="offset points",
                    fontsize=7, color="#263238"
                )

    # Garis tren
    m, b = np.polyfit(df_2025["SD"], df_2025["Total_Warga_Rentan"], 1)
    x_l = np.linspace(df_2025["SD"].min(), df_2025["SD"].max(), 100)
    ax.plot(x_l, m*x_l+b, "--", color="#78909C", lw=1.5, label="Tren keseluruhan")

    ax.set_xlabel("Jumlah Gedung SD per Kecamatan", fontsize=10)
    ax.set_ylabel("Total Warga Rentan Pendidikan", fontsize=10)
    ax.set_title("Scatter: SD vs Warga Rentan\n(ukuran gelembung ∝ populasi kecamatan)", fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    ax.legend(fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.text(0.02, -0.17,
        "★ Temuan: Tren naik dikendalikan kepadatan penduduk, bukan kualitas infrastruktur.\n"
        "   Kecamatan merah & biru berbagi jumlah SD serupa → faktor non-fisik lebih dominan.",
        transform=ax.transAxes, **NOTE_FONT)

    # ── Panel kanan: rata-rata SD per kelas risiko ──────────────────────────
    ax2 = axes[1]
    avg_sd = (df_2025.groupby("Status_Resiko", observed=True)["SD"]
              .mean().reindex(["Rendah","Sedang","Tinggi"]))
    bars = ax2.bar(avg_sd.index, avg_sd.values,
                   color=[PALETTE[s] for s in avg_sd.index],
                   width=0.5, edgecolor="white", linewidth=1.2)
    for bar, val in zip(bars, avg_sd.values):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.15,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax2.set_title("Rata-rata Jumlah SD\nper Kelas Risiko (2025)", fontsize=11)
    ax2.set_ylabel("Rata-rata Gedung SD", fontsize=10)
    ax2.set_ylim(0, avg_sd.max() * 1.35)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.text(0.02, -0.17,
        "★ Temuan: Tidak ada perbedaan signifikan rata-rata SD antar kelas risiko →\n"
        "   Penambahan gedung SD saja tidak cukup menekan angka putus sekolah.",
        transform=ax2.transAxes, **NOTE_FONT)

    plt.tight_layout()
    out = f"{OUTPUT_DIR}/pb1_infrastruktur_vs_putus_sekolah.png"
    fig.savefig(out, dpi=EXPORT_DPI, bbox_inches="tight")
    plt.close()
    print(f"✅ PB1 tersimpan → {out}")


# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN BISNIS 2
# Sejauh mana rasio warga rentan berkorelasi dengan status risiko pendidikan?
# ══════════════════════════════════════════════════════════════════════════════
def plot_pb2(df_master, df_2025):
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle(
        "PB 2 · Rasio Warga Rentan Ekonomi vs Status Risiko Pendidikan",
        **TITLE_FONT, y=1.02
    )
    gs = GridSpec(1, 2, figure=fig, wspace=0.38)

    # ── Panel kiri: boxplot ─────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    order = ["Rendah","Sedang","Tinggi"]
    sns.boxplot(
        data=df_2025, x="Status_Resiko", y="Rasio_Warga_Rentan",
        order=order, hue="Status_Resiko", palette=PALETTE,
        width=0.45, legend=False,
        flierprops=dict(marker="o", markerfacecolor="#B0BEC5", markersize=5),
        ax=ax1
    )
    for i, s in enumerate(order):
        med = df_2025[df_2025["Status_Resiko"]==s]["Rasio_Warga_Rentan"].median()
        ax1.text(i, med+0.08, f"Median\n{med:.1f}%",
                 ha="center", va="bottom", fontsize=8.5, color="#1A237E", fontweight="bold")

    ax1.set_title("Distribusi Rasio Warga Rentan\nper Kelas Risiko (2025)", fontsize=11)
    ax1.set_xlabel("Status Risiko", fontsize=10)
    ax1.set_ylabel("Rasio Warga Rentan (%)", fontsize=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.text(0.02, -0.17,
        "★ Temuan: Setiap kelas risiko terpisah jelas tanpa overlap →\n"
        "   Rasio warga rentan adalah prediktor sangat kuat untuk status risiko.",
        transform=ax1.transAxes, **NOTE_FONT)

    # ── Panel kanan: heatmap korelasi ───────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    enc = {"Rendah":0,"Sedang":1,"Tinggi":2}
    df_c = df_2025[["Rasio_Warga_Rentan","SD","Total_Bantuan_PIP","Total_Populasi"]].copy()
    df_c["Status_Resiko_Num"] = df_2025["Status_Resiko"].map(enc)
    corr = df_c.corr()[["Status_Resiko_Num"]].drop("Status_Resiko_Num")
    corr.index = ["Rasio Warga Rentan","Jumlah SD","Bantuan PIP","Total Populasi"]

    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="RdYlGn_r",
        vmin=-1, vmax=1, linewidths=0.5,
        cbar_kws={"shrink":0.75, "label":"Korelasi Pearson"},
        ax=ax2
    )
    ax2.set_title("Korelasi Fitur\nterhadap Status Risiko", fontsize=11)
    ax2.set_xlabel(""); ax2.set_ylabel("")
    ax2.text(0.02, -0.17,
        "★ Temuan: Rasio Warga Rentan memiliki korelasi tertinggi terhadap status risiko →\n"
        "   Faktor ekonomi jauh lebih berpengaruh dibanding ketersediaan infrastruktur.",
        transform=ax2.transAxes, **NOTE_FONT)

    plt.tight_layout()
    out = f"{OUTPUT_DIR}/pb2_rasio_rentan_vs_status_risiko.png"
    fig.savefig(out, dpi=EXPORT_DPI, bbox_inches="tight")
    plt.close()
    print(f"✅ PB2 tersimpan → {out}")


# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN BISNIS 3
# Kecamatan mana prioritas tertinggi untuk perluasan kuota PIP?
# ══════════════════════════════════════════════════════════════════════════════
def plot_pb3(df_2025):
    df_p = df_2025.copy()
    df_p["Cakupan_PIP_Pct"] = (df_p["Total_Bantuan_PIP"] / df_p["Total_Warga_Rentan"]) * 100
    df_p["Gap_Intervensi"]  = df_p["Total_Warga_Rentan"] - df_p["Total_Bantuan_PIP"]
    tinggi = (df_p[df_p["Status_Resiko"]=="Tinggi"]
              .sort_values("Gap_Intervensi", ascending=False))

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(
        "PB 3 · Prioritas Kecamatan untuk Perluasan Kuota PIP",
        **TITLE_FONT, y=1.02
    )

    # ── Panel kiri: horizontal bar gap ─────────────────────────────────────
    ax = axes[0]
    colors = ["#B71C1C" if i < 3 else "#EF9A9A" for i in range(len(tinggi))]
    bars = ax.barh(tinggi["Kecamatan"].str.title(),
                   tinggi["Gap_Intervensi"],
                   color=colors, edgecolor="white", height=0.7)
    ax.invert_yaxis()
    ax.set_title("Gap Intervensi PIP\n(Kecamatan Risiko Tinggi)", fontsize=11)
    ax.set_xlabel("Estimasi Warga Rentan Belum Terjangkau PIP", fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    for bar in bars:
        ax.text(bar.get_width()+100, bar.get_y()+bar.get_height()/2,
                f"{int(bar.get_width()):,}", va="center", fontsize=8)

    p1 = mpatches.Patch(color="#B71C1C", label="Top 3 Prioritas Absolut")
    p2 = mpatches.Patch(color="#EF9A9A", label="Prioritas Lanjutan")
    ax.legend(handles=[p1,p2], fontsize=8, loc="lower right")
    ax.text(0.02, -0.13,
        "★ Batang merah tua = kecamatan paling urgen untuk penambahan kuota PIP segera.",
        transform=ax.transAxes, **NOTE_FONT)

    # ── Panel kanan: scatter cakupan vs rasio ───────────────────────────────
    ax2 = axes[1]
    for status, grp in df_p.groupby("Status_Resiko", observed=True):
        ax2.scatter(
            grp["Rasio_Warga_Rentan"], grp["Cakupan_PIP_Pct"],
            color=PALETTE[status], s=80, alpha=0.82,
            edgecolors="#37474F", lw=0.5, label=f"Resiko {status}"
        )
    ax2.axhline(100, color="#78909C", linestyle="--", lw=1.2, label="Ideal (100%)")

    # Annotate top 3
    for _, row in tinggi.head(3).iterrows():
        ax2.annotate(
            row["Kecamatan"].title(),
            xy=(row["Rasio_Warga_Rentan"], row["Cakupan_PIP_Pct"]),
            xytext=(6, 6), textcoords="offset points",
            fontsize=7.5, color="#B71C1C",
            arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=0.8)
        )

    ax2.set_title("Cakupan PIP vs Rasio Warga Rentan\n(semua kecamatan, 2025)", fontsize=11)
    ax2.set_xlabel("Rasio Warga Rentan (%)", fontsize=10)
    ax2.set_ylabel("Cakupan PIP (% dari warga rentan)", fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.text(0.02, -0.13,
        "★ Kuadran kanan-bawah = risiko tinggi + cakupan PIP rendah → prioritas intervensi non-fisik.",
        transform=ax2.transAxes, **NOTE_FONT)

    plt.tight_layout()
    out = f"{OUTPUT_DIR}/pb3_prioritas_pip_kecamatan.png"
    fig.savefig(out, dpi=EXPORT_DPI, bbox_inches="tight")
    plt.close()
    print(f"✅ PB3 tersimpan → {out}")


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    plot_pb1(df_2025)
    plot_pb2(df_master, df_2025)
    plot_pb3(df_2025)
    print("\n🎉 Semua visualisasi explanatory berhasil dibuat!")
