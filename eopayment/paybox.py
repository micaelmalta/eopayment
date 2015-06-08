# -*- coding: utf-8 -*-

import logging
import hashlib
import hmac

VARS = {
    'PBX_SITE': 'Numéro de site (fourni par Paybox)',
    'PBX_RANG': 'Numéro de rang (fourni par Paybox)',
    'PBX_IDENTIFIANT': 'Identifiant interne (fourni par Paybox)',
    'PBX_TOTAL': 'Montant total de la transaction',
    'PBX_DEVISE': 'Devise de la transaction',
    'PBX_CMD':  'Référence commande côté commerçant',
    'PBX_PORTEUR': 'Adresse E - mail de l’acheteur',
    'PBX_RETOUR': 'Liste des variables à retourner par Paybox',
    'PBX_HASH': 'Type d’algorit hme de hachage pour le calcul de l’empreinte',
    'PBX_TIME': 'Horodatage de la transaction',
    'PBX_HMAC': 'Signature calculée avec la clé secrète',
}

ALGOS = {
    'SHA512': hashlib.sha512,
    'SHA256': hashlib.sha256,
    'SHA384': hashlib.sha384,
    'SHA224': hashlib.sha224,
}

def sign(data, key):
    '''Take a list of tuple key, value and sign it by building a string to
       sign.
    '''
    logger = logging.getLogger(__name__)
    algo = None
    logger.debug('signature key %r', key)
    logger.debug('signed data %r', data)
    for k, v in data:
        if k == 'PBX_HASH' and v in ALGOS:
            algo = ALGOS[v]
            break
    assert algo, 'Missing or invalid PBX_HASH'
    tosign = ['%s=%s' % (k, v) for k, v in data]
    tosign = '&'.join(tosign)
    print tosign
    logger.debug('signed string %r', tosign)
    signature = hmac.new(key, tosign, algo)
    return tuple(data) + (('PBX_HMAC', signature.hexdigest().upper()),)

if __name__ == '__main__':
    key = '0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF'.decode('hex')
    for k, v in sign([
                ['PBX_SITE', '1999888'],
                ['PBX_RANG', '32'],
                ['PBX_IDENTIFIANT', '110647233'],
                ['PBX_TOTAL', '999'], 
                ['PBX_DEVISE', '978'],
                ['PBX_CMD', 'TEST Paybox'],
                ['PBX_PORTEUR', 'test@paybox.com'],
                ['PBX_RETOUR', 'Mt:M;Ref:R;Auto:A;Erreur:E'],
                ['PBX_HASH', 'SHA512'],
                ['PBX_TIME', '2015-06-08T16:21:16+02:00']],
            key):
        print k, v
