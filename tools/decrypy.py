import sys
import hashlib
from Crypto.Cipher import AES

def decrypt_file(infile, key):
    """
    Entschlüsselt eine Datei, die mit AES-GCM verschlüsselt wurde.
    Es wird angenommen, dass die Datei wie folgt aufgebaut ist:
      - Nonce: erste 16 Byte
      - Tag: nächste 16 Byte
      - Ciphertext: Rest der Datei
    """
    with open(infile, "rb") as f:
        data = f.read()
    
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        print("Fehler bei der Entschlüsselung:", e)
        sys.exit(1)
    
    return plaintext

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python decrypt.py <encrypted_file> <plaintext_key> <output_file>")
        sys.exit(1)
    
    encrypted_file = sys.argv[1]
    plaintext_key = sys.argv[2]
    output_file = sys.argv[3]
    
    # Berechne den 32-Byte Schlüssel über SHA-256 aus dem eingegebenen Schlüssel (Klartext)
    key = hashlib.sha256(plaintext_key.encode()).digest()
    
    decrypted_data = decrypt_file(encrypted_file, key)
    
    # Schreibe den entschlüsselten Inhalt in die angegebene Ausgabedatei
    with open(output_file, "wb") as f:
        f.write(decrypted_data)
    
    print(f"Decrypted content written to {output_file}.")
