"""
PROMETHEE Calculation Engine
Metode: PROMETHEE II dengan Usual Criterion
"""
import pandas as pd
import numpy as np


def hitung_selisih(nilai_a, nilai_b):
    """Hitung selisih d = nilai_a - nilai_b untuk setiap kriteria."""
    return [a - b for a, b in zip(nilai_a, nilai_b)]


def fungsi_preferensi(d):
    """
    Usual Criterion:
    h(d) = 1 jika d > 0
    h(d) = 0 jika d <= 0
    """
    return [1 if val > 0 else 0 for val in d]


def hitung_semua_pasangan(df_nilai):
    """
    Hitung selisih d dan h(d) untuk semua pasangan alternatif.
    
    Parameters:
        df_nilai: DataFrame dengan kolom = kriteria, index = alternatif
    
    Returns:
        dict berisi:
          - 'pasangan': list of tuples (a, b)
          - 'd': dict {(a,b): list selisih per kriteria}
          - 'h': dict {(a,b): list h(d) per kriteria}
    """
    alternatif = df_nilai.index.tolist()
    kriteria = df_nilai.columns.tolist()
    
    hasil_d = {}
    hasil_h = {}
    pasangan = []
    
    for a in alternatif:
        for b in alternatif:
            if a != b:
                nilai_a = df_nilai.loc[a].values.tolist()
                nilai_b = df_nilai.loc[b].values.tolist()
                d = hitung_selisih(nilai_a, nilai_b)
                h = fungsi_preferensi(d)
                pasangan.append((a, b))
                hasil_d[(a, b)] = d
                hasil_h[(a, b)] = h
    
    return {
        'pasangan': pasangan,
        'd': hasil_d,
        'h': hasil_h,
        'kriteria': kriteria,
        'alternatif': alternatif
    }


def hitung_index_preferensi(hasil_pasangan):
    """
    Hitung Index Preferensi P(a,b) = rata-rata h(d) untuk semua kriteria.
    
    Returns:
        dict {(a,b): float index preferensi}
    """
    index_pref = {}
    for key, h_values in hasil_pasangan['h'].items():
        index_pref[key] = sum(h_values) / len(h_values)
    return index_pref


def buat_matriks_preferensi(index_pref, alternatif):
    """
    Buat matriks preferensi (DataFrame) dari index preferensi.
    """
    n = len(alternatif)
    matrix = pd.DataFrame(
        np.zeros((n, n)),
        index=alternatif,
        columns=alternatif
    )
    for (a, b), val in index_pref.items():
        matrix.loc[a, b] = val
    return matrix


def hitung_flow(matriks_pref):
    """
    Hitung Leaving Flow, Entering Flow, dan Net Flow.
    
    Leaving Flow  φ+(a) = (1/(n-1)) * Σ P(a,b) untuk semua b ≠ a
    Entering Flow φ-(a) = (1/(n-1)) * Σ P(b,a) untuk semua b ≠ a
    Net Flow = Leaving - Entering
    """
    alternatif = matriks_pref.index.tolist()
    n = len(alternatif)
    
    leaving = {}
    entering = {}
    net = {}
    
    for a in alternatif:
        leaving[a] = matriks_pref.loc[a].sum() / (n - 1)
        entering[a] = matriks_pref[a].sum() / (n - 1)
        net[a] = leaving[a] - entering[a]
    
    flow_df = pd.DataFrame({
        'Alternatif': alternatif,
        'Leaving Flow': [leaving[a] for a in alternatif],
        'Entering Flow': [entering[a] for a in alternatif],
        'Net Flow': [net[a] for a in alternatif]
    })
    
    return flow_df


def ranking(flow_df):
    """
    Urutkan alternatif berdasarkan Net Flow (descending) dan beri ranking.
    """
    result = flow_df.sort_values('Net Flow', ascending=False).reset_index(drop=True)
    result['Ranking'] = range(1, len(result) + 1)
    return result


def jalankan_promethee(df_nilai):
    """
    Jalankan seluruh proses PROMETHEE dan kembalikan semua hasil perhitungan.
    
    Parameters:
        df_nilai: DataFrame, index=nama alternatif, columns=nama kriteria, values=bobot numerik
    
    Returns:
        dict berisi semua langkah perhitungan
    """
    # Step 1: Hitung selisih dan preferensi semua pasangan
    hasil_pasangan = hitung_semua_pasangan(df_nilai)
    
    # Step 2: Hitung index preferensi
    index_pref = hitung_index_preferensi(hasil_pasangan)
    
    # Step 3: Buat matriks preferensi
    matriks_pref = buat_matriks_preferensi(index_pref, hasil_pasangan['alternatif'])
    
    # Step 4: Hitung flow
    flow_df = hitung_flow(matriks_pref)
    
    # Step 5: Ranking
    ranking_df = ranking(flow_df)
    
    return {
        'df_nilai': df_nilai,
        'hasil_pasangan': hasil_pasangan,
        'index_pref': index_pref,
        'matriks_pref': matriks_pref,
        'flow_df': flow_df,
        'ranking_df': ranking_df
    }
