from unittest import TestCase
from decimal import Decimal
import base64
import urllib

import eopayment.paybox as paybox
import eopayment

BACKEND_PARAMS = {
            'platform': 'test',
            'site': '12345678',
            'rang': '001',
            'identifiant': '12345678',
            'shared_secret': '0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF',
            'callback': 'http://example.com/callback',
}

class PayboxTests(TestCase):
    def test_sign(self):
        key = '0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF'.decode('hex')
        d = dict(paybox.sign([
                    ['PBX_SITE', '12345678'],
                    ['PBX_RANG', '32'],
                    ['PBX_IDENTIFIANT', '12345678'],
                    ['PBX_TOTAL', '999'],
                    ['PBX_DEVISE', '978'],
                    ['PBX_CMD', 'TEST Paybox'],
                    ['PBX_PORTEUR', 'test@paybox.com'],
                    ['PBX_RETOUR', 'Mt:M;Ref:R;Auto:A;Erreur:E'],
                    ['PBX_HASH', 'SHA512'],
                    ['PBX_TIME', '2015-06-08T16:21:16+02:00'],
                ],
                key))
        result = '475FE1C45A0D09D26D2CAC9A1AC39C024773D790F50B6DD15B260F55FCD527FD3AD4AA3998F4162EFE9BDC494B9850A673355A32ACC4F85B67F8566037836F8E'
        self.assertIn('PBX_HMAC', d)
        self.assertEqual(d['PBX_HMAC'], result)

    def test_request(self):
        backend = eopayment.Payment('paybox', BACKEND_PARAMS)
        time = '2015-07-15T18:26:32+02:00'
        email = 'bdauvergne@entrouvert.com'
        order_id = '20160216'
        transaction = '1234'
        amount = '19.99'
        transaction_id, kind, what = backend.request(
            Decimal(amount), email=email, orderid=order_id,
            transaction_id=transaction, time=time)
        self.assertEqual(kind, eopayment.FORM)
        self.assertEqual(transaction_id, '1234')
        from xml.etree import ElementTree as ET
        root = ET.fromstring(str(what))
        self.assertEqual(root.tag, 'form')
        self.assertEqual(root.attrib['method'], 'POST')
        self.assertEqual(root.attrib['action'], paybox.URLS['test'])
        for node in root:
            self.assertIn(node.attrib['type'], ('hidden', 'submit'))
            if node.attrib['type'] == 'submit':
                self.assertEqual(set(node.attrib.keys()), set(['type', 'value']))
            if node.attrib['type'] == 'hidden':
                self.assertEqual(set(node.attrib.keys()), set(['type', 'name', 'value']))
                name = node.attrib['name']
                reference = order_id + eopayment.common.ORDERID_TRANSACTION_SEPARATOR + transaction
                values = {
                    'PBX_RANG': '01',
                    'PBX_SITE': '12345678',
                    'PBX_IDENTIFIANT': '12345678',
                    'PBX_RETOUR': 'montant:M;reference:R;code_autorisation:A;erreur:E;signature:K',
                    'PBX_TIME': time,
                    'PBX_PORTEUR': email,
                    'PBX_CMD': reference,
                    'PBX_TOTAL': amount.replace('.', ''),
                    'PBX_DEVISE': '978',
                    'PBX_HASH': 'SHA512',
                    'PBX_HMAC': '173483CFF84A7ECF21039F99E9A95C5FB53D98A1562184F5B2C4543E4F87BFA227CC2CA10DE989D6C8B4DC03BC2ED44B7D7BDF5B4FABA8274D5D37C2F6445F36',
                    'PBX_ARCHIVAGE': '1234',
                    'PBX_REPONDRE_A': 'http://example.com/callback',
                }
                self.assertIn(name, values)
                self.assertEqual(node.attrib['value'], values[name])

    def test_response(self):
        backend = eopayment.Payment('paybox', BACKEND_PARAMS)
        order_id = '20160216'
        transaction = '1234'
        reference = order_id + eopayment.common.ORDERID_TRANSACTION_SEPARATOR + transaction
        data = {'montant': '4242', 'reference': reference,
                'code_autorisation': 'A', 'erreur': '00000'}
        response = backend.response(urllib.urlencode(data))
        self.assertEqual(response.order_id, order_id)

    def test_rsa_signature_validation(self):
        pkey = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUgYufHuheMztK1LhQSG6xsOzb
UX4D2A/QcMvkEcRVXFx5tQqcE9/JnMqE41TF/ebn7jC/MBxxtPFkUN7+EZoeMN7x
OWzAMDm/xsCWRvvel4GGixgm3aQRUPyTrlm4Ksy32Ya0rNnEDMAvB3dxOn7cp8GR
ZdzrudBlevZXpr6iYwIDAQAB
-----END PUBLIC KEY-----'''
        data = 'coin\n'
        sig64 = '''VCt3sgT0ecacmDEWWNVXJ+jGmIPBMApK42tBJV0FlDjpllOGPy8MsAmLW4/QjTtx
z0Dkz0NjxvU+5WzQZh9Uuxr/egRCwV4NMRWqu0zaVVioeBvl4/5CWm4f4/1L9+0m
FBFKOZhgBJnkC+l6+XhT4aYWKaQ4ocmOMV92yjeXTE4='''
        self.assertTrue(paybox.verify(data, base64.b64decode(sig64), key=pkey))
