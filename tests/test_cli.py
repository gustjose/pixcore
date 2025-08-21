import pytest
from typer.testing import CliRunner
from src.pixcore.cli import app
from pathlib import Path

runner = CliRunner()

@pytest.fixture
def pix_args():
    """Fornece uma lista com os argumentos de dados do Pix para os testes de CLI."""
    return [
        "--key", "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "--name", "Empresa de Exemplo S.A.",
        "--city", "SAO PAULO",
        "--amount", "123.45",
        "--txid", "TXID",
        "--info", "Pagamento referente ao pedido 12345.",
        "--cep", "01001000",
        "--mcc", "5411",
        "--initiation-method", "12",
        "--lang", "pt_BR",
        "--alt-name", "Example Company Inc.",
        "--alt-city", "SAO PAULO",
    ]

def test_cli_payload_sucesso(pix_args):
    """
    Verifica se o comando 'payload' gera a string correta do BR Code
    com todos os argumentos fornecidos.
    """
    args = ["payload", *pix_args]
    result = runner.invoke(app, args)
    
    assert result.exit_code == 0
    assert result.stdout.replace('\n','') == '00020101021226580014BR.GOV.BCB.PIX0136a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d5204541153039865406123.455802BR5923Empresa de Exemplo S.A.6009SAO PAULO61080100100062080504TXID64460005pt_BR0120Example Company Inc.0209SAO PAULO63047EB4'

def test_cli_qrcode_sucesso_salva_arquivo(tmp_path: Path, pix_args):
    """
    Verifica se o comando 'qrcode' cria e salva com sucesso
    um arquivo de imagem no caminho especificado.
    """
    arquivo_saida = tmp_path / "test_pix.png"
    
    args = ["qrcode", *pix_args, "--output", str(arquivo_saida)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert arquivo_saida.exists()
    assert arquivo_saida.is_file()

def test_cli_decode_sucesso(pix_args):
    args = ["decode", "00020126580014BR.GOV.BCB.PIX0136a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d5204000053039865406150.755802BR5921Empresa Completa LTDA6009SAO PAULO61080100100062150511Pedido1234564460005en_US0120Complete Company LLC0209SAO PAULO63042BE4"]
    result = runner.invoke(app, args)
    
    assert result.exit_code == 0
    assert "Empresa Completa LTDA" in result.stdout
    assert "SAO PAULO" in result.stdout
    assert "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d" in result.stdout
    assert "150.75" in result.stdout
    assert "Pedido12345" in result.stdout
    assert "0000" in result.stdout
    assert "01001000" in result.stdout
    assert "BR" in result.stdout
    assert "BR.GOV.BCB.PIX" in result.stdout