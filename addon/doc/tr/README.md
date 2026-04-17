# komutYardımcısı

Karmaşık tuş kombinasyonlarına basmakta zorlanan kişiler için komutları çalıştırmanın alternatif bir yöntemini sağlar.

### Kullanım şekli

Öncelikle yardımcıyı çağırmak için bir Kısayol tanımlamak gerekir. NVDA tercihler > Girdi Hareketleri iletişim kutusunda bir klavye hareketi atanabilir. Ayrıca eklenti ayarlarında kontrol tuşu da yapılandırılabilir (aşağıya bakın).

Yardımcı çağrıldığında aşağıdaki seçeneklere sahip bir klavye komut katmanı etkinleşir:

* Sol ve sağ ok tuşları bir kategori seçer.
* A’dan Z’ye herhangi bir harf, İlgili harfle başlayan kategoriye gider.
* Yukarı ve aşağı ok tuşları seçilen kategoride bir komut seçer.
* Boşluk tuşu sesli aramayı başlatır.
* Enter komutu çalıştırır.
* Shift+Enter komutu, ilgili tuş kombinasyonu hızlıca iki kez basılmış gibi çalıştırır.
* Control+Enter komutu, ilgili tuş kombinasyonu üç kez basılmış gibi çalıştırır.
* F1 seçili komuta karşılık gelen hareketi seslendirir.
* Escape komut katmanından çıkar ve klavyenin normal işlevini geri yükler.

### Yapılandırma

Komut yardımcısını etkinleştiren tuş kombinasyonu NVDA tercihler > Girdi Hareketleri iletişim kutusundan değiştirilebilir.

Bazı diğer tuşlar NVDA tercihler > Ayarlar > Komut Yardımcısı alt dalından özelleştirilebilir.

* Kontrol tuşu yardımcıyı başlatır.
* Klavye Komut katmanını kapatma.
* Bir komuta atanan hareketi seslendirme tuşu.
* Klavye komut katmanında sayısal tuş takınını kullan.

#### Yardımcıyı çağırmak için kontrol tuşunun kullanımı

Bu seçenek etkinleştirildiğinde kontrol tuşuna art arda beş kez basarak yardımcı çağrılır. Bu, aynı anda birden fazla tuşa basmakta zorlanan kişiler için faydalıdır. Ancak bazen kontrol tuşunun başka amaçlarla kullanımı sırasında (örneğin kopyala ve yapıştır için control+C ve control+V) yardımcı istemeden etkinleşebilir. Bunu önlemek için klavye tekrar hızını düşürmek gerekir. Bu, Windows Denetim Masası’ndan yapılır. Eklenti Ayarlar iletişim kutusunda, basıldığında doğrudan oraya götüren bir düğme vardır. Ayrıca Windows+R tuşlarına basıp Çalıştır kutusuna control.exe keyboard yazarak da açılabilir. “Tekrar hızı” kaydırıcısında mümkün olduğunca düşük bir değer ayarlanmalıdır. Sıfıra ayarlanırsa sorun yaşanmaz ancak kontrol tuşunu basılı tutarak yardımcıyı etkinleştirme özelliği çalışmaz; bu da hızlı tekrar basış yapmakta zorlanan ve bu yöntemi tercih eden bazı hareket kısıtlılığı olan kullanıcılar için dezavantaj olabilir. Evrensel bir ayar yoktur; her kullanıcı kendi ihtiyaçlarına veya tercihlerine en uygun olanı bulmalıdır.

#### Sayısal tuş takımı

Bu seçenek etkinleştirildiğinde yardımcı sayısal tuş takımı ile kullanılabilir.

* 4 ve 6 kategori seçer.
* 2 ve 8 seçilen kategoride bir komut seçer.
* 5 seçili komuta karşılık gelen hareketi seslendirir.
* Enter komutu çalıştırır.
* Artı (+) tuşu komutu, ilgili tuş kombinasyonu hızlıca iki kez basılmış gibi çalıştırır.
* Eksi (-) tuşu komutu, ilgili tuş kombinasyonu üç kez basılmış gibi çalıştırır.
* Delete komut katmanından çıkar ve klavyenin normal işlevini geri yükler.

#### Ses ile filtreleme

Sanal menüde boşluk tuşuna basın ve mikrofona konuşun. Menü yalnızca söylenen kelimelerle eşleşen komutları gösterecektir. Sonuç tatmin edici değilse, yeni bir arama yapmak için tekrar boşluk tuşuna basın veya tam menüye dönmek için escape tuşuna basın.

Çalışması için internet bağlantısı gereklidir.

Uyumluluk notu: Eklenti, NVDA’nın önceki sürümleriyle çalışacak şekilde hazırlanmıştır. Test edilen en eski sürüm 2018.1’dir ancak daha eski sürümlerle de çalışması beklenir. Bununla birlikte bu sürümlerde ortaya çıkabilecek özel sorunlar için gelecekte destek sağlanmayacaktır.
