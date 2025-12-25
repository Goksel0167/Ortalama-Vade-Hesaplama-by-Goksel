"""
Ortalama vade hesaplama ve Excel export fonksiyonları
"""
import pandas as pd
from io import BytesIO
from datetime import datetime


def toplam_tutar_hesapla(tutarlar):
    """
    Fatura tutarlarının toplamını hesaplar
    
    Args:
        tutarlar (list): Fatura tutarları listesi
    
    Returns:
        float: Toplam tutar
    """
    return sum(tutarlar)


def agirlikli_ortalama_vade_hesapla(tutarlar, vadeler):
    """
    Ağırlıklı ortalama vade hesaplar
    
    Formül: Σ(Tutar × Vade) / Σ(Tutar)
    
    Args:
        tutarlar (list): Fatura tutarları listesi
        vadeler (list): Vade günleri listesi
    
    Returns:
        float: Ağırlıklı ortalama vade (gün)
    """
    if not tutarlar or sum(tutarlar) == 0:
        return 0
    
    toplam_agirlikli = sum(tutar * vade for tutar, vade in zip(tutarlar, vadeler))
    toplam_tutar = sum(tutarlar)
    
    return toplam_agirlikli / toplam_tutar


def excel_export(df, valor_tarihi, ortalama_vade, cek_vadesi):
    """
    Fatura bilgilerini ve hesaplama sonuçlarını Excel dosyasına aktarır
    
    Args:
        df (DataFrame): Fatura bilgileri
        valor_tarihi (date): Valör tarihi
        ortalama_vade (float): Hesaplanan ortalama vade
        cek_vadesi (date): Önerilen çek vadesi
    
    Returns:
        BytesIO: Excel dosyası buffer
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Fatura listesi sayfası
        df_export = df.copy()
        df_export.to_excel(writer, sheet_name='Faturalar', index=False)
        
        # Özet bilgiler sayfası
        ozet_data = {
            'Açıklama': [
                'Valör Tarihi',
                'Toplam Fatura Tutarı',
                'Toplam Fatura Sayısı',
                'Ağırlıklı Ortalama Vade',
                'Önerilen Çek Vadesi'
            ],
            'Değer': [
                valor_tarihi.strftime('%d.%m.%Y'),
                f"₺{df['Tutar'].sum():,.2f}",
                len(df),
                f"{ortalama_vade:.1f} gün",
                cek_vadesi.strftime('%d.%m.%Y')
            ]
        }
        ozet_df = pd.DataFrame(ozet_data)
        ozet_df.to_excel(writer, sheet_name='Özet', index=False)
        
        # Hesaplama detayları sayfası
        detay_data = []
        for idx, row in df.iterrows():
            detay_data.append({
                'Fatura No': row['Fatura No'],
                'Tutar': row['Tutar'],
                'Vade (Gün)': row['Vade (Gün)'],
                'Ağırlık (Tutar × Vade)': row['Tutar'] * row['Vade (Gün)'],
                'Oran (%)': (row['Tutar'] / df['Tutar'].sum()) * 100
            })
        
        detay_df = pd.DataFrame(detay_data)
        detay_df.to_excel(writer, sheet_name='Hesaplama Detayı', index=False)
    
    output.seek(0)
    return output


def vade_analizi(tutarlar, vadeler):
    """
    Vade dağılımı analizi yapar
    
    Args:
        tutarlar (list): Fatura tutarları
        vadeler (list): Vade günleri
    
    Returns:
        dict: Analiz sonuçları
    """
    if not tutarlar:
        return {}
    
    toplam = sum(tutarlar)
    
    # Vade gruplarına ayır
    groups = {
        '0-30 gün': {'tutar': 0, 'adet': 0},
        '31-60 gün': {'tutar': 0, 'adet': 0},
        '61-90 gün': {'tutar': 0, 'adet': 0},
        '90+ gün': {'tutar': 0, 'adet': 0}
    }
    
    for tutar, vade in zip(tutarlar, vadeler):
        if vade <= 30:
            groups['0-30 gün']['tutar'] += tutar
            groups['0-30 gün']['adet'] += 1
        elif vade <= 60:
            groups['31-60 gün']['tutar'] += tutar
            groups['31-60 gün']['adet'] += 1
        elif vade <= 90:
            groups['61-90 gün']['tutar'] += tutar
            groups['61-90 gün']['adet'] += 1
        else:
            groups['90+ gün']['tutar'] += tutar
            groups['90+ gün']['adet'] += 1
    
    # Yüzdeleri hesapla
    for group in groups.values():
        group['oran'] = (group['tutar'] / toplam * 100) if toplam > 0 else 0
    
    return groups


def min_max_vade_hesapla(tutarlar, vadeler):
    """
    En kısa ve en uzun vadeleri bulur
    
    Args:
        tutarlar (list): Fatura tutarları
        vadeler (list): Vade günleri
    
    Returns:
        tuple: (min_vade, max_vade, min_tutar, max_tutar)
    """
    if not vadeler:
        return (0, 0, 0, 0)
    
    min_vade = min(vadeler)
    max_vade = max(vadeler)
    
    min_idx = vadeler.index(min_vade)
    max_idx = vadeler.index(max_vade)
    
    min_tutar = tutarlar[min_idx]
    max_tutar = tutarlar[max_idx]
    
    return (min_vade, max_vade, min_tutar, max_tutar)

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red)
![License](https://img.shields.io/badge/License-MIT-green)
