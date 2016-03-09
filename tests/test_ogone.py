from unittest import TestCase
import urllib

import eopayment
import eopayment.ogone as ogone
from eopayment import ResponseError

PSPID = '2352566'

BACKEND_PARAMS = {
    'environment': ogone.ENVIRONMENT_TEST,
    'pspid': PSPID,
    'sha_in': 'secret',
    'sha_out': 'secret'
}

class OgoneTests(TestCase):

    def test_request(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        amount = '42.42'
        order_id = 'myorder'
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

    def test_response(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        order_id = 'myorder'
        data = {'orderid': order_id + eopayment.common.ORDERID_TRANSACTION_SEPARATOR + 'RtEpMXZn4dX8k1rYbwLlby',
                'payid': '32100123', 'status': 9, 'ncerror': 0}
        response = ogone_backend.response(urllib.urlencode(data))
        self.assertEqual(response.order_id, order_id)

    def test_bad_response(self):
        ogone_backend = eopayment.Payment('ogone', BACKEND_PARAMS)
        order_id = 'myorder'
        data = {'payid': '32100123', 'status': 9, 'ncerror': 0}
        with self.assertRaises(ResponseError):
            response = ogone_backend.response(urllib.urlencode(data))
