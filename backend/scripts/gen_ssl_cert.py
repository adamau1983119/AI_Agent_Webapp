"""
產生本機 HTTPS 自簽憑證（僅供開發／測試 Meta 連接用）。
若無 OpenSSL，可改用此腳本（需 pip install cryptography）。
執行一次即可，產生的檔案請勿提交到 Git。
"""
import sys
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent
certs_dir = backend_root / "certs"
certs_dir.mkdir(exist_ok=True)
key_path = certs_dir / "key.pem"
cert_path = certs_dir / "cert.pem"

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from datetime import datetime, timedelta
except ImportError:
    print("請先安裝: pip install cryptography")
    print("或使用 PowerShell 腳本: .\\scripts\\gen_ssl_cert.ps1（需系統有 OpenSSL，如 Git for Windows）")
    sys.exit(1)

def main():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(key, hashes.SHA256(), default_backend())
    )
    key_path.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print("完成。憑證位置：")
    print(f"  私鑰: {key_path}")
    print(f"  憑證: {cert_path}")
    print("\n啟動後端 HTTPS 範例（在 backend 目錄執行，請先關閉佔用 8000 的程式）：")
    print("  .\\scripts\\start_backend_https.ps1")

if __name__ == "__main__":
    main()
