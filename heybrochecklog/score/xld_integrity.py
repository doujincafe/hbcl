# Source from https://github.com/OPSnet/xld_logchecker.py/blob/master/xld_logchecker.py

import base64


def rotate_left(n, k):
    return ((n << k) & 0xFFFFFFFF) | (n >> (32 - k))


def rotate_right(n, k):
    return rotate_left(n, 32 - k)


def sha256(data, initial_state):
    # Non-standard initial state
    state = initial_state

    # Standard round constants
    round_constants = (
        0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5, 0xD807AA98,
        0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174, 0xE49B69C1, 0xEFBE4786,
        0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA, 0x983E5152, 0xA831C66D, 0xB00327C8,
        0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967, 0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
        0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85, 0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819,
        0xD6990624, 0xF40E3585, 0x106AA070, 0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A,
        0x5B9CCA4F, 0x682E6FF3, 0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7,
        0xC67178F2)

    # Pad the data with a single 1 bit, enough zeroes, and the original message bit length
    L = 8 * len(data)
    K = next(i for i in range(0, 512) if (L + 1 + i + 64) % 512 == 0)

    data += b'\x80' + (b'\x00' * ((K - 7) // 8)) + L.to_bytes(8, 'big')

    for start in range(0, len(data), 64):
        # Process chunks of 64 bytes
        chunk = data[start:start + 64]
        round_state = 4 * [int.from_bytes(chunk[i:i + 4], 'big') for i in range(0, len(chunk), 4)]

        for i in range(16, 64):
            s0 = rotate_right(round_state[i - 15], 7) ^ rotate_right(round_state[i - 15], 18) ^ (
                    round_state[i - 15] >> 3)
            s1 = rotate_right(round_state[i - 2], 17) ^ rotate_right(round_state[i - 2], 19) ^ (
                    round_state[i - 2] >> 10)

            round_state[i] = (round_state[i - 16] + s0 + round_state[i - 7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, h = state

        for i in range(64):
            s0 = rotate_right(a, 2) ^ rotate_right(a, 13) ^ rotate_right(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = s0 + maj

            s1 = rotate_right(e, 6) ^ rotate_right(e, 11) ^ rotate_right(e, 25)
            ch = (e & f) ^ ((~e) & g)
            t1 = h + s1 + ch + round_constants[i] + round_state[i]

            h = g
            g = f
            f = e
            e = (d + t1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (t1 + t2) & 0xFFFFFFFF

        state = [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]

    return b''.join([i.to_bytes(4, 'big') for i in state[:8]]).hex()


def scramble(data):
    MAGIC_CONSTANTS = [0x99036946, 0xE99DB8E7, 0xE3AE2FA7, 0xA339740, 0xF06EB6A9, 0x92FF9B65, 0x28F7873, 0x9070E316]

    # Split off the unaligned part
    unaligned_chunk = b''

    if len(data) % 8 != 0:
        stop = 8 * (len(data) // 8)

        unaligned_chunk = data[stop:]
        data = data[:stop] + b'\x00' * 8

    output = []

    # Magic initial state
    X = 0x6479B873
    Y = 0x48853AFC

    for offset in range(0, len(data), 8):
        # Read off two 32-bit integers
        X ^= int.from_bytes(data[offset:offset + 4], 'big')
        Y ^= int.from_bytes(data[offset + 4:offset + 8], 'big')

        # Scramble them around
        for _ in range(4):
            for i in range(2):
                Y ^= X

                a = (MAGIC_CONSTANTS[4 * i + 0] + Y) & 0xFFFFFFFF
                b = (a - 1 + rotate_left(a, 1)) & 0xFFFFFFFF

                X ^= b ^ rotate_left(b, 4)

                c = (MAGIC_CONSTANTS[4 * i + 1] + X) & 0xFFFFFFFF
                d = (c + 1 + rotate_left(c, 2)) & 0xFFFFFFFF

                e = (MAGIC_CONSTANTS[4 * i + 2] + (d ^ rotate_left(d, 8))) & 0xFFFFFFFF
                f = (rotate_left(e, 1) - e) & 0xFFFFFFFF

                Y ^= (X | f) ^ rotate_left(f, 16)

                g = (MAGIC_CONSTANTS[4 * i + 3] + Y) & 0xFFFFFFFF
                X ^= (g + 1 + rotate_left(g, 2)) & 0xFFFFFFFF

        output.append(X.to_bytes(4, 'big') + Y.to_bytes(4, 'big'))

    # Handle the unaligned last chunk differently
    if unaligned_chunk:
        last_scramble = output.pop()

        # Implicitly truncates to the actual length of the data
        output.append(bytearray(a ^ b for a, b in zip(last_scramble, unaligned_chunk)))

    return b''.join(output)


def nonstandard_base64_encode(data, alphabet):
    # Non-standard base64 alphabet
    mapping = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/', alphabet)

    return base64.b64encode(data).decode('ascii').translate(mapping)


def extract_info(data):
    version = data.splitlines()[0]

    if not version.startswith('X Lossless Decoder version'):
        version = None
    else:
        version = version.split()[4]

    if '\n-----BEGIN XLD SIGNATURE-----\n' not in data:
        signature = None
    else:
        data, signature_parts = data.split('\n-----BEGIN XLD SIGNATURE-----\n', 1)
        signature = signature_parts.split('\n-----END XLD SIGNATURE-----\n')[0].strip()

    return data, version, signature


def xld_verify(data):
    data, version, old_signature = extract_info(data)

    INITIAL_STATE = (0x1D95E3A4, 0x06520EF5, 0x3A9CFB75, 0x6104BCAE, 0x09CEDA82, 0xBA55E60B, 0xEAEC16C6, 0xEB19AF15)

    # SHA256 with a different initial state
    checksum = sha256(data.encode('utf-8'), INITIAL_STATE).encode('ascii')

    # A fixed version string is appended to the hex digest of the log text
    scrambled = scramble(checksum + b'\nVersion=0001')

    # No padding bytes
    signature = nonstandard_base64_encode(scrambled, '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._').rstrip('=')

    return data, version, old_signature, signature

