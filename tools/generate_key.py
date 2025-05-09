from Crypto.Random import get_random_bytes
import binascii

def generate_random_aes_key(length=32):
    """
    Erzeugt einen zufälligen AES-Schlüssel der angegebenen Länge (Standard 32 Byte für AES-256)
    und gibt diesen im Hex‑Format aus.
    """
    key = get_random_bytes(length)
    print("Randomer AES-Schlüssel (Hex):", binascii.hexlify(key).decode())
    return key

if __name__ == "__main__":
    generate_random_aes_key()
