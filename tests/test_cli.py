import pytest
import csv
from typer.testing import CliRunner
from src.pixcore.cli import app
from pathlib import Path
import configparser

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

@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch):
    """
    Fixture que isola o ambiente de configuração.

    Usa monkeypatch para redirecionar o typer.get_app_dir para um
    diretório temporário, garantindo que os testes não afetem a
    configuração real do usuário.
    """
    temp_config_file = tmp_path / "config.ini"
    try:
        monkeypatch.setattr("src.pixcore.config_manager.CONFIG_FILE", temp_config_file)
    except AttributeError:
        pytest.fail(
            "Não foi possível aplicar o patch em 'src.pixcore.config_manager.CONFIG_FILE'. "
            "Verifique se o caminho do módulo e o nome da variável estão corretos."
        )

    return temp_config_file

@pytest.fixture
def csv_valido(tmp_path: Path):
    """Cria um arquivo CSV válido para os testes de lote."""
    csv_path = tmp_path / "cobrancas.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["valor", "txid", "nome", "cidade", "chave"])
        writer.writerow(["10.50", "TXID001", "CLIENTE A", "SAO PAULO", "chave1@pix.com"])
        writer.writerow(["25.00", "TXID002", "CLIENTE B", "RIO DE JANEIRO", "chave2@pix.com"])
    return csv_path

@pytest.fixture
def csv_com_erros(tmp_path: Path):
    """Cria um CSV com uma linha válida e uma com valor inválido."""
    csv_path = tmp_path / "cobrancas_erradas.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["valor", "txid", "nome", "cidade", "chave"])
        writer.writerow(["15.75", "TXIDVALIDO", "CLIENTE OK", "RECIFE", "chave_ok@pix.com"])
        writer.writerow(["abc", "TXIDINVALIDO", "CLIENTE RUIM", "SALVADOR", "chave_ruim@pix.com"])
        writer.writerow(["50.00", "TXIDVALIDO2", "CLIENTE OK 2", "MANAUS", "chave_ok2@pix.com"])
    return csv_path

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

# ==============================================================================
# Testes para o subcomando 'config'
# ==============================================================================

def test_config_set_sucesso(isolated_config):
    """
    Verifica se o comando 'config set' salva corretamente uma configuração.
    """
    config_file = isolated_config
    
    result = runner.invoke(app, ["config", "set", "name", "Meu Nome Salvo"])
    
    assert result.exit_code == 0
    assert "Configuração 'name' salva como 'Meu Nome Salvo'" in result.stdout
    
    assert config_file.exists()
    
    parser = configparser.ConfigParser()
    parser.read(config_file)
    assert parser.get('default', 'name') == 'Meu Nome Salvo'

def test_config_show_sucesso(isolated_config):
    """
    Verifica se o comando 'config show' exibe as configurações salvas.
    """
    runner.invoke(app, ["config", "set", "name", "Usuario Teste"])
    runner.invoke(app, ["config", "set", "city", "CIDADE TESTE"])
    
    result = runner.invoke(app, ["config", "show"])
    
    assert result.exit_code == 0
    assert "Configurações Salvas" in result.stdout
    assert "Usuario Teste" in result.stdout
    assert "CIDADE TESTE" in result.stdout

def test_config_set_chave_invalida(isolated_config):
    """
    Verifica se o comando 'config set' falha ao tentar usar uma chave inválida.
    """
    result = runner.invoke(app, ["config", "set", "chave_invalida", "valor"])
    
    assert result.exit_code == 1
    assert "Chave 'chave_invalida' inválida" in result.stdout

def test_config_show_sem_configuracao(isolated_config):
    """
    Verifica a saída do comando 'config show' quando não há configurações salvas.
    """
    result = runner.invoke(app, ["config", "show"])
    
    assert result.exit_code == 0
    assert "Nenhuma configuração salva encontrada" in result.stdout

def test_lote_sucesso(csv_valido, tmp_path: Path):
    """
    Verifica se o comando 'lote' gera todos os QR Codes de um CSV válido.
    """
    output_dir = tmp_path / "qrcodes"
    
    result = runner.invoke(app, ["lote", str(csv_valido), str(output_dir)])
    
    assert result.exit_code == 0
    assert "Geração em lote concluída" in result.stdout
    assert (output_dir / "TXID001.png").exists()
    assert (output_dir / "TXID002.png").exists()
    arquivos_gerados = list(output_dir.glob("*.png"))
    assert len(arquivos_gerados) == 2

def test_lote_cria_diretorio_saida(csv_valido, tmp_path: Path):
    """
    Verifica se o comando 'lote' cria o diretório de saída se ele não existir.
    """
    output_dir = tmp_path / "novo_diretorio"
    assert not output_dir.exists()
    
    result = runner.invoke(app, ["lote", str(csv_valido), str(output_dir)])
    
    assert result.exit_code == 0
    assert output_dir.exists()
    assert output_dir.is_dir()

def test_lote_arquivo_csv_nao_encontrado(tmp_path: Path):
    """
    Verifica se o comando falha com uma mensagem clara se o CSV não for encontrado.
    """
    output_dir = tmp_path / "qrcodes"
    arquivo_inexistente = "nao_existe.csv"
    
    result = runner.invoke(app, ["lote", arquivo_inexistente, str(output_dir)])
    
    assert result.exit_code == 1
    assert "Arquivo não encontrado" in result.stdout
    assert arquivo_inexistente in result.stdout

def test_lote_pula_linha_com_valor_invalido(csv_com_erros, tmp_path: Path):
    """
    Verifica se o comando ignora linhas com dados inválidos e continua o processo.
    """
    output_dir = tmp_path / "qrcodes_erros"
    
    result = runner.invoke(app, ["lote", str(csv_com_erros), str(output_dir)])
    
    assert result.exit_code == 0
    assert "Geração em lote concluída" in result.stdout
    
    assert "Valor 'abc' é inválido" in result.stdout
    
    assert (output_dir / "TXIDVALIDO.png").exists()
    assert (output_dir / "TXIDVALIDO2.png").exists()
    
    assert not (output_dir / "TXIDINVALIDO.png").exists()

    arquivos_gerados = list(output_dir.glob("*.png"))
    assert len(arquivos_gerados) == 2

def test_lote_fallback_para_config(tmp_path: Path, isolated_config):
    """
    Verifica se o 'lote' usa valores da configuração quando faltam no CSV.
    """
    runner.invoke(app, ["config", "set", "name", "Nome Padrao Global"])
    runner.invoke(app, ["config", "set", "city", "CIDADE PADRAO"])
    runner.invoke(app, ["config", "set", "key", "chave@padrao.com"])

    csv_path = tmp_path / "cobrancas_minimas.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["valor", "txid"])
        writer.writerow(["99.99", "TXIDMINIMO"])

    output_dir = tmp_path / "qrcodes_config"
    
    result = runner.invoke(app, ["lote", str(csv_path), str(output_dir)])
    
    assert result.exit_code == 0, result.stdout
    assert "Geração em lote concluída" in result.stdout
    assert (output_dir / "TXIDMINIMO.png").exists()