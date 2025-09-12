from pathlib import Path
from afrec.integrity import hash_file

def test_hashing(tmp_path: Path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"hello world\n")
    assert hash_file(p, "sha256")
    assert hash_file(p, "md5")
