"""
SPK PROMETHEE — Sistem Pendukung Keputusan
Metode PROMETHEE II · Pemilihan Penerima Beasiswa Tugas Belajar
Kelompok 3 — SPK-A
"""
import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from promethee import jalankan_promethee

# ──────────────────────────────────────────────────────────────
# KONFIGURASI
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPK PROMETHEE · Beasiswa Tugas Belajar",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*{font-family:'Inter',sans-serif}

.hero{
    background:linear-gradient(135deg,#4a4a4a 0%,#6b6b6b 100%);
    padding:2rem 2.5rem;border-radius:16px;margin-bottom:1.5rem;
    color:#fff;box-shadow:0 4px 16px rgba(0,0,0,.15);
    position:relative;overflow:hidden;
}
.hero::after{
    content:'';position:absolute;top:-50%;right:-15%;width:280px;height:280px;
    background:radial-gradient(circle,rgba(255,255,255,.12) 0%,transparent 70%);
    border-radius:50%;
}
.hero h1{margin:0;font-size:1.7rem;font-weight:700;letter-spacing:-.01em;color:#fff !important}
.hero p{margin:.4rem 0 0;opacity:.9;font-size:.95rem;font-weight:300;color:#fff !important}

.metric-card{
    background:#fff;border:1px solid #e0e2ea;border-radius:12px;
    padding:1.2rem;text-align:center;transition:transform .2s;
    box-shadow:0 2px 8px rgba(0,0,0,.04);
}
.metric-card:hover{transform:scale(1.02);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.metric-card h2{margin:0;font-size:2rem;color:#4a4a4a;font-weight:700}
.metric-card p{margin:.2rem 0 0;color:#888;font-size:.85rem}

.winner-box{
    background:linear-gradient(135deg,#43b89c 0%,#5cc9a7 100%);
    color:#fff;padding:1.6rem 2rem;border-radius:14px;
    font-size:1.1rem;font-weight:600;text-align:center;
    box-shadow:0 4px 16px rgba(67,184,156,.20);
    animation:pop .35s ease;
}
@keyframes pop{0%{transform:scale(.94);opacity:0}100%{transform:scale(1);opacity:1}}

.step-badge{
    display:inline-block;background:#555;
    color:#fff;font-weight:600;font-size:.78rem;padding:.25rem .8rem;
    border-radius:16px;margin-bottom:.4rem;
}

[data-testid="stSidebar"]{background:#f0f1f5}
[data-testid="stSidebar"] *{color:#444 !important}

.streamlit-expanderHeader{font-weight:600 !important;font-size:1rem !important}
div[data-testid="stExpander"]{border-radius:10px;border:1px solid #e0e2ea;margin-bottom:.4rem;
    background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.03)}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# DATA & MAPPING KRITERIA
# ──────────────────────────────────────────────────────────────
KRITERIA_INFO = {
    'K1': {'nama': 'Masa Kerja',
           'opsi': {'≥ 10 Tahun': 3, '6-9 Tahun': 2, '2-5 Tahun': 1},
           'help': 'Lamanya calon bekerja di instansi'},
    'K2': {'nama': 'Penghasilan',
           'opsi': {'2 - 2,5 juta/bln': 3, '2,5 - 3,5 juta/bln': 2, 'Passive': 1},
           'help': 'Pendapatan per bulan'},
    'K3': {'nama': 'Pengeluaran / bulan',
           'opsi': {'> 3 juta/bln': 3, '2 - 3 juta/bln': 2, '< 2 juta/bln': 1},
           'help': 'Total pengeluaran bulanan calon'},
    'K4': {'nama': 'Status Kepegawaian',
           'opsi': {'PNS': 2, 'PPPK': 1},
           'help': 'Status resmi kepegawaian calon'},
    'K5': {'nama': 'Kesesuaian Pendidikan',
           'opsi': {'Sesuai': 2, 'Tidak Sesuai': 1},
           'help': 'Kesesuaian pendidikan dengan kebutuhan daerah'},
}

DEFAULT_ALT = {
    'A1': {'K1': '≥ 10 Tahun',  'K2': '2,5 - 3,5 juta/bln', 'K3': '2 - 3 juta/bln', 'K4': 'PNS',  'K5': 'Sesuai'},
    'A2': {'K1': '6-9 Tahun',    'K2': '2,5 - 3,5 juta/bln', 'K3': '2 - 3 juta/bln', 'K4': 'PNS',  'K5': 'Sesuai'},
    'A3': {'K1': '≥ 10 Tahun',  'K2': 'Passive',             'K3': '< 2 juta/bln',   'K4': 'PNS',  'K5': 'Sesuai'},
    'A4': {'K1': '2-5 Tahun',    'K2': '2 - 2,5 juta/bln',   'K3': '2 - 3 juta/bln', 'K4': 'PPPK', 'K5': 'Sesuai'},
    'A5': {'K1': '6-9 Tahun',    'K2': '2 - 2,5 juta/bln',   'K3': '> 3 juta/bln',   'K4': 'PPPK', 'K5': 'Sesuai'},
}


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## PROMETHEE")
    st.caption("Sistem Pendukung Keputusan")
    st.divider()

    halaman = st.radio(
        "Navigasi",
        ["Beranda & Input", "Proses Perhitungan", "Hasil Akhir"],
        help="Pilih halaman yang ingin ditampilkan",
    )

    st.divider()
    st.markdown(
        "Metode **PROMETHEE II** untuk membantu memilih "
        "penerima **Beasiswa Tugas Belajar** secara objektif."
    )
    st.divider()
    st.caption("Kelompok 3 · SPK-A · 2026")


# ══════════════════════════════════════════════════════════════
#   HALAMAN 1 — BERANDA & INPUT
# ══════════════════════════════════════════════════════════════
if halaman == "Beranda & Input":

    st.markdown("""
    <div class="hero">
        <h1>Selamat Datang</h1>
        <p>Masukkan data calon penerima beasiswa, lalu tekan Hitung untuk memulai analisis</p>
    </div>
    """, unsafe_allow_html=True)

    tab_ref, tab_input = st.tabs(["Referensi Kriteria", "Input Data Calon"])

    # ── Tab Referensi ──
    with tab_ref:
        st.subheader("Panduan Penilaian Kriteria")
        st.info(
            "Tabel di bawah menjelaskan arti tiap nilai pada masing-masing kriteria. "
            "Gunakan sebagai acuan saat mengisi data calon."
        )
        cols = st.columns(len(KRITERIA_INFO))
        for i, (kode, info) in enumerate(KRITERIA_INFO.items()):
            with cols[i]:
                st.markdown(f"**{kode} — {info['nama']}**")
                df_b = pd.DataFrame(list(info['opsi'].items()), columns=['Kategori', 'Bobot'])
                st.dataframe(df_b, hide_index=True, use_container_width=True)

    # ── Tab Input ──
    with tab_input:
        st.subheader("Data Calon Penerima Beasiswa")

        jumlah_alt = st.number_input(
            "Jumlah calon yang dinilai",
            min_value=2, max_value=20, value=5, step=1,
            help="Minimal 2 calon agar bisa dibandingkan",
        )

        st.divider()

        default_names = list(DEFAULT_ALT.keys())
        data_rows = []

        for i in range(jumlah_alt):
            dname = default_names[i] if i < len(default_names) else f"A{i+1}"
            defaults = DEFAULT_ALT.get(dname, {})

            with st.expander(f"Calon #{i+1}", expanded=(i < 3)):
                nama = st.text_input(
                    "Nama / Kode",
                    value=dname,
                    key=f"nama_{i}",
                    help="Nama lengkap atau kode singkat",
                )
                c1, c2, c3, c4, c5 = st.columns(5)
                nilai = {}
                for col_w, (kode, info) in zip([c1, c2, c3, c4, c5], KRITERIA_INFO.items()):
                    with col_w:
                        opts = list(info['opsi'].keys())
                        def_val = defaults.get(kode, opts[0])
                        def_idx = opts.index(def_val) if def_val in opts else 0
                        pilihan = st.selectbox(
                            f"{kode} — {info['nama']}",
                            options=opts, index=def_idx,
                            key=f"{kode}_{i}", help=info['help'],
                        )
                        nilai[kode] = info['opsi'][pilihan]
                data_rows.append({'Alternatif': nama, **nilai})

        df_input = pd.DataFrame(data_rows)

        # Ringkasan
        st.divider()
        st.subheader("Ringkasan Data")
        st.dataframe(df_input.style.format(precision=0), use_container_width=True, hide_index=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><h2>{len(KRITERIA_INFO)}</h2><p>Kriteria</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><h2>{len(df_input)}</h2><p>Calon Dinilai</p></div>', unsafe_allow_html=True)
        with m3:
            pairs = len(df_input) * (len(df_input) - 1)
            st.markdown(f'<div class="metric-card"><h2>{pairs}</h2><p>Pasangan Dibandingkan</p></div>', unsafe_allow_html=True)

        # Tombol Hitung
        st.markdown("")
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            if st.button("Hitung PROMETHEE", use_container_width=True, type="primary"):
                with st.spinner("Sedang memproses perhitungan..."):
                    time.sleep(0.5)
                    df_nilai = df_input.set_index('Alternatif')
                    hasil = jalankan_promethee(df_nilai)
                    st.session_state.hasil = hasil
                    st.session_state.df_input = df_input
                st.toast("Perhitungan selesai!", icon="✅")
                st.success("Berhasil! Silakan buka halaman **Proses Perhitungan** atau **Hasil Akhir** di sidebar.")


# ══════════════════════════════════════════════════════════════
#   HALAMAN 2 — PROSES PERHITUNGAN (7 Langkah)
# ══════════════════════════════════════════════════════════════
elif halaman == "Proses Perhitungan":

    st.markdown("""
    <div class="hero">
        <h1>Langkah Perhitungan PROMETHEE</h1>
        <p>Seluruh proses ditampilkan secara transparan — klik setiap langkah untuk detailnya</p>
    </div>
    """, unsafe_allow_html=True)

    if 'hasil' not in st.session_state:
        st.warning("Belum ada data untuk dihitung. Silakan kembali ke **Beranda & Input**, isi data, lalu tekan **Hitung PROMETHEE**.")
        st.stop()

    hasil = st.session_state.hasil
    hp = hasil['hasil_pasangan']
    alt_list = hp['alternatif']
    krit_list = hp['kriteria']
    n = len(alt_list)

    # ── Langkah 1 — Hasil Pembobotan ──
    with st.expander("Langkah 1 — Hasil Pembobotan", expanded=True):
        st.markdown('<span class="step-badge">LANGKAH 1</span>', unsafe_allow_html=True)
        st.markdown(
            "Tabel ini menunjukkan **nilai bobot numerik** setiap calon berdasarkan "
            "data kualitatif yang telah dimasukkan."
        )
        st.dataframe(hasil['df_nilai'], use_container_width=True)

    # ── Langkah 2 — Cari Nilai Preferensi ──
    with st.expander("Langkah 2 — Cari Nilai Preferensi"):
        st.markdown('<span class="step-badge">LANGKAH 2</span>', unsafe_allow_html=True)
        st.markdown(
            "Untuk setiap pasangan **(a, b)**, hitung selisih **d = nilai(a) − nilai(b)**, "
            "lalu tentukan fungsi preferensi **h(d)** menggunakan *Usual Criterion*."
        )
        st.info("**Usual Criterion:** jika d > 0 → h(d) = 1 (a lebih baik) · jika d ≤ 0 → h(d) = 0 (tidak lebih baik)")

        for (a, b) in hp['pasangan']:
            d_vals = hp['d'][(a, b)]
            h_vals = hp['h'][(a, b)]
            st.markdown(f"**Pasangan ({a}, {b})**")
            col_d, col_h = st.columns(2)
            with col_d:
                st.caption("Selisih d")
                st.dataframe(pd.DataFrame([dict(zip(krit_list, d_vals))]), use_container_width=True, hide_index=True)
            with col_h:
                st.caption("Preferensi h(d)")
                st.dataframe(pd.DataFrame([dict(zip(krit_list, h_vals))]), use_container_width=True, hide_index=True)
            st.divider()

    # ── Langkah 3 — Cari Index Preferensi ──
    with st.expander("Langkah 3 — Cari Index Preferensi P(a, b)"):
        st.markdown('<span class="step-badge">LANGKAH 3</span>', unsafe_allow_html=True)
        st.markdown(
            "Index preferensi = rata-rata h(d) dari seluruh kriteria:  \n"
            "**P(a, b) = Σ h(d) / jumlah kriteria**"
        )
        rows_idx = []
        for (a, b) in hp['pasangan']:
            h_vals = hp['h'][(a, b)]
            p_val = sum(h_vals) / len(h_vals)
            rows_idx.append({
                'Pasangan': f"({a}, {b})",
                'h(d) per Kriteria': " + ".join(str(v) for v in h_vals),
                'Σ h(d)': sum(h_vals),
                f'P(a,b) = Σ/{len(krit_list)}': round(p_val, 4),
            })
        st.dataframe(pd.DataFrame(rows_idx), use_container_width=True, hide_index=True)

    # ── Langkah 4 — Tampilkan Matriks Index Preferensi ──
    with st.expander("Langkah 4 — Matriks Index Preferensi"):
        st.markdown('<span class="step-badge">LANGKAH 4</span>', unsafe_allow_html=True)
        st.markdown(
            "Semua nilai P(a, b) disusun ke dalam matriks. "
            "Baris = alternatif **a**, Kolom = alternatif **b**. Diagonal = 0."
        )
        st.dataframe(hasil['matriks_pref'].round(4), use_container_width=True)

    # ── Langkah 5 — Leaving Flow ──
    matriks = hasil['matriks_pref']

    with st.expander("Langkah 5 — Cari Leaving Flow φ⁺(a)"):
        st.markdown('<span class="step-badge">LANGKAH 5</span>', unsafe_allow_html=True)
        st.markdown(
            "**Leaving Flow** mengukur seberapa besar alternatif mendominasi yang lain.  \n"
            f"**φ⁺(a) = (1 / (n−1)) × Σ P(a, b)**  \n"
            f"Jumlah alternatif **n = {n}**, sehingga pembagi = **n − 1 = {n} − 1 = {n-1}**"
        )
        rows_lf = []
        for a in alt_list:
            others = [b for b in alt_list if b != a]
            vals = [matriks.loc[a, b] for b in others]
            sigma = sum(vals)
            lf = sigma / (n - 1)
            detail = " + ".join(f"P({a},{b})={v:.4f}" for b, v in zip(others, vals))
            rows_lf.append({
                'Alternatif': a,
                'Detail Penjumlahan': detail,
                'Σ P(a,b)': round(sigma, 4),
                f'φ⁺ = Σ/{n-1}': round(lf, 4),
            })
        st.dataframe(pd.DataFrame(rows_lf), use_container_width=True, hide_index=True)

    # ── Langkah 6 — Entering Flow ──
    with st.expander("Langkah 6 — Cari Entering Flow φ⁻(a)"):
        st.markdown('<span class="step-badge">LANGKAH 6</span>', unsafe_allow_html=True)
        st.markdown(
            "**Entering Flow** mengukur seberapa besar alternatif didominasi yang lain.  \n"
            f"**φ⁻(a) = (1 / (n−1)) × Σ P(b, a)**  \n"
            f"Jumlah alternatif **n = {n}**, sehingga pembagi = **n − 1 = {n} − 1 = {n-1}**"
        )
        rows_ef = []
        for a in alt_list:
            others = [b for b in alt_list if b != a]
            vals = [matriks.loc[b, a] for b in others]
            sigma = sum(vals)
            ef = sigma / (n - 1)
            detail = " + ".join(f"P({b},{a})={v:.4f}" for b, v in zip(others, vals))
            rows_ef.append({
                'Alternatif': a,
                'Detail Penjumlahan': detail,
                'Σ P(b,a)': round(sigma, 4),
                f'φ⁻ = Σ/{n-1}': round(ef, 4),
            })
        st.dataframe(pd.DataFrame(rows_ef), use_container_width=True, hide_index=True)

    # ── Langkah 7 — Net Flow ──
    with st.expander("Langkah 7 — Cari Net Flow"):
        st.markdown('<span class="step-badge">LANGKAH 7</span>', unsafe_allow_html=True)
        st.markdown("**Net Flow = φ⁺ − φ⁻** — semakin tinggi (positif) → semakin baik.")

        flow_df = hasil['flow_df'].copy()
        flow_df['Perhitungan'] = flow_df.apply(
            lambda r: f"{r['Leaving Flow']:.4f} − {r['Entering Flow']:.4f} = {r['Net Flow']:.4f}", axis=1,
        )
        st.dataframe(
            flow_df[['Alternatif', 'Leaving Flow', 'Entering Flow', 'Net Flow', 'Perhitungan']].round(4),
            use_container_width=True, hide_index=True,
        )
        st.success("Semua langkah selesai. Buka halaman **Hasil Akhir** untuk melihat peringkat.")


# ══════════════════════════════════════════════════════════════
#   HALAMAN 3 — HASIL AKHIR
# ══════════════════════════════════════════════════════════════
elif halaman == "Hasil Akhir":

    st.markdown("""
    <div class="hero">
        <h1>Hasil & Peringkat Akhir</h1>
        <p>Rekomendasi berdasarkan perhitungan PROMETHEE II</p>
    </div>
    """, unsafe_allow_html=True)

    if 'hasil' not in st.session_state:
        st.warning("Belum ada hasil. Silakan kembali ke **Beranda & Input**, isi data, lalu tekan **Hitung PROMETHEE**.")
        st.stop()

    hasil = st.session_state.hasil
    ranking_df = hasil['ranking_df'].copy()
    pemenang = ranking_df.iloc[0]

    # Winner
    st.markdown(
        f'<div class="winner-box">'
        f'Rekomendasi terbaik: <b>{pemenang["Alternatif"]}</b> '
        f'dengan Net Flow <b>{pemenang["Net Flow"]:.4f}</b>'
        f'</div>', unsafe_allow_html=True,
    )
    st.markdown("")

    # Tabel + Chart side by side
    col_tabel, col_chart = st.columns([1, 1])

    with col_tabel:
        st.subheader("Tabel Peringkat")
        rank_emoji = {1: '🥇', 2: '🥈', 3: '🥉'}
        rd = ranking_df.copy()
        rd['Ranking'] = rd['Ranking'].apply(lambda r: f"{rank_emoji.get(r, '   ')} {r}")
        rd[['Net Flow', 'Leaving Flow', 'Entering Flow']] = rd[['Net Flow', 'Leaving Flow', 'Entering Flow']].round(4)
        st.dataframe(
            rd[['Ranking', 'Alternatif', 'Leaving Flow', 'Entering Flow', 'Net Flow']],
            use_container_width=True, hide_index=True,
        )

    with col_chart:
        st.subheader("Visualisasi Net Flow")
        colors = ['#43b89c' if v >= 0 else '#e05c5c' for v in ranking_df['Net Flow']]
        fig = go.Figure(go.Bar(
            x=ranking_df['Alternatif'], y=ranking_df['Net Flow'],
            marker_color=colors, text=ranking_df['Net Flow'].round(4),
            textposition='outside', textfont=dict(size=13, color='#333'),
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#444', family='Inter'),
            xaxis=dict(title='Alternatif', gridcolor='#e8e8e8'),
            yaxis=dict(title='Net Flow', gridcolor='#e8e8e8',
                       zeroline=True, zerolinecolor='#ccc'),
            margin=dict(t=20, b=40), height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Leaving vs Entering
    st.divider()
    st.subheader("Perbandingan Leaving vs Entering Flow")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name='Leaving Flow φ⁺', x=ranking_df['Alternatif'], y=ranking_df['Leaving Flow'],
        marker_color='#555', text=ranking_df['Leaving Flow'].round(3), textposition='outside',
    ))
    fig2.add_trace(go.Bar(
        name='Entering Flow φ⁻', x=ranking_df['Alternatif'], y=ranking_df['Entering Flow'],
        marker_color='#999', text=ranking_df['Entering Flow'].round(3), textposition='outside',
    ))
    fig2.update_layout(
        barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#444', family='Inter'),
        xaxis=dict(title='Alternatif', gridcolor='#e8e8e8'),
        yaxis=dict(gridcolor='#e8e8e8'),
        legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'),
        margin=dict(t=40, b=40), height=350,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Kesimpulan
    st.divider()
    st.subheader("Kesimpulan")
    n_alt = len(ranking_df)
    st.markdown(
        f"Berdasarkan pemeringkatan dengan **{n_alt} data** penilaian calon penerima beasiswa, "
        f"alternatif **{pemenang['Alternatif']}** memperoleh **Net Flow tertinggi "
        f"({pemenang['Net Flow']:.4f})** dan merupakan calon yang **direkomendasikan** "
        f"untuk menerima beasiswa tugas belajar."
    )
