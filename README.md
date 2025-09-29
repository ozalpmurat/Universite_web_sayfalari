# Universite_web_sayfalari
Üniversitelerin ana web sayfasını indirip boyutunu hesaplıyor

# Özellikler
- `urls.txt` içinden URL'leri okur (başında http yoksa https ekler)
- Paralel olarak her URL'yi açar, lazy-load + video tetikler
- `selenium-wire` ile tüm HTTP(S) isteklerini yakalar
- Tek CSV'ye yazar: domain, istek sayısı, toplam boyut (MB)
- Ekrana her tamamlanan iş için progress (i/total) formatında satır yazar
- Tüm işlemin toplam süresini özet olarak gösterir

# Ayarlar
Kodların girişinde ayarlar yapılabilir. Aşağıda varsayılan ayarlar görülmektedir:
```python
# Ayarlar
INPUT_FILE = "urls.txt"
OUTPUT_FILE = "site_summary.csv"
MAX_WORKERS = 10         # Aynı anda kaç site açılsın?
SCROLL_PAUSE = 2         # her scroll sonrası bekleme (saniye)
MAX_SCROLLS = 60         # maksimum scroll denemesi
VIDEO_PLAY_WAIT = 5      # video.play() sonrası bekleme (saniye)
HEADLESS = True          # False yaparsan tarayıcı görünür açılır
```
# Çıktılar
- site_summary.csv dosyasına her URL için; istek sayısı ve sayfa boyutu (MB cinsinden yazar)
- Çalışma sırasında ekranda canlı çıktı verir. Kaçıncı URL olduğunu yazar.
- Çalışma sonunda toplam süreyi verir.

**Örnek çıktı:**
```
(173/177) ufuk.edu.tr: requests=102, size=22.767 MB
(174/177) toros.edu.tr: requests=114, size=38.346 MB
(175/177) uskudar.edu.tr: requests=161, size=5.658 MB
(176/177) thk.edu.tr: requests=221, size=259.973 MB
(177/177) yiu.edu.tr: requests=113, size=46.875 MB

✅ Tamamlandı. Çıktı: site_summary.csv
Toplam işlem süresi: 10 dakika 19 saniye
```
