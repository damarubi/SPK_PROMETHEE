# SPK PROMETHEE — Sistem Pendukung Keputusan

Aplikasi web interaktif untuk pemilihan penerima **Beasiswa Tugas Belajar** menggunakan metode **PROMETHEE II** (Preference Ranking Organization Method for Enrichment Evaluations).

Dibuat oleh **Kelompok 3 — SPK-A**.

---

## Fitur

- Input data calon penerima beasiswa secara manual
- Perhitungan PROMETHEE II dengan 7 langkah transparan
- Visualisasi hasil ranking dengan chart interaktif
- Kesimpulan otomatis berdasarkan Net Flow

---

## Prasyarat

Pastikan sudah terinstall:

- **Python** 3.8 atau lebih baru — [Download Python](https://www.python.org/downloads/)
- **pip** (biasanya sudah terinstall bersama Python)

---

## Cara Menjalankan

### 1. Clone repositori

```bash
git clone https://github.com/<username>/SPK_PROMETHEE.git
cd SPK_PROMETHEE
```

### 2. Install dependensi

```bash
pip install -r requirements.txt
```

### 3. Jalankan aplikasi

```bash
python -m streamlit run app.py
```

### 4. Buka di browser

Setelah perintah di atas dijalankan, buka browser dan akses:

```
http://localhost:8501
```

---

## Cara Menggunakan

1. Di halaman **Beranda & Input**, masukkan data calon penerima beasiswa
2. Tekan tombol **Hitung PROMETHEE**
3. Buka halaman **Proses Perhitungan** untuk melihat langkah-langkah perhitungan
4. Buka halaman **Hasil Akhir** untuk melihat peringkat dan rekomendasi

---

## Teknologi

- [Streamlit](https://streamlit.io/) — Framework web app
- [Pandas](https://pandas.pydata.org/) — Pengolahan data
- [Plotly](https://plotly.com/) — Visualisasi chart
- Python — Bahasa pemrograman
