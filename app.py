import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calculations
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- EXCEL İNDİRME FONKSİYONU (GELİŞMİŞ) ---
def to_excel_bytes(df_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Format tanımlamaları
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        currency_format = workbook.add_format({
            'num_format': '₺#,##0.00',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd.mm.yyyy',
            'border': 1,
            'align': 'center'
        })
        
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
            worksheet = writer.sheets[sheet_name]
            
            # Başlıkları formatla
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Sütun genişliklerini ayarla ve formatla
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_length)
                
                # Para birimi sütunları için format
                if 'Tutar' in col or 'Fark' in col or 'Toplam' in col:
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, idx, df.iloc[row_num-1][col], currency_format)
                # Sayı sütunları için format
                elif 'Gün' in col or 'Vade' in col or 'Adet' in col:
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, idx, df.iloc[row_num-1][col], number_format)
    
    return output.getvalue()

# Ana uygulama başlığı
st.set_page_config(page_title="Ortalama Vade Hesaplama", page_icon="📊", layout="wide")
st.title("📊 Ortalama Vade Hesaplama Programı")

# Session state başlatma
if 'faturalar' not in st.session_state:
    st.session_state.faturalar = []
if 'cekler' not in st.session_state:
    st.session_state.cekler = []
if 'musteri_gecmisi' not in st.session_state:
    st.session_state.musteri_gecmisi = []  # Son 5 müşteri kaydı
if 'show_filters' not in st.session_state:
    st.session_state.show_filters = False
if 'filter_min_tutar' not in st.session_state:
    st.session_state.filter_min_tutar = 0.0
if 'filter_max_tutar' not in st.session_state:
    st.session_state.filter_max_tutar = 1000000.0
if 'filter_min_vade' not in st.session_state:
    st.session_state.filter_min_vade = 0
if 'filter_max_vade' not in st.session_state:
    st.session_state.filter_max_vade = 365

# Ana içerik - 2 sütun
col1, col2 = st.columns([1, 1])

# SOL SÜTUN: Fatura Bilgileri
with col1:
    st.subheader("📝 Fatura Bilgileri")
    
    # HIZLI FATURA GİRİŞİ
    form_col1, form_col2 = st.columns([2, 2])
    with form_col1:
        fatura_no = st.text_input("Fatura No", placeholder="örn: FAT-2025-001", key="fatura_no")
    with form_col2:
        fatura_tutari = st.number_input(
            "Fatura Tutarı (₺)", 
            min_value=0.0, 
            step=100.0,
            format="%.2f",
            key="fatura_tutari",
            value=None,
            placeholder="örn: 10000"
        )
    
    form_col3, form_col4 = st.columns([2, 2])
    with form_col3:
        fatura_tarihi_input = st.date_input(
            "Fatura Tarihi", 
            value=datetime.now().date(),
            key="fatura_tarihi_input"
        )
        if isinstance(fatura_tarihi_input, tuple):
            if len(fatura_tarihi_input) > 0:
                fatura_tarihi = fatura_tarihi_input[0]
            else:
                fatura_tarihi = datetime.now().date()
        else:
            fatura_tarihi = fatura_tarihi_input
    
    with form_col4:
        vade_gun = st.number_input(
            "Vade (Gün)",
            min_value=0,
            max_value=365,
            value=90,
            step=1,
            key="vade_gun"
        )
        if fatura_tarihi is not None and hasattr(fatura_tarihi, 'strftime'):
            hesaplanan_valor = fatura_tarihi + timedelta(days=vade_gun)
            valor_str = hesaplanan_valor.strftime('%d.%m.%Y')
        else:
            hesaplanan_valor = None
            valor_str = "-"
        st.info(f"📅 Valör Tarihi: **{valor_str}** ({vade_gun} gün sonra)")

    # Ekle butonu
    if st.button("➕ Fatura Ekle", type="primary", use_container_width=True, key="add_fatura_btn"):
        if fatura_no and fatura_tutari and fatura_tutari > 0:
            if not any(f['Fatura No'] == fatura_no for f in st.session_state.faturalar):
                fatura_tarihi_str = fatura_tarihi.strftime('%d.%m.%Y') if fatura_tarihi is not None and hasattr(fatura_tarihi, 'strftime') else "-"
                valor_str = hesaplanan_valor.strftime('%d.%m.%Y') if hesaplanan_valor is not None and hasattr(hesaplanan_valor, 'strftime') else "-"
                st.session_state.faturalar.append({
                    'Fatura No': fatura_no,
                    'Tutar': fatura_tutari,
                    'Fatura Tarihi': fatura_tarihi_str,
                    'Vade (Gün)': vade_gun,
                    'Valör Tarihi': valor_str,
                    'Fatura Tarihi Raw': fatura_tarihi,
                    'Valör Tarihi Raw': hesaplanan_valor
                })
                st.success(f"✅ {fatura_no} eklendi!")
                st.rerun()
            else:
                st.error(f"❌ {fatura_no} zaten ekli!")
        else:
            st.error("❌ Lütfen tüm alanları doldurun!")

    # Fatura listesi
    if st.session_state.faturalar:
        st.markdown("#### 📋 Eklenen Faturalar")
        
        for idx, fatura in enumerate(st.session_state.faturalar):
            fcol1, fcol2 = st.columns([5, 1])
            with fcol1:
                st.text(f"{fatura['Fatura No']}: ₺{fatura['Tutar']:,.2f} | {fatura['Vade (Gün)']} gün | Fatura: {fatura['Fatura Tarihi']} → Valör: {fatura['Valör Tarihi']}")
            with fcol2:
                if st.button("🗑️", key=f"del_fatura_{idx}", help="Sil"):
                    st.session_state.faturalar.pop(idx)
                    st.rerun()
        
        # Temizleme butonu
        if st.button("🗑️ Tüm Faturaları Temizle", type="secondary"):
            st.session_state.faturalar = []
            st.rerun()
    else:
        st.info("👆 Yukarıdaki formu kullanarak fatura ekleyin.")

# SAĞ SÜTUN: Çek Bilgileri
with col2:
    st.subheader("💳 Çek Bilgileri")
    
    # MÜŞTERİ BİLGİSİ
    musteri_adi = st.text_input(
        "👤 Müşteri Adı", 
        placeholder="örn: ABC Ltd. Şti.",
        key="musteri_adi"
    )
    
    # SON 5 MÜŞTERİ HIZLI SEÇİM
    if st.session_state.musteri_gecmisi:
        st.caption("Son kullanılan müşteriler:")
        musteri_col = st.columns(min(len(st.session_state.musteri_gecmisi), 5))
        for idx, musteri in enumerate(st.session_state.musteri_gecmisi[:5]):
            with musteri_col[idx]:
                if st.button(f"📌 {musteri}", key=f"musteri_hizli_{idx}", use_container_width=True):
                    st.session_state.musteri_adi = musteri
                    st.rerun()
    
    # ÇEK GİRİŞİ
    cek_col1, cek_col2 = st.columns([2, 2])
    with cek_col1:
        cek_no = st.text_input("Çek No", placeholder="örn: ÇEK-001", key="cek_no")
    with cek_col2:
        cek_tutari = st.number_input(
            "Çek Tutarı (₺)", 
            min_value=0.0, 
            step=100.0,
            format="%.2f",
            key="cek_tutari",
            value=None,
            placeholder="örn: 10000"
        )
    
    cek_col3, cek_col4 = st.columns([2, 2])
    with cek_col3:
        # İlk fatura tarihini bul ve 90 gün ekle
        if st.session_state.faturalar:
            ilk_fatura_tarihi_cek = None
            for fatura in st.session_state.faturalar:
                fatura_raw = fatura.get('Fatura Tarihi Raw')
                if fatura_raw:
                    if ilk_fatura_tarihi_cek is None or fatura_raw < ilk_fatura_tarihi_cek:
                        ilk_fatura_tarihi_cek = fatura_raw
            
            if ilk_fatura_tarihi_cek:
                default_cek_tarihi = ilk_fatura_tarihi_cek + timedelta(days=90)
            else:
                default_cek_tarihi = datetime.now().date() + timedelta(days=90)
        else:
            default_cek_tarihi = datetime.now().date() + timedelta(days=90)
        
        cek_vade_tarihi = st.date_input(
            "Çek Vade Tarihi",
            value=default_cek_tarihi,
            key="cek_vade_tarihi"
        )
        if isinstance(cek_vade_tarihi, tuple):
            if len(cek_vade_tarihi) > 0:
                cek_vade_tarihi = cek_vade_tarihi[0]
            else:
                cek_vade_tarihi = default_cek_tarihi
    
    with cek_col4:
        # Vade gün hesaplama - fatura tarihinden
        if st.session_state.faturalar and ilk_fatura_tarihi_cek:
            cek_vade_gun = (cek_vade_tarihi - ilk_fatura_tarihi_cek).days
            referans_tarihi_str = ilk_fatura_tarihi_cek.strftime('%d.%m.%Y')
            
            # Vade süresine göre renk ve emoji belirleme
            if cek_vade_gun > 90:
                vade_renk = "error"  # Kırmızı
                vade_emoji = "⚠️"
                vade_mesaj = f"📅 Vade: **{cek_vade_gun} gün** sonra {vade_emoji}"
                vade_detay = f"Fatura tarihinden ({referans_tarihi_str}) itibaren"
            elif cek_vade_gun < 90:
                vade_renk = "success"  # Yeşil
                vade_emoji = "✅"
                vade_mesaj = f"📅 Vade: **{cek_vade_gun} gün** sonra {vade_emoji}"
                vade_detay = f"Fatura tarihinden ({referans_tarihi_str}) itibaren"
            else:  # cek_vade_gun == 90
                vade_renk = "info"  # Mavi
                vade_emoji = "ℹ️"
                vade_mesaj = f"📅 Vade: **{cek_vade_gun} gün** sonra {vade_emoji}"
                vade_detay = f"Fatura tarihinden ({referans_tarihi_str}) itibaren"
            
            # Renkli uyarı göster
            if vade_renk == "error":
                st.error(vade_mesaj)
                st.caption(vade_detay)
            elif vade_renk == "success":
                st.success(vade_mesaj)
                st.caption(vade_detay)
            else:
                st.info(vade_mesaj)
                st.caption(vade_detay)
        else:
            cek_vade_gun = (cek_vade_tarihi - datetime.now().date()).days
            st.warning(f"📅 Vade: **{cek_vade_gun} gün** sonra")
            st.caption("⚠️ Önce fatura ekleyin")

    # Ekle butonu
    if st.button("➕ Çek Ekle", type="primary", use_container_width=True, key="add_cek_btn"):
        if cek_no and cek_tutari and cek_tutari > 0 and musteri_adi:
            if not any(c['Çek No'] == cek_no for c in st.session_state.cekler):
                cek_vade_tarihi_str = cek_vade_tarihi.strftime('%d.%m.%Y') if hasattr(cek_vade_tarihi, 'strftime') else "-"
                
                # Vade gün bilgisini hesapla
                if st.session_state.faturalar and ilk_fatura_tarihi_cek:
                    cek_vade_gun_kayit = (cek_vade_tarihi - ilk_fatura_tarihi_cek).days
                else:
                    cek_vade_gun_kayit = (cek_vade_tarihi - datetime.now().date()).days
                
                # Müşteri geçmişine ekle (son 5'i tut)
                if musteri_adi not in st.session_state.musteri_gecmisi:
                    st.session_state.musteri_gecmisi.insert(0, musteri_adi)
                    if len(st.session_state.musteri_gecmisi) > 5:
                        st.session_state.musteri_gecmisi = st.session_state.musteri_gecmisi[:5]
                else:
                    # Eğer varsa en başa taşı
                    st.session_state.musteri_gecmisi.remove(musteri_adi)
                    st.session_state.musteri_gecmisi.insert(0, musteri_adi)
                
                st.session_state.cekler.append({
                    'Çek No': cek_no,
                    'Tutar': cek_tutari,
                    'Müşteri': musteri_adi,
                    'Vade Tarihi': cek_vade_tarihi_str,
                    'Vade Tarihi Raw': cek_vade_tarihi,
                    'Vade (Gün)': cek_vade_gun_kayit
                })
                st.success(f"✅ {cek_no} eklendi! (Müşteri: {musteri_adi})")
                st.rerun()
            else:
                st.error(f"❌ {cek_no} zaten ekli!")
        else:
            st.error("❌ Lütfen tüm alanları doldurun (Müşteri adı dahil)!")

    # Çek listesi
    if st.session_state.cekler:
        st.markdown("#### 📋 Eklenen Çekler")
        
        for idx, cek in enumerate(st.session_state.cekler):
            ccol1, ccol2 = st.columns([5, 1])
            with ccol1:
                # Vade gün bilgisini göster
                vade_gun_info = cek.get('Vade (Gün)', 0)
                musteri_info = cek.get('Müşteri', 'Bilinmiyor')
                if vade_gun_info > 90:
                    vade_icon = "🔴"
                elif vade_gun_info < 90:
                    vade_icon = "🟢"
                else:
                    vade_icon = "🔵"
                st.text(f"👤 {musteri_info} | {cek['Çek No']}: ₺{cek['Tutar']:,.2f} | Vade: {cek['Vade Tarihi']} ({vade_gun_info} gün {vade_icon})")
            with ccol2:
                if st.button("🗑️", key=f"del_cek_{idx}", help="Sil"):
                    st.session_state.cekler.pop(idx)
                    st.rerun()
        
        if st.button("🗑️ Tüm Çekleri Temizle", type="secondary"):
            st.session_state.cekler = []
            st.rerun()
    else:
        st.info("💡 Müşteriden alacağınız çekleri ekleyin")

st.divider()
st.info("💡 Çek vade tarihi otomatik olarak fatura tarihinden 90 gün sonraya ayarlanır. 🟢 90 günden az = İyi, 🔴 90 günden fazla = Dikkat!")
st.divider()

# GENİŞ EKRAN İÇİN CSS
st.markdown("""
<style>
    /* Ana container'ı genişlet ama üst bölüm için değil */
    .main .block-container {
        max-width: 95% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Üst kısımdaki columns (Fatura ve Çek Bilgileri) korunuyor */
    [data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
    }
    
    /* Hesaplama sonuçları bölümü için tam genişlik */
    div.stMarkdown > div[data-testid="stMarkdownContainer"] > h2 {
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# HESAPLAMA SONUÇLARI - TAM GENİŞLİKTE
if st.session_state.faturalar and st.session_state.cekler:
    st.markdown("## 💰 Hesaplama Sonuçları")
    
    # FİLTRELEME BÖLÜMÜ
    col_filter1, col_filter2 = st.columns([1, 4])
    with col_filter1:
        if st.button("🔍 Filtreleme", use_container_width=True):
            st.session_state.show_filters = not st.session_state.show_filters
    
    if st.session_state.show_filters:
        with st.expander("🔍 Veri Filtreleme Seçenekleri", expanded=True):
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                st.markdown("**Tutar Aralığı (₺)**")
                filter_min_tutar = st.number_input("Min Tutar", min_value=0.0, value=0.0, step=1000.0, key="filter_min_input")
                filter_max_tutar = st.number_input("Max Tutar", min_value=0.0, value=1000000.0, step=1000.0, key="filter_max_input")
            with filter_col2:
                st.markdown("**Vade Aralığı (Gün)**")
                filter_min_vade = st.number_input("Min Vade", min_value=0, value=0, step=10, key="filter_vade_min_input")
                filter_max_vade = st.number_input("Max Vade", min_value=0, value=365, step=10, key="filter_vade_max_input")
            
            if st.button("✅ Filtreyi Uygula", type="primary", use_container_width=True):
                st.session_state.filter_min_tutar = filter_min_tutar
                st.session_state.filter_max_tutar = filter_max_tutar
                st.session_state.filter_min_vade = filter_min_vade
                st.session_state.filter_max_vade = filter_max_vade
                st.success("✅ Filtre uygulandı!")
                st.rerun()
    
    df_faturalar = pd.DataFrame(st.session_state.faturalar)
    df_cekler = pd.DataFrame(st.session_state.cekler)
    
    # Filtreleme uygula
    df_faturalar_filtered = df_faturalar[
        (df_faturalar['Tutar'] >= st.session_state.filter_min_tutar) & 
        (df_faturalar['Tutar'] <= st.session_state.filter_max_tutar) &
        (df_faturalar['Vade (Gün)'] >= st.session_state.filter_min_vade) &
        (df_faturalar['Vade (Gün)'] <= st.session_state.filter_max_vade)
    ].copy()
    
    df_cekler_filtered = df_cekler[
        (df_cekler['Tutar'] >= st.session_state.filter_min_tutar) & 
        (df_cekler['Tutar'] <= st.session_state.filter_max_tutar)
    ].copy()
    
    # Eğer filtre sonucu veri yoksa uyarı ver
    if df_faturalar_filtered.empty or df_cekler_filtered.empty:
        st.warning("⚠️ Filtre kriterleriyle eşleşen veri bulunamadı!")
        df_faturalar_filtered = df_faturalar
        df_cekler_filtered = df_cekler
    
    toplam_fatura = df_faturalar_filtered['Tutar'].sum()
    toplam_cek = df_cekler_filtered['Tutar'].sum()

    # Hesaplama tablosu (detay)
    hesaplamalar = []
    for _, fatura in df_faturalar_filtered.iterrows():
        fatura_tarihi = fatura['Fatura Tarihi Raw']
        valor_tarihi = fatura['Valör Tarihi Raw']
        for _, cek in df_cekler_filtered.iterrows():
            cek_vade_tarihi = cek['Vade Tarihi Raw']
            vade_gun_valor = (valor_tarihi - fatura_tarihi).days
            vade_gun_cek = (cek_vade_tarihi - fatura_tarihi).days
            hesaplamalar.append({
                'Fatura No': fatura['Fatura No'],
                'Fatura Tutar': fatura['Tutar'],
                'Fatura Tarihi': fatura['Fatura Tarihi'],
                'Valör Tarihi': fatura['Valör Tarihi'],
                'Çek No': cek['Çek No'],
                'Çek Tutar': cek['Tutar'],
                'Çek Vade': cek['Vade Tarihi'],
                'Vade (Gün) - Valör': vade_gun_valor,
                'Vade (Gün) - Çek': vade_gun_cek,
                'Vade Farkı': vade_gun_cek - vade_gun_valor
            })
    df_hesap = pd.DataFrame(hesaplamalar)

    # Özet metrikler için DataFrame
    df_ozet = pd.DataFrame([
        {"Açıklama": "Toplam Fatura", "Tutar": toplam_fatura, "Adet": len(df_faturalar_filtered)},
        {"Açıklama": "Toplam Çek", "Tutar": toplam_cek, "Adet": len(df_cekler_filtered)},
        {"Açıklama": "Fark", "Tutar": toplam_cek-toplam_fatura, "Adet": "-"}
    ])
    
    # Faturalar detay tablosu
    df_faturalar_detay = df_faturalar_filtered[['Fatura No', 'Tutar', 'Fatura Tarihi', 'Valör Tarihi', 'Vade (Gün)']].copy()
    df_faturalar_detay.columns = ['Fatura No', 'Tutar (₺)', 'Fatura Tarihi', 'Valör Tarihi', 'Vade (Gün)']
    
    # Çekler detay tablosu
    df_cekler_detay = df_cekler_filtered[['Çek No', 'Tutar', 'Vade Tarihi']].copy()
    df_cekler_detay.columns = ['Çek No', 'Tutar (₺)', 'Vade Tarihi']

    # Genel ortalama vadeler hesapla
    tum_fatura_tutarlar = df_faturalar_filtered['Tutar'].tolist()
    tum_valor_vadeler = []
    for _, row in df_faturalar_filtered.iterrows():
        fatura_raw = row['Fatura Tarihi Raw']
        valor_raw = row['Valör Tarihi Raw']
        if fatura_raw and valor_raw:
            vade_gun = (valor_raw - fatura_raw).days
            tum_valor_vadeler.append(vade_gun)
        else:
            tum_valor_vadeler.append(0)
    
    genel_ort_valor = calculations.agirlikli_ortalama_vade_hesapla(tum_fatura_tutarlar, tum_valor_vadeler)
    
    # Tüm çek vadeleri için ağırlıklı ortalama
    tum_cek_tutarlar = []
    tum_cek_vade_gunler = []
    
    # En erken fatura tarihini bul
    ilk_fatura_tarihi = None
    for _, row in df_faturalar_filtered.iterrows():
        if row['Fatura Tarihi Raw']:
            if ilk_fatura_tarihi is None or row['Fatura Tarihi Raw'] < ilk_fatura_tarihi:
                ilk_fatura_tarihi = row['Fatura Tarihi Raw']
    
    for _, cek in df_cekler_filtered.iterrows():
        tum_cek_tutarlar.append(cek['Tutar'])
        if cek['Vade Tarihi Raw'] and ilk_fatura_tarihi:
            vade_gun = (cek['Vade Tarihi Raw'] - ilk_fatura_tarihi).days
            tum_cek_vade_gunler.append(vade_gun)
        else:
            tum_cek_vade_gunler.append(0)
    
    genel_ort_cek = calculations.agirlikli_ortalama_vade_hesapla(tum_cek_tutarlar, tum_cek_vade_gunler)
    
    # Vade dağılım analizi
    vade_gruplari = calculations.vade_analizi(tum_fatura_tutarlar, tum_valor_vadeler)
    df_vade_dagilim = pd.DataFrame([
        {
            "Vade Grubu": grup,
            "Tutar (₺)": data['tutar'],
            "Adet": data['adet'],
            "Oran (%)": data['oran']
        }
        for grup, data in vade_gruplari.items()
    ])

    # Excel indirme butonu - GELİŞMİŞ
    excel_data = {
        "Özet": df_ozet,
        "Hesaplama Detayı": df_hesap,
        "Faturalar": df_faturalar_detay,
        "Çekler": df_cekler_detay,
        "Vade Dağılımı": df_vade_dagilim
    }
    excel_bytes = to_excel_bytes(excel_data)
    
    st.markdown("---")
    st.markdown("### 📥 Hesaplama Sonuçlarını İndir")
    st.download_button(
        label="📥 Tüm Detayları Excel'e İndir (Formatlanmış)",
        data=excel_bytes,
        file_name=f"ortalama_vade_hesaplama_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )
    st.caption("💡 Excel dosyası 5 sayfa içerir: Özet, Hesaplama Detayı, Faturalar, Çekler ve Vade Dağılımı")

    # GENİŞ METRİK BARI
    st.markdown(f"""
    <style>
    .wide-metrics-bar {{
        position: relative;
        width: 95vw !important;
        max-width: 95vw !important;
        margin: 32px calc(-47.5vw + 50%) !important;
        padding: 50px 40px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 24px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.1);
        display: flex;
        flex-wrap: nowrap;
        justify-content: space-evenly;
        align-items: center;
        gap: 48px;
    }}
    .metric-block {{
        flex: 1;
        min-width: 220px;
        text-align: center;
        padding: 24px;
    }}
    .metric-value {{
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 16px;
        text-shadow: 0 3px 6px rgba(0,0,0,0.12);
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: 1.5rem;
        color: #495057;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    .metric-sublabel {{
        font-size: 1.25rem;
        color: #6c757d;
        margin-top: 10px;
        font-weight: 500;
    }}
    @media (max-width: 1400px) {{
        .wide-metrics-bar {{
            flex-wrap: wrap;
            width: 100%;
            margin-left: 0;
        }}
        .metric-block {{
            min-width: 180px;
        }}
    }}
    </style>
    <div class='wide-metrics-bar'>
        <div class='metric-block'>
            <div class='metric-value' style='color: #0d6efd;'>₺{toplam_fatura:,.0f}</div>
            <div class='metric-label'>Toplam Fatura</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: #198754;'>₺{toplam_cek:,.0f}</div>
            <div class='metric-label'>Toplam Çek</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: {'#198754' if toplam_cek - toplam_fatura >= 0 else '#dc3545'};'>₺{abs(toplam_cek - toplam_fatura):,.0f}</div>
            <div class='metric-label'>Fark</div>
            <div class='metric-sublabel'>{'Fazla ✅' if toplam_cek - toplam_fatura >= 0 else 'Eksik ⚠️'}</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: #fd7e14;'>{genel_ort_valor:.1f}</div>
            <div class='metric-label'>Ort. Valör Vadesi</div>
            <div class='metric-sublabel'>gün</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: #6f42c1;'>{genel_ort_cek:.1f}</div>
            <div class='metric-label'>Ort. Çek Vadesi</div>
            <div class='metric-sublabel'>gün</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 📊 GRAFİK GÖRSELLEŞTİRMELER
    st.markdown("## 📊 Grafik Analizler")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Vade Dağılımı", "🎯 Karşılaştırma", "📅 Zaman Çizelgesi", "💹 Detaylı Analiz"])
    
    with tab1:
        st.markdown("### 📈 Vade Dağılımı Grafiği")
        
        graph_col1, graph_col2 = st.columns(2)
        
        with graph_col1:
            # Bar Chart - Vade Gruplarına Göre Tutar Dağılımı
            fig_bar = px.bar(
                df_vade_dagilim,
                x='Vade Grubu',
                y='Tutar (₺)',
                text='Tutar (₺)',
                title='Vade Gruplarına Göre Tutar Dağılımı',
                color='Tutar (₺)',
                color_continuous_scale='Blues'
            )
            fig_bar.update_traces(texttemplate='₺%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(
                xaxis_title="Vade Grubu",
                yaxis_title="Tutar (₺)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with graph_col2:
            # Pie Chart - Vade Gruplarına Göre Oran
            fig_pie = px.pie(
                df_vade_dagilim[df_vade_dagilim['Tutar (₺)'] > 0],
                values='Tutar (₺)',
                names='Vade Grubu',
                title='Vade Gruplarına Göre Tutar Oranı (%)',
                hole=0.4
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Tutar: ₺%{value:,.0f}<br>Oran: %{percent}<extra></extra>'
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.markdown("### 🎯 Fatura vs Çek Karşılaştırması")
        
        # Fatura ve Çek tutarlarını karşılaştır
        comparison_data = pd.DataFrame({
            'Kategori': ['Fatura', 'Çek'],
            'Toplam Tutar': [toplam_fatura, toplam_cek],
            'Adet': [len(df_faturalar_filtered), len(df_cekler_filtered)],
            'Ortalama': [toplam_fatura/len(df_faturalar_filtered) if len(df_faturalar_filtered) > 0 else 0,
                        toplam_cek/len(df_cekler_filtered) if len(df_cekler_filtered) > 0 else 0]
        })
        
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            # Tutar karşılaştırma
            fig_comp1 = go.Figure(data=[
                go.Bar(name='Toplam Tutar', x=comparison_data['Kategori'], y=comparison_data['Toplam Tutar'],
                       text=comparison_data['Toplam Tutar'].apply(lambda x: f'₺{x:,.0f}'),
                       textposition='outside',
                       marker_color=['#0d6efd', '#198754'])
            ])
            fig_comp1.update_layout(
                title='Toplam Tutar Karşılaştırması',
                xaxis_title='',
                yaxis_title='Tutar (₺)',
                height=400
            )
            st.plotly_chart(fig_comp1, use_container_width=True)
        
        with comp_col2:
            # Adet ve ortalama karşılaştırma
            fig_comp2 = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Adet', 'Ortalama Tutar'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            fig_comp2.add_trace(
                go.Bar(x=comparison_data['Kategori'], y=comparison_data['Adet'],
                       text=comparison_data['Adet'], textposition='outside',
                       marker_color=['#0d6efd', '#198754'], showlegend=False),
                row=1, col=1
            )
            
            fig_comp2.add_trace(
                go.Bar(x=comparison_data['Kategori'], y=comparison_data['Ortalama'],
                       text=comparison_data['Ortalama'].apply(lambda x: f'₺{x:,.0f}'),
                       textposition='outside',
                       marker_color=['#0d6efd', '#198754'], showlegend=False),
                row=1, col=2
            )
            
            fig_comp2.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_comp2, use_container_width=True)
        
        # Vade karşılaştırma
        st.markdown("#### 📊 Ortalama Vade Karşılaştırması")
        vade_comp_data = pd.DataFrame({
            'Vade Tipi': ['Valör Vadesi', 'Çek Vadesi'],
            'Ortalama Gün': [genel_ort_valor, genel_ort_cek]
        })
        
        fig_vade = px.bar(
            vade_comp_data,
            x='Vade Tipi',
            y='Ortalama Gün',
            text='Ortalama Gün',
            title='Ortalama Vade Karşılaştırması (Gün)',
            color='Vade Tipi',
            color_discrete_map={'Valör Vadesi': '#fd7e14', 'Çek Vadesi': '#6f42c1'}
        )
        fig_vade.update_traces(texttemplate='%{text:.1f} gün', textposition='outside')
        fig_vade.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_vade, use_container_width=True)
    
    with tab3:
        st.markdown("### 📅 Vade Zaman Çizelgesi")
        
        # Timeline grafiği için veri hazırlama
        timeline_data = []
        
        # Faturaları ekle
        for _, fatura in df_faturalar_filtered.iterrows():
            timeline_data.append({
                'Tip': 'Fatura',
                'No': fatura['Fatura No'],
                'Başlangıç': fatura['Fatura Tarihi Raw'],
                'Bitiş': fatura['Valör Tarihi Raw'],
                'Tutar': fatura['Tutar'],
                'Açıklama': f"{fatura['Fatura No']} - ₺{fatura['Tutar']:,.0f}"
            })
        
        # Çekleri ekle
        if ilk_fatura_tarihi:
            for _, cek in df_cekler_filtered.iterrows():
                timeline_data.append({
                    'Tip': 'Çek',
                    'No': cek['Çek No'],
                    'Başlangıç': ilk_fatura_tarihi,
                    'Bitiş': cek['Vade Tarihi Raw'],
                    'Tutar': cek['Tutar'],
                    'Açıklama': f"{cek['Çek No']} - ₺{cek['Tutar']:,.0f}"
                })
        
        df_timeline = pd.DataFrame(timeline_data)
        
        if not df_timeline.empty:
            fig_timeline = px.timeline(
                df_timeline,
                x_start='Başlangıç',
                x_end='Bitiş',
                y='Açıklama',
                color='Tip',
                title='Fatura ve Çek Vade Zaman Çizelgesi',
                color_discrete_map={'Fatura': '#0d6efd', 'Çek': '#198754'},
                hover_data=['Tutar']
            )
            fig_timeline.update_layout(
                xaxis_title='Tarih',
                yaxis_title='',
                height=max(400, len(df_timeline) * 30)
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Vade dağılım grafiği - Scatter
        st.markdown("#### 📊 Vade-Tutar İlişkisi")
        scatter_data = []
        for _, fatura in df_faturalar_filtered.iterrows():
            scatter_data.append({
                'Vade (Gün)': fatura['Vade (Gün)'],
                'Tutar': fatura['Tutar'],
                'Tip': 'Fatura',
                'No': fatura['Fatura No']
            })
        
        df_scatter = pd.DataFrame(scatter_data)
        
        fig_scatter = px.scatter(
            df_scatter,
            x='Vade (Gün)',
            y='Tutar',
            size='Tutar',
            color='Tip',
            hover_data=['No'],
            title='Vade Süresine Göre Fatura Tutarları',
            color_discrete_map={'Fatura': '#0d6efd'}
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.markdown("### 💹 Detaylı İstatistiksel Analiz")
        
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.markdown("#### 📋 Fatura İstatistikleri")
            st.metric("Toplam Fatura Sayısı", len(df_faturalar_filtered))
            st.metric("Toplam Tutar", f"₺{toplam_fatura:,.0f}")
            st.metric("Ortalama Tutar", f"₺{toplam_fatura/len(df_faturalar_filtered):,.0f}" if len(df_faturalar_filtered) > 0 else "₺0")
            st.metric("Medyan Tutar", f"₺{df_faturalar_filtered['Tutar'].median():,.0f}" if not df_faturalar_filtered.empty else "₺0")
            st.metric("Std Sapma", f"₺{df_faturalar_filtered['Tutar'].std():,.0f}" if not df_faturalar_filtered.empty else "₺0")
        
        with detail_col2:
            st.markdown("#### 💳 Çek İstatistikleri")
            st.metric("Toplam Çek Sayısı", len(df_cekler_filtered))
            st.metric("Toplam Tutar", f"₺{toplam_cek:,.0f}")
            st.metric("Ortalama Tutar", f"₺{toplam_cek/len(df_cekler_filtered):,.0f}" if len(df_cekler_filtered) > 0 else "₺0")
            st.metric("Medyan Tutar", f"₺{df_cekler_filtered['Tutar'].median():,.0f}" if not df_cekler_filtered.empty else "₺0")
            st.metric("Std Sapma", f"₺{df_cekler_filtered['Tutar'].std():,.0f}" if not df_cekler_filtered.empty else "₺0")
        
        with detail_col3:
            st.markdown("#### 📊 Vade İstatistikleri")
            st.metric("Ort. Valör Vadesi", f"{genel_ort_valor:.1f} gün")
            st.metric("Ort. Çek Vadesi", f"{genel_ort_cek:.1f} gün")
            st.metric("Min Vade", f"{min(tum_valor_vadeler) if tum_valor_vadeler else 0} gün")
            st.metric("Max Vade", f"{max(tum_valor_vadeler) if tum_valor_vadeler else 0} gün")
            st.metric("Vade Std Sapma", f"{np.std(tum_valor_vadeler):.1f} gün" if tum_valor_vadeler else "0 gün")
        
        # Histogram - Tutar dağılımı
        st.markdown("#### 📊 Tutar Dağılım Histogramı")
        
        hist_col1, hist_col2 = st.columns(2)
        
        with hist_col1:
            fig_hist_fatura = px.histogram(
                df_faturalar_filtered,
                x='Tutar',
                nbins=10,
                title='Fatura Tutar Dağılımı',
                color_discrete_sequence=['#0d6efd']
            )
            fig_hist_fatura.update_layout(
                xaxis_title='Tutar (₺)',
                yaxis_title='Frekans',
                height=350
            )
            st.plotly_chart(fig_hist_fatura, use_container_width=True)
        
        with hist_col2:
            fig_hist_vade = px.histogram(
                df_faturalar_filtered,
                x='Vade (Gün)',
                nbins=10,
                title='Vade Süresi Dağılımı',
                color_discrete_sequence=['#fd7e14']
            )
            fig_hist_vade.update_layout(
                xaxis_title='Vade (Gün)',
                yaxis_title='Frekans',
                height=350
            )
            st.plotly_chart(fig_hist_vade, use_container_width=True)
    
    st.divider()
    
    # Genel Vade Analizi
    st.markdown("### 📊 Genel Vade Analizi")
    
    # İnteraktif veri tablosu
    with st.expander("📋 Detaylı Hesaplama Tablosu", expanded=False):
        st.dataframe(
            df_hesap.style.format({
                'Fatura Tutar': '₺{:,.2f}',
                'Çek Tutar': '₺{:,.2f}',
                'Vade (Gün) - Valör': '{:.0f}',
                'Vade (Gün) - Çek': '{:.0f}',
                'Vade Farkı': '{:.0f}'
            }),
            use_container_width=True,
            height=400
        )
    
    # Vade dağılımı analizi
    vade_gruplari = calculations.vade_analizi(tum_fatura_tutarlar, tum_valor_vadeler)
    
    col_analiz1, col_analiz2 = st.columns([1, 1])
    
    with col_analiz1:
        st.markdown("#### 📈 Vade Dağılımı (Valör Bazlı)")
        dagilim_data = []
        for grup, data in vade_gruplari.items():
            dagilim_data.append({
                "Vade Grubu": grup,
                "Tutar": f"₺{data['tutar']:,.0f}",
                "Adet": data['adet'],
                "Oran": f"{data['oran']:.1f}%"
            })
        st.dataframe(pd.DataFrame(dagilim_data), use_container_width=True, hide_index=True)
    
    with col_analiz2:
        # Min-Max vadeler
        min_vade, max_vade, min_tutar, max_tutar = calculations.min_max_vade_hesapla(tum_fatura_tutarlar, tum_valor_vadeler)
        
        st.markdown("#### 📊 Vade İstatistikleri")
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.metric("En Kısa Vade", f"{min_vade} gün", f"₺{min_tutar:,.0f}")
            st.metric("Ortalama Vade", f"{genel_ort_valor:.1f} gün")
        with stat_col2:
            st.metric("En Uzun Vade", f"{max_vade} gün", f"₺{max_tutar:,.0f}")
            std_vade = np.std(tum_valor_vadeler) if tum_valor_vadeler else 0
            st.metric("Standart Sapma", f"{std_vade:.1f} gün")
    
    st.divider()
    
    # Çek bazlı ortalama vadeler
    st.markdown("### 💳 Çek Bazlı Vade Analizi")
    
    for idx, cek_no in enumerate(df_cekler_filtered['Çek No']):
        with st.expander(f"💳 {cek_no}", expanded=(idx == 0)):
            cek_data = df_hesap[df_hesap['Çek No'] == cek_no]
            
            # Bu çek için ağırlıklı ortalama
            tutarlar = cek_data['Fatura Tutar'].tolist()
            vadeler_valor = cek_data['Vade (Gün) - Valör'].tolist()
            vadeler_cek = cek_data['Vade (Gün) - Çek'].tolist()
            
            ort_valor = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler_valor)
            ort_cek = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler_cek)
            
            # Büyük metrikler
            vade_col1, vade_col2 = st.columns(2)
            with vade_col1:
                st.markdown("<h4 style='text-align: center;'>📅 Ort. Valör Vadesi</h4>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center; color: #fd7e14;'>{ort_valor:.1f} gün</h1>", unsafe_allow_html=True)
            with vade_col2:
                st.markdown("<h4 style='text-align: center;'>📝 Ort. Çek Vadesi</h4>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center; color: #6f42c1;'>{ort_cek:.1f} gün</h1>", unsafe_allow_html=True)
            
            # Detaylı istatistikler
            detay_col1, detay_col2 = st.columns(2)
            with detay_col1:
                cek_vadeler_valor = cek_data['Vade (Gün) - Valör'].tolist()
                min_v_valor = min(cek_vadeler_valor) if cek_vadeler_valor else 0
                max_v_valor = max(cek_vadeler_valor) if cek_vadeler_valor else 0
                std_v_valor = np.std(cek_vadeler_valor) if len(cek_vadeler_valor) > 1 else 0
                
                st.markdown("**Valör Vade İstatistikleri:**")
                st.write(f"• Min: {min_v_valor} gün")
                st.write(f"• Max: {max_v_valor} gün")
                st.write(f"• Std: {std_v_valor:.1f} gün")
            
            with detay_col2:
                cek_vadeler_cek = cek_data['Vade (Gün) - Çek'].tolist()
                min_v_cek = min(cek_vadeler_cek) if cek_vadeler_cek else 0
                max_v_cek = max(cek_vadeler_cek) if cek_vadeler_cek else 0
                std_v_cek = np.std(cek_vadeler_cek) if len(cek_vadeler_cek) > 1 else 0
                
                st.markdown("**Çek Vade İstatistikleri:**")
                st.write(f"• Min: {min_v_cek} gün")
                st.write(f"• Max: {max_v_cek} gün")
                st.write(f"• Std: {std_v_cek:.1f} gün")
            
            st.markdown("---")
            st.markdown("**📋 İlgili Faturalar:**")
            for _, row in cek_data.iterrows():
                st.markdown(f"• **{row['Fatura No']}**: ₺{row['Fatura Tutar']:,.0f} → Valör: **{row['Vade (Gün) - Valör']} gün**, Çek: **{row['Vade (Gün) - Çek']} gün**")

elif st.session_state.faturalar and not st.session_state.cekler:
    st.warning("⚠️ Lütfen en az bir çek ekleyin!")
elif not st.session_state.faturalar and st.session_state.cekler:
    st.warning("⚠️ Lütfen en az bir fatura ekleyin!")
else:
    st.info("📝 Fatura ve çek ekleyerek hesaplama yapın.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
<small>© 2025 Ortalama Vade Hesaplama Programı | By Goksel</small>
</div>
""", unsafe_allow_html=True)
