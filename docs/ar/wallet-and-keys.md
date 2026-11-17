<div dir="rtl">

# المحفظة والمفاتيح

محافظ Janzeer مشابهة لبنية BIP39 لكنها تستخدم ثوابت خاصة بالسلسلة، لذلك فإن أي مكتبة bip32 جاهزة أو مكتبة Ethereum تشتق **مفتاحًا** مختلفًا من عبارة الاسترداد نفسها. اشتق دائمًا باستخدام SDK (أو عميل يجتاز [متجهات المطابقة](../conformance.md)).

## الإنشاء أو الاستيراد

```python
from janzeer import Account, mnemonic

phrase  = mnemonic.generate()                 # 12 كلمة (مرر 256 للحصول على 24)
account = Account.from_mnemonic(phrase)       # الوسيط الثاني اختياري: عبارة مرور BIP39
account.address            # الصيغة المعيارية بأحرف صغيرة — ما تخزنه السلسلة وما توقع به
account.checksum_address   # صيغة EIP-55 مختلطة الحالة — للعرض وكشف الأخطاء المطبعية
account.public_key_hex     # secp256k1 مضغوط، 66 حرفًا سداسيًا

Account.from_private_key("6dea…8efc")                       # استيراد المفتاح الخام
Account.from_seed(mnemonic.to_seed(phrase), "m/0/1/0")      # مسار آخر غير مُصلَّب (متقدم)
```

يتحقق `mnemonic.validate(phrase)` من قائمة الكلمات ومن مجموع التحقق؛ ويثير `Account.from_mnemonic` الخطأ `ValueError` عند وجود عبارة غير صالحة. يعرض `repr(account)` العنوان فقط — فلا يطبع SDK المفتاح الخاص أبدًا.

## كيف يعمل الاشتقاق (derivation) (لتتمكن من تدقيقه)

| الخطوة | Janzeer | BIP39/32 القياسي |
|---|---|---|
| البذرة (seed) | PBKDF2-HMAC-SHA512، ‏2048 جولة، الملح `"@_Janzeer_Blockchain_@" + passphrase` | الملح `"mnemonic" + passphrase` |
| المفتاح الرئيسي | HMAC-SHA512 بمفتاح `"@_Janzeer_Blockchain_@"` | بمفتاح `"Bitcoin seed"` |
| المسار | `m/0/0/0`، كلها غير مُصلَّبة | يختلف |
| عنوان | `0x` + أول 20 بايتًا من keccak256(المفتاح العام **المضغوط**)، بأحرف صغيرة | Ethereum يجزّئ المفتاح غير المضغوط |

تعيش الدوال منخفضة المستوى في `janzeer.crypto`: `mnemonic_to_seed`، و`seed_to_master_key`، و`derive_child`، و`derive_path`، و`public_key_to_address`. إن Keccak-256 هنا هو متغير Ethereum، **وليس** `hashlib.sha3_256`.

## العناوين

```python
from janzeer import is_valid_address, normalize_address, to_checksum_address

is_valid_address("0x06e1c0FA9955A700876f8cB0Acc7f13fBA9FB8BA")   # True (صيغة EIP-55 صحيحة)
is_valid_address("0x06E1c0fa9955a700876f8cb0acc7f13fba9fb8ba")   # False (خطأ في حالة الأحرف: على الأرجح خطأ مطبعي)
normalize_address("0x06e1c0FA…")                                 # '0x06e1c0fa…'
```

تقبل العقدة العناوين الصغيرة أو ذات حالة الأحرف الصحيحة وترد دائمًا بأحرف صغيرة. وقّع وخزّن الصيغة الصغيرة؛ واعرض صيغة المجموع التحققي.

## التوقيع

ينتج `account.sign(hash_hex)` توقيعًا حتميًا وفق RFC-6979، ومنخفض S، ومشفرًا بـ DER، ومشفرًا بـ Base64 على الملخص ذي 32 بايتًا — وهو بالضبط ما تتحقق منه العقدة. نادرًا ما تستدعيه مباشرة: فالدالة `account.sign_tx(unsigned_tx)` تجزّئ معاملة بناها `TxBuilder` وتوقعها. ويمكن لمحفظة عتادية أو KMS توقيع `unsigned_tx.hash()` خارجيًا وإرفاقه باستخدام `unsigned_tx.with_signature(signature, public_key_hex)`.

## حفظ العبارة أثناء التخزين

استخدم دوال [الخزينة (vault)](../vault.md) أو التخزين الآمن في نظامك. لا ترسل عبارة الاسترداد أو أي مفتاح خاص إلى أي خادم أبدًا: فلا توجد لدى العقدة أي نقطة نهاية تقبل ذلك.

</div>
