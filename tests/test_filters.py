from afrec.explorer import _ext_matches

def test_ext_matches():
    assert _ext_matches("/a/b/c.docx", [".docx", ".pdf"])
    assert not _ext_matches("/a/b/c.txt", [".docx", ".pdf"])
    assert _ext_matches("/a/b/c.TXT", ["txt"])
