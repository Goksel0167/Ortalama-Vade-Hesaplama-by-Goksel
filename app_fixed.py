import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calculations
import io

# --- EXCEL İNDİRME FONKSİYONU ---
def to_excel_bytes(df_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
    return output.getvalue()

# Ana uygulama başlığı
st.set_page_config(page_title="Ortalama Vade Hesaplama", page_icon="📊", layout="wide")
st.title("📊 Ortalama Vade Hesaplama Programı")

# Session state başlatma
if 'faturalar' not in st.session_state:
    st.session_state.faturalar = []
if 'cekler' not in st.session_state:
    st.session_state.cekler = []

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

    # Otomatik ekleme: tüm alanlar doluysa ve fatura_no yeni ise ekle
    if fatura_no and fatura_tutari and fatura_tutari > 0 and not any(f['Fatura No'] == fatura_no for f in st.session_state.faturalar):
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
        st.success(f"✅ {fatura_no} eklendi! Valör: {valor_str} ({vade_gun} gün)")
        st.rerun()

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
        cek_vade_tarihi = st.date_input(
            "Çek Vade Tarihi",
            value=datetime.now().date() + timedelta(days=120),
            key="cek_vade_tarihi"
        )
        if isinstance(cek_vade_tarihi, tuple):
            if len(cek_vade_tarihi) > 0:
                cek_vade_tarihi = cek_vade_tarihi[0]
            else:
                cek_vade_tarihi = datetime.now().date() + timedelta(days=120)
    
    with cek_col4:
        cek_vade_gun = (cek_vade_tarihi - datetime.now().date()).days
        st.info(f"📅 Vade: **{cek_vade_gun} gün** sonra")

    # Otomatik ekleme
    if cek_no and cek_tutari and cek_tutari > 0 and not any(c['Çek No'] == cek_no for c in st.session_state.cekler):
        cek_vade_tarihi_str = cek_vade_tarihi.strftime('%d.%m.%Y') if hasattr(cek_vade_tarihi, 'strftime') else "-"
        st.session_state.cekler.append({
            'Çek No': cek_no,
            'Tutar': cek_tutari,
            'Vade Tarihi': cek_vade_tarihi_str,
            'Vade Tarihi Raw': cek_vade_tarihi
        })
        st.success(f"✅ {cek_no} eklendi! Vade: {cek_vade_tarihi_str}")
        st.rerun()

    # Çek listesi
    if st.session_state.cekler:
        st.markdown("#### 📋 Eklenen Çekler")
        
        for idx, cek in enumerate(st.session_state.cekler):
            ccol1, ccol2 = st.columns([5, 1])
            with ccol1:
                st.text(f"{cek['Çek No']}: ₺{cek['Tutar']:,.2f} | Vade: {cek['Vade Tarihi']}")
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
st.info("💡 Birden fazla çek ekleyerek faturaları çeklere dağıtabilirsiniz.")
st.divider()

# HESAPLAMA SONUÇLARI - TAM GENİŞLİKTE
if st.session_state.faturalar and st.session_state.cekler:
    st.subheader("💰 Hesaplama Sonuçları")
    
    df_faturalar = pd.DataFrame(st.session_state.faturalar)
    df_cekler = pd.DataFrame(st.session_state.cekler)
    
    toplam_fatura = df_faturalar['Tutar'].sum()
    toplam_cek = df_cekler['Tutar'].sum()

    # Hesaplama tablosu (detay)
    hesaplamalar = []
    for _, fatura in df_faturalar.iterrows():
        fatura_tarihi = fatura['Fatura Tarihi Raw']
        valor_tarihi = fatura['Valör Tarihi Raw']
        for _, cek in df_cekler.iterrows():
            cek_vade_tarihi = cek['Vade Tarihi Raw']
            vade_gun_valor = (valor_tarihi - fatura_tarihi).days
            vade_gun_cek = (cek_vade_tarihi - fatura_tarihi).days
            hesaplamalar.append({
                'Fatura No': fatura['Fatura No'],
                'Fatura Tutar': fatura['Tutar'],
                'Çek No': cek['Çek No'],
                'Çek Tutar': cek['Tutar'],
                'Çek Vade': cek['Vade Tarihi'],
                'Vade (Gün) - Valör': vade_gun_valor,
                'Vade (Gün) - Çek': vade_gun_cek
            })
    df_hesap = pd.DataFrame(hesaplamalar)

    # Özet metrikler için DataFrame
    df_ozet = pd.DataFrame([
        {"Toplam Fatura": toplam_fatura, "Toplam Çek": toplam_cek, "Fark": toplam_cek-toplam_fatura}
    ])

    # Genel ortalama vadeler hesapla
    tum_fatura_tutarlar = df_faturalar['Tutar'].tolist()
    tum_valor_vadeler = [(row['Valör Tarihi Raw'] - row['Fatura Tarihi Raw']).days for _, row in df_faturalar.iterrows()]
    
    genel_ort_valor = calculations.agirlikli_ortalama_vade_hesapla(tum_fatura_tutarlar, tum_valor_vadeler)
    
    # Tüm çek vadeleri için ağırlıklı ortalama
    tum_cek_tutarlar = []
    tum_cek_vade_gunler = []
    for _, cek in df_cekler.iterrows():
        tum_cek_tutarlar.append(cek['Tutar'])
        tum_cek_vade_gunler.append((cek['Vade Tarihi Raw'] - df_faturalar['Fatura Tarihi Raw'].min()).days)
    genel_ort_cek = calculations.agirlikli_ortalama_vade_hesapla(tum_cek_tutarlar, tum_cek_vade_gunler)

    # Excel indirme butonu
    excel_bytes = to_excel_bytes({"Hesaplama": df_hesap, "Özet": df_ozet})
    st.download_button(
        label="📥 Hesaplama Sonuçlarını Excel'e İndir",
        data=excel_bytes,
        file_name="ortalama_vade_hesaplama_sonuclari.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # GENİŞ METRİK BARI
    st.markdown(f"""
    <style>
    .wide-metrics-bar {{
        width: 100%;
        margin: 32px 0;
        padding: 40px 24px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        align-items: center;
        gap: 32px;
    }}
    .metric-block {{
        flex: 1;
        min-width: 200px;
        text-align: center;
        padding: 20px;
    }}
    .metric-value {{
        font-size: 2.8rem;
        font-weight: bold;
        margin-bottom: 12px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .metric-label {{
        font-size: 1.3rem;
        color: #495057;
        font-weight: 500;
    }}
    .metric-sublabel {{
        font-size: 1.1rem;
        color: #6c757d;
        margin-top: 8px;
    }}
    @media (max-width: 1200px) {{
        .wide-metrics-bar {{
            flex-direction: column;
        }}
        .metric-block {{
            width: 100%;
            min-width: auto;
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
    
    # Genel Vade Analizi
    st.markdown("### 📊 Genel Vade Analizi")
    
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
    
    for cek_no in df_cekler['Çek No']:
        with st.expander(f"💳 {cek_no}", expanded=False):
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
