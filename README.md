# Universite_web_sayfalari
Üniversitelerin ana web sayfasını indirip boyutunu hesaplıyor

# Özellikler:
- `urls.txt` içinden URL'leri okur (başında http yoksa https ekler)
- Paralel olarak her URL'yi açar, lazy-load + video tetikler
- `selenium-wire` ile tüm HTTP(S) isteklerini yakalar
- Tek CSV'ye yazar: domain, istek sayısı, toplam boyut (MB)
- Ekrana her tamamlanan iş için progress (i/total) formatında satır yazar
- Tüm işlemin toplam süresini özet olarak gösterir
