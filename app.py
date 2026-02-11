import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calculations
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- LANGUAGE DICTIONARY ---
LANGUAGES = {
    'TR': {
        'page_title': 'Ortalama Vade Hesaplama',
        'app_title': '📊 Ortalama Vade Hesaplama Programı',
        'history_btn': '📚 Geçmiş Hesaplamalar',
        'last_calculations': '📚 Son 5 Hesaplama',
        'invoice': 'Fatura',
        'check': 'Çek',
        'items': 'adet',
        'load': '📂 Yükle',
        'close': '❌ Kapat',
        'loaded_success': 'tarihli hesaplama yüklendi!',
        'invoice_info': '📝 Fatura Bilgileri',
        'invoice_no': 'Fatura No',
        'invoice_no_placeholder': 'örn: FAT-2025-001',
        'invoice_amount': 'Fatura Tutarı (₺)',
        'amount_placeholder': 'örn: 10000',
        'invoice_date': 'Fatura Tarihi',
        'maturity_days': 'Vade (Gün)',
        'value_date': 'Valör Tarihi',
        'days_later': 'gün sonra',
        'add_invoice': '➕ Fatura Ekle',
        'added': 'eklendi!',
        'already_exists': 'zaten ekli!',
        'fill_all_fields': 'Lütfen tüm alanları doldurun!',
        'added_invoices': '📋 Eklenen Faturalar',
        'days': 'gün',
        'delete': 'Sil',
        'clear_all_invoices': '🗑️ Tüm Faturaları Temizle',
        'use_form_above': '👆 Yukarıdaki formu kullanarak fatura ekleyin.',
        'check_info': '💳 Çek Bilgileri',
        'customer_name': '👤 Müşteri Adı',
        'customer_placeholder': 'örn: ABC Ltd. Şti.',
        'recent_customers': 'Son kullanılan müşteriler:',
        'check_no': 'Çek No',
        'check_no_placeholder': 'örn: ÇEK-001',
        'check_amount': 'Çek Tutarı (₺)',
        'check_maturity_date': 'Çek Vade Tarihi',
        'maturity': 'Vade',
        'from_invoice_date': 'Fatura tarihinden',
        'onwards': 'itibaren',
        'add_invoice_first': '⚠️ Önce fatura ekleyin',
        'add_check': '➕ Çek Ekle',
        'customer': 'Müşteri',
        'fill_all_fields_customer': 'Lütfen tüm alanları doldurun (Müşteri adı dahil)!',
        'added_checks': '📋 Eklenen Çekler',
        'unknown': 'Bilinmiyor',
        'clear_all_checks': '🗑️ Tüm Çekleri Temizle',
        'add_checks_info': '💡 Müşteriden alacağınız çekleri ekleyin',
        'check_maturity_info': '💡 Çek vade tarihi otomatik olarak fatura tarihinden 90 gün sonraya ayarlanır. 🟢 90 günden az = İyi, 🔴 90 günden fazla = Dikkat!',
        'calculation_results': '💰 Hesaplama Sonuçları',
        'filter': '🔍 Filtreleme',
        'filter_options': '🔍 Veri Filtreleme Seçenekleri',
        'amount_range': 'Tutar Aralığı (₺)',
        'min_amount': 'Min Tutar',
        'max_amount': 'Max Tutar',
        'maturity_range': 'Vade Aralığı (Gün)',
        'min_maturity': 'Min Vade',
        'max_maturity': 'Max Vade',
        'apply_filter': '✅ Filtreyi Uygula',
        'filter_applied': '✅ Filtre uygulandı!',
        'no_data_filter': '⚠️ Filtre kriterleriyle eşleşen veri bulunamadı!',
        'total_invoice': 'Toplam Fatura',
        'total_check': 'Toplam Çek',
        'difference': 'Fark',
        'surplus': 'Fazla ✅',
        'deficit': 'Eksik ⚠️',
        'avg_value_maturity': 'Ort. Valör Vadesi',
        'avg_check_maturity': 'Ort. Çek Vadesi',
        'avg_invoice_maturity': 'Ort. Fatura Vadesi',
        'avg_overall_maturity': 'Vade Farkı',
        'avg_invoice_maturity_subtitle': 'Fatura-Valör',
        'avg_check_maturity_subtitle': 'Fatura-Çek',
        'avg_overall_maturity_subtitle': 'Çek - Valör',
        'download_results': '📥 Hesaplama Sonuçlarını İndir',
        'download_excel': '📥 Tüm Detayları Excel\'e İndir (Formatlanmış)',
        'excel_info': '💡 Excel dosyası 6 sayfa içerir: Özet, Hesaplama Detayı, Faturalar, Çekler, Fatura Vade Dağılımı ve Çek Vade Dağılımı',
        'chart_analysis': '📊 Grafik Analizler',
        'maturity_distribution': '📈 Vade Dağılımı',
        'comparison': '🎯 Karşılaştırma',
        'timeline': '📅 Zaman Çizelgesi',
        'detailed_analysis': '💹 Detaylı Analiz',
        'currency': '₺',
        'date_format': '%d.%m.%Y',
        'excel_date_format': 'dd.mm.yyyy',
        'excel_currency': '₺#,##0.00',
        'sheet_summary': 'Özet',
        'sheet_calculation': 'Hesaplama Detayı',
        'sheet_invoices': 'Faturalar',
        'sheet_checks': 'Çekler',
        'sheet_invoice_distribution': 'Fatura Vade Dağılımı',
        'sheet_check_distribution': 'Çek Vade Dağılımı',
        'add_one_check': '⚠️ Lütfen en az bir çek ekleyin!',
        'add_one_invoice': '⚠️ Lütfen en az bir fatura ekleyin!',
        'add_to_calculate': '📝 Fatura ve çek ekleyerek hesaplama yapın.',
        'footer': '© 2025 Ortalama Vade Hesaplama Programı | By Goksel',
        'invoice_maturity_dist': '📝 Fatura Vade Dağılımı (Valör Bazlı)',
        'invoice_amount_by_groups': 'Vade Gruplarına Göre Fatura Tutarları',
        'invoice_maturity_ratios': 'Fatura Vade Oranları',
        'check_maturity_dist': '💳 Çek Vade Dağılımı',
        'check_amount_by_groups': 'Vade Gruplarına Göre Çek Tutarları',
        'check_maturity_ratios': 'Çek Vade Oranları',
        'maturity_group': 'Vade Grubu',
        'count': 'Adet',
        'ratio': 'Oran (%)',
        'invoice_vs_check': '🎯 Fatura vs Çek Karşılaştırması',
        'category': 'Kategori',
        'total_amount': 'Toplam Tutar',
        'average': 'Ortalama',
        'amount_comparison': 'Toplam Tutar Karşılaştırması',
        'count_comparison': 'Adet',
        'average_amount': 'Ortalama Tutar',
        'avg_maturity_comparison': '📊 Ortalama Vade Karşılaştırması',
        'maturity_type': 'Vade Türü',
        'average_days': 'Ortalama Gün',
        'value_maturity': 'Valör Vadesi',
        'check_maturity': 'Çek Vadesi',
        'maturity_timeline': '📅 Vade Zaman Çizelgesi',
        'invoice_check_timeline': 'Fatura ve Çek Vade Zaman Çizelgesi',
        'date': 'Tarih',
        'maturity_amount_relation': '📊 Vade-Tutar İlişkisi',
        'invoice_by_maturity': 'Vade Periyoduna Göre Fatura Tutarları',
        'amount': 'Tutar',
        'type': 'Tür',
        'detailed_stats': '💹 Detaylı İstatistik Analizi',
        'invoice_stats': '📋 Fatura İstatistikleri',
        'check_stats': '💳 Çek İstatistikleri',
        'maturity_stats': '📊 Vade İstatistikleri',
        'total_invoice_count': 'Toplam Fatura Sayısı',
        'total_check_count': 'Toplam Çek Sayısı',
        'median_amount': 'Medyan Tutar',
        'std_deviation': 'Standart Sapma',
        'maturity_std_dev': 'Vade Std Sapma',
        'amount_dist_histogram': '📊 Tutar Dağılım Histogramı',
        'invoice_amount_dist': 'Fatura Tutar Dağılımı',
        'maturity_period_dist': 'Vade Periyodu Dağılımı',
        'frequency': 'Frekans',
        'general_maturity_analysis': '📊 Genel Vade Analizi',
        'detailed_calc_table': '📋 Detaylı Hesaplama Tablosu',
        'shortest_maturity': 'En Kısa Vade',
        'longest_maturity': 'En Uzun Vade',
        'average_maturity': 'Ortalama Vade',
        'standard_deviation': 'Standart Sapma',
        'check_based_analysis': '💳 Çek Bazlı Vade Analizi',
        'avg_value_mat': '📅 Ort. Valör Vadesi',
        'avg_check_mat': '📝 Ort. Çek Vadesi',
        'value_mat_stats': '**Valör Vadesi İstatistikleri:**',
        'check_mat_stats': '**Çek Vadesi İstatistikleri:**',
        'related_invoices': '**📋 İlgili Faturalar:**',
        'no_checks_warning': '⚠️ Lütfen en az bir çek ekleyin!',
        'no_invoices_warning': '⚠️ Lütfen en az bir fatura ekleyin!',
        'add_data_info': '📝 Hesaplama yapmak için fatura ve çek ekleyin.',
        'min': 'Min',
        'max': 'Max',
        'std': 'Std'
    },
    'EN': {
        'page_title': 'Average Maturity Calculation',
        'app_title': '📊 Average Maturity Calculation Program',
        'history_btn': '📚 Calculation History',
        'last_calculations': '📚 Last 5 Calculations',
        'invoice': 'Invoice',
        'check': 'Check',
        'items': 'items',
        'load': '📂 Load',
        'close': '❌ Close',
        'loaded_success': 'calculation loaded!',
        'invoice_info': '📝 Invoice Information',
        'invoice_no': 'Invoice No',
        'invoice_no_placeholder': 'e.g: INV-2025-001',
        'invoice_amount': 'Invoice Amount ($)',
        'amount_placeholder': 'e.g: 10000',
        'invoice_date': 'Invoice Date',
        'maturity_days': 'Maturity (Days)',
        'value_date': 'Value Date',
        'days_later': 'days later',
        'add_invoice': '➕ Add Invoice',
        'added': 'added!',
        'already_exists': 'already exists!',
        'fill_all_fields': 'Please fill in all fields!',
        'added_invoices': '📋 Added Invoices',
        'days': 'days',
        'delete': 'Delete',
        'clear_all_invoices': '🗑️ Clear All Invoices',
        'use_form_above': '👆 Use the form above to add invoices.',
        'check_info': '💳 Check Information',
        'customer_name': '👤 Customer Name',
        'customer_placeholder': 'e.g: ABC Ltd. Co.',
        'recent_customers': 'Recently used customers:',
        'check_no': 'Check No',
        'check_no_placeholder': 'e.g: CHK-001',
        'check_amount': 'Check Amount ($)',
        'check_maturity_date': 'Check Maturity Date',
        'maturity': 'Maturity',
        'from_invoice_date': 'From invoice date',
        'onwards': '',
        'add_invoice_first': '⚠️ Add invoice first',
        'add_check': '➕ Add Check',
        'customer': 'Customer',
        'fill_all_fields_customer': 'Please fill in all fields (including customer name)!',
        'added_checks': '📋 Added Checks',
        'unknown': 'Unknown',
        'clear_all_checks': '🗑️ Clear All Checks',
        'add_checks_info': '💡 Add checks you will receive from customers',
        'check_maturity_info': '💡 Check maturity date is automatically set to 90 days after invoice date. 🟢 Less than 90 days = Good, 🔴 More than 90 days = Caution!',
        'calculation_results': '💰 Calculation Results',
        'filter': '🔍 Filter',
        'filter_options': '🔍 Data Filtering Options',
        'amount_range': 'Amount Range ($)',
        'min_amount': 'Min Amount',
        'max_amount': 'Max Amount',
        'maturity_range': 'Maturity Range (Days)',
        'min_maturity': 'Min Maturity',
        'max_maturity': 'Max Maturity',
        'apply_filter': '✅ Apply Filter',
        'filter_applied': '✅ Filter applied!',
        'no_data_filter': '⚠️ No data found matching filter criteria!',
        'total_invoice': 'Total Invoice',
        'total_check': 'Total Check',
        'difference': 'Difference',
        'surplus': 'Surplus ✅',
        'deficit': 'Deficit ⚠️',
        'avg_value_maturity': 'Avg. Value Maturity',
        'avg_check_maturity': 'Avg. Check Maturity',
        'avg_invoice_maturity': 'Avg. Invoice Maturity',
        'avg_overall_maturity': 'Maturity Gap',
        'avg_invoice_maturity_subtitle': 'Invoice-Value',
        'avg_check_maturity_subtitle': 'Invoice-Check',
        'avg_overall_maturity_subtitle': 'Check - Value',
        'download_results': '📥 Download Calculation Results',
        'download_excel': '📥 Download All Details to Excel (Formatted)',
        'excel_info': '💡 Excel file contains 6 sheets: Summary, Calculation Detail, Invoices, Checks, Invoice Maturity Distribution and Check Maturity Distribution',
        'chart_analysis': '📊 Chart Analysis',
        'maturity_distribution': '📈 Maturity Distribution',
        'comparison': '🎯 Comparison',
        'timeline': '📅 Timeline',
        'detailed_analysis': '💹 Detailed Analysis',
        'currency': '$',
        'date_format': '%m/%d/%Y',
        'excel_date_format': 'mm/dd/yyyy',
        'excel_currency': '$#,##0.00',
        'sheet_summary': 'Summary',
        'sheet_calculation': 'Calculation Detail',
        'sheet_invoices': 'Invoices',
        'sheet_checks': 'Checks',
        'sheet_invoice_distribution': 'Invoice Maturity Distribution',
        'sheet_check_distribution': 'Check Maturity Distribution',
        'add_one_check': '⚠️ Please add at least one check!',
        'add_one_invoice': '⚠️ Please add at least one invoice!',
        'add_to_calculate': '📝 Add invoices and checks to perform calculation.',
        'footer': '© 2025 Average Maturity Calculation Program | By Goksel',
        'invoice_maturity_dist': '📝 Invoice Maturity Distribution (Value Based)',
        'invoice_amount_by_groups': 'Invoice Amount by Maturity Groups',
        'invoice_maturity_ratios': 'Invoice Maturity Ratios',
        'check_maturity_dist': '💳 Check Maturity Distribution',
        'check_amount_by_groups': 'Check Amount by Maturity Groups',
        'check_maturity_ratios': 'Check Maturity Ratios',
        'maturity_group': 'Maturity Group',
        'count': 'Count',
        'ratio': 'Ratio (%)',
        'invoice_vs_check': '🎯 Invoice vs Check Comparison',
        'category': 'Category',
        'total_amount': 'Total Amount',
        'average': 'Average',
        'amount_comparison': 'Total Amount Comparison',
        'count_comparison': 'Count',
        'average_amount': 'Average Amount',
        'avg_maturity_comparison': '📊 Average Maturity Comparison',
        'maturity_type': 'Maturity Type',
        'average_days': 'Average Days',
        'value_maturity': 'Value Maturity',
        'check_maturity': 'Check Maturity',
        'maturity_timeline': '📅 Maturity Timeline',
        'invoice_check_timeline': 'Invoice and Check Maturity Timeline',
        'date': 'Date',
        'maturity_amount_relation': '📊 Maturity-Amount Relationship',
        'invoice_by_maturity': 'Invoice Amounts by Maturity Period',
        'amount': 'Amount',
        'type': 'Type',
        'detailed_stats': '💹 Detailed Statistical Analysis',
        'invoice_stats': '📋 Invoice Statistics',
        'check_stats': '💳 Check Statistics',
        'maturity_stats': '📊 Maturity Statistics',
        'total_invoice_count': 'Total Invoice Count',
        'total_check_count': 'Total Check Count',
        'median_amount': 'Median Amount',
        'std_deviation': 'Std Deviation',
        'maturity_std_dev': 'Maturity Std Dev',
        'amount_dist_histogram': '📊 Amount Distribution Histogram',
        'invoice_amount_dist': 'Invoice Amount Distribution',
        'maturity_period_dist': 'Maturity Period Distribution',
        'frequency': 'Frequency',
        'general_maturity_analysis': '📊 General Maturity Analysis',
        'detailed_calc_table': '📋 Detailed Calculation Table',
        'shortest_maturity': 'Shortest Maturity',
        'longest_maturity': 'Longest Maturity',
        'average_maturity': 'Average Maturity',
        'standard_deviation': 'Standard Deviation',
        'check_based_analysis': '💳 Check-Based Maturity Analysis',
        'avg_value_mat': '📅 Avg. Value Maturity',
        'avg_check_mat': '📝 Avg. Check Maturity',
        'value_mat_stats': '**Value Maturity Statistics:**',
        'check_mat_stats': '**Check Maturity Statistics:**',
        'related_invoices': '**📋 Related Invoices:**',
        'no_checks_warning': '⚠️ Please add at least one check!',
        'no_invoices_warning': '⚠️ Please add at least one invoice!',
        'add_data_info': '📝 Add invoices and checks to perform calculation.',
        'min': 'Min',
        'max': 'Max',
        'std': 'Std'
    }
}

# --- EXCEL DOWNLOAD FUNCTION (ADVANCED) ---
def to_excel_bytes(df_dict, lang='TR'):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Format definitions
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        currency_format = workbook.add_format({
            'num_format': LANGUAGES[lang]['excel_currency'],
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': LANGUAGES[lang]['excel_date_format'],
            'border': 1,
            'align': 'center'
        })
        
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
            worksheet = writer.sheets[sheet_name]
            
            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Adjust column widths and format
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_length)
                
                # Format for currency columns
                if any(keyword in col for keyword in ['Amount', 'Total', 'Tutar', 'Toplam']):
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, idx, df.iloc[row_num-1][col], currency_format)
                # Format for number columns (including Maturity Difference)
                elif any(keyword in col for keyword in ['Days', 'Maturity', 'Count', 'Difference', 'Gün', 'Vade', 'Adet', 'Fark']):
                    for row_num in range(1, len(df) + 1):
                        worksheet.write(row_num, idx, df.iloc[row_num-1][col], number_format)
    
    return output.getvalue()

# Main application title
st.set_page_config(page_title="Average Maturity Calculation", page_icon="📊", layout="wide")

# Session state başlatma - EN BAŞTA OLMALI
if 'language' not in st.session_state:
    st.session_state.language = 'TR'  # Default language
if 'faturalar' not in st.session_state:
    st.session_state.faturalar = []
if 'cekler' not in st.session_state:
    st.session_state.cekler = []
if 'musteri_gecmisi' not in st.session_state:
    st.session_state.musteri_gecmisi = []  # Son 5 müşteri kaydı
if 'hesaplama_gecmisi' not in st.session_state:
    st.session_state.hesaplama_gecmisi = []  # Son 5 hesaplama kaydı
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

# --- MONETARY PARSING FONKSIYONLARI ---
def parse_amount(val):
    """
    Monetary format parser supporting both Turkish (1.000.000,00) and English (1,000,000.00) formats.
    Intelligently detects which separator is the decimal point.
    """
    if val is None or val == '':
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    # Remove currency symbols
    for symbol in ['₺', '$', '€', '£', 'TL', 'USD', 'EUR', 'GBP']:
        val_str = val_str.replace(symbol, '')
    val_str = val_str.strip()
    
    if not val_str or val_str == '-':
        return 0.0
    
    # Count separators
    dot_count = val_str.count('.')
    comma_count = val_str.count(',')
    
    # Find last separator positions
    last_dot = val_str.rfind('.')
    last_comma = val_str.rfind(',')
    
    # Determine format based on separator positions and counts
    if dot_count == 0 and comma_count == 0:
        # No separators - plain number
        return float(val_str)
    elif dot_count > 0 and comma_count == 0:
        # Only dots
        if dot_count == 1 and last_dot > len(val_str) - 4:
            # Single dot in last 3 positions: decimal point (e.g., "100.50")
            return float(val_str)
        else:
            # Multiple dots or dot not in decimal position: thousand separator (e.g., "1.000.000")
            return float(val_str.replace('.', ''))
    elif comma_count > 0 and dot_count == 0:
        # Only commas
        if comma_count == 1 and last_comma > len(val_str) - 4:
            # Single comma in last 3 positions: decimal point (e.g., "100,50")
            return float(val_str.replace(',', '.'))
        else:
            # Multiple commas: thousand separator (e.g., "1,000,000")
            return float(val_str.replace(',', ''))
    else:
        # Both separators present
        if last_comma > last_dot:
            # Comma comes last: Turkish format (1.000.000,00)
            # Remove dots (thousand), replace comma with dot (decimal)
            cleaned = val_str.replace('.', '').replace(',', '.')
            return float(cleaned)
        else:
            # Dot comes last: English format (1,000,000.00)
            # Remove commas (thousand), keep dot (decimal)
            cleaned = val_str.replace(',', '')
            return float(cleaned)

def sanitize_records(records):
    """Clean monetary amounts in record lists before calculations."""
    cleaned = []
    for rec in records:
        rec_copy = rec.copy()
        if 'Tutar' in rec_copy:
            rec_copy['Tutar'] = parse_amount(rec_copy['Tutar'])
        cleaned.append(rec_copy)
    return cleaned

# Get current language texts
lang = st.session_state.language
t = LANGUAGES[lang]

# Language selector in sidebar
with st.sidebar:
    st.markdown("### 🌐 Language / Dil")
    selected_lang = st.radio(
        "Select Language",
        options=['TR', 'EN'],
        format_func=lambda x: '🇹🇷 Türkçe' if x == 'TR' else '🇬🇧 English',
        index=0 if st.session_state.language == 'TR' else 1,
        key='lang_selector'
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    st.divider()

# Title and history button
title_col1, title_col2 = st.columns([4, 1])
with title_col1:
    st.title(t['app_title'])
with title_col2:
    if st.session_state.hesaplama_gecmisi:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t['history_btn'], use_container_width=True, type="secondary"):
            st.session_state.show_history = not st.session_state.get('show_history', False)
            st.rerun()

# Show calculation history
if st.session_state.get('show_history', False) and st.session_state.hesaplama_gecmisi:
    with st.expander(t['last_calculations'], expanded=True):
        for idx, gecmis in enumerate(st.session_state.hesaplama_gecmisi):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{idx+1}.** {gecmis['tarih']}")
            with col2:
                st.write(f"{t['invoice']}: {gecmis['fatura_adet']} {t['items']}, {t['check']}: {gecmis['cek_adet']} {t['items']}")
            with col3:
                if st.button(t['load'], key=f"load_history_{idx}", use_container_width=True):
                    st.session_state.faturalar = gecmis['faturalar']
                    st.session_state.cekler = gecmis['cekler']
                    st.success(f"✅ {gecmis['tarih']} {t['loaded_success']}")
                    st.session_state.show_history = False
                    st.rerun()
        if st.button(t['close'], use_container_width=True):
            st.session_state.show_history = False
            st.rerun()
    st.divider()

# Ana içerik - 2 sütun
col1, col2 = st.columns([1, 1])

# LEFT COLUMN: Invoice Information
with col1:
    st.subheader(t['invoice_info'])
    
    # QUICK INVOICE ENTRY
    form_col1, form_col2 = st.columns([2, 2])
    with form_col1:
        fatura_no = st.text_input(t['invoice_no'], placeholder=t['invoice_no_placeholder'], key="fatura_no")
    with form_col2:
        fatura_tutari = st.number_input(
            t['invoice_amount'], 
            min_value=0.0, 
            step=100.0,
            format="%.2f",
            key="fatura_tutari",
            value=None,
            placeholder=t['amount_placeholder']
        )
    
    form_col3, form_col4 = st.columns([2, 2])
    with form_col3:
        fatura_tarihi_input = st.date_input(
            t['invoice_date'], 
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
            t['maturity_days'],
            min_value=0,
            max_value=365,
            value=90,
            step=1,
            key="vade_gun"
        )
        if fatura_tarihi is not None and hasattr(fatura_tarihi, 'strftime'):
            hesaplanan_valor = fatura_tarihi + timedelta(days=vade_gun)
            valor_str = hesaplanan_valor.strftime(t['date_format'])
        else:
            hesaplanan_valor = None
            valor_str = "-"
        st.info(f"📅 {t['value_date']}: **{valor_str}** ({vade_gun} {t['days_later']})")

    # Add button
    if st.button(t['add_invoice'], type="primary", use_container_width=True, key="add_fatura_btn"):
        if fatura_no and fatura_tutari and fatura_tutari > 0:
            if not any(f['Fatura No'] == fatura_no for f in st.session_state.faturalar):
                fatura_tarihi_str = fatura_tarihi.strftime(t['date_format']) if fatura_tarihi is not None and hasattr(fatura_tarihi, 'strftime') else "-"
                valor_str = hesaplanan_valor.strftime(t['date_format']) if hesaplanan_valor is not None and hasattr(hesaplanan_valor, 'strftime') else "-"
                st.session_state.faturalar.append({
                    'Fatura No': fatura_no,
                    'Tutar': fatura_tutari,
                    'Fatura Tarihi': fatura_tarihi_str,
                    'Vade (Gün)': vade_gun,
                    'Valör Tarihi': valor_str,
                    'Fatura Tarihi Raw': fatura_tarihi,
                    'Valör Tarihi Raw': hesaplanan_valor
                })
                st.success(f"✅ {fatura_no} {t['added']}")
                st.rerun()
            else:
                st.error(f"❌ {fatura_no} {t['already_exists']}")
        else:
            st.error(f"❌ {t['fill_all_fields']}")

    # Invoice list
    if st.session_state.faturalar:
        st.markdown(f"#### {t['added_invoices']}")
        
        for idx, fatura in enumerate(st.session_state.faturalar):
            fcol1, fcol2 = st.columns([5, 1])
            with fcol1:
                st.text(f"{fatura['Fatura No']}: {t['currency']}{fatura['Tutar']:,.2f} | {fatura['Vade (Gün)']} {t['days']} | {t['invoice']}: {fatura['Fatura Tarihi']} → {t['value_date']}: {fatura['Valör Tarihi']}")
            with fcol2:
                if st.button("🗑️", key=f"del_fatura_{idx}", help=t['delete']):
                    st.session_state.faturalar.pop(idx)
                    st.rerun()
        
        # Clear button
        if st.button(t['clear_all_invoices'], type="secondary"):
            st.session_state.faturalar = []
            st.rerun()
    else:
        st.info(t['use_form_above'])

# RIGHT COLUMN: Check Information
with col2:
    st.subheader(t['check_info'])
    
    # CUSTOMER INFORMATION
    musteri_adi = st.text_input(
        t['customer_name'], 
        placeholder=t['customer_placeholder'],
        key="musteri_adi"
    )
    
    # LAST 5 CUSTOMER QUICK SELECT
    if st.session_state.musteri_gecmisi:
        st.caption(t['recent_customers'])
        musteri_col = st.columns(min(len(st.session_state.musteri_gecmisi), 5))
        for idx, musteri in enumerate(st.session_state.musteri_gecmisi[:5]):
            with musteri_col[idx]:
                if st.button(f"📌 {musteri}", key=f"musteri_hizli_{idx}", use_container_width=True):
                    st.session_state.musteri_adi = musteri
                    st.rerun()
    
    # CHECK ENTRY
    cek_col1, cek_col2 = st.columns([2, 2])
    with cek_col1:
        cek_no = st.text_input(t['check_no'], placeholder=t['check_no_placeholder'], key="cek_no")
    with cek_col2:
        cek_tutari = st.number_input(
            t['check_amount'], 
            min_value=0.0, 
            step=100.0,
            format="%.2f",
            key="cek_tutari",
            value=None,
            placeholder=t['amount_placeholder']
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
            t['check_maturity_date'],
            value=default_cek_tarihi,
            key="cek_vade_tarihi"
        )
        if isinstance(cek_vade_tarihi, tuple):
            if len(cek_vade_tarihi) > 0:
                cek_vade_tarihi = cek_vade_tarihi[0]
            else:
                cek_vade_tarihi = default_cek_tarihi
    
    with cek_col4:
        # Maturity day calculation - from invoice date
        if st.session_state.faturalar and ilk_fatura_tarihi_cek:
            cek_vade_gun = (cek_vade_tarihi - ilk_fatura_tarihi_cek).days
            referans_tarihi_str = ilk_fatura_tarihi_cek.strftime(t['date_format'])
            
            # Determine color and emoji based on maturity period
            if cek_vade_gun > 90:
                vade_renk = "error"  # Red
                vade_emoji = "⚠️"
                vade_mesaj = f"📅 {t['maturity']}: **{cek_vade_gun} {t['days']}** {t['days_later']} {vade_emoji}"
                vade_detay = f"{t['from_invoice_date']} ({referans_tarihi_str}) {t['onwards']}"
            elif cek_vade_gun < 90:
                vade_renk = "success"  # Green
                vade_emoji = "✅"
                vade_mesaj = f"📅 {t['maturity']}: **{cek_vade_gun} {t['days']}** {t['days_later']} {vade_emoji}"
                vade_detay = f"{t['from_invoice_date']} ({referans_tarihi_str}) {t['onwards']}"
            else:  # cek_vade_gun == 90
                vade_renk = "info"  # Blue
                vade_emoji = "ℹ️"
                vade_mesaj = f"📅 {t['maturity']}: **{cek_vade_gun} {t['days']}** {t['days_later']} {vade_emoji}"
                vade_detay = f"{t['from_invoice_date']} ({referans_tarihi_str}) {t['onwards']}"
            
            # Show colored warning
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
            st.warning(f"📅 {t['maturity']}: **{cek_vade_gun} {t['days']}** {t['days_later']}")
            st.caption(t['add_invoice_first'])

    # Add button
    if st.button(t['add_check'], type="primary", use_container_width=True, key="add_cek_btn"):
        if cek_no and cek_tutari and cek_tutari > 0 and musteri_adi:
            if not any(c['Çek No'] == cek_no for c in st.session_state.cekler):
                cek_vade_tarihi_str = cek_vade_tarihi.strftime(t['date_format']) if hasattr(cek_vade_tarihi, 'strftime') else "-"
                
                # Calculate maturity days
                if st.session_state.faturalar and ilk_fatura_tarihi_cek:
                    cek_vade_gun_kayit = (cek_vade_tarihi - ilk_fatura_tarihi_cek).days
                else:
                    cek_vade_gun_kayit = (cek_vade_tarihi - datetime.now().date()).days
                
                # Add to customer history (keep last 5)
                if musteri_adi not in st.session_state.musteri_gecmisi:
                    st.session_state.musteri_gecmisi.insert(0, musteri_adi)
                    if len(st.session_state.musteri_gecmisi) > 5:
                        st.session_state.musteri_gecmisi = st.session_state.musteri_gecmisi[:5]
                else:
                    # If exists, move to top
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
                st.success(f"✅ {cek_no} {t['added']} ({t['customer']}: {musteri_adi})")
                st.rerun()
            else:
                st.error(f"❌ {cek_no} {t['already_exists']}")
        else:
            st.error(f"❌ {t['fill_all_fields_customer']}")

    # Check list
    if st.session_state.cekler:
        st.markdown(f"#### {t['added_checks']}")
        
        for idx, cek in enumerate(st.session_state.cekler):
            ccol1, ccol2 = st.columns([5, 1])
            with ccol1:
                # Show maturity day info
                vade_gun_info = cek.get('Vade (Gün)', 0)
                musteri_info = cek.get('Müşteri', t['unknown'])
                if vade_gun_info > 90:
                    vade_icon = "🔴"
                elif vade_gun_info < 90:
                    vade_icon = "🟢"
                else:
                    vade_icon = "🔵"
                st.text(f"👤 {musteri_info} | {cek['Çek No']}: {t['currency']}{cek['Tutar']:,.2f} | {t['maturity']}: {cek['Vade Tarihi']} ({vade_gun_info} {t['days']} {vade_icon})")
            with ccol2:
                if st.button("🗑️", key=f"del_cek_{idx}", help=t['delete']):
                    st.session_state.cekler.pop(idx)
                    st.rerun()
        
        if st.button(t['clear_all_checks'], type="secondary"):
            st.session_state.cekler = []
            st.rerun()
    else:
        st.info(t['add_checks_info'])

st.divider()
st.info(t['check_maturity_info'])
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
    # Hesaplamayı geçmişe kaydet
    gecmis_kayit = {
        'tarih': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        'faturalar': st.session_state.faturalar.copy(),
        'cekler': st.session_state.cekler.copy(),
        'fatura_adet': len(st.session_state.faturalar),
        'cek_adet': len(st.session_state.cekler)
    }
    
    # Aynı veri varsa tekrar ekleme
    aynisi_var = False
    for gecmis in st.session_state.hesaplama_gecmisi:
        if (gecmis['fatura_adet'] == gecmis_kayit['fatura_adet'] and 
            gecmis['cek_adet'] == gecmis_kayit['cek_adet']):
            # Daha detaylı kontrol
            if len(gecmis['faturalar']) > 0 and len(gecmis_kayit['faturalar']) > 0:
                if gecmis['faturalar'][0] == gecmis_kayit['faturalar'][0]:
                    aynisi_var = True
                    break
    
    if not aynisi_var:
        st.session_state.hesaplama_gecmisi.insert(0, gecmis_kayit)
        if len(st.session_state.hesaplama_gecmisi) > 5:
            st.session_state.hesaplama_gecmisi = st.session_state.hesaplama_gecmisi[:5]
    
    st.markdown("## 💰 Calculation Results")
    
    st.markdown(f"## {t['calculation_results']}")
    
    # FILTERING SECTION
    col_filter1, col_filter2 = st.columns([1, 4])
    with col_filter1:
        if st.button(t['filter'], use_container_width=True):
            st.session_state.show_filters = not st.session_state.show_filters
    
    if st.session_state.show_filters:
        with st.expander(t['filter_options'], expanded=True):
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                st.markdown(f"**{t['amount_range']}**")
                filter_min_tutar = st.number_input(t['min_amount'], min_value=0.0, value=0.0, step=1000.0, key="filter_min_input")
                filter_max_tutar = st.number_input(t['max_amount'], min_value=0.0, value=1000000.0, step=1000.0, key="filter_max_input")
            with filter_col2:
                st.markdown(f"**{t['maturity_range']}**")
                filter_min_vade = st.number_input(t['min_maturity'], min_value=0, value=0, step=10, key="filter_vade_min_input")
                filter_max_vade = st.number_input(t['max_maturity'], min_value=0, value=365, step=10, key="filter_vade_max_input")
            
            if st.button(t['apply_filter'], type="primary", use_container_width=True):
                st.session_state.filter_min_tutar = filter_min_tutar
                st.session_state.filter_max_tutar = filter_max_tutar
                st.session_state.filter_min_vade = filter_min_vade
                st.session_state.filter_max_vade = filter_max_vade
                st.success(t['filter_applied'])
                st.rerun()
    
    # Sanitize monetary amounts before creating DataFrames
    faturalar_clean = sanitize_records(st.session_state.faturalar)
    cekler_clean = sanitize_records(st.session_state.cekler)
    
    df_faturalar = pd.DataFrame(faturalar_clean)
    df_cekler = pd.DataFrame(cekler_clean)
    
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
    
    # Warn if no data matches filter
    if df_faturalar_filtered.empty or df_cekler_filtered.empty:
        st.warning(t['no_data_filter'])
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

    # DataFrame for summary metrics
    df_ozet = pd.DataFrame([
        {t['sheet_summary'].split()[0] if lang == 'EN' else 'Açıklama': t['total_invoice'], 
         t['sheet_summary'].split()[-1] if lang == 'EN' else 'Tutar': toplam_fatura, 
         'Adet' if lang == 'TR' else 'Count': len(df_faturalar_filtered)},
        {t['sheet_summary'].split()[0] if lang == 'EN' else 'Açıklama': t['total_check'], 
         t['sheet_summary'].split()[-1] if lang == 'EN' else 'Tutar': toplam_cek, 
         'Adet' if lang == 'TR' else 'Count': len(df_cekler_filtered)},
        {t['sheet_summary'].split()[0] if lang == 'EN' else 'Açıklama': t['difference'], 
         t['sheet_summary'].split()[-1] if lang == 'EN' else 'Tutar': toplam_cek-toplam_fatura, 
         'Adet' if lang == 'TR' else 'Count': "-"}
    ])
    
    # Invoice detail table
    df_faturalar_detay = df_faturalar_filtered[['Fatura No', 'Tutar', 'Fatura Tarihi', 'Valör Tarihi', 'Vade (Gün)']].copy()
    if lang == 'TR':
        df_faturalar_detay.columns = ['Fatura No', f'Tutar ({t["currency"]})', 'Fatura Tarihi', 'Valör Tarihi', 'Vade (Gün)']
    else:
        df_faturalar_detay.columns = ['Invoice No', f'Amount ({t["currency"]})', 'Invoice Date', 'Value Date', 'Maturity (Days)']
    
    # Check detail table
    df_cekler_detay = df_cekler_filtered[['Çek No', 'Tutar', 'Vade Tarihi']].copy()
    if lang == 'TR':
        df_cekler_detay.columns = ['Çek No', f'Tutar ({t["currency"]})', 'Vade Tarihi']
    else:
        df_cekler_detay.columns = ['Check No', f'Amount ({t["currency"]})', 'Maturity Date']

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
    
    # === MUHASEBE MANTIĞI: DOĞRU AĞIRLIKLI ORTALAMA TARİH HESAPLAMA ===
    
    # Referans tarihi: 1 Ocak 1970 (timestamp mantığı)
    epoch = datetime(1970, 1, 1).date()
    
    # 1. ORTALAMA FATURA TARİHİNİ HESAPLA
    agirlikli_fatura_tarihi_toplam = 0
    for _, row in df_faturalar_filtered.iterrows():
        if row['Fatura Tarihi Raw']:
            gun_farki = (row['Fatura Tarihi Raw'] - epoch).days
            agirlikli_fatura_tarihi_toplam += row['Tutar'] * gun_farki
    
    if toplam_fatura > 0:
        ortalama_fatura_gun = agirlikli_fatura_tarihi_toplam / toplam_fatura
        ortalama_fatura_tarihi_hesaplanan = epoch + timedelta(days=ortalama_fatura_gun)
    else:
        ortalama_fatura_tarihi_hesaplanan = datetime.now().date()
    
    # 2. ORTALAMA VALÖR TARİHİNİ HESAPLA
    agirlikli_valor_tarihi_toplam = 0
    for _, row in df_faturalar_filtered.iterrows():
        if row['Valör Tarihi Raw']:
            gun_farki = (row['Valör Tarihi Raw'] - epoch).days
            agirlikli_valor_tarihi_toplam += row['Tutar'] * gun_farki
    
    if toplam_fatura > 0:
        ortalama_valor_gun = agirlikli_valor_tarihi_toplam / toplam_fatura
        ortalama_valor_tarihi = epoch + timedelta(days=ortalama_valor_gun)
    else:
        ortalama_valor_tarihi = datetime.now().date()
    
    # 3. ORTALAMA ÇEK VADE TARİHİNİ HESAPLA
    agirlikli_cek_tarihi_toplam = 0
    for _, cek in df_cekler_filtered.iterrows():
        if cek['Vade Tarihi Raw']:
            gun_farki = (cek['Vade Tarihi Raw'] - epoch).days
            agirlikli_cek_tarihi_toplam += cek['Tutar'] * gun_farki
    
    if toplam_cek > 0:
        ortalama_cek_gun = agirlikli_cek_tarihi_toplam / toplam_cek
        ortalama_cek_tarihi = epoch + timedelta(days=ortalama_cek_gun)
    else:
        ortalama_cek_tarihi = datetime.now().date()
    
    # 4. METRIC CARD DEĞERLERİ - Ortalama Fatura Tarihinden İtibaren
    # Ortalama Fatura Vadesi = Ortalama Valör Tarihi - Ortalama Fatura Tarihi
    genel_ort_fatura_vadesi = (ortalama_valor_tarihi - ortalama_fatura_tarihi_hesaplanan).days
    
    # Ortalama Çek Vadesi = Ortalama Çek Tarihi - Ortalama Fatura Tarihi
    genel_ort_cek_vadesi = (ortalama_cek_tarihi - ortalama_fatura_tarihi_hesaplanan).days
    
    # Vade Farkı = Çek Vadesi - Fatura Vadesi
    genel_ort_genel = genel_ort_cek_vadesi - genel_ort_fatura_vadesi
    
    # Maturity distribution analysis - INVOICES (Value based)
    vade_gruplari = calculations.vade_analizi(tum_fatura_tutarlar, tum_valor_vadeler)
    df_fatura_vade_dagilim = pd.DataFrame([
        {
            'Vade Grubu' if lang == 'TR' else 'Maturity Group': grup,
            f'Tutar ({t["currency"]})' if lang == 'TR' else f'Amount ({t["currency"]})': data['tutar'],
            'Adet' if lang == 'TR' else 'Count': data['adet'],
            'Oran (%)' if lang == 'TR' else 'Ratio (%)': data['oran']
        }
        for grup, data in vade_gruplari.items()
    ])
    
    # Maturity distribution analysis - CHECKS
    cek_vade_gruplari = calculations.vade_analizi(tum_cek_tutarlar, tum_cek_vade_gunler)
    df_cek_vade_dagilim = pd.DataFrame([
        {
            'Vade Grubu' if lang == 'TR' else 'Maturity Group': grup,
            f'Tutar ({t["currency"]})' if lang == 'TR' else f'Amount ({t["currency"]})': data['tutar'],
            'Adet' if lang == 'TR' else 'Count': data['adet'],
            'Oran (%)' if lang == 'TR' else 'Ratio (%)': data['oran']
        }
        for grup, data in cek_vade_gruplari.items()
    ])

    # Excel download button - ADVANCED
    excel_data = {
        t['sheet_summary']: df_ozet,
        t['sheet_calculation']: df_hesap,
        t['sheet_invoices']: df_faturalar_detay,
        t['sheet_checks']: df_cekler_detay,
        t['sheet_invoice_distribution']: df_fatura_vade_dagilim,
        t['sheet_check_distribution']: df_cek_vade_dagilim
    }
    excel_bytes = to_excel_bytes(excel_data, lang)
    
    st.markdown("---")
    st.markdown(f"### {t['download_results']}")
    st.download_button(
        label=t['download_excel'],
        data=excel_bytes,
        file_name=f"average_maturity_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )
    st.caption(t['excel_info'])

    # WIDE METRICS BAR
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
            <div class='metric-value' style='color: #0d6efd;'>{t['currency']}{toplam_fatura:,.0f}</div>
            <div class='metric-label'>{t['total_invoice']}</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: #198754;'>{t['currency']}{toplam_cek:,.0f}</div>
            <div class='metric-label'>{t['total_check']}</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: {'#198754' if toplam_cek - toplam_fatura >= 0 else '#dc3545'};'>{t['currency']}{abs(toplam_cek - toplam_fatura):,.0f}</div>
            <div class='metric-label'>{t['difference']}</div>
            <div class='metric-sublabel'>{t['surplus'] if toplam_cek - toplam_fatura >= 0 else t['deficit']}</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: #17a2b8;'>{genel_ort_fatura_vadesi:.1f}</div>
            <div class='metric-label'>{t['avg_invoice_maturity']}</div>
            <div class='metric-sublabel'>{t['avg_invoice_maturity_subtitle']}</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: #6f42c1;'>{genel_ort_cek_vadesi:.1f}</div>
            <div class='metric-label'>{t['avg_check_maturity']}</div>
            <div class='metric-sublabel'>{t['avg_check_maturity_subtitle']}</div>
        </div>
        <div class='metric-block'>
            <div class='metric-value' style='color: {'#28a745' if genel_ort_genel >= 0 else '#dc3545'}; font-weight: 900;'>{genel_ort_genel:.1f}</div>
            <div class='metric-label' style='font-weight: 700;'>{t['avg_overall_maturity']}</div>
            <div class='metric-sublabel' style='font-weight: 600;'>{t['avg_overall_maturity_subtitle']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 📊 CHART VISUALIZATIONS
    st.markdown(f"## {t['chart_analysis']}")
    
    tab1, tab2, tab3, tab4 = st.tabs([t['maturity_distribution'], t['comparison'], t['timeline'], t['detailed_analysis']])
    
    with tab1:
        st.markdown(f"### {t['maturity_distribution']}")
        
        # Two separate charts: Invoice and Check
        st.markdown(f"#### {t['invoice_maturity_dist']}")
        graph_col1a, graph_col2a = st.columns(2)
        
        with graph_col1a:
            # Bar Chart - Invoice Amount Distribution by Maturity Groups
            # Get column names dynamically
            amount_col = 'Tutar (₺)' if lang == 'TR' else 'Amount ($)'
            group_col = 'Vade Grubu' if lang == 'TR' else 'Maturity Group'
            
            fig_bar_fatura = px.bar(
                df_fatura_vade_dagilim,
                x=group_col,
                y=amount_col,
                text=amount_col,
                title=t['invoice_amount_by_groups'],
                color=amount_col,
                color_continuous_scale='Blues'
            )
            fig_bar_fatura.update_traces(texttemplate=f"{t['currency']}%{{text:,.0f}}", textposition='outside')
            fig_bar_fatura.update_layout(
                xaxis_title=t['maturity_group'],
                yaxis_title=f"{t['amount']} ({t['currency']})",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_bar_fatura, use_container_width=True)
        
        with graph_col2a:
            # Pie Chart - Invoice Percentage Distribution
            amount_col = 'Tutar (₺)' if lang == 'TR' else 'Amount ($)'
            group_col = 'Vade Grubu' if lang == 'TR' else 'Maturity Group'
            
            fig_pie_fatura = px.pie(
                df_fatura_vade_dagilim[df_fatura_vade_dagilim[amount_col] > 0],
                values=amount_col,
                names=group_col,
                title=t['invoice_maturity_ratios'],
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pie_fatura.update_traces(texttemplate='%{label}<br>%{percent:.1%}', textposition='outside')
            fig_pie_fatura.update_layout(height=400)
            st.plotly_chart(fig_pie_fatura, use_container_width=True)
        
        st.divider()
        st.markdown(f"#### {t['check_maturity_dist']}")
        graph_col1b, graph_col2b = st.columns(2)
        
        with graph_col1b:
            # Bar Chart - Check Amount Distribution by Maturity Groups
            amount_col = 'Tutar (₺)' if lang == 'TR' else 'Amount ($)'
            group_col = 'Vade Grubu' if lang == 'TR' else 'Maturity Group'
            
            fig_bar_cek = px.bar(
                df_cek_vade_dagilim,
                x=group_col,
                y=amount_col,
                text=amount_col,
                title=t['check_amount_by_groups'],
                color=amount_col,
                color_continuous_scale='Greens'
            )
            fig_bar_cek.update_traces(texttemplate=f"{t['currency']}%{{text:,.0f}}", textposition='outside')
            fig_bar_cek.update_layout(
                xaxis_title=t['maturity_group'],
                yaxis_title=f"{t['amount']} ({t['currency']})",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_bar_cek, use_container_width=True)
        
        with graph_col2b:
            # Pie Chart - Check Percentage Distribution
            fig_pie_cek = px.pie(
                df_cek_vade_dagilim[df_cek_vade_dagilim[amount_col] > 0],
                values=amount_col,
                names=group_col,
                title=t['check_maturity_ratios'],
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig_pie_cek.update_traces(texttemplate='%{label}<br>%{percent:.1%}', textposition='outside')
            fig_pie_cek.update_layout(height=400)
            st.plotly_chart(fig_pie_cek, use_container_width=True)
    
    with tab2:
        st.markdown(f"### {t['invoice_vs_check']}")
        
        # Compare invoice and check amounts
        comparison_data = pd.DataFrame({
            t['category']: [t['invoice'], t['check']],
            t['total_amount']: [toplam_fatura, toplam_cek],
            t['count']: [len(df_faturalar_filtered), len(df_cekler_filtered)],
            t['average']: [toplam_fatura/len(df_faturalar_filtered) if len(df_faturalar_filtered) > 0 else 0,
                        toplam_cek/len(df_cekler_filtered) if len(df_cekler_filtered) > 0 else 0]
        })
        
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            # Amount comparison
            fig_comp1 = go.Figure(data=[
                go.Bar(name=t['total_amount'], x=comparison_data[t['category']], y=comparison_data[t['total_amount']],
                       text=comparison_data[t['total_amount']].apply(lambda x: f"{t['currency']}{x:,.0f}"),
                       textposition='outside',
                       marker_color=['#0d6efd', '#198754'])
            ])
            fig_comp1.update_layout(
                title=t['amount_comparison'],
                xaxis_title='',
                yaxis_title=f"{t['amount']} ({t['currency']})",
                height=400
            )
            st.plotly_chart(fig_comp1, use_container_width=True)
        
        with comp_col2:
            # Count and average comparison
            fig_comp2 = make_subplots(
                rows=1, cols=2,
                subplot_titles=(t['count'], t['average_amount']),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            fig_comp2.add_trace(
                go.Bar(x=comparison_data[t['category']], y=comparison_data[t['count']],
                       text=comparison_data[t['count']], textposition='outside',
                       marker_color=['#0d6efd', '#198754'], showlegend=False),
                row=1, col=1
            )
            
            fig_comp2.add_trace(
                go.Bar(x=comparison_data[t['category']], y=comparison_data[t['average']],
                       text=comparison_data[t['average']].apply(lambda x: f"{t['currency']}{x:,.0f}"),
                       textposition='outside',
                       marker_color=['#0d6efd', '#198754'], showlegend=False),
                row=1, col=2
            )
            
            fig_comp2.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_comp2, use_container_width=True)
        
        # Maturity comparison
        st.markdown(f"#### {t['avg_maturity_comparison']}")
        vade_comp_data = pd.DataFrame({
            t['maturity_type']: [t['value_maturity'], t['check_maturity']],
            t['average_days']: [genel_ort_valor, genel_ort_cek]
        })
        
        fig_vade = px.bar(
            vade_comp_data,
            x=t['maturity_type'],
            y=t['average_days'],
            text=t['average_days'],
            title=f"{t['avg_maturity_comparison']} ({t['days']})",
            color=t['maturity_type'],
            color_discrete_map={t['value_maturity']: '#fd7e14', t['check_maturity']: '#6f42c1'}
        )
        fig_vade.update_traces(texttemplate=f'%{{text:.1f}} {t["days"]}', textposition='outside')
        fig_vade.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_vade, use_container_width=True)
    
    with tab3:
        st.markdown(f"### {t['maturity_timeline']}")
        
        # Prepare data for timeline chart
        timeline_data = []
        
        # Add invoices
        for _, fatura in df_faturalar_filtered.iterrows():
            timeline_data.append({
                t['type']: t['invoice'],
                'No': fatura['Fatura No'],
                'Start': fatura['Fatura Tarihi Raw'],
                'End': fatura['Valör Tarihi Raw'],
                t['amount']: fatura['Tutar'],
                'Description': f"{fatura['Fatura No']} - {t['currency']}{fatura['Tutar']:,.0f}"
            })
        
        # Add checks
        if ilk_fatura_tarihi:
            for _, cek in df_cekler_filtered.iterrows():
                timeline_data.append({
                    t['type']: t['check'],
                    'No': cek['Çek No'],
                    'Start': ilk_fatura_tarihi,
                    'End': cek['Vade Tarihi Raw'],
                    t['amount']: cek['Tutar'],
                    'Description': f"{cek['Çek No']} - {t['currency']}{cek['Tutar']:,.0f}"
                })
        
        df_timeline = pd.DataFrame(timeline_data)
        
        if not df_timeline.empty:
            fig_timeline = px.timeline(
                df_timeline,
                x_start='Start',
                x_end='End',
                y='Description',
                color=t['type'],
                title=t['invoice_check_timeline'],
                color_discrete_map={t['invoice']: '#0d6efd', t['check']: '#198754'},
                hover_data=[t['amount']]
            )
            fig_timeline.update_layout(
                xaxis_title=t['date'],
                yaxis_title='',
                height=max(400, len(df_timeline) * 30)
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Maturity distribution chart - Scatter
        st.markdown(f"#### {t['maturity_amount_relation']}")
        scatter_data = []
        for _, fatura in df_faturalar_filtered.iterrows():
            scatter_data.append({
                t['maturity_days']: fatura['Vade (Gün)'],
                t['amount']: fatura['Tutar'],
                t['type']: t['invoice'],
                'No': fatura['Fatura No']
            })
        
        df_scatter = pd.DataFrame(scatter_data)
        
        fig_scatter = px.scatter(
            df_scatter,
            x=t['maturity_days'],
            y=t['amount'],
            size=t['amount'],
            color=t['type'],
            hover_data=['No'],
            title=t['invoice_by_maturity'],
            color_discrete_map={t['invoice']: '#0d6efd'}
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.markdown(f"### {t['detailed_stats']}")
        
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.markdown(f"#### {t['invoice_stats']}")
            st.metric(t['total_invoice_count'], len(df_faturalar_filtered))
            st.metric(t['total_amount'], f"{t['currency']}{toplam_fatura:,.0f}")
            st.metric(t['average_amount'], f"{t['currency']}{toplam_fatura/len(df_faturalar_filtered):,.0f}" if len(df_faturalar_filtered) > 0 else f"{t['currency']}0")
            st.metric(t['median_amount'], f"{t['currency']}{df_faturalar_filtered['Tutar'].median():,.0f}" if not df_faturalar_filtered.empty else f"{t['currency']}0")
            st.metric(t['std_deviation'], f"{t['currency']}{df_faturalar_filtered['Tutar'].std():,.0f}" if not df_faturalar_filtered.empty else f"{t['currency']}0")
        
        with detail_col2:
            st.markdown(f"#### {t['check_stats']}")
            st.metric(t['total_check_count'], len(df_cekler_filtered))
            st.metric(t['total_amount'], f"{t['currency']}{toplam_cek:,.0f}")
            st.metric(t['average_amount'], f"{t['currency']}{toplam_cek/len(df_cekler_filtered):,.0f}" if len(df_cekler_filtered) > 0 else f"{t['currency']}0")
            st.metric(t['median_amount'], f"{t['currency']}{df_cekler_filtered['Tutar'].median():,.0f}" if not df_cekler_filtered.empty else f"{t['currency']}0")
            st.metric(t['std_deviation'], f"{t['currency']}{df_cekler_filtered['Tutar'].std():,.0f}" if not df_cekler_filtered.empty else f"{t['currency']}0")
        
        with detail_col3:
            st.markdown(f"#### {t['maturity_stats']}")
            st.metric(t['avg_value_maturity'], f"{genel_ort_valor:.1f} {t['days']}")
            st.metric(t['avg_check_maturity'], f"{genel_ort_cek:.1f} {t['days']}")
            st.metric(t['min_maturity'], f"{min(tum_valor_vadeler) if tum_valor_vadeler else 0} {t['days']}")
            st.metric(t['max_maturity'], f"{max(tum_valor_vadeler) if tum_valor_vadeler else 0} {t['days']}")
            st.metric(t['maturity_std_dev'], f"{np.std(tum_valor_vadeler):.1f} {t['days']}" if tum_valor_vadeler else f"0 {t['days']}")
        
        # Histogram - Amount distribution
        st.markdown(f"#### {t['amount_dist_histogram']}")
        
        hist_col1, hist_col2 = st.columns(2)
        
        with hist_col1:
            fig_hist_fatura = px.histogram(
                df_faturalar_filtered,
                x='Tutar',
                nbins=10,
                title=t['invoice_amount_dist'],
                color_discrete_sequence=['#0d6efd']
            )
            fig_hist_fatura.update_layout(
                xaxis_title=f"{t['amount']} ({t['currency']})",
                yaxis_title=t['frequency'],
                height=350
            )
            st.plotly_chart(fig_hist_fatura, use_container_width=True)
        
        with hist_col2:
            fig_hist_vade = px.histogram(
                df_faturalar_filtered,
                x='Vade (Gün)',
                nbins=10,
                title=t['maturity_period_dist'],
                color_discrete_sequence=['#fd7e14']
            )
            fig_hist_vade.update_layout(
                xaxis_title=t['maturity_days'],
                yaxis_title=t['frequency'],
                height=350
            )
            st.plotly_chart(fig_hist_vade, use_container_width=True)
    
    st.divider()
    
    # General Maturity Analysis
    st.markdown(f"### {t['general_maturity_analysis']}")
    
    # Interactive data table
    with st.expander(t['detailed_calc_table'], expanded=False):
        st.dataframe(
            df_hesap.style.format({
                'Fatura Tutar': '${:,.2f}',
                'Çek Tutar': '${:,.2f}',
                'Vade (Gün) - Valör': '{:.0f}',
                'Vade (Gün) - Çek': '{:.0f}',
                'Vade Farkı': '{:.0f}'
            }),
            use_container_width=True,
            height=400
        )
    
    # Maturity distribution analysis - already calculated above, just display here
    col_analiz1, col_analiz2 = st.columns([1, 1])
    
    with col_analiz1:
        st.markdown(f"#### {t['invoice_maturity_dist']}")
        # df_fatura_vade_dagilim already calculated above, format and display
        dagilim_display = df_fatura_vade_dagilim.copy()
        amount_col = 'Tutar (₺)' if lang == 'TR' else 'Amount ($)'
        ratio_col = 'Oran (%)' if lang == 'TR' else 'Ratio (%)'
        dagilim_display[amount_col] = dagilim_display[amount_col].apply(lambda x: f"{t['currency']}{x:,.0f}")
        dagilim_display[ratio_col] = dagilim_display[ratio_col].apply(lambda x: f"{x:.1f}%")
        st.dataframe(dagilim_display, use_container_width=True, hide_index=True)
    
    with col_analiz2:
        # Min-Max maturities
        min_vade, max_vade, min_tutar, max_tutar = calculations.min_max_vade_hesapla(tum_fatura_tutarlar, tum_valor_vadeler)
        
        st.markdown(f"#### {t['maturity_stats']}")
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.metric(t['shortest_maturity'], f"{min_vade} {t['days']}", f"{t['currency']}{min_tutar:,.0f}")
            st.metric(t['average_maturity'], f"{genel_ort_valor:.1f} {t['days']}")
        with stat_col2:
            st.metric(t['longest_maturity'], f"{max_vade} {t['days']}", f"{t['currency']}{max_tutar:,.0f}")
            std_vade = np.std(tum_valor_vadeler) if tum_valor_vadeler else 0
            st.metric(t['standard_deviation'], f"{std_vade:.1f} {t['days']}")
    
    st.divider()
    
    # Check-based average maturities
    st.markdown(f"### {t['check_based_analysis']}")
    
    for idx, cek_no in enumerate(df_cekler_filtered['Çek No']):
        with st.expander(f"💳 {cek_no}", expanded=(idx == 0)):
            cek_data = df_hesap[df_hesap['Çek No'] == cek_no]
            
            # Weighted average for this check
            tutarlar = cek_data['Fatura Tutar'].tolist()
            vadeler_valor = cek_data['Vade (Gün) - Valör'].tolist()
            vadeler_cek = cek_data['Vade (Gün) - Çek'].tolist()
            
            ort_valor = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler_valor)
            ort_cek = calculations.agirlikli_ortalama_vade_hesapla(tutarlar, vadeler_cek)
            
            # Large metrics
            vade_col1, vade_col2 = st.columns(2)
            with vade_col1:
                st.markdown(f"<h4 style='text-align: center;'>{t['avg_value_mat']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center; color: #fd7e14;'>{ort_valor:.1f} {t['days']}</h1>", unsafe_allow_html=True)
            with vade_col2:
                st.markdown(f"<h4 style='text-align: center;'>{t['avg_check_mat']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center; color: #6f42c1;'>{ort_cek:.1f} {t['days']}</h1>", unsafe_allow_html=True)
            
            # Detailed statistics
            detay_col1, detay_col2 = st.columns(2)
            with detay_col1:
                cek_vadeler_valor = cek_data['Vade (Gün) - Valör'].tolist()
                min_v_valor = min(cek_vadeler_valor) if cek_vadeler_valor else 0
                max_v_valor = max(cek_vadeler_valor) if cek_vadeler_valor else 0
                std_v_valor = np.std(cek_vadeler_valor) if len(cek_vadeler_valor) > 1 else 0
                
                st.markdown(t['value_mat_stats'])
                st.write(f"• {t['min']}: {min_v_valor} {t['days']}")
                st.write(f"• {t['max']}: {max_v_valor} {t['days']}")
                st.write(f"• {t['std']}: {std_v_valor:.1f} {t['days']}")
            
            with detay_col2:
                cek_vadeler_cek = cek_data['Vade (Gün) - Çek'].tolist()
                min_v_cek = min(cek_vadeler_cek) if cek_vadeler_cek else 0
                max_v_cek = max(cek_vadeler_cek) if cek_vadeler_cek else 0
                std_v_cek = np.std(cek_vadeler_cek) if len(cek_vadeler_cek) > 1 else 0
                
                st.markdown(t['check_mat_stats'])
                st.write(f"• {t['min']}: {min_v_cek} {t['days']}")
                st.write(f"• {t['max']}: {max_v_cek} {t['days']}")
                st.write(f"• {t['std']}: {std_v_cek:.1f} {t['days']}")
            
            st.markdown("---")
            st.markdown(t['related_invoices'])
            for _, row in cek_data.iterrows():
                st.markdown(f"• **{row['Fatura No']}**: {t['currency']}{row['Fatura Tutar']:,.0f} → {t['value_maturity']}: **{row['Vade (Gün) - Valör']} {t['days']}**, {t['check_maturity']}: **{row['Vade (Gün) - Çek']} {t['days']}**")

elif st.session_state.faturalar and not st.session_state.cekler:
    st.warning(t['no_checks_warning'])
elif not st.session_state.faturalar and st.session_state.cekler:
    st.warning(t['no_invoices_warning'])
else:
    st.info(t['add_data_info'])

# Footer
st.divider()
st.markdown(f"""
<div style='text-align: center; color: gray; padding: 20px;'>
<small>{t['footer']}</small>
</div>
""", unsafe_allow_html=True)
