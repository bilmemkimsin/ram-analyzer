# RAM Analyzer

RAM Analyzer, süreçlerin RAM kullanımını listeleyip seçilen bir süreç için bellek okuma/yazma denemeleri yapabilen basit bir masaüstü arayüzü sunar. Uygulama **/proc/<pid>/mem** üzerinden erişim sağladığı için yönetici (root) yetkisi gerektirir.

> **Uyarı:** Belleğe müdahale etmek sistem kararlılığını bozabilir. Oyunlar ve uygulamalar açısından EULA / kullanım koşullarını ihlal edebilir. Sadece yetkili ve güvenli ortamlarda kullanın.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
sudo .venv/bin/python src/main.py
```

## Özellikler

- Süreç listesini RAM kullanımına göre sıralama
- Süreç arama ve filtreleme
- Seçili süreç için bellek adresinden okuma/yazma (int/float/bytes)

## Notlar

- Okuma/yazma işlemleri hedef sürecin belleğinde izinlere bağlıdır.
- Bellek adreslerini bulmak için ek analiz gereklidir (memory scan, pointer map vb.).
- Uygulama bir başlangıç prototipidir; daha gelişmiş tarama/izleme için ek modüller eklenebilir.
