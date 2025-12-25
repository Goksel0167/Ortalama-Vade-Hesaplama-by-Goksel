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

# Sidebar - Çek bilgileri
with st.sidebar:
    st.header("⚙️ Çek Bilgileri")
    
    # Çek listesi için session state
    if 'cekler' not in st.session_state:
        st.session_state.cekler = []
    
    with st.form("cek_form"):
        st.subheader("➕ Çek Ekle")
        cek_no = st.text_input("Çek No", placeholder="örn: ÇEK-001")
        cek_tutari = st.number_input("Çek Tutarı (₺)", min_value=0.0, step=1000.0, format="%.2f")
        cek_vade_tarihi = st.date_input(
            "Çek Vade Tarihi",
            value=datetime.now().date() + timedelta(days=45)
        )
        
        if st.form_submit_button("Çek Ekle", use_container_width=True):
            if cek_no and cek_tutari > 0:
                st.session_state.cekler.append({
                    'Çek No': cek_no,
                    'Tutar': cek_tutari,
                    'Vade Tarihi': cek_vade_tarihi.strftime('%d.%m.%Y'),
                    'Vade Tarihi Raw': cek_vade_tarihi
                })
                st.success(f"✅ {cek_no} eklendi!")
                st.rerun()
    
    if st.session_state.cekler:
        st.markdown("#### 📋 Eklenen Çekler")
        for idx, cek in enumerate(st.session_state.cekler):
            st.text(f"{cek['Çek No']}: ₺{cek['Tutar']:,.0f} - {cek['Vade Tarihi']}")
        
        if st.button("🗑️ Tüm Çekleri Temizle", type="secondary", use_container_width=True):
            st.session_state.cekler = []
            st.rerun()
    else:
        st.info("💡 Müşteriden alacağınız çekleri ekleyin")
    
    st.divider()
    st.info("💡 Birden fazla çek ekleyerek faturaları çeklere dağıtabilirsiniz.")

# Ana içerik
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Fatura Bilgileri")
    
    # Fatura girişi için session state
    if 'faturalar' not in st.session_state:
        st.session_state.faturalar = []
    
    # Yeni fatura ekleme formu
    with st.form("fatura_form", clear_on_submit=True):
        form_col1, form_col2 = st.columns([2, 2])
        
        with form_col1:
            fatura_no = st.text_input("Fatura No", placeholder="örn: FAT-2025-001")
        
        with form_col2:
            fatura_tutari = st.number_input(
                "Fatura Tutarı (₺)", 
                min_value=0.0, 
                step=100.0,
                format="%.2f"
            )
        
        form_col3, form_col4 = st.columns([2, 2])
        
        with form_col3:
            fatura_tarihi_input = st.date_input(
                "Fatura Tarihi", 
                value=datetime.now().date(),
                help="Fatura kesilme tarihi"
            )
        
        with form_col4:
            valor_tarihi_input = st.date_input(
                "Valör Tarihi",
                value=datetime.now().date() + timedelta(days=30),
                help="Faturanın valör tarihi"
            )
        
        submitted = st.form_submit_button("➕ Fatura Ekle", use_container_width=True)
        
        if submitted:
            if fatura_no and fatura_tutari > 0:
                st.session_state.faturalar.append({
                    'Fatura No': fatura_no,
                    'Tutar': fatura_tutari,
                    'Fatura Tarihi': fatura_tarihi_input.strftime('%d.%m.%Y'),
                    'Valör Tarihi': valor_tarihi_input.strftime('%d.%m.%Y'),
                    'Fatura Tarihi Raw': fatura_tarihi_input,
                    'Valör Tarihi Raw': valor_tarihi_input
                })
                st.success(f"✅ {fatura_no} eklendi!")
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
    
    if st.session_state.faturalar and st.session_state.cekler:
        # DataFrame oluştur
        df_faturalar = pd.DataFrame(st.session_state.faturalar)
        df_cekler = pd.DataFrame(st.session_state.cekler)
        
        # Hesaplamalar için raw tarihleri kullan
        toplam_fatura = df_faturalar['Tutar'].sum()
        toplam_cek = df_cekler['Tutar'].sum()
        
        # Her fatura için her çek ile vade hesapla
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
        
        # Özet metrikler
        st.metric("Toplam Fatura", f"₺{toplam_fatura:,.2f}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Toplam Çek", f"₺{toplam_cek:,.2f}")
        with col_b:
            fark = toplam_cek - toplam_fatura
            st.metric("Fark", f"₺{fark:,.2f}", delta=f"{'Fazla' if fark > 0 else 'Eksik'}")
        
        st.divider()
        
        # Çek bazlı ortalama vadeler
        st.subheader("📊 Çek Bazlı Vade Analizi")
        
        for cek_no in df_cekler['Çek No']:
            with st.expander(f"💳 {cek_no}", expanded=True):
                cek_data = df_hesap[df_hesap['Çek No'] == cek_no]
                
                # Bu çek için ağırlıklı ortalama
                tutarlar = cek_data['Fatura Tutar'].tolist()
                vadeler_valor = cek_data['Vade (Gün) - Valör'].tolist()
                vadeler_cek = cek_data['Vade (Gün) - Çek'].tolist()
                
                ort_valor = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler_valor)
                ort_cek = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler_cek)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Ort. Valör Vadesi", f"{ort_valor:.1f} gün")
                with col2:
                    st.metric("Ort. Çek Vadesi", f"{ort_cek:.1f} gün")
                
                st.markdown("**İlgili Faturalar:**")
                for _, row in cek_data.iterrows():
                    st.text(f"• {row['Fatura No']}: ₺{row['Fatura Tutar']:,.0f} - Valör: {row['Vade (Gün) - Valör']} gün, Çek: {row['Vade (Gün) - Çek']} gün")
    
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
