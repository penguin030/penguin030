from pathlib import Path
import base64, hashlib
p=Path('asset-seeds/browseroneclick.webp.b64')
s=p.read_text().strip()
expected='3b5cf907621411ff566aa9cfff2d177461ab5ef5be195ed61e4b790da9134887'
if len(s)==10394:
    patch='DvPtHzaubzUFBd/Id59o+bVzeagoLv5CjOvW5Hri1XN5qCgucwYOA9+oB9HtgL+i0DWaTwqtXN5qCgu/jRqDb0LV8Cd69IiXfyHefaO6+Ni5kOA3cpG9qAsMEd7r/nSCm+TxDuMAdIKYcQjDDvPtHzaubz3fkO8+0fNrouEPJIoLv5'
    s=s[:1519]+patch+s[1519:]
assert hashlib.sha256(base64.b64decode(s)).hexdigest()==expected
p.write_text(s+'\n')
print('Browser screenshot transport verified against original SHA-256.')
