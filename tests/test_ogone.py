# -*- coding: utf-8 -*-

from unittest import TestCase
import urllib.request, urllib.parse, urllib.error

import eopayment
import eopayment.ogone as ogone
from eopayment import ResponseError

PSPID = '2352566ö'

BACKEND_PARAMS = {
    'environment': ogone.ENVIRONMENT_TEST,
    'pspid': PSPID,
    'sha_in': 'sécret',
    'sha_out': 'sécret',
    'automatic_return_url': 'http://example.com/autömatic_réturn_url'
}

class OgoneTests(TestCase):

    def test_request(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        amount = '42.42'
        order_id = 'my ordér'
        reference, kind, what = ogone_backend.request(amount=amount,
                                        orderid=order_id, email='foo@example.com')
        self.assertEqual(len(reference), 30)
        assert reference.startswith(order_id)
        from xml.etree import ElementTree as ET
        root = ET.fromstring(str(what))
        self.assertEqual(root.tag, 'form')
        self.assertEqual(root.attrib['method'], 'POST')
        self.assertEqual(root.attrib['action'], ogone.ENVIRONMENT_TEST_URL)
        values = {
            'CURRENCY': 'EUR',
            'ORDERID': reference,
            'PSPID': PSPID,
            'EMAIL': 'foo@example.com',
            'AMOUNT': amount.replace('.', ''),
            'LANGUAGE': 'fr_FR',
        }
        values.update({'SHASIGN': ogone_backend.backend.sha_sign_in(values)})
        for node in root:
            self.assertIn(node.attrib['type'], ('hidden', 'submit'))
            self.assertEqual(set(node.attrib.keys()), set(['type', 'name', 'value']))
            name = node.attrib['name']
            if node.attrib['type'] == 'hidden':
                self.assertIn(name, values)
                self.assertEqual(node.attrib['value'], values[name])

    def test_unicode_response(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        order_id = 'myorder'
        data = {'orderid': 'myorder', 'status': '9', 'payid': '3011229363',
                'cn': 'Usér', 'ncerror': '0',
                'trxdate': '10/24/16', 'acceptance': 'test123',
                'currency': 'eur', 'amount': '7.5',
                'shasign': '3EE0CF69B5A8514962C9CF8A545861F0CA1C6891'}
        # uniformize to utf-8 first
        for k in data:
            data[k] = eopayment.common.force_byte(data[k])
        response = ogone_backend.response(urllib.parse.urlencode(data))
        assert response.signed
        self.assertEqual(response.order_id, order_id)

    def test_iso_8859_1_response(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        order_id = 'lRXK4Rl1N2yIR3R5z7Kc'
        backend_response = 'orderID=lRXK4Rl1N2yIR3R5z7Kc&currency=EUR&amount=7%2E5&PM=CreditCard&ACCEPTANCE=test123&STATUS=9&CARDNO=XXXXXXXXXXXX9999&ED=0118&CN=Miha%EF+Serghe%EF&TRXDATE=10%2F24%2F16&PAYID=3011228911&NCERROR=0&BRAND=MasterCard&IP=80%2E12%2E92%2E47&SHASIGN=435D5E36E1F4B17739C1054FFD204218E65C15AB'
        response = ogone_backend.response(backend_response)
        assert response.signed
        self.assertEqual(response.order_id, order_id)


    def test_bad_response(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        order_id = 'myorder'
        data = {'payid': '32100123', 'status': 9, 'ncerror': 0}
        with self.assertRaises(ResponseError):
            response = ogone_backend.response(urllib.parse.urlencode(data))
