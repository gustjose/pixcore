import pytest
from src.pixcore.validate import validar_cpf, validar_cnpj, validar_chave_aleatoria, validar_email, validar_telefone

def test_validar_cpf_valido():
    assert validar_cpf("105.324.350-28") == True
    assert validar_cpf("10532435028") == True

def test_validar_cpf_invalido():
    assert validar_cpf("00000000000") == False

def test_validar_cnpj_valido():
    assert validar_cnpj("00.000.000/0001-91") == True
    assert validar_cnpj("00000000000191") == True

def test_validar_cnpj_invalido():
    assert validar_cnpj("00.000.000/0001-00") == False
    assert validar_cnpj("00000000000100") == False

def test_validar_chave_aleatoria_valida():
    assert validar_chave_aleatoria("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d") == True

def test_validar_chave_aleatoria_invalida():
    assert validar_chave_aleatoria("chave_invalida") == False

def test_validar_email_valido():
    assert validar_email("test@test.com") == True

def test_validar_email_invalido():
    assert validar_email("invalido.email") == False

def test_validar_telefone_valido():
    assert validar_telefone("+5511999999999") == True
    assert validar_telefone("+55 (11) 99999-9999") == True

def test_validar_telefone_invalido():
    assert validar_telefone("telefone_invalido") == False