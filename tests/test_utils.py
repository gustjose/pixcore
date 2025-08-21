import pytest
from src.pixcore.utils import calculate_crc16, parse_tlv
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

def test_parse_tlv_sucesso(pix_payload_valido):
    """Verifica se o parse_tlv processa corretamente um payload complexo."""
    payload_sem_crc = pix_payload_valido[:-8]
    
    result = list(parse_tlv(payload_sem_crc))

    expected = [
        ('00', 2, '01'),
        ('26', 58, '0014BR.GOV.BCB.PIX0136a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d'),
        ('52', 4, '0000'),
        ('53', 3, '986'),
        ('54', 6, '150.75'),
        ('58', 2, 'BR'),
        ('59', 21, 'Empresa Completa LTDA'),
        ('60', 9, 'SAO PAULO'),
        ('61', 8, '01001000'),
        ('62', 15, '0511Pedido12345'),
        ('64', 46, '0005en_US0120Complete Company LLC0209SAO PAULO')
    ]
    
    assert result == expected