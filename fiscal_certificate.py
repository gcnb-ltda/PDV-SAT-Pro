from __future__ import annotations
import base64, hashlib, ssl, tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from lxml import etree
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12

DS = "http://www.w3.org/2000/09/xmldsig#"

class A1Certificate:
    def __init__(self, path: str, password: str):
        raw=Path(path).read_bytes()
        self.key, self.cert, self.chain=pkcs12.load_key_and_certificates(raw,password.encode())
        if not self.key or not self.cert: raise ValueError("Arquivo A1 não contém certificado e chave privada.")
        now=datetime.now(timezone.utc)
        start=getattr(self.cert,"not_valid_before_utc",self.cert.not_valid_before.replace(tzinfo=timezone.utc))
        end=getattr(self.cert,"not_valid_after_utc",self.cert.not_valid_after.replace(tzinfo=timezone.utc))
        if not start <= now <= end: raise ValueError("Certificado A1 vencido ou ainda não válido.")

    def sign_inf_nfe(self, root: etree._Element) -> etree._Element:
        targets=root.xpath(".//*[@Id]")
        inf=targets[0] if targets else (root if root.get("Id") else None)
        if inf is None: raise ValueError("XML sem elemento identificável por Id para assinatura.")
        sig=etree.Element(etree.QName(DS,"Signature"),nsmap={None:DS})
        signed=etree.SubElement(sig,etree.QName(DS,"SignedInfo"))
        etree.SubElement(signed,etree.QName(DS,"CanonicalizationMethod"),Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        etree.SubElement(signed,etree.QName(DS,"SignatureMethod"),Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256")
        ref=etree.SubElement(signed,etree.QName(DS,"Reference"),URI="#"+inf.get("Id"))
        transforms=etree.SubElement(ref,etree.QName(DS,"Transforms"))
        etree.SubElement(transforms,etree.QName(DS,"Transform"),Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature")
        etree.SubElement(transforms,etree.QName(DS,"Transform"),Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        etree.SubElement(ref,etree.QName(DS,"DigestMethod"),Algorithm="http://www.w3.org/2001/04/xmlenc#sha256")
        digest=hashlib.sha256(etree.tostring(inf,method="c14n",exclusive=False)).digest()
        etree.SubElement(ref,etree.QName(DS,"DigestValue")).text=base64.b64encode(digest).decode()
        signature=self.key.sign(etree.tostring(signed,method="c14n",exclusive=False),padding.PKCS1v15(),hashes.SHA256())
        etree.SubElement(sig,etree.QName(DS,"SignatureValue")).text=base64.b64encode(signature).decode()
        key_info=etree.SubElement(sig,etree.QName(DS,"KeyInfo")); x509=etree.SubElement(key_info,etree.QName(DS,"X509Data"))
        etree.SubElement(x509,etree.QName(DS,"X509Certificate")).text=base64.b64encode(self.cert.public_bytes(serialization.Encoding.DER)).decode()
        # NF-e assina como filha de NFe; eventos/inutilização assinam junto ao
        # elemento que contém a informação identificada.
        (root if root.tag.endswith("NFe") or root.tag.endswith("evento") or root.tag.endswith("inutNFe") else inf.getparent()).append(sig)
        return root

    @contextmanager
    def ssl_context(self):
        cert_pem=self.cert.public_bytes(serialization.Encoding.PEM)+b"".join(c.public_bytes(serialization.Encoding.PEM) for c in self.chain)
        key_pem=self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
        with tempfile.TemporaryDirectory(prefix="pdv-a1-") as folder:
            cp,kp=Path(folder)/"cert.pem",Path(folder)/"key.pem"; cp.write_bytes(cert_pem); kp.write_bytes(key_pem)
            ctx=ssl.create_default_context(); ctx.minimum_version=ssl.TLSVersion.TLSv1_2; ctx.load_cert_chain(cp,kp)
            yield ctx
