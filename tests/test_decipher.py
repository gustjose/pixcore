import pytest
from src.pixcore.decipher import decode
from src.pixcore.models import PixData

@pytest.fixture
def pix_data_valida():
    """Fornece uma instância padrão de PixData para os testes."""
    return PixData(
        recebedor_nome="Empresa Completa LTDA",
        recebedor_cidade="SAO PAULO",
        pix_key="a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        valor=150.75,
        transacao_id="Pedido12345",
        recebedor_cep="01001000",
        info_adicional="Pagamento referente ao pedido 12345.",
        idioma_preferencia="en_US",
        recebedor_nome_alt="Complete Company LLC",
        recebedor_cidade_alt="SAO PAULO"
    )

@pytest.fixture
def pix_payload_valido():
    return "00020126580014BR.GOV.BCB.PIX0136a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d5204000053039865406150.755802BR5921Empresa Completa LTDA6009SAO PAULO61080100100062150511Pedido1234564460005en_US0120Complete Company LLC0209SAO PAULO63042BE4"

def test_decodificacao_sucesso(pix_payload_valido, pix_data_valida):
    result = decode(pix_payload_valido)

    assert result['pix_key'] == pix_data_valida.pix_key
    assert result['merchant_name'] == pix_data_valida.recebedor_nome
    assert result['merchant_city'] == pix_data_valida.recebedor_cidade
    assert result['transaction_amount'] == pix_data_valida.valor
    assert result['transaction_id'] == pix_data_valida.transacao_id
    assert result['postal_code'] == pix_data_valida.recebedor_cep
    assert result['language_preference'] == pix_data_valida.idioma_preferencia
    assert result['merchant_name_alt'] == pix_data_valida.recebedor_nome_alt
    assert result['merchant_city_alt'] == pix_data_valida.recebedor_cidade_alt
    assert result['merchant_category_code'] == '0000'
    assert result['country_code'] == 'BR'