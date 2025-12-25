# 📊 Ortalama Vade Hesaplama Programı

Müşterilerinizin faturalarına göre **ağırlıklı ortalama vade** hesaplayıp, uygun çek vadesi önerileri sunan profesyonel bir web uygulaması.

## 🎯 Özellikler

- ✅ Çoklu fatura girişi
- ✅ Ağırlıklı ortalama vade hesaplama
- ✅ Otomatik çek vadesi önerisi
- ✅ Detaylı hesaplama açıklamaları
- ✅ Excel'e aktarma özelliği
- ✅ Kullanıcı dostu arayüz
- ✅ Valör tarihi bazlı hesaplama

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adımlar

1. **Projeyi indirin veya klonlayın**

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı başlatın:**
```bash
streamlit run app.py
```

4. **Tarayıcınızda açın:**
Uygulama otomatik olarak varsayılan tarayıcınızda açılacaktır. 
Açılmazsa: `http://localhost:8501`

## 📖 Kullanım

### 1. Valör Tarihi Ayarlama
Sol taraftaki yan panelden valör tarihini seçin. Bu tarih, çeklerin tahsil edileceği başlangıç referans tarihidir.

### 2. Fatura Ekleme
- **Fatura No:** Fatura numarasını girin
- **Fatura Tutarı:** Fatura tutarını TL cinsinden girin
- **Vade (Gün):** Fatura vadesini gün olarak girin
- **"➕ Fatura Ekle"** butonuna tıklayın

### 3. Hesaplama Sonuçları
Sağ tarafta aşağıdaki bilgileri görebilirsiniz:
- **Toplam Fatura Tutarı:** Eklenen tüm faturaların toplamı
- **Ağırlıklı Ortalama Vade:** Hesaplanan ortalama vade süresi
- **Önerilen Çek Vadesi:** Müşteriden alınması gereken çek tarihi

### 4. Excel'e Aktarma
"📥 Excel'e Aktar" butonu ile tüm fatura bilgilerini, hesaplama detaylarını ve özet bilgileri Excel formatında indirebilirsiniz.

## 🧮 Hesaplama Yöntemi

Ağırlıklı ortalama vade şu formül ile hesaplanır:

```
Ortalama Vade = Σ(Fatura Tutarı × Vade Günü) / Σ(Fatura Tutarı)
```

### Örnek:
- Fatura 1: 10.000 TL - 30 gün
- Fatura 2: 20.000 TL - 60 gün
- Fatura 3: 15.000 TL - 45 gün

```
Ortalama Vade = (10.000×30 + 20.000×60 + 15.000×45) / (10.000 + 20.000 + 15.000)
               = (300.000 + 1.200.000 + 675.000) / 45.000
               = 2.175.000 / 45.000
               = 48,3 gün
```

## 📁 Dosya Yapısı

```
ORTALAMA VADE WEB PROGRAMI BY GOKSEL/
│
├── app.py                 # Ana Streamlit uygulaması
├── calculations.py        # Hesaplama fonksiyonları
├── requirements.txt       # Python paket bağımlılıkları
└── README.md             # Bu dosya
```

## 🛠️ Teknik Detaylar

- **Framework:** Streamlit (Web UI)
- **Veri İşleme:** Pandas
- **Excel Export:** OpenPyXL
- **Dil:** Python 3.x

## 💡 İpuçları

1. **Toplu Fatura Girişi:** Birden fazla fatura ekleyerek daha doğru ortalama vade hesaplayabilirsiniz.

2. **Valör Tarihi:** Genellikle bugünün tarihi veya çek tahsil edilmek istenen başlangıç tarihi seçilir.

3. **Excel Raporu:** Müşterilerinize sunmak için detaylı Excel raporu oluşturabilirsiniz.

4. **Temizleme:** "🗑️ Tüm Faturaları Temizle" butonu ile hızlıca yeni hesaplama başlatabilirsiniz.

## 🎓 Kullanım Senaryoları

### Senaryo 1: Tedarikçi Ödemeleri
Tedarikçinizden aldığınız 3 fatura var:
- 15.000 TL - 30 gün
- 25.000 TL - 45 gün  
- 10.000 TL - 60 gün

Program size 43,5 günlük ortalama vade hesaplayacak ve uygun çek tarihini önerecektir.

### Senaryo 2: Müşteri Tahsilatları
Müşterinize kestirdiğiniz faturalar için uygun çek vadesi belirleme:
- Müşteri faturalarını girin
- Sistem ortalama vadeyi hesaplar
- Müşteriden bu vadeye uygun çek talep edersiniz

## 📞 Destek

Sorularınız için:
- GitHub Issues bölümünü kullanabilirsiniz
- E-posta: [E-posta adresiniz]

## 📄 Lisans

Bu proje Göksel tarafından geliştirilmiştir.

## 🔄 Güncellemeler

### v1.0.0 (26 Aralık 2025)
- İlk sürüm yayınlandı
- Temel hesaplama özellikleri
- Excel export özelliği
- Kullanıcı dostu arayüz

---

**© 2025 Ortalama Vade Hesaplama Programı | By Goksel**
