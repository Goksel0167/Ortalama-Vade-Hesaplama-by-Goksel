import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calculations

# Sayfa yapılandırması
st.set_page_config(
    page_title="Ortalama Vade Hesaplama",
    page_icon="📊",
    layout="wide"
)

# Başlık ve açıklama
st.title("📊 Ortalama Vade Hesaplama Programı")
st.markdown("""
### Hoş Geldiniz!
Bu uygulama ile müşterilerinizin faturalarına göre **ağırlıklı ortalama vade** hesaplayabilir 
ve uygun çek vadesi önerileri alabilirsiniz.
""")

st.divider()

# Sidebar - Valör tarihi seçimi
with st.sidebar:
    st.header("⚙️ Ayarlar")
    valor_tarihi = st.date_input(
        "Valör Tarihi",
        value=datetime.now().date(),
        help="Hesaplamaların başlangıç tarihi"
    )
    st.info("💡 Valör tarihi, çeklerin tahsil edileceği referans tarihtir.")

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Fatura Bilgileri")
    
    # Fatura girişi için session state
    if 'faturalar' not in st.session_state:
        st.session_state.faturalar = []
    
    # Yeni fatura ekleme formu
    with st.form("fatura_form", clear_on_submit=True):
        form_col1, form_col2, form_col3 = st.columns([2, 2, 2])
        
        with form_col1:
            fatura_no = st.text_input("Fatura No", placeholder="örn: FAT-2025-001")
        
        with form_col2:
            fatura_tutari = st.number_input(
                "Fatura Tutarı (₺)", 
                min_value=0.0, 
                step=100.0,
                format="%.2f"
            )
        
        with form_col3:
            fatura_tarihi_input = st.date_input(
                "Fatura Tarihi", 
                value=valor_tarihi + timedelta(days=30),
                min_value=valor_tarihi,
                help="Fatura vade tarihi"
            )
        
        submitted = st.form_submit_button("➕ Fatura Ekle", use_container_width=True)
        
        if submitted:
            if fatura_no and fatura_tutari > 0:
                # Vade gününü hesapla (Fatura tarihi - Valör tarihi)
                fatura_vadesi = (fatura_tarihi_input - valor_tarihi).days
                
                st.session_state.faturalar.append({
                    'Fatura No': fatura_no,
                    'Tutar': fatura_tutari,
                    'Vade (Gün)': fatura_vadesi,
                    'Vade Tarihi': fatura_tarihi_input.strftime('%d.%m.%Y')
                })
                st.success(f"✅ {fatura_no} eklendi! ({fatura_vadesi} gün vade)")
                st.rerun()
            else:
                st.error("⚠️ Lütfen fatura numarası ve geçerli bir tutar girin!")
    
    # Fatura listesi
    if st.session_state.faturalar:
        st.markdown("#### 📋 Eklenen Faturalar")
        df = pd.DataFrame(st.session_state.faturalar)
        
        # Tutarı formatla
        df_display = df.copy()
        df_display['Tutar'] = df_display['Tutar'].apply(lambda x: f"₺{x:,.2f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Temizleme butonu
        if st.button("🗑️ Tüm Faturaları Temizle", type="secondary"):
            st.session_state.faturalar = []
            st.rerun()
    else:
        st.info("👆 Yukarıdaki formu kullanarak fatura ekleyin.")

with col2:
    st.subheader("💰 Hesaplama Sonuçları")
    
    if st.session_state.faturalar:
        # Hesaplamaları yap
        df = pd.DataFrame(st.session_state.faturalar)
        tutarlar = df['Tutar'].tolist()
        vadeler = df['Vade (Gün)'].tolist()
        
        toplam_tutar = calculations.toplam_tutar_hesapla(tutarlar)
        ortalama_vade = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler)
        cek_vadesi = valor_tarihi + timedelta(days=int(ortalama_vade))
        
        # Sonuçları göster
        st.metric(label="Toplam Fatura Tutarı", value=f"₺{toplam_tutar:,.2f}")
        st.metric(label="Ağırlıklı Ortalama Vade", value=f"{ortalama_vade:.1f} gün")
        st.metric(label="Önerilen Çek Vadesi", value=cek_vadesi.strftime('%d.%m.%Y'))
        
        st.divider()
        
        # Detaylı açıklama
        with st.expander("📊 Hesaplama Detayları", expanded=True):
            st.markdown(f"""
            **Hesaplama Yöntemi:**
            
            Ağırlıklı ortalama vade formülü:
            ```
            Ortalama Vade = Σ(Tutar × Vade) / Σ(Tutar)
            ```
            
            **Sizin Hesabınız:**
            """)
            
            # Her fatura için hesaplama
            for idx, row in df.iterrows():
                tutar = row['Tutar']
                vade = row['Vade (Gün)']
                agirlik = (tutar * vade)
                st.markdown(f"- {row['Fatura No']}: ₺{tutar:,.2f} × {vade} gün = {agirlik:,.2f}")
            
            st.markdown(f"""
            **Toplam:** {toplam_tutar:,.2f} ₺
            
            **Ortalama Vade:** {ortalama_vade:.1f} gün
            
            **Sonuç:** Müşterinizden **{cek_vadesi.strftime('%d.%m.%Y')}** vadeli çek almalısınız.
            """)
        
        # Excel'e aktar
        st.divider()
        if st.button("📥 Excel'e Aktar", use_container_width=True):
            # Excel oluşturma işlemi için
            df_export = df.copy()
            output = calculations.excel_export(df_export, valor_tarihi, ortalama_vade, cek_vadesi)
            
            st.download_button(
                label="💾 İndir",
                data=output,
                file_name=f"ortalama_vade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("📝 Hesaplama için en az bir fatura ekleyin.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <small>© 2025 Ortalama Vade Hesaplama Programı | By Goksel</small>
</div>
""", unsafe_allow_html=True)
