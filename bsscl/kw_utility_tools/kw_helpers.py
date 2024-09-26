# -*- coding: utf-8 -*-
import socket 
from Crypto.Cipher import AES
import base64

    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

##used for crypting
SALT_KEY    = b"b\xd9\xb2\xca#o\xc7\x04\x01z\x8f\xdc'\xf0\x86\xd6" #b'VOQaBG3UuxsVrM6wrHhjzHygieAUo8aeJncMZwsoRvQ='

def encrypt_msg(privateInfo):
    #32 bytes = 256 bits
    #16 = 128 bits
    # the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
    BLOCK_SIZE  = 16
    # the character used for padding
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING     = '{'
  
    pad         = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    # encrypt with AES, encode with base64
    EncodeAES   = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    # generate a randomized secret key with urandom
    # secret      = os.urandom(BLOCK_SIZE)
    
    # creates the cipher obj using the key
    cipher      = AES.new(SALT_KEY)
    # encodes you private info!
    encoded     = EncodeAES(cipher, privateInfo)
    # print('Encrypted string:', encoded)

    return encoded

def decrypt_msg(encryptedString):
    PADDING     = '{'
    DecodeAES   = lambda c, e: c.decrypt(base64.b64decode(e)).decode('utf8').rstrip(PADDING)
    #Key is FROM the printout of 'secret' in encryption
    #below is the encryption.
    encryption  = encryptedString
    # key         = ''
    cipher      = AES.new(SALT_KEY)
    decoded     = DecodeAES(cipher, encryption)
    # print(decoded)

    return decoded

