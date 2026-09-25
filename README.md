# talep-tahmin-zaman-serisi

Hareketli ortalama, üstel düzeltme, Holt ve Holt-Winters yöntemleri ile aylık talep tahmini - yöntem karşılaştırması ve hata metrikleri (MAD/MSE/RMSE/MAPE)

## Açıklama

Bu proje, üretim ve tedarik zinciri planlamasında sıkça kullanılan klasik zaman serisi
talep tahmin yöntemlerini **sıfırdan (yalnızca NumPy ile)** uygular ve karşılaştırır.
Trend ve mevsimsellik içeren sentetik bir aylık talep verisi üzerinde dört farklı
yöntemin performansı ölçülür, en iyi yöntemle gelecek dönem talebi tahmin edilir.

## Uygulanan Yöntemler

| Yöntem | Trend | Mevsimsellik | Kullanım Alanı |
|---|:---:|:---:|---|
| Hareketli Ortalama | ✗ | ✗ | Kısa vadeli, durağan talep |
| Basit Üstel Düzeltme (SES) | ✗ | ✗ | Durağan talep, az veri |
| Holt Doğrusal Trend (DES) | ✓ | ✗ | Artan/azalan trendli talep |
| Holt-Winters (TES, toplamsal) | ✓ | ✓ | Trend + mevsimsel talep |

## Hata Metrikleri

Her yöntem için aşağıdaki metrikler hesaplanır ve yöntemler RMSE'ye göre sıralanır:

- **MAD** — Ortalama Mutlak Sapma
- **MSE** — Ortalama Kare Hata
- **RMSE** — Kök Ortalama Kare Hata
- **MAPE (%)** — Ortalama Mutlak Yüzde Hata

## Kurulum

```bash
git clone https://github.com/burakefearslanturk/talep-tahmin-zaman-serisi.git
cd talep-tahmin-zaman-serisi
pip install -r requirements.txt
```

## Kullanım

```bash
# 1) Trend + mevsimsellik içeren örnek aylık talep verisini üret
python veri_uretici.py

# 2) Yöntemleri karşılaştır, en iyisini seç ve 6 aylık ileri tahmin üret
python talep_tahmin.py
```

## Örnek Çıktı

```
YÖNTEM KARŞILAŞTIRMA TABLOSU (RMSE'ye göre sıralı)
                                MAD       MSE    RMSE  MAPE (%)
Holt-Winters Mevsimsel        27.58   1129.01   33.60      4.22
Hareketli Ortalama (k=3)      78.70   8048.97   89.72     12.19
Basit Üstel Düzeltme (α=0.3)  81.97   8502.29   92.21     12.72
Holt Doğrusal Trend           95.73  11690.87  108.12     15.25

EN İYİ YÖNTEM: Holt-Winters Mevsimsel

Sonraki 6 aylık talep tahmini:
  2026-01: 657 birim
  2026-02: 665 birim
  2026-03: 744 birim
  ...
```

`gorseller/` klasörüne iki grafik kaydedilir:

- **yontem_karsilastirma.png** — Gerçek talep vs. dört yöntemin tahminleri
- **gelecek_tahmin.png** — En iyi yöntemle 6 aylık ileri tahmin

## Klasör Yapısı

```
talep-tahmin-zaman-serisi/
├── veri_uretici.py       # Sentetik aylık talep verisi üretici
├── talep_tahmin.py       # Tahmin yöntemleri, hata metrikleri, karşılaştırma
├── veri/
│   └── aylik_talep.csv   # Üretilen örnek veri seti
├── gorseller/
│   ├── yontem_karsilastirma.png
│   └── gelecek_tahmin.png
├── requirements.txt
└── README.md
```

## Kendi Verinizle Kullanım

Kendi talep verinizi kullanmak için `veri/aylik_talep.csv` dosyasını
`Tarih, Talep` sütunlarını içerecek şekilde kendi verinizle değiştirmeniz yeterlidir.
Mevsimsel veri en az 24 gözlem (2 tam yıl) içermelidir.

## Lisans

MIT
