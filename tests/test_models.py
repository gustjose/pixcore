import pytest
from src.pixcore.models import PixData

def test_criacao_com_dados_obrigatorios_e_validos():
    """
    Testa a criação de uma instância de PixData com todos os dados obrigatórios e válidos.
    """
    try:
        instance = PixData(
            recebedor_nome="Nome do Recebedor",
            recebedor_cidade="Cidade",
            pix_key="chave_pix_valida@email.com",
            valor=10.50,
            transacao_id="ID12345",
            recebedor_cep="12345678"
        )
        assert instance.recebedor_nome == "Nome do Recebedor"
        assert instance.recebedor_cidade == "Cidade"
        assert instance.pix_key == "chave_pix_valida@email.com"
        assert instance.valor == 10.50
        assert instance.transacao_id == "ID12345"
        assert instance.recebedor_cep == "12345678"
    except ValueError:
        pytest.fail("A criação da instância de PixData falhou inesperadamente com dados válidos.")

def test_transacao_id_com_valor_padrao():
    """
    Testa se a instância pode ser criada com o valor padrão "***" para transacao_id.
    """
    instance = PixData(
        recebedor_nome="Recebedor",
        recebedor_cidade="Cidade",
        pix_key="chave_pix_valida@email.com"
    )
    assert instance.transacao_id == "***"