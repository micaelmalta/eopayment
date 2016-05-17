import pytest
import pprint

import eopayment

def test_build_request():
    backend = eopayment.Payment('sips2', {})
    assert backend.request(amount='12')

def test_options():
    payment = eopayment.Payment('sips2', {'capture_mode': 'VALIDATION'})
    assert payment.backend.get_data()['captureMode'] == 'VALIDATION'

def test_parse_response():
    qs = '''Data=captureDay%3D0%7CcaptureMode%3DAUTHOR_CAPTURE%7CcurrencyCode%3D978%7CmerchantId%3D002001000000001%7CorderChannel%3DINTERNET%7CresponseCode%3D00%7CtransactionDateTime%3D2016-02-01T17%3A44%3A20%2B01%3A00%7CtransactionReference%3D668930%7CkeyVersion%3D1%7CacquirerResponseCode%3D00%7Camount%3D1200%7CauthorisationId%3D12345%7CcardCSCResultCode%3D4E%7CpanExpiryDate%3D201605%7CpaymentMeanBrand%3DMASTERCARD%7CpaymentMeanType%3DCARD%7CcustomerIpAddress%3D82.244.203.243%7CmaskedPan%3D5100%23%23%23%23%23%23%23%23%23%23%23%2300%7CorderId%3Dd4903de7027f4d56ac01634fd7ab9526%7CholderAuthentRelegation%3DN%7CholderAuthentStatus%3D3D_ERROR%7CtransactionOrigin%3DINTERNET%7CpaymentPattern%3DONE_SHOT&Seal=6ca3247765a19b45d25ad54ef4076483e7d55583166bd5ac9c64357aac097602&InterfaceVersion=HP_2.0&Encode='''
    backend = eopayment.Payment('sips2', {})
    assert backend.response(qs)
