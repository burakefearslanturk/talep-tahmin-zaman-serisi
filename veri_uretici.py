"""
veri_uretici.py
----------------
Talep tahmin modellerini test etmek için trend + mevsimsellik + rastgele
gürültü içeren sentetik bir aylık talep serisi üretir ve veri/aylik_talep.csv
dosyasına kaydeder.

Kullanım:
    python veri_uretici.py
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)


def aylik_talep_uret(baslangic_yil=2022, yil_sayisi=4, temel_talep=500,
                      trend_egimi=6.0, mevsim_genligi=120, gurultu_std=25):
    """
    Trend + mevsimsel bileşen + gürültü içeren aylık talep verisi üretir.

    Parametreler
    ------------
    baslangic_yil : int
        Verinin başlayacağı yıl.
    yil_sayisi : int
        Kaç yıllık aylık veri üretileceği.
    temel_talep : float
        Serinin başlangıç seviyesi.
    trend_egimi : float
        Ay başına ortalama artış miktarı.
    mevsim_genligi : float
        Mevsimsel dalgalanmanın genliği (yaz/kış farkı gibi).
    gurultu_std : float
        Rastgele gürültünün standart sapması.

    Dönüş
    -----
    pandas.DataFrame  (Tarih, Talep)
    """
    ay_sayisi = yil_sayisi * 12
    tarihler = pd.date_range(start=f"{baslangic_yil}-01-01", periods=ay_sayisi, freq="MS")

    t = np.arange(ay_sayisi)
    trend = temel_talep + trend_egimi * t

    # 12 aylık mevsimsel desen (örn. yaz aylarında talep artışı)
    mevsim_deseni = np.array([-0.9, -0.7, -0.2, 0.3, 0.7, 1.0,
                               1.0, 0.8, 0.3, -0.2, -0.6, -0.8])
    mevsimsellik = mevsim_genligi * np.tile(mevsim_deseni, yil_sayisi)

    gurultu = np.random.normal(0, gurultu_std, ay_sayisi)

    talep = trend + mevsimsellik + gurultu
    talep = np.round(np.maximum(talep, 0)).astype(int)

    return pd.DataFrame({"Tarih": tarihler, "Talep": talep})


if __name__ == "__main__":
    df = aylik_talep_uret()

    os.makedirs("veri", exist_ok=True)
    cikti_yolu = os.path.join("veri", "aylik_talep.csv")
    df.to_csv(cikti_yolu, index=False)

    print(f"Örnek veri seti oluşturuldu: {cikti_yolu}")
    print(f"Toplam {len(df)} aylık gözlem üretildi.")
    print(df.head(12).to_string(index=False))
