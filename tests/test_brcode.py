import pytest
from PIL import Image
from pathlib import Path

from src.pixcore.brcode import Pix
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

def test_geracao_payload_correto(pix_data_valida):
    """
    Testa se o payload gerado corresponde a um valor conhecido ("Golden Master").
    """
    br_code = Pix(pix_data_valida)
    payload_gerado = br_code.payload()

    payload_esperado = "00020126580014BR.GOV.BCB.PIX0136a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d5204000053039865406150.755802BR5921Empresa Completa LTDA6009SAO PAULO61080100100062150511Pedido1234564460005en_US0120Complete Company LLC0209SAO PAULO63042BE4"
    
    assert payload_gerado == payload_esperado

def test_gerar_qrcode_retorna_objeto_imagem(pix_data_valida):
    """Testa se o método gerar_qrcode, sem caminho, retorna um objeto de imagem."""
    br_code = Pix(pix_data_valida)
    
    imagem = br_code.qrcode()
    
    assert isinstance(imagem, Image.Image)

def test_gerar_qrcode_salva_arquivo(pix_data_valida, tmp_path: Path):
    """
    Testa se o método gerar_qrcode, com caminho, salva um arquivo.
    """
    br_code = Pix(pix_data_valida)
    
    caminho_saida = tmp_path / "test_pix.png"
    
    assert not caminho_saida.exists()

    br_code.save_qrcode(caminho_arquivo_saida=str(caminho_saida))
    
    assert caminho_saida.exists()
    assert caminho_saida.is_file()