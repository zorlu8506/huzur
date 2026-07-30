"""
Sekine — içerik havuzunu ve taksonomi matrisini JSON'a döker.
Prototipteki veriyi buraya taşıdık; canlıda:
  - AYET metinleri Quran.com gibi doğrulanmış bir API'den senkronlanır
  - RISALE için 'orijinal' + 'sade/şerh' alanları uzman onayıyla doldurulur
  - matris (hangi alt-duyguya hangi içerik) uzman tarafından denetlenir
Çalıştır:  python build_data.py
"""
import json, pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

# ---------- KUR'AN havuzu (layer: ruh) ----------
AYET = {
 "rad28":{"ar":"أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ","meal":"Bilesiniz ki kalpler ancak Allah'ı anmakla huzura kavuşur.","ref":"Ra'd, 28"},
 "talak3":{"ar":"وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ","meal":"Kim Allah'a tevekkül ederse, O ona yeter.","ref":"Talâk, 3"},
 "talak7":{"ar":"سَيَجْعَلُ اللَّهُ بَعْدَ عُسْرٍ يُسْرًا","meal":"Allah, bir güçlükten sonra bir kolaylık yaratacaktır.","ref":"Talâk, 7"},
 "ali173":{"ar":"حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ","meal":"Allah bize yeter, O ne güzel vekildir.","ref":"Âl-i İmran, 173"},
 "bakara286":{"ar":"لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا","meal":"Allah kimseye gücünün üstünde bir yük yüklemez.","ref":"Bakara, 286"},
 "bakara153":{"ar":"إِنَّ اللَّهَ مَعَ الصَّابِرِينَ","meal":"Şüphesiz Allah sabredenlerle beraberdir.","ref":"Bakara, 153"},
 "nisa28":{"ar":"يُرِيدُ اللَّهُ أَن يُخَفِّفَ عَنكُمْ","meal":"Allah sizden (yükü) hafifletmek ister.","ref":"Nisâ, 28"},
 "insirah6":{"ar":"إِنَّ مَعَ الْعُسْرِ يُسْرًا","meal":"Şüphesiz zorlukla beraber bir kolaylık vardır.","ref":"İnşirah, 6"},
 "zumer53":{"ar":"لَا تَقْنَطُوا مِن رَّحْمَةِ اللَّهِ","meal":"Allah'ın rahmetinden ümit kesmeyin.","ref":"Zümer, 53"},
 "yusuf87":{"ar":"لَا تَيْأَسُوا مِن رَّوْحِ اللَّهِ","meal":"Allah'ın rahmetinden ümidinizi kesmeyin.","ref":"Yûsuf, 87"},
 "tevbe40":{"ar":"لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا","meal":"Üzülme, çünkü Allah bizimle beraberdir.","ref":"Tevbe, 40"},
 "duha3":{"ar":"مَا وَدَّعَكَ رَبُّكَ وَمَا قَلَىٰ","meal":"Rabbin seni terk etmedi ve sana darılmadı.","ref":"Duhâ, 3"},
 "duha5":{"ar":"وَلَسَوْفَ يُعْطِيكَ رَبُّكَ فَتَرْضَىٰ","meal":"Elbette Rabbin sana verecek ve sen razı olacaksın.","ref":"Duhâ, 5"},
 "hadid4":{"ar":"وَهُوَ مَعَكُمْ أَيْنَ مَا كُنْتُمْ","meal":"Nerede olursanız olun, O sizinle beraberdir.","ref":"Hadîd, 4"},
 "bakara186":{"ar":"وَإِذَا سَأَلَكَ عِبَادِي عَنِّي فَإِنِّي قَرِيبٌ","meal":"Kullarım beni sana sorarsa, ben yakınım.","ref":"Bakara, 186"},
 "kaf16":{"ar":"وَنَحْنُ أَقْرَبُ إِلَيْهِ مِنْ حَبْلِ الْوَرِيدِ","meal":"Biz ona şah damarından daha yakınız.","ref":"Kaf, 16"},
 "aliimran134":{"ar":"وَالْكَاظِمِينَ الْغَيْظَ وَالْعَافِينَ عَنِ النَّاسِ","meal":"Öfkelerini yutanlar ve insanları affedenler...","ref":"Âl-i İmran, 134"},
 "fussilet34":{"ar":"ادْفَعْ بِالَّتِي هِيَ أَحْسَنُ","meal":"Kötülüğü en güzel olan şeyle sav.","ref":"Fussilet, 34"},
 "araf199":{"ar":"خُذِ الْعَفْوَ وَأْمُرْ بِالْعُرْفِ","meal":"Sen af yolunu tut, iyiliği emret.","ref":"A'raf, 199"},
 "ibrahim7":{"ar":"لَئِن شَكَرْتُمْ لَأَزِيدَنَّكُمْ","meal":"Eğer şükrederseniz, elbette size (nimetimi) artırırım.","ref":"İbrahim, 7"},
 "bakara152":{"ar":"فَاذْكُرُونِي أَذْكُرْكُمْ","meal":"Öyleyse siz beni anın ki ben de sizi anayım.","ref":"Bakara, 152"},
 "hud6":{"ar":"وَمَا مِن دَابَّةٍ فِي الْأَرْضِ إِلَّا عَلَى اللَّهِ رِزْقُهَا","meal":"Yeryüzünde hiçbir canlı yoktur ki rızkı Allah'a ait olmasın.","ref":"Hûd, 6"},
 # --- suçluluk/utanç, kıskançlık, şüphe için eklenenler ---
 "nisa110":{"ar":"وَمَن يَعْمَلْ سُوءًا أَوْ يَظْلِمْ نَفْسَهُ ثُمَّ يَسْتَغْفِرِ اللَّهَ يَجِدِ اللَّهَ غَفُورًا رَّحِيمًا","meal":"Kim bir kötülük yapar veya nefsine zulmeder de sonra Allah'tan bağışlanma dilerse, Allah'ı çok bağışlayıcı ve esirgeyici bulur.","ref":"Nisâ, 110"},
 "hud114":{"ar":"إِنَّ الْحَسَنَاتِ يُذْهِبْنَ السَّيِّئَاتِ","meal":"Şüphesiz iyilikler kötülükleri giderir.","ref":"Hûd, 114"},
 "aliimran135":{"ar":"وَالَّذِينَ إِذَا فَعَلُوا فَاحِشَةً أَوْ ظَلَمُوا أَنفُسَهُمْ ذَكَرُوا اللَّهَ فَاسْتَغْفَرُوا لِذُنُوبِهِمْ","meal":"Onlar bir kötülük yaptıklarında ya da nefislerine zulmettiklerinde Allah'ı anıp hemen günahları için bağışlanma dilerler.","ref":"Âl-i İmran, 135"},
 "tahrim8":{"ar":"يَا أَيُّهَا الَّذِينَ آمَنُوا تُوبُوا إِلَى اللَّهِ تَوْبَةً نَّصُوحًا","meal":"Ey iman edenler! Allah'a içtenlikle (nasûh) tevbe edin.","ref":"Tahrîm, 8"},
 "felak5":{"ar":"وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ","meal":"Ve hased ettiği zaman hasetçinin şerrinden (Allah'a sığınırım).","ref":"Felak, 5"},
 "nisa32":{"ar":"وَلَا تَتَمَنَّوْا مَا فَضَّلَ اللَّهُ بِهِ بَعْضَكُمْ عَلَىٰ بَعْضٍ","meal":"Allah'ın kiminizi kiminizden üstün kıldığı şeyleri (haset ederek) temenni etmeyin.","ref":"Nisâ, 32"},
 "bakara2":{"ar":"ذَٰلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِّلْمُتَّقِينَ","meal":"Bu, kendisinde şüphe olmayan, muttakiler için yol gösterici bir kitaptır.","ref":"Bakara, 2"},
 "muhammed17":{"ar":"وَالَّذِينَ اهْتَدَوْا زَادَهُمْ هُدًى","meal":"Doğru yolu bulanların ise Allah hidayetlerini artırır.","ref":"Muhammed, 17"},
 # --- alternatif çoğaltma turu: her alt-duyguya daha fazla âyet çeşidi ---
 "bakara216":{"ar":"وَعَسَىٰ أَن تَكْرَهُوا شَيْئًا وَهُوَ خَيْرٌ لَّكُمْ","meal":"Hoşunuza gitmeyen bir şey hakkınızda hayırlı olabilir.","ref":"Bakara, 216"},
 "taha25":{"ar":"رَبِّ اشْرَحْ لِي صَدْرِي وَيَسِّرْ لِي أَمْرِي","meal":"Rabbim! Göğsümü aç (genişlet) ve işimi kolaylaştır.","ref":"Tâhâ, 25-26"},
 "aliimran139":{"ar":"وَلَا تَهِنُوا وَلَا تَحْزَنُوا وَأَنتُمُ الْأَعْلَوْنَ إِن كُنتُم مُّؤْمِنِينَ","meal":"Gevşemeyin, üzülmeyin; eğer mü'minseniz en üstün olan sizsiniz.","ref":"Âl-i İmran, 139"},
 "bakara155":{"ar":"وَلَنَبْلُوَنَّكُم بِشَيْءٍ مِّنَ الْخَوْفِ وَالْجُوعِ ... وَبَشِّرِ الصَّابِرِينَ","meal":"Sizi biraz korku, açlık ve eksiklikle deneriz; sabredenleri müjdele.","ref":"Bakara, 155"},
 "shura40":{"ar":"وَجَزَاءُ سَيِّئَةٍ سَيِّئَةٌ مِّثْلُهَا فَمَنْ عَفَا وَأَصْلَحَ فَأَجْرُهُ عَلَى اللَّهِ","meal":"Bir kötülüğün cezası misliyle bir kötülüktür; ama kim affeder ve barışırsa onun ecri Allah'a aittir.","ref":"Şûrâ, 40"},
 "rad11":{"ar":"إِنَّ اللَّهَ لَا يُغَيِّرُ مَا بِقَوْمٍ حَتَّىٰ يُغَيِّرُوا مَا بِأَنفُسِهِمْ","meal":"Bir toplum kendindekini değiştirmedikçe Allah onların durumunu değiştirmez.","ref":"Ra'd, 11"},
 "yunus57":{"ar":"يَا أَيُّهَا النَّاسُ قَدْ جَاءَتْكُم مَّوْعِظَةٌ مِّن رَّبِّكُمْ وَشِفَاءٌ لِّمَا فِي الصُّدُورِ","meal":"Ey insanlar! Size Rabbinizden bir öğüt ve gönüllerdeki dertlere şifa geldi.","ref":"Yûnus, 57"},
 "bakara45":{"ar":"وَاسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ","meal":"Sabır ve namazla yardım isteyin.","ref":"Bakara, 45"},
 "furkan63":{"ar":"وَعِبَادُ الرَّحْمَٰنِ الَّذِينَ يَمْشُونَ عَلَى الْأَرْضِ هَوْنًا وَإِذَا خَاطَبَهُمُ الْجَاهِلُونَ قَالُوا سَلَامًا","meal":"Rahmân'ın kulları yeryüzünde vakarla yürüyenlerdir; cahiller onlara laf attığında 'selam' derler (ve geçerler).","ref":"Furkan, 63"},
 "nahl97":{"ar":"مَنْ عَمِلَ صَالِحًا مِّن ذَكَرٍ أَوْ أُنثَىٰ وَهُوَ مُؤْمِنٌ فَلَنُحْيِيَنَّهُ حَيَاةً طَيِّبَةً","meal":"Erkek ya da kadın, kim mü'min olarak salih amel işlerse, ona hoş (tayyib) bir hayat yaşatırız.","ref":"Nahl, 97"},
}

# ---------- RISALE-İ NUR havuzu (layer: kalp) ----------
# NOT: 'orijinal' alanı canlıda uzman onaylı ASIL pasajla doldurulacak.
# Şimdilik 'sade' = temayı özetleyen sade metin (telif-güvenli placeholder).
RISALE = {
 "tevekkul":{"orijinal":"Zira, madem ki bir insan Cenab-ı Hakkın hıfz ve himayesinde bulunmak nimetine mazhar olmuştur; artık onun için korku, endişe, üzüntü, yılma, usanma ve saire gibi şeyler bahis mevzuu olamaz.","kaynak":"Asâ-yı Mûsâ, s.422","sade":"Kaygı, çoğu zaman henüz gelmemiş bir yükü bugünden omuzlamaktır. İnsana düşen, içinde bulunduğu ânın vazifesini görüp gerisini bir ölçüyle idare eden Kudret'e emanet etmektir. Tevekkül tembellik değil; yükü asıl taşıyabilecek olana bırakmanın rahatlığıdır.","ref":"Tevekkül teması"},
 "kader_teslim":{"orijinal":"Kadere iman eden, kederden kurtulur.","kaynak":"Barla Lâhikası, s.88","sade":"Yarını bilmemek bir eksiklik değil, bir rahmettir; çünkü bilseydin belki taşıyamazdın. Perdeyi kaldırmaya çalışmak yerine ardındaki hikmete güvenmek kalbi dinlendirir.","ref":"Kadere teslimiyet teması"},
 "kader_hikmet":{"orijinal":"İşte bu hakikat-i Kur’âniyenin vücuduna, mevcudatta meşhut sühulet-i mutlaka içinde intizam-ı ekmel şahadet ettiği gibi, gelecek temsil dahi onun sırr-ı hikmetini gösterir.","kaynak":"Sözler, s.267","sade":"Her hâlin altında görünmeyen bir hikmet işler. Sana zorluk gibi görünen şey çoğu zaman bir olgunlaşmanın kabuğudur. Bu güveni taşımak, belirsizliği bir tehdit olmaktan çıkarır.","ref":"Hikmet teması"},
 "rizik_tevekkul":{"orijinal":"Hem çok ediplerin ve çok ulemanın fakr-ı hâli ve çok aptalların servet ve gınâsı dahi gösteriyor ki, celb-i rızkın medarı zekâ ve iktidar değildir, belki acz ve iftikardır, tevekkülvari bir teslimdir ve lisan-ı kàl ve lisan-ı hâl ve lisan-ı fiil ile bir duadır.","kaynak":"Mektubat, s.709","sade":"Rızık endişesi çoğu zaman sana verilmiş güveni unutmaktan doğar. Bugüne kadar seni yaşatan Kudret, yarın da seni unutacak değildir. Tevekkül, çabayı bırakmak değil; çabadan sonra huzuru seçmektir.","ref":"Rızık ve tevekkül teması"},
 "huzur_iman":{"orijinal":"Her an huzur-u İlâhîde bulunmak bahtiyarlığına eren bir kulun ruhunu, hangi fânî emel ve arzular, hangi zavallı teveccüh ve iltifatlar ve hangi pespaye gàye ve ihtiraslar tatmin, teskin ve teselli edebilir?","kaynak":"Asâ-yı Mûsâ, s.422","sade":"Sıkıntı ânında kalbin sığınacağı tek liman, seni yaratanın huzurudur. Orada insan, meselesinin büyüklüğü karşısında değil, Rabbinin kudretinin büyüklüğü karşısında durur.","ref":"Huzur ve iman teması"},
 "vesvese_21":{"orijinal":"Tedai-yi hayalât, tahattur-u faraziyat, bir nevi irtisam-ı gayriihtiyarîdir.","kaynak":"Mektubat, s.62","sade":"Vesvese, aldırış edildikçe büyüyen bir gölgedir; üstüne varılmazsa kendiliğinden söner. O düşünce senin değil, zihninde gelip geçen bir misafirdir.","ref":"Vesvese teması (bkz. 21. Söz)"},
 "sabir_kis":{"orijinal":"Sen, Cenab-ı Hakkın sana verdiği bütün sabır kuvvetini böyle sağa sola dağıtma, bu saatteki eleme karşı tahşit et, \"Yâ Sabûr!\" de, dayan.","kaynak":"Lem'alar, s.479","sade":"Hüzün, kalbin bir kışıdır; ama her kış, altında bir baharın tohumunu saklar. Bu hâl geçecek, senden geriye incelen bir kalp kalacak.","ref":"Sabır teması"},
 "sefkat_teselli":{"orijinal":"Ruh-u beşerin eşedd-i ihtiyaç ile muhtaç olduğu hakikî teselliyi nerede bulabilirsiniz?","kaynak":"Sözler, s.1029","sade":"Ağlayan bir kalp, bir şeye değer verdiğinin işaretidir; hüznün, sevginin gölgesidir. O gölgeyi seni hiç yalnız bırakmayan bir bakışın altında taşıdığını bilmek yükü hafifletir.","ref":"Şefkat ve teselli teması"},
 "an_yasama":{"orijinal":"Çünkü, geçmiş günlerin zahmeti, bugün rahmete kalbolmuş.","kaynak":"Sözler, s.424","sade":"Geçmişin acısı ile geleceğin korkusu arasında sıkışan kalp bugünü kaçırır. Oysa rahmet hep şimdidedir: nefes, ışık, bir sonraki adım.","ref":"Ânı yaşama teması"},
 "nefis_terbiye":{"orijinal":"Nefsini ıslah etmeyen başkasını ıslah edemez.","kaynak":"Sözler, s.421","sade":"Öfke, bir kıvılcımla koca bir emeği yakabilen bir ateştir. Onu yutmak zayıflık değil, en zor terbiyelerden biridir. Gerçek güç, kendi öfkene galip gelmektir.","ref":"Nefis terbiyesi teması"},
 "af_olgunluk":{"orijinal":"Meselâ, hatalı bir adama müteallik, bîçâre ihtiyar valide ve pederi ve mâsum çoluk-çocukları ezmek, perişan etmek, tarafgirâne adâvet etmek, şefkatin esasına zıttır.","kaynak":"Emirdağ Lâhikası, s.33","sade":"Öfkenin altında çoğu zaman incinmiş bir adalet duygusu yatar. O yarayı anlayarak iyileştirmek olgunluktur. Affeden, aslında kendi kalbini serbest bırakır.","ref":"Af ve olgunluk teması"},
 "yeis_kurtulus":{"orijinal":"Yeis, mâni-i her kemaldir.","kaynak":"Tarihçe-i Hayat, s.92","sade":"Ye'is, insanı olduğu yerde donduran en ağır perdedir. Gecenin en koyu ânı, şafağa en yakın olan ândır. Sana düşen, umudu bir amel gibi seçmektir.","ref":"Ye'isten kurtuluş teması"},
 "umit_gayret":{"orijinal":"Sonra irşadın iktizasındandır ki, havf ile reca arasındaki muvazene, devamla muhafaza edilsin ki; reca ile doğru yollara sülûk edilsin, havf ile de eğri yollara gidilmesin.","kaynak":"İşârâtü'l-İ'câz, s.104","sade":"Bir tek adım atacak kadar ışık, bütün yolu görmekten kıymetlidir. Rahmet, tükendiğini sandığın yerde yeniden başlar.","ref":"Ümit ve gayret teması"},
 "affedilme_rahmet":{"orijinal":"Muhakkak ki Allah çok tevbe edenleri ve temiz olanları sever.","kaynak":"Lem'alar, s.872","sade":"Rahmetin kapısı senin kapanmandan daha geniştir. Kendini affedememek, rahmetin genişliğini küçük görmektir. Dönüş her zaman mümkün.","ref":"Affedilme teması (bkz. Kastamonu Lahikası)"},
 "kendine_merhamet":{"orijinal":"Fakat, acz ve fakrımı vesile yaparak, Rabbime iltica ettim.","kaynak":"Mesnevî-i Nuriye, s.79","sade":"Kendine merhamet de bir edeptir; bedenin ve kalbin senin üzerinde bir hakkı vardır. Kendini kırarak değil kuşatarak ilerlemek asıl güçlü yoldur.","ref":"Kendine merhamet teması"},
 "marifetullah":{"orijinal":"Onu hakikî tanımayan, sevmeyen, nihayetsiz şekavete, âlâma ve evhama manen ve maddeten müptelâ olur.","kaynak":"Asâ-yı Mûsâ, s.364","sade":"İnsan, kendini kimsesiz sandığı anda bile bir bakışın altındadır. Yalnızlık hissi, kalbin bir yakınlık arayışıdır; o yakınlık en çok hiç uzaklaşmayanla kurulur.","ref":"Marifetullah teması"},
 "unsiyet":{"orijinal":"Ben yalnız değilim, tevahhuş manasızdır\" diyerek, imanlı bir hayattan ünsiyetli bir zevk alır, saadet-i hayatiye manasını anlar, Allah’a şükreder.","kaynak":"Mektubat, s.751","sade":"Ünsiyetin en derini, seni bir an bile bırakmayanla olandır. Odanda yalnızken bile duan işitiliyor. Bu bilinç en ıssız ânı bir huzura çevirir.","ref":"Ünsiyet teması"},
 "ic_dunya":{"sade":"Anlaşılmamak acıtır; ama seni yaratanın seni tam bilmesi o boşluğu doldurur. En derin görülme, insanların değil, her hâlini bilenin nezdindedir.","ref":"İç dünya teması"},
 "teslim_yuk":{"orijinal":"Tertib-i mukaddematta tefviz tembelliktir; terettüb-ü neticede tevekküldür.","kaynak":"Mektubat, s.1098","sade":"Sana verilen yük taşıyabileceğinden bir gram fazla değildir; bunu bilmek başlı başına bir rahatlıktır. Bunalma çoğu zaman aynı anda her şeyi düşünmekten doğar.","ref":"Teslimiyet teması"},
 "an_vazife":{"orijinal":"Yalnız her günün âlâmını çektirir, müterakim olmuş âlâmı unutturur.","kaynak":"Sözler, s.1174","sade":"İnsan bir günde yalnızca bir günü yaşayabilir; bütün ömrün yükünü bir güne sığdırmak olmayan bir ağırlığı taşımaktır. Bugünün vazifesini gör.","ref":"Ânın vazifesi teması"},
 "sukur":{"orijinal":"İşte, bu suretle oruç çok cihetlerle hakikî vazife-i insaniye olan şükrün anahtarı hükmüne geçer.","kaynak":"Mektubat, s.676","sade":"Şükür, elindekini görme sanatıdır; yokluğa değil varlığa bakmayı öğretir. Nefes almak, bir bardak su, bir aydınlık — fark edilmeyi bekleyen nimetlerdir.","ref":"Şükür teması"},
 "nimet_farketme":{"orijinal":"Hâlbuki, iftar vaktinde, o kuru ekmek, bir mü’minin nazarında çok kıymettar bir nimet-i İlâhiye olduğuna kuvve-i zaikası şahadet eder.","kaynak":"Mektubat, s.676","sade":"Yorgun kalp verilenleri değil verilmeyenleri sayar; oysa sayılamayacak kadar çok nimet her an sessizce çalışır. Bir tekini fark etmek kalbe nefes açar.","ref":"Nimeti fark etme teması"},
 # --- suçluluk/utanç, kıskançlık, şüphe için eklenenler (orijinal/kaynak uzman onayı bekliyor, bkz. ic_dunya) ---
 "tevbe_kapisi":{"sade":"Tevbe kapısı, kulun kendi kapattığından daha geniştir. Geçmişteki hatanın ağırlığı, bugünkü samimi bir dönüşü engelleyecek kadar büyük değildir. Kapı her an açık.","ref":"Tevbe kapısının genişliği teması"},
 "mahcubiyet_rahmet":{"sade":"Allah'a karşı mahcup hissetmek, O'ndan uzaklaşmak için değil, O'na sığınmak için bir sebeptir. Kulun mahcubiyeti, Rabbin merhametini küçültmez; tam tersine ona duyulan ihtiyacı hatırlatır.","ref":"Mahcubiyet ve rahmet teması"},
 "hased_sukur":{"sade":"Herkesin nasibi kendine göre biçilmiştir; başkasına verilen, senden alınmış değildir. Elindekine şükür, başkasınınkine göz dikmenin açtığı yarayı kapatır.","ref":"Hased karşısında şükür teması"},
 "supheden_kurtulus":{"sade":"Kalbe gelen şüphe, çoğu zaman imanın söndüğü değil, imtihan edildiği andır. Ona karşı direnmek değil, zikir ve sebatla üstüne gitmemek şüpheyi zayıflatır.","ref":"Şüpheden kurtuluş teması"},
 # --- alternatif çoğaltma turu: her alt-duyguya daha fazla Risale teması ---
 "sabir_ecir":{"sade":"Sabır, karşılıksız bir bekleyiş değildir; sabredenlerin ecri hesapsız verilir. Katlandığın her an, görünmeyen bir terazide tartılıyor.","ref":"Sabrın ecri teması"},
 "musibet_hikmet":{"sade":"Görünen musibetin ardında çoğu zaman görünmeyen bir hikmet perdesi vardır. Şikâyeti erteleyip hikmete güvenmek, belirsizliğin ağırlığını hafifletir.","ref":"Musibette hikmet teması"},
 "degisim_gayret":{"sade":"Dışarıdaki hal, önce içerideki gayretle değişir. Beklemek yerine atılabilecek en küçük adım, çaresizliğin kilidini ilk açan şeydir.","ref":"Değişim ve gayret teması"},
 "af_ferahlik":{"sade":"Affetmek karşındakini haklı çıkarmak değildir; kendi kalbini taşıdığı ağırlıktan kurtarmaktır. Öfkeyi taşımak, onu bırakmaktan daha yorucudur.","ref":"Af ve ferahlık teması"},
 "dua_zaman":{"sade":"Duanın gecikmesi, reddedilmesi değildir. Her şeyin bir vakti vardır; sana düşen, elinden geleni yapıp zamanlamayı bilene bırakmaktır.","ref":"Dua ve zamanlama teması"},
 "kalp_yumusama":{"sade":"Katılaşan bir kalp, kaybolmuş değil; sadece geçici bir uykudadır. Zikir ve küçük bir hatırlayış, o kalbi yeniden uyandırır.","ref":"Kalbin yumuşaması teması"},
}

# ---------- SOMATİK havuzu (layer: nefis) ----------
SOMATIK = {
 "box":{"title":"Kutu nefesi","intro":"Bedeni sakinleştirdiğinde zihin de yavaşlar.","breath":[["Al",4,1.2],["Tut",4,1.2],["Ver",4,0.8],["Bekle",4,0.8]]},
 "b478":{"title":"4-7-8 nefesi","intro":"Parasempatik sistemi devreye sokan yatıştırıcı bir ritim.","breath":[["Al",4,1.2],["Tut",7,1.2],["Ver",8,0.8]]},
 "ground":{"title":"5-4-3-2-1 topraklama","intro":"Zihin felaket senaryolarına kaçtığında duyular seni ana getirir.","steps":["Gördüğün 5 şeyi say","Dokunabildiğin 4 şeyi fark et","Duyduğun 3 sesi dinle","2 kokuyu ara","1 tadı fark et"]},
 "fizyo":{"title":"Fizyolojik boşaltım","intro":"Öfke bedende birikir; onu güvenli yoldan akıt.","steps":["Hızlı bir yürüyüş ya da birkaç şınav","Soğuk su ile yüzünü yıka","Yavaşlayan nabzını fark et"]},
 "duyusal":{"title":"Duyusal şarj","intro":"Küçük hazlar tükenmiş sistemi yeniden çalıştırır.","steps":["Sevdiğin bir sesi/kokuyu/tadı seç","2 dakika sadece ona odaklan","'Bu da bir nimet' diye fark et"]},
 # somatik hareket / duruş — hadis ("ayaktaysan otur…") ↔ somatik reset
 "durus":{"title":"Duruş değişimi (somatik reset)","intro":"Ruh hâli bedenin duruşuyla değişir. Konumunu değiştir, gerginliği bırak.","steps":["Ayaktaysan otur, oturuyorsan sırtüstü uzan","Omuzlarını aşağı düşür","Çeneni serbest bırak, dilini damağından ayır"]},
 "abdest":{"title":"Su ile sıfırlama","intro":"Yüze/bileklere soğuk su, yatıştırıcı dalış refleksini (parasempatik) devreye sokar.","steps":["Abdest al ya da bileklerini soğuk suyun altına tut","Yüzünü serin suyla yıka","Yavaşlayan nabzını birkaç saniye fark et"]},
}

# ---------- BİLİŞSEL havuzu (layer: akil) ----------
BILISSEL = {
 "senaryo":{"school":"BDT · Felaketsizleştirme","title":"Senaryo sınama","intro":"Zihnin ürettiği en kötü sonuç gerçekten ne kadar olası?","steps":["En kötü senaryoyu tek cümle yaz","'Gerçekleşme ihtimali gerçekten ne?' diye sor","Olsa bile baş etme planını 1 cümleyle yaz"]},
 "kontrol":{"school":"BDT · Kontrol çemberi","title":"Neyi kontrol edebilirim?","intro":"Kaygının çoğu elimizde olmayana harcanır.","steps":["Seni kaygılandıran şeyi yaz","'Neresi benim elimde?' diye sor","Elindeki tek eyleme karar ver, gerisini bırak"]},
 "defusion":{"school":"ACT · Bilişsel ayrışma","title":"Düşünceyi izle, ona dönüşme","intro":"Bir düşünce bir gerçek değildir; zihinden geçen bir olaydır.","steps":["'Kötü bir şey olacak' yerine:","'Şu an, kötü bir şey olacağına dair bir düşüncem var' de","Bu fark seninle düşüncen arasına bir aralık koyar"]},
 "kaygi_ertele":{"school":"BDT · Endişe erteleme","title":"Kaygıya randevu ver","intro":"Sınırsız alan verilen kaygı büyür; ona bir zaman dilimi ayır.","steps":["Kaygını bir yere not et","'Bunu akşam 15 dk düşüneceğim' de","O ana kadar zihnini nazikçe şimdiye çağır"]},
 "kanit":{"school":"BDT · Bilişsel yeniden yapılandırma","title":"Düşüncenin kanıtını ara","intro":"'Hiçbir şey düzelmez' bir duygu mu, kanıt mı?","steps":["Düşünceyi yaz","Lehine ve aleyhine birer kanıt bul","Daha dengeli bir cümleyle yeniden yaz"]},
 "degerler":{"school":"ACT · Değerler","title":"Derdinle değil, değerinle ilerle","intro":"Acıyı yok etmek yerine senin için önemli olana yönel.","steps":["Sana anlamlı gelen 1 değeri seç","Bu değere uygun küçük 1 adım ne olabilir?","O adımı at — his değil, yön değişir"]},
 "yeniden":{"school":"BDT · Yeniden çerçeveleme","title":"Başka bir okuma mümkün mü?","intro":"Aynı olayın daha adil bir yorumu olabilir.","steps":["Olayı tek cümlede yaz","'Başka bir açıklaması olabilir mi?' diye sor","En makul iyimser yorumu da ekle"]},
 "mektup":{"school":"Öz-şefkat","title":"Kendine şefkatli bir not","intro":"Zor gündeki bir dosta yazar gibi kendine yaz.","steps":["'Sevgili ben…' diye başla","Ne hissettiğini yargısızca yaz","Sonuna bir cümle şefkat ekle"]},
 "uc_iyi":{"school":"Pozitif Psikoloji · Şükran","title":"Üç iyi şey","intro":"Beyin olumsuza kilitlenir; şükran bu ayarı dengeler.","steps":["Bugün iyi giden 3 küçük şeyi yaz","Yanına 'neden iyiydi?' notu düş","Birkaç gün sürdür"]},
 "beyin":{"school":"BDT · Zihin boşaltma","title":"Beyin boşaltma","intro":"Üst üste binen işleri dışarı dök, sonra sırala.","steps":["Aklındaki her işi bir kağıda yaz","Sadece 1 tanesini bugüne seç","Gerisini 'sonra' kutusuna al"]},
 "tek_adim":{"school":"Davranışsal aktivasyon","title":"Tek sonraki adım","intro":"Her şeyi değil, yalnızca bir sonrakini çöz.","steps":["'Şu an atabileceğim en küçük adım ne?' diye sor","Sadece onu yap","Bitince tekrar tek bir adım sor"]},
}

# ---------- MİKRO-EYLEM havuzu (katman bazlı, 'Yaptım' butonu için) ----------
# Doğa/biyofili yönlendirmeleri de burada (madde 3).
MICRO = {
 "nefis":["Şimdi kalk ve yüzünü soğuk suyla yıka.","Ayaklarını yere bas, 10 saniye topuklarını hisset.","Bir bardak su iç, yavaşça.","Pencereyi aç, rüzgârı yüzünde hisset.","İmkânın varsa çıplak ayakla toprağa/çimene bas.","Bir bitkiye ya da çiçeğe dokun, dokusunu fark et."],
 "akil":["En büyük kaygını bir kağıda yaz, katla ve çekmeceye koy.","Telefonunu 10 dakika uzağa bırak.","Zihnindeki cümleyi yüksek sesle 'bu bir düşünce' diye tekrarla."],
 "kalp":["Bir yakınına karşılıksız güzel bir mesaj at.","İçinden bir sadaka niyeti geçir.","Sevdiğin birini bir iyilikle hatırla."],
 "ruh":["Seçilen âyeti bir kez de kendi sesinle yavaşça oku.","Bir dakika, hiçbir şey istemeden sadece şükret.","Bu meali bugünlük duvar kağıdın yap."],
}

# ---------- SİRKADİYEN yönlendirme (madde 3): saate göre ----------
CIRCADIAN = {
 "gunduz":"Gündüzse: birkaç dakika ışığa çık, güneşi teninde hisset — ritmin dengelenir.",
 "gece":"Geceyse: ekran ışığını kıs, sesi azalt, kendini sessizliğe çek — zihnin yavaşlar.",
}

# ---------- MAKAM / SES önerisi (madde 1) — ana duyguya göre ----------
# NOT: Makam-duygu eşleşmesi geleneksel/teoriktir (klinik 'tedavi' iddiası değildir).
# Arayüzde varsayılan olarak üretilen kahverengi gürültü çalar; makam kaydı lisanslı eklenebilir.
MAKAM = {
 "kaygi":{"makam":"Rast / Hüseyni","etki":"huzur ve sükûnet"},
 "huzun":{"makam":"Nihavend","etki":"yumuşama ve teselli"},
 "ofke":{"makam":"Hüseyni","etki":"ferahlık ve yatışma"},
 "yalnizlik":{"makam":"Nihavend","etki":"sıcaklık ve yakınlık"},
 "yeis":{"makam":"Rast","etki":"neşe ve umut"},
 "tukenmislik":{"makam":"Rast","etki":"canlanma"},
 "korku":{"makam":"Rehavi / Hüseyni","etki":"gece zihnini dindirme"},
 "suclu":{"makam":"Hicaz","etki":"tövbe ve arınma"},
 "hased":{"makam":"Hüseyni","etki":"gönül ferahlığı ve şükür"},
 "supheler":{"makam":"Saba","etki":"içe dönüş ve yakîn"},
}

# ---------- KISSA / TEMSİL havuzu (madde 5, Metafor Terapisi) ----------
# Kendi sözcüklerimizle, kıssalardan ilhamla kısa temsiller (telif-güvenli).
KISSA = {
 "yunus":{"text":"Hz. Yunus (a.s.) balığın karnında, üç kat karanlığın içindeydi: gecenin, denizin ve balığın karanlığı. Elinden gelen hiçbir şey kalmamıştı. Ama tam da her kapı kapandığında, tek bir samimi yöneliş, o üç karanlığı birden aydınlattı. Bazen çıkış, dışarıda değil; kalbin tek bir dönüşündedir.","ref":"Temsil · Hz. Yunus (a.s.) kıssası"},
 "tohum":{"text":"Toprağa düşen tohum, karanlıkta çatlarken sanır ki mahvoluyor. Oysa o çatlama, ölüm değil; filizin doğmasıdır. Bazen dağıldığını sandığın şey, aslında yeni bir şeyin açılmasıdır.","ref":"Temsil · tohum ve filiz"},
 "gemi":{"text":"Fırtınadaki yolcu, gemiyi yüzdürmeye çalışmaz; onu yüzdüren başkasıdır. Yolcuya düşen tek şey, güverteye tutunup kendi sükûnetini korumaktır. Sen de her dalgayı taşımak zorunda değilsin.","ref":"Temsil · fırtına ve yolcu"},
 "ayna":{"text":"Küçücük bir ayna, koca güneşi içine alır ve yansıtır. Güneş aynaya sığmaz ama aynada görünür. Sen de küçük olabilirsin; bu, büyük bir nura ayna olmana engel değil, tam tersine hikmetidir.","ref":"Temsil · ayna ve güneş"},
 "misafir":{"text":"Kapını çalan her düşünce senin değildir; çoğu sadece gelip geçen bir yolcudur. Selam verip geçenle, içeri buyur edip ağırladığın ayrı şeydir. Vesveseye kapıyı açmadan da yoluna devam edebilirsin.","ref":"Temsil · kapıdaki misafir"},
}
# hangi alt-duyguya hangi temsil (main, sub) -> [kissa id]
KISSA_MAP = {
 ("yeis","caresizlik"):["yunus","tohum"], ("yeis","genel"):["tohum","yunus"],
 ("yeis","affedememe"):["yunus"], ("huzun","degersizlik"):["ayna"],
 ("huzun","anlamsizlik"):["tohum"], ("yalnizlik","manevi"):["ayna"],
 ("yalnizlik","anlasilmamak"):["ayna"], ("korku","vesvese"):["misafir"],
 ("korku","panik"):["gemi"], ("kaygi","belirsizlik"):["gemi"],
 ("kaygi","istikbal"):["gemi"], ("kaygi","olum"):["yunus"],
}
# öfke/panik'e somatik reset (duruş/su) ekle
SOMATIK_EXTRA = {
 ("ofke","haksizlik"):["durus"], ("ofke","kirginlik"):["durus"],
 ("ofke","kendine"):["durus"], ("korku","panik"):["durus","abdest"],
 ("kaygi","belirsizlik"):["durus"],
}

# ---------- TAKSONOMİ + ÇAPRAZ-REFERANS MATRİSİ ----------
# Her alt-duygu 4 katmana içerik ID'leriyle bağlanır (uzman-onaylı matris).
# 'seeds' = serbest metni bu alt-duyguya YÖNLENDİRMEK için örnek ifadeler
#           (embedding ile bu cümlelerin vektörüne yakınlığa bakılır).
TAX = {
 "kaygi":{"label":"Kaygı","subs":{
   "istikbal":{"label":"Gelecek / istikbal kaygısı","note":"Zihnin yarına koşuyor. Onu şu ana, sonra teslimiyete getirelim.",
     "seeds":["gelecekten korkuyorum","yarın ne olacak bilmiyorum","istikbal kaygısı yaşıyorum","ileride ne olacağını düşünüp gerginleşiyorum"],
     "nefis":["box","b478"],"akil":["senaryo","kontrol","defusion"],"kalp":["tevekkul","kader_teslim","kader_hikmet","dua_zaman"],"ruh":["talak3","duha5","insirah6","bakara216"]},
   "rizik":{"label":"Rızık / geçim endişesi","note":"Yarının rızkını bugünden taşımak yorar. Yükü bugüne indirelim.",
     "seeds":["para yetişmeyecek diye korkuyorum","para endişesinden geceleri uyuyamıyorum","geçimimi sağlayamayacağım","işimi kaybedersem ne olur","borçlarım beni boğuyor","ay sonunu getiremeyeceğim diye kaygılanıyorum"],
     "nefis":["box"],"akil":["kontrol","kanit"],"kalp":["rizik_tevekkul","tevekkul","dua_zaman"],"ruh":["hud6","talak3","talak7","aliimran139"]},
   "belirsizlik":{"label":"Belirsizlik / kontrol kaybı","note":"Bilmemek ürkütücü. Kontrol edebildiğine tutunalım.",
     "seeds":["hiçbir şeyi kontrol edemiyorum","her şey belirsiz","ne yapacağımı bilmiyorum","kontrolüm dışında hissediyorum"],
     "nefis":["ground","box"],"akil":["kontrol","kaygi_ertele","defusion"],"kalp":["kader_hikmet","teslim_yuk","musibet_hikmet","dua_zaman"],"ruh":["bakara286","talak7","ali173","bakara216"]},
   "olum":{"label":"Ölüm korkusu","note":"Bu korku çok insanidir. Onu bir yakınlıkla yumuşatalım.",
     "seeds":["ölmekten korkuyorum","ölüm aklıma geldikçe daralıyorum","ecel korkusu","öleceğim diye panikliyorum"],
     "nefis":["b478"],"akil":["degerler","defusion"],"kalp":["huzur_iman","kader_teslim","an_yasama"],"ruh":["duha3","kaf16","bakara286"]},
 }},
 "huzun":{"label":"Hüzün","subs":{
   "yas":{"label":"Yas / kayıp","note":"Kaybın görülmeyi hak ediyor. Onu bastırmadan yanında duralım.",
     "seeds":["birini kaybettim","yasım var","çok sevdiğim biri öldü","kaybımın acısı geçmiyor"],
     "nefis":["b478"],"akil":["mektup","defusion"],"kalp":["sabir_kis","sefkat_teselli","sabir_ecir"],"ruh":["tevbe40","duha3","insirah6","bakara155"]},
   "degersizlik":{"label":"Değersizlik hissi","note":"Kendine değersiz demek bir gerçek değil, bir yorgunluk sesidir.",
     "seeds":["değersiz hissediyorum","işe yaramaz biriyim","hiçbir şeyi beceremiyorum","kimse bana değer vermiyor"],
     "nefis":["duyusal"],"akil":["kanit","uc_iyi"],"kalp":["sefkat_teselli","marifetullah","kendine_merhamet"],"ruh":["duha3","duha5","kaf16","nahl97"]},
   "anlamsizlik":{"label":"Anlamsızlık / boşluk","note":"Boşluk hissi, aslında bir anlam arayışıdır. Yönü birlikte bulalım.",
     "seeds":["her şey anlamsız","içimde bir boşluk var","neden yaşadığımı bilmiyorum","hiçbir şey anlam ifade etmiyor","hayat anlamını yitirdi, içim bomboş","yaptığım hiçbir şeyin anlamı kalmadı"],
     "nefis":["ground"],"akil":["degerler","uc_iyi"],"kalp":["an_yasama","ic_dunya","degisim_gayret"],"ruh":["duha5","bakara152","nahl97"]},
 }},
 "ofke":{"label":"Öfke","subs":{
   "haksizlik":{"label":"Haksızlığa öfke","note":"Öfken bir adalet duygusundan geliyor. Önce onu güvene alalım.",
     "seeds":["bana haksızlık yapıldı","çok adaletsiz bir duruma maruz kaldım","hak etmediğim halde suçlandım","bu haksızlığa çok öfkeliyim, içim yanıyor","adaletsizlik karşısında öfkem kabarıyor","bana yapılan haksızlıktan dolayı çok kızgınım"],
     "nefis":["fizyo","box"],"akil":["yeniden","kontrol"],"kalp":["nefis_terbiye","af_olgunluk","af_ferahlik"],"ruh":["aliimran134","fussilet34","shura40"]},
   "kirginlik":{"label":"Yakınına kırgınlık","note":"En çok, sevdiğimiz incitir. Bu yarayı anlayarak tutalım.",
     "seeds":["sevdiğim biri beni kırdı","çok kırgınım","küstüm ona","yakınım beni incitti"],
     "nefis":["box"],"akil":["yeniden","defusion"],"kalp":["af_olgunluk","nefis_terbiye","af_ferahlik"],"ruh":["araf199","aliimran134","furkan63"]},
   "kendine":{"label":"Kendine öfke / pişmanlık","note":"Kendine kızmak yorar. Rahmetin kapısı senin kapanmandan geniş.",
     "seeds":["kendime çok kızgınım","kendi kendime öfkeliyim","kendi hatamdan dolayı kendime kızıyorum","aptallık ettiğim için kendime çok öfkeliyim","neden öyle yaptım diye kendime kızıyorum"],
     "nefis":["b478"],"akil":["mektup","kanit"],"kalp":["affedilme_rahmet","kendine_merhamet","tevbe_kapisi"],"ruh":["zumer53","duha3","nisa110"]},
 }},
 "yalnizlik":{"label":"Yalnızlık","subs":{
   "terk":{"label":"Terk edilmişlik","note":"Bırakılmış hissetmek acıtır. Ama seni bırakmayan bir yakınlık var.",
     "seeds":["herkes beni terk etti","yalnız bırakıldım","kimse yanımda değil","bıraktılar beni"],
     "nefis":["duyusal"],"akil":["mektup"],"kalp":["unsiyet","sefkat_teselli","marifetullah"],"ruh":["duha3","hadid4","yunus57"]},
   "anlasilmamak":{"label":"Anlaşılmamak","note":"Görülmemek boşluk açar. En derin görülme her hâlini bilenin yanındadır.",
     "seeds":["kimse beni anlamıyor","anlaşılmıyorum","yalnız hissediyorum kalabalıkta","kendimi kimseye anlatamıyorum"],
     "nefis":["ground"],"akil":["defusion","degerler"],"kalp":["marifetullah","ic_dunya","unsiyet"],"ruh":["bakara186","kaf16","yunus57"]},
   "manevi":{"label":"Manevi yalnızlık","note":"Kalabalıkta bile hissedilen o boşluğu bir yakınlıkla dolduralım.",
     "seeds":["içsel yalnızlık","ruhen yalnızım","Allah'a uzak, manen yalnız hissediyorum","maneviyatımdan kopmuş hissediyorum"],
     "nefis":["b478"],"akil":["uc_iyi"],"kalp":["marifetullah","unsiyet","ic_dunya"],"ruh":["bakara186","kaf16","hadid4"]},
 }},
 "yeis":{"label":"Umutsuzluk","subs":{
   "genel":{"label":"Tükenmiş umut","note":"Çıkış görünmüyor olabilir. Yolun tamamını değil, bir adımı görmen yeter.",
     "seeds":["hiç umudum kalmadı","artık bitti","çıkış yok","pes ettim"],
     "nefis":["box"],"akil":["tek_adim","kanit"],"kalp":["yeis_kurtulus","umit_gayret","degisim_gayret"],"ruh":["insirah6","zumer53","talak7"]},
   "affedememe":{"label":"Kendini affedememe","note":"Geçmişe takılan kalp yorulur. Dönüş her zaman mümkün.",
     "seeds":["kendimi affedemiyorum","yaptığım hatayı bir türlü affedemiyorum","yaptığım hata aklımdan çıkmıyor","günahlarım yüzünden umutsuzum","geçmişime takıldım","suçluluk içindeyim, kendimi bağışlayamıyorum"],
     "nefis":["b478"],"akil":["mektup"],"kalp":["affedilme_rahmet","kendine_merhamet","tevbe_kapisi"],"ruh":["zumer53","yusuf87","nisa110"]},
   "caresizlik":{"label":"Çaresizlik","note":"Elinden bir şey gelmiyormuş gibi. Küçük bir adım bu duvarı deler.",
     "seeds":["çaresizim","elimden bir şey gelmiyor","yapabileceğim hiçbir şey yok","kilitlenmiş durumdayım"],
     "nefis":["ground"],"akil":["tek_adim","kontrol"],"kalp":["umit_gayret","kader_teslim","degisim_gayret"],"ruh":["talak7","yusuf87","bakara286"]},
 }},
 "tukenmislik":{"label":"Tükenmişlik","subs":{
   "yuk":{"label":"Aşırı yük / yetişememe","note":"Her şey üstüne geliyor. Onları taşınabilir parçalara ayıralım.",
     "seeds":["iş ve sorumluluklara yetişmekten tükendim","üstümdeki görevler giderek ağırlaşıyor","gün boyu koşturmaktan bittim, dinlenemiyorum","sorumlulukların yükü altında ezildim","sürekli çalışmaktan yorgun düştüm"],
     "nefis":["b478","box"],"akil":["beyin","tek_adim"],"kalp":["teslim_yuk","an_vazife","sabir_ecir"],"ruh":["bakara286","nisa28","talak7","taha25"]},
   "duyarsizlik":{"label":"Şükürsüzlük / duyarsızlaşma","note":"İyi olan her şey gözden kaybolmuş. Onları yeniden görünür kılalım.",
     "seeds":["uzun süredir hiçbir şeyden keyif almıyorum","içim tükendi, şükredecek hal bulamıyorum","duygusuzlaştım, hiçbir şey beni etkilemiyor","enerjim kalmadı, sabah kalkmak istemiyorum","her şeye karşı hissizleştim"],
     "nefis":["duyusal"],"akil":["uc_iyi"],"kalp":["sukur","nimet_farketme","an_yasama"],"ruh":["ibrahim7","bakara152","duha5"]},
 }},
 "korku":{"label":"Korku / Panik","subs":{
   "panik":{"label":"Panik anı","note":"Beden alarma geçmiş. Önce onu güvene alalım, sonra düşünelim.",
     "seeds":["panik atak geçiriyorum","nefes alamıyorum","birden kalbim hızlandı, boğuluyormuş gibi oldum","göğsüm sıkışıyor, boğulacak gibiyim","kalbim küt küt atıyor, kriz geçiriyorum"],
     "nefis":["b478","ground"],"akil":["defusion"],"kalp":["huzur_iman","an_yasama","dua_zaman"],"ruh":["bakara286","ali173","bakara45"]},
   "vesvese":{"label":"Vesvese / takıntılı düşünce","note":"O düşünce senin değil; üstüne varmadıkça söner.",
     "seeds":["aklıma takılan bir düşünce","aklıma kötü kötü düşünceler geliyor durduramıyorum","istemsiz kötü düşünceler zihnimden geçip duruyor","zihnime gelen düşünceleri durduramıyorum","vesvese","sürekli aynı şeyi düşünüyorum","takıntı haline geldi"],
     "nefis":["box"],"akil":["defusion","kaygi_ertele"],"kalp":["vesvese_21","huzur_iman","kalp_yumusama"],"ruh":["ali173","rad28","yunus57"]},
 }},
 "suclu":{"label":"Suçluluk / Utanç","subs":{
   "vicdan_azabi":{"label":"Vicdan azabı","note":"Vicdanın seni bir hatadan dolayı sızlatıyor. Onu susturmadan, dönüşe çevirelim.",
     "seeds":["vicdanım beni rahat bırakmıyor","yaptığım şey vicdanımı sızlatıyor","içimde sürekli bir suçluluk duygusu var","o olayı düşündükçe içim burkuluyor","yaptığımdan dolayı huzursuzum ve rahat edemiyorum"],
     "nefis":["box"],"akil":["mektup","kanit"],"kalp":["tevbe_kapisi","kendine_merhamet","af_ferahlik"],"ruh":["nisa110","hud114","aliimran135"]},
   "utanma_mahcubiyet":{"label":"Utanç / mahcubiyet","note":"İnsanların önünde küçük düşme korkusu ağır bir yüktür. Değerini başkasının gözünde arama.",
     "seeds":["çok utanıyorum","rezil oldum, herkesin önünde küçük düştüm","insanların önünde mahcup oldum","yüzüm kızarıyor utancımdan","herkes ne düşünür diye çok utanıyorum"],
     "nefis":["duyusal","durus"],"akil":["yeniden","degerler"],"kalp":["kendine_merhamet","sefkat_teselli","tevbe_kapisi"],"ruh":["aliimran135","hud114","nisa110"]},
   "allaha_mahcubiyet":{"label":"Allah'a karşı mahcubiyet","note":"Günahından dolayı Allah'a yüzün olmadığını hissetmek, aslında O'na dönüşün başlangıcıdır.",
     "seeds":["Allah'a karşı yüzüm yok","günahlarımdan dolayı Allah'a mahcubum","dua etmeye bile utanıyorum","Rabbime karşı çok mahcup hissediyorum","günahkarlığımdan dolayı ibadet etmeye yüzüm yok"],
     "nefis":["b478"],"akil":["mektup"],"kalp":["mahcubiyet_rahmet","affedilme_rahmet","tevbe_kapisi"],"ruh":["tahrim8","nisa110","hud114"],"kissa":["yunus"]},
 }},
 "hased":{"label":"Kıskançlık","subs":{
   "kiyaslama":{"label":"Başkasıyla kıyaslama","note":"Başkasının vitrinini kendi arka planınla kıyaslamak seni yorar. Elindekine dönelim.",
     "seeds":["başkalarıyla kendimi kıyaslıyorum","onun sahip olduklarını çok istiyorum","herkes benden ileride sanki","sosyal medyada başkalarını görünce kendimi kötü hissediyorum","neden onda var da bende yok diye düşünüyorum"],
     "nefis":["box"],"akil":["yeniden","uc_iyi"],"kalp":["hased_sukur","sukur","degisim_gayret"],"ruh":["nisa32","ibrahim7","nahl97"]},
   "hased_ici_yanma":{"label":"Hased / içten içe yanma","note":"Başkasının nimetine dayanamamak seni içten yakar. Şükür bu ateşi söndürür.",
     "seeds":["onun başarısına dayanamıyorum","içim kıskançlıktan yanıyor","başkasının iyiliğine sevinemiyorum","kıskançlığımdan kendimden nefret ediyorum","onun elindekini kaybetmesini istercesine hissediyorum"],
     "nefis":["fizyo","box"],"akil":["mektup","degerler"],"kalp":["hased_sukur","nimet_farketme","af_ferahlik"],"ruh":["felak5","nisa32","nahl97"],"kissa":["ayna"]},
 }},
 "supheler":{"label":"Şüphe / İman Zayıflığı","subs":{
   "iman_supheleri":{"label":"İnanç şüpheleri","note":"Kalbe gelen şüphe imanın bittiği an değil, sınandığı andır. Üstüne varmadan zikirle geçelim.",
     "seeds":["Allah'ın varlığından şüphe ediyorum","inancımda şüpheler var","imanımdan emin olamıyorum","aklıma dini konularda şüpheler geliyor","inancımı sürekli sorguluyorum"],
     "nefis":["box"],"akil":["defusion","kanit"],"kalp":["supheden_kurtulus","huzur_iman","kalp_yumusama"],"ruh":["bakara2","muhammed17","rad28"],"kissa":["misafir"]},
   "kalp_katiligi":{"label":"Kalp katılığı","note":"İbadette bir şey hissetmemek maneviyatın bittiği anlamına gelmez. Küçük bir dokunuş yeter.",
     "seeds":["namaz kılarken hiçbir şey hissetmiyorum","kalbim katılaştı","ibadet ederken içim boş","dua ederken bir şey hissedemiyorum","maneviyatımı kaybettim gibi hissediyorum"],
     "nefis":["ground"],"akil":["uc_iyi"],"kalp":["marifetullah","huzur_iman","kalp_yumusama"],"ruh":["rad28","bakara152","muhammed17"]},
 }},
}

def main():
    # taksonomiye temsil (kıssa) ve ek somatik teknikleri enjekte et
    for mk, mv in TAX.items():
        for sk, sv in mv["subs"].items():
            key = (mk, sk)
            if key in KISSA_MAP:
                sv["kissa"] = KISSA_MAP[key]
            if key in SOMATIK_EXTRA:
                for tech in SOMATIK_EXTRA[key]:
                    if tech not in sv["nefis"]:
                        sv["nefis"].append(tech)

    content = {"ayet":AYET,"risale":RISALE,"somatik":SOMATIK,"bilissel":BILISSEL,
               "micro":MICRO,"kissa":KISSA,"circadian":CIRCADIAN,"makam":MAKAM}
    (DATA/"content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA/"taxonomy.json").write_text(json.dumps(TAX, ensure_ascii=False, indent=2), encoding="utf-8")
    n_sub = sum(len(m["subs"]) for m in TAX.values())
    print(f"Yazıldı: content.json ({len(AYET)} ayet, {len(RISALE)} risale, {len(SOMATIK)} somatik, "
          f"{len(BILISSEL)} bilissel, {len(KISSA)} kıssa)")
    print(f"Yazıldı: taxonomy.json ({len(TAX)} ana duygu, {n_sub} alt-duygu)")

if __name__ == "__main__":
    main()
