# Adım 1 çalışma planı (günde 1 saat, yaklaşık 2 hafta)

Kodun çalışan bir ilk sürümü hazır. Amaç kodu kopyalamak değil, her satırı
mülakatta anlatabilecek hale gelmek. Her günün sonunda küçük bir commit atın.

## Hafta 1: Anlamak ve yayınlamak

**Gün 1: Kurulum ve GitHub**
- GitHub'da `battery-soc-ekf` adında herkese açık bir repo açın, bu klasörü yükleyin.
- README'deki "Run" komutlarını çalıştırın, grafiği ve 8 geçen testi görün.

**Gün 2: Batarya modeli (`model.py`)**
- R0, R1, C1 ve OCV'nin fiziksel anlamını kendi cümlelerinizle not alın.
- Deneme: `run_demo.py` içinde R0'ı 2 katına çıkarın. Gerilim grafiğinde ne değişti?

**Gün 3: Coulomb sayımı**
- Neden yanlış başlangıç değerini hiç düzeltemiyor? Akım ofseti (bias) zamanla ne yapıyor?
- Deneme: `SOC0_GUESS = 0.95` yapın, sadece bias'ın etkisini görün.

**Gün 4: Kalman filtresi teorisi**
- Predict ve correct adımlarını kağıda yazın. P, Q, R ve K ne anlama geliyor?
- Kaynak önerisi: Gregory Plett, "Battery Management Systems Vol. 2" (ders videoları da var).

**Gün 5: EKF kodu (`estimators.py`)**
- `H = [dOCV/dsoc, -1]` neden böyle? "Extended" kelimesi nereden geliyor?
- Kodu satır satır yorumlayın, kendi yorumlarınızla commit edin.

## Hafta 2: Kendi katkınız

**Gün 6: Q ve R ayarı**
- R'yi 100 kat büyütün ve küçültün. Yakınsama hızı ve gürültü nasıl değişiyor?
- Sonuçları README'ye küçük bir tablo olarak ekleyin.

**Gün 7: Parametre hatası (önemli)**
- Gerçek hücre `CellParams(capacity_ah=2.7, r0=0.04)`, filtre `CellParams()` olsun.
- EKF hâlâ iyi mi? Bu, gerçek donanımda karşılaşacağınız durumun ta kendisi.

**Gün 8: Yeni test yazın**
- Gün 7'deki senaryo için bir pytest testi ekleyin (ör. hata %5'in altında kalmalı).
- Test mühendisliği deneyiminizi gösterdiğiniz yer burası.

**Gün 9: Açık veri seti**
- Gerçek ölçülmüş 18650 verisi bulun (ör. Mendeley Data'da LG 18650HG2 veya
  Panasonic 18650PF veri setleri) ve bir yükleme fonksiyonu yazın.

**Gün 10: Toparlama**
- README'yi kendi sonuçlarınızla güncelleyin.
- LinkedIn için 3-4 cümlelik kısa bir paylaşım taslağı yazın.

## Mülakatta anlatabilmeniz gerekenler
1. Coulomb sayımı neden tek başına yetmez?
2. EKF gerilim ölçümünü SoC'u düzeltmek için nasıl kullanır?
3. OCV eğrisinin düz olduğu bölgede (ör. %40-60) EKF neden daha zor çalışır?
4. Q ve R'yi nasıl seçtiniz?
