Interface with French's bank online credit card processing services
===================================================================

Services supported are:
- ATOS/SIPS used by:
  - BNP under the name Mercanet,
  - Banque Populaire (before 2010/2011) under the name Cyberplus,
  - CCF under the name Elysnet,
  - HSBC under the name Elysnet,
  - Crédit Agricole under the name e-Transactions,
  - La Banque Postale under the name ScelliusNet,
  - LCL under the name Sherlocks,
  - Société Générale under the name Sogenactif
  - and Crédit du Nord under the name Webaffaires,
- SystemPay by Banque Populaire (since 2010/2011) and Caisse d'Épargne
- TIPI
- Ogone
- Paybox
- SPPlus by Caisse d'épargne (obsolete)
- Payzen

You can emit payment request under a simple API which takes as input a
dictionnary as configuration and an amount to pay. You get back a
transaction_id. Another unique API allows to handle the notifications coming
from those services, reporting whether the transaction was successful and which
one it was. The full content (which is specific to the service) is also
reported for logging purpose.

The spplus and paybox module also depend upon the python Crypto library for DES
decoding of the merchant key and RSA signature validation on the responses.

Some backends allow to specify the order and transaction ids in different
fields, in order to allow to match them in payment system backoffice. They are:
- Payzen
- SIPS
- SystemPay

For other backends, the order and transaction ids, separated by '!' are sent in
order id field, so they can be matched in backoffice.

Changelog
=========

1.8
---
- fix UTF-8 character in non unicode log message

1.7
---
- check responses and raise ResponseError when theyr are malformed

1.6
---
- fix payzen service_url
- rationalize Payment object constructors

1.5
---
- uniformize constructors
- fix service_url in the payzen backend

1.4
---
- add sips2 backend to conform with version 2.3 of their interface

1.3
---
- add payzen backend
