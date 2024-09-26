# -*- coding: utf-8 -*-
import decimal
import socket
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
import base64
from datetime import date, datetime, timedelta
from dateutil import relativedelta


def get_ip():
    """ Used to get the server IP address
        Don't use it get the client IP address as it is not useful
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# #used for crypting
# SALT_KEY = b"b\xd9\xb2\xca#o\xc7\x04\x01z\x8f\xdc'\xf0\x86\xd6"
SALT_KEY = b'VOQaBG3UuxsVrM6wrHhjzHygieAUo8aeJncMZwsoRvQ='


def encrypt_msg(text):
    # print("encrypt_msg >>>>>>>>>>>>>>>>  ", SALT_KEY, text)
    fernet = Fernet(SALT_KEY)
    enc_text = fernet.encrypt(text.encode())
    return enc_text


def decrypt_msg(text):
    # print("decrypt_msg >>>>>>>>>>>>>>>> ", SALT_KEY, text)
    fernet = Fernet(SALT_KEY)
    dec_text = fernet.decrypt(text).decode()
    return dec_text


def encrypt_msg2(privateInfo):
    # 32 bytes = 256 bits
    # 16 = 128 bits
    # the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
    BLOCK_SIZE = 16
    # the character used for padding
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    PADDING = '{'

    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    # encrypt with AES, encode with base64
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    # generate a randomized secret key with urandom
    # secret      = os.urandom(BLOCK_SIZE)

    # creates the cipher obj using the key
    cipher = AES.new(SALT_KEY)
    # encodes you private info!
    encoded = EncodeAES(cipher, privateInfo)
    # print('Encrypted string:', encoded)

    return encoded


def decrypt_msg2(encryptedString):
    PADDING = '{'
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode('utf8').rstrip(PADDING)
    # Key is FROM the printout of 'secret' in encryption
    # below is the encryption.
    encryption = encryptedString
    # key         = ''
    cipher = AES.new(SALT_KEY)
    decoded = DecodeAES(cipher, encryption)
    # print(decoded)

    return decoded


def num_to_words(num):
    """
    return the word for given number
    :param num:
    :return:

    num_str = num_to_words(181200.65)
    print(f'Rupees {num_str} Paise only')
    """
    num = decimal.Decimal(num)
    decimal_part = num - int(num)
    num = int(num)

    if decimal_part:
        return num_to_words(num) + " and " + ("".join(num_to_words(str(round(decimal_part, 2))[2:]))) + ""

    under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven',
                'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    above_100 = {100: 'Hundred', 1000: 'Thousand', 100000: 'Lakh', 10000000: 'Crore'}

    if num < 20:
        return under_20[num]

    if num < 100:
        return tens[num // 10 - 2] + ('' if num % 10 == 0 else ' ' + under_20[num % 10])

    # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
    pivot = max([key for key in above_100.keys() if key <= num])

    return num_to_words(num // pivot) + ' ' + above_100[pivot] + (
        '' if num % pivot == 0 else ' ' + num_to_words(num % pivot))

# def get_previous_week_sunday_date():
#     today = date.today()
#     idx = (today.weekday() + 1) % 7
#     prvs_week_sunday_date = today - timedelta(7 + idx)
#     return prvs_week_sunday_date
