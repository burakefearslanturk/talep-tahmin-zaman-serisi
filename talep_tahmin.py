"""
talep_tahmin.py
-----------------
Klasik zaman serisi talep tahmin yöntemlerinin sıfırdan (numpy ile) uygulanması:

    1) Hareketli Ortalama (Moving Average)
    2) Basit Üstel Düzeltme (Simple Exponential Smoothing)
    3) Holt'un Doğrusal Trend Yöntemi (Double Exponential Smoothing)
    4) Holt-Winters Mevsimsel Yöntem (Triple Exponential Smoothing)

Her yöntem için MAD, MSE, RMSE ve MAPE hata metrikleri hesaplanır, yöntemler
karşılaştırılır ve sonuçlar görselleştirilir.

Kullanım:
    python talep_tahmin.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


# ---------------------------------------------------------------------------
# 1) HAREKETLİ ORTALAMA
# ---------------------------------------------------------------------------
def hareketli_ortalama(veri, pencere=3):
    """
    Basit hareketli ortalama ile tek adım ileri tahmin üretir.
    İlk (pencere) kadar gözlem için tahmin üretilemez (NaN döner).
    """
    veri = np.asarray(veri, dtype=float)
    tahmin = np.full(len(veri), np.nan)
    for t in range(pencere, len(veri)):
        tahmin[t] = veri[t - pencere:t].mean()
    return tahmin


# ---------------------------------------------------------------------------
# 2) BASİT ÜSTEL DÜZELTME (SES)
# ---------------------------------------------------------------------------
def basit_ustel_duzeltme(veri, alpha=0.3):
    """
    Basit üstel düzeltme (trend/mevsimsellik olmayan seriler için).
    S_t = alpha * X_t + (1 - alpha) * S_(t-1)
    """
    veri = np.asarray(veri, dtype=float)
    n = len(veri)
    duzeltilmis = np.zeros(n)
    duzeltilmis[0] = veri[0]

    for t in range(1, n):
        duzeltilmis[t] = alpha * veri[t - 1] + (1 - alpha) * duzeltilmis[t - 1]

    return duzeltilmis


# ---------------------------------------------------------------------------
# 3) HOLT'UN DOĞRUSAL TREND YÖNTEMİ (DES)
# ---------------------------------------------------------------------------
def holt_dogrusal_trend(veri, alpha=0.3, beta=0.2, ileri_adim=0):
    """
    Trend içeren seriler için Holt'un çift üstel düzeltme yöntemi.

    Seviye:  L_t = alpha * X_t + (1 - alpha) * (L_(t-1) + T_(t-1))
    Trend :  T_t = beta  * (L_t - L_(t-1)) + (1 - beta) * T_(t-1)
    Tahmin:  F_(t+1) = L_t + T_t
    """
    veri = np.asarray(veri, dtype=float)
    n = len(veri)

    seviye = np.zeros(n)
    trend = np.zeros(n)
    tahmin = np.full(n, np.nan)

    seviye[0] = veri[0]
    trend[0] = veri[1] - veri[0] if n > 1 else 0.0

    for t in range(1, n):
        seviye[t] = alpha * veri[t] + (1 - alpha) * (seviye[t - 1] + trend[t - 1])
        trend[t] = beta * (seviye[t] - seviye[t - 1]) + (1 - beta) * trend[t - 1]
        tahmin[t] = seviye[t - 1] + trend[t - 1]

    gelecek_tahminler = None
    if ileri_adim > 0:
        gelecek_tahminler = [seviye[-1] + (h + 1) * trend[-1] for h in range(ileri_adim)]

    return tahmin, gelecek_tahminler


# ---------------------------------------------------------------------------
# 4) HOLT-WINTERS MEVSİMSEL YÖNTEM (TES - toplamsal model)
# ---------------------------------------------------------------------------
def holt_winters_mevsimsel(veri, alpha=0.3, beta=0.1, gamma=0.2,
                            mevsim_uzunlugu=12, ileri_adim=0):
    """
    Toplamsal (additive) Holt-Winters yöntemi: seviye + trend + mevsimsellik.

    Seviye     : L_t = alpha*(X_t - S_(t-m)) + (1-alpha)*(L_(t-1)+T_(t-1))
    Trend      : T_t = beta*(L_t - L_(t-1)) + (1-beta)*T_(t-1)
    Mevsimsel  : S_t = gamma*(X_t - L_t) + (1-gamma)*S_(t-m)
    Tahmin     : F_(t+1) = L_t + T_t + S_(t+1-m)
    """
    veri = np.asarray(veri, dtype=float)
    n = len(veri)
    m = mevsim_uzunlugu

    if n < 2 * m:
        raise ValueError("Holt-Winters için en az 2 mevsim döngüsü kadar veri gereklidir.")

    seviye = np.zeros(n)
    trend = np.zeros(n)
    mevsim = np.zeros(n)
    tahmin = np.full(n, np.nan)

    # Başlangıç değerleri: ilk mevsim döngüsünün ortalaması ve mevsim ortalamadan sapması
    ilk_ortalama = veri[:m].mean()
    seviye[m - 1] = ilk_ortalama
    trend[m - 1] = (veri[m:2 * m].mean() - veri[:m].mean()) / m
    for i in range(m):
        mevsim[i] = veri[i] - ilk_ortalama

    for t in range(m, n):
        mevsim_idx = t - m
        tahmin[t] = seviye[t - 1] + trend[t - 1] + mevsim[mevsim_idx]

        seviye[t] = alpha * (veri[t] - mevsim[mevsim_idx]) + (1 - alpha) * (seviye[t - 1] + trend[t - 1])
        trend[t] = beta * (seviye[t] - seviye[t - 1]) + (1 - beta) * trend[t - 1]
        mevsim[t] = gamma * (veri[t] - seviye[t]) + (1 - gamma) * mevsim[mevsim_idx]

    gelecek_tahminler = None
    if ileri_adim > 0:
        gelecek_tahminler = []
        for h in range(1, ileri_adim + 1):
            mevsim_idx = n - m + ((h - 1) % m)
            gelecek_tahminler.append(seviye[-1] + h * trend[-1] + mevsim[mevsim_idx])

    return tahmin, gelecek_tahminler


# ---------------------------------------------------------------------------
# HATA METRİKLERİ
# ---------------------------------------------------------------------------
def hata_metrikleri(gercek, tahmin):
    """
    NaN olan gözlemleri dışlayarak MAD, MSE, RMSE ve MAPE hesaplar.
    """
    gercek = np.asarray(gercek, dtype=float)
    tahmin = np.asarray(tahmin, dtype=float)

    gecerli = ~np.isnan(tahmin)
    gercek_g = gercek[gecerli]
    tahmin_g = tahmin[gecerli]

    hata = gercek_g - tahmin_g
    mad = np.mean(np.abs(hata))
    mse = np.mean(hata ** 2)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs(hata / gercek_g)) * 100

    return {"MAD": mad, "MSE": mse, "RMSE": rmse, "MAPE (%)": mape}


# ---------------------------------------------------------------------------
# KARŞILAŞTIRMA VE GÖRSELLEŞTİRME
# ---------------------------------------------------------------------------
def yontemleri_karsilastir(df, mevsim_uzunlugu=12, ileri_adim=6):
    talep = df["Talep"].values

    sonuclar = {}

    ho_tahmin = hareketli_ortalama(talep, pencere=3)
    sonuclar["Hareketli Ortalama (k=3)"] = ho_tahmin

    ses_tahmin = basit_ustel_duzeltme(talep, alpha=0.3)
    sonuclar["Basit Üstel Düzeltme (α=0.3)"] = ses_tahmin

    holt_tahmin, holt_gelecek = holt_dogrusal_trend(talep, alpha=0.3, beta=0.2, ileri_adim=ileri_adim)
    sonuclar["Holt Doğrusal Trend"] = holt_tahmin

    hw_tahmin, hw_gelecek = holt_winters_mevsimsel(
        talep, alpha=0.3, beta=0.1, gamma=0.2,
        mevsim_uzunlugu=mevsim_uzunlugu, ileri_adim=ileri_adim
    )
    sonuclar["Holt-Winters Mevsimsel"] = hw_tahmin

    # --- Hata metrikleri tablosu ---
    metrik_tablosu = pd.DataFrame({
        yontem: hata_metrikleri(talep, tahmin) for yontem, tahmin in sonuclar.items()
    }).T
    metrik_tablosu = metrik_tablosu.sort_values("RMSE")

    en_iyi_yontem = metrik_tablosu.index[0]

    # --- Grafik: gerçek vs tahminler ---
    os.makedirs("gorseller", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(df["Tarih"], talep, label="Gerçek Talep", color="black", linewidth=2)
    for yontem, tahmin in sonuclar.items():
        plt.plot(df["Tarih"], tahmin, "--", label=yontem, alpha=0.8)
    plt.title("Talep Tahmin Yöntemlerinin Karşılaştırılması")
    plt.xlabel("Tarih")
    plt.ylabel("Talep")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join("gorseller", "yontem_karsilastirma.png"), dpi=150)
    plt.close()

    # --- Grafik: en iyi yöntemle gelecek tahmini ---
    gelecek_tarihler = pd.date_range(
        start=df["Tarih"].iloc[-1] + pd.DateOffset(months=1), periods=ileri_adim, freq="MS"
    )
    gelecek_deger = hw_gelecek if en_iyi_yontem == "Holt-Winters Mevsimsel" else holt_gelecek

    plt.figure(figsize=(12, 6))
    plt.plot(df["Tarih"], talep, label="Geçmiş Talep", color="black")
    if gelecek_deger is not None:
        plt.plot(gelecek_tarihler, gelecek_deger, "o--", color="tab:red",
                  label=f"Gelecek Tahmin ({en_iyi_yontem})")
    plt.title(f"{ileri_adim} Aylık Talep Tahmini — En İyi Yöntem: {en_iyi_yontem}")
    plt.xlabel("Tarih")
    plt.ylabel("Talep")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join("gorseller", "gelecek_tahmin.png"), dpi=150)
    plt.close()

    return metrik_tablosu, en_iyi_yontem, gelecek_tarihler, gelecek_deger


# ---------------------------------------------------------------------------
# ANA PROGRAM
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    veri_yolu = os.path.join("veri", "aylik_talep.csv")
    if not os.path.exists(veri_yolu):
        raise FileNotFoundError(
            "Önce 'python veri_uretici.py' komutunu çalıştırarak örnek veri seti oluşturun."
        )

    df = pd.read_csv(veri_yolu, parse_dates=["Tarih"])

    metrik_tablosu, en_iyi_yontem, gelecek_tarihler, gelecek_deger = yontemleri_karsilastir(
        df, mevsim_uzunlugu=12, ileri_adim=6
    )

    print("=" * 60)
    print("YÖNTEM KARŞILAŞTIRMA TABLOSU (RMSE'ye göre sıralı)")
    print("=" * 60)
    print(metrik_tablosu.round(2).to_string())

    print("\n" + "=" * 60)
    print(f"EN İYİ YÖNTEM: {en_iyi_yontem}")
    print("=" * 60)
    print("\nSonraki 6 aylık talep tahmini:")
    for tarih, deger in zip(gelecek_tarihler, gelecek_deger):
        print(f"  {tarih.strftime('%Y-%m')}: {deger:.0f} birim")

    print("\nGrafikler 'gorseller/' klasörüne kaydedildi:")
    print("  - yontem_karsilastirma.png")
    print("  - gelecek_tahmin.png")
