import urlparse

from eopayment.systempayv2 import Payment

PARAMS = {
    'secret_test': '1122334455667788'
}


def test_systempayv2():
    p = Payment(PARAMS)
    qs = 'vads_version=V2&vads_page_action=PAYMENT&vads_action_mode=INTERACTIV' \
         'E&vads_payment_config=SINGLE&vads_site_id=12345678&vads_ctx_mode=TES' \
         'T&vads_trans_id=654321&vads_trans_date=20090501193530&vads_amount=15' \
         '24&vads_currency=978'
    qs = urlparse.parse_qs(qs)
    for key in qs.keys():
        qs[key] = qs[key][0]
    assert p.signature(qs) == '606b369759fac4f0864144c803c73676cbe470ff'
