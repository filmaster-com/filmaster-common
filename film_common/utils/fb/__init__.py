import base64
import json
import hmac, hashlib

def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor 
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

def parse_signed_request(data, secret):
    data, secret = str(data), str(secret)
    sig, payload = data.split('.')
    sig = base64_url_decode(sig)

    data = json.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        logger.error('unknown signature algorithm: %r', data.get('algorithm'))
        return None
    expected_sig = hmac.new(secret, msg=payload,
                            digestmod=hashlib.sha256).digest()
    if expected_sig != sig:
        return None

    return data

