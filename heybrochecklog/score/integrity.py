# Log Integrity Checker
# Glorified modification to make use of latest pprp and python 3.9 :)
# Source from https://github.com/puddly/eac_logsigner/blob/master/eac.py

import pprp


def eac_checksum(text):
    # Ignore newlines
    text = text.replace('\r', '').replace('\n', '')

    # Fuzzing reveals BOMs are also ignored
    text = text.replace('\ufeff', '').replace('\ufffe', '')

    # Setup Rijndael-256 with a 256-bit blocksize
    cipher = pprp.crypto.rijndael(
        # Probably SHA256('super secret password') but it doesn't actually matter
        key=bytes.fromhex('9378716cf13e4265ae55338e940b376184da389e50647726b35f6f341ee3efd9'),
        block_size=256 // 8
    )

    # Encode the text as UTF-16-LE
    plaintext = text.encode('utf-16-le')

    # The IV is all zeroes so we don't have to handle it
    signature = b'\x00' * 32

    # Process it block-by-block
    for i in range(0, len(plaintext), 32):
        # Zero-pad the last block, if necessary
        plaintext_block = plaintext[i:i + 32].ljust(32, b'\x00')

        # CBC mode (XOR the previous ciphertext block into the plaintext)
        cbc_plaintext = bytes((ord_or_int(a)) ^ (ord_or_int(b)) for a, b in zip(signature, plaintext_block))

        # New signature is the ciphertext.
        signature = cipher.encrypt(cbc_plaintext)

    # Textual signature is just the hex representation
    chunks = chunk_string((bytes(signature, "utf-16-le").hex().upper()), 4)
    chunk_result = list()
    for i in chunks:
        if i.endswith('00'):
            chunk_result.append(i[:-2])

    return str.join("", chunk_result)


def chunk_string(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def ord_or_int(data):
    if type(data) is int:
        return data

    return ord(data)


def extract_info(text):
    if '\r\n\r\n==== Log checksum' not in text:
        signature = None
    else:
        text, signature_parts = text.split('\r\n\r\n==== Log checksum', 1)
        signature = signature_parts.split()[0].strip()

    return text, signature


def eac_verify(text):
    # Strip off BOM
    if text.startswith('\ufeff'):
        text = text[1:]

    # Null bytes screw it up
    if '\x00' in text:
        text = text[:text.index('\x00')]

    unsigned_text, old_signature = extract_info(text)
    return old_signature, eac_checksum(unsigned_text)


def check_integrity(text):
    text = text.replace('\n', '\r\n')  # dunno
    old_signature, actual_signature = eac_verify(text)

    if old_signature is None:
        return "LOG_CHECKSUM_NOT_PRESENT"

    if old_signature == actual_signature:
        return "LOG_OK"

    return "LOG_NOT_OK"
