""" Verifica que el filtro por extensión (_ext_matches) funciona correctamente.
Comprueba que:
.docx y .pdf coincidan,
.txt no coincida,
comparación insensible a mayúsculas/minúsculas. 
Asegura que el inventario filtra bien los tipos de archivo."""

from afrec.explorer import _ext_matches

def test_ext_matches():
    assert _ext_matches("/a/b/c.docx", [".docx", ".pdf"])
    assert not _ext_matches("/a/b/c.txt", [".docx", ".pdf"])
    assert _ext_matches("/a/b/c.TXT", ["txt"])
