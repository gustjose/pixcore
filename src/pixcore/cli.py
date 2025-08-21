import typer
from typing import Optional
from . import brcode, models
from . import exceptions
from . import decipher
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pyfiglet
from importlib.metadata import version, PackageNotFoundError

console = Console()
app = typer.Typer(
    add_completion=False
)

try:
    __version__ = version("pixcore")
except PackageNotFoundError:
    __version__ = "dev"

def version_callback(value: bool):
    if value:
        console.print(f"PixCore CLI Versão: [cyan][b]{__version__}")
        raise typer.Exit()
    
def help_callback(value: bool):
    if not value:
        return

    table_comandos = Table(
        show_header=False, 
        header_style="bold magenta",
        padding=(0, 1),
        box=None
    )

    table_comandos.add_column("Comando / Opção", style="cyan", no_wrap=True, width=10)
    table_comandos.add_column("Descrição", width=75)

    # Seção de Comandos
    table_comandos.add_section()
    table_comandos.add_row(
        "payload",
        "Gera e exibe um [b]payload PIX[/] no formato TLV (Copia e Cola)."
    )
    table_comandos.add_row(
        "qrcode", 
        "Gera um [b]QR Code PIX[/] e o exibe no terminal ou salva em um arquivo."
    )
    table_comandos.add_row(
        "decode", 
        "Decodifica uma string PIX 'Copia e Cola' e exibe seus dados."
    )
    
    table_global = Table(
        show_header=False, 
        header_style="bold magenta",
        padding=(0, 1),
        box=None
    )

    table_global.add_column("Comando / Opção", style="cyan", no_wrap=True, width=10)
    table_global.add_column("Atalhos", style="green", width=15)
    table_global.add_column("Descrição", width=60)

    table_global.add_section()
    table_global.add_row(
        "--version", 
        "-v, --versao", 
        "Mostra a versão instalada do PixCore CLI."
    )
    table_global.add_row(
        "--help", 
        "-h", 
        "Mostra esta mensagem de ajuda detalhada."
    )

    f = pyfiglet.Figlet(
        font='starwars'
    )
    console.print(
        f.renderText('PixCore'),
        style="bold blue",
    )

    console.print("Uma ferramenta de linha de comando para gerar PIX de forma rápida e fácil.")
    console.print("Para mais informações, acesse: https://github.com/gustjose/pixcore\n")
    
    console.print(
        Panel(
            table_comandos,
            title="Comandos",
            expand=False,
            title_align='left',
        )
    )

    console.print(
        Panel(
            table_global,
            title="Opções Globais",
            expand=False,
            title_align='left',
        ))

    console.print("Para ajuda sobre um comando específico, use: [b][yellow]pixcore [NOME_DO_COMANDO] --help[/]\n")
    raise typer.Exit()

def panel(titulo, mensagem, color="red"):
    return Panel(
        renderable=mensagem,
        title=titulo,
        title_align='left',
        subtitle='PixCore',
        subtitle_align='left',
        border_style=color,
        padding=0,
        expand=False,
    )

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        "--versao",
        help="Mostra a versão do PixCore.",
        callback=version_callback,
        is_eager=True,
    ),
    help: Optional[bool] = typer.Option(
        None,
        "--help", "-h",
        callback=help_callback,
        is_eager=True,
        help="Mostra a mensagem de ajuda customizada.",
    )
):
    if ctx.invoked_subcommand is None:
        help_callback(True)

@app.command(
    help="Gera um payload PIX no formato TLV (Copia e Cola).",
)
def payload(
    key: str = typer.Option(..., "--key", "-k", help="Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória).", prompt=True),
    name: str = typer.Option(..., "--name", "-n", help="Nome do beneficiário.", prompt=True),
    city: str = typer.Option(..., "--city", "-c", help="Cidade do beneficiário (maiúsculas, sem acentos).", prompt=True),
    amount: Optional[float] = typer.Option(None, "--amount", "-a", help="Valor da transação. Ex: 10.50"),
    txid: str = typer.Option("***", "--txid", "-t", help="ID da transação (Transaction ID)."),
    info: Optional[str] = typer.Option(None, "--info", "-i", help="Informações adicionais para o pagador."),
    cep: Optional[str] = typer.Option(None, "--cep", help="CEP do beneficiário (formato XXXXXXXX)."),
    mcc: str = typer.Option("0000", "--mcc", help="Merchant Category Code (Código da Categoria do Comerciante)."),
    initiation_method: Optional[str] = typer.Option(None, "--initiation-method", help="Método de iniciação (ex: '11' para estático, '12' para dinâmico)."),
    language: Optional[str] = typer.Option(None, "--lang", help="Idioma de preferência para dados alternativos (ex: pt_BR, en_US)."),
    alt_name: Optional[str] = typer.Option(None, "--alt-name", help="Nome alternativo do beneficiário (em outro idioma)."),
    alt_city: Optional[str] = typer.Option(None, "--alt-city", help="Cidade alternativa do beneficiário (em outro idioma)."),
):
    try:
        data = models.PixData(
            recebedor_nome=name,
            recebedor_cidade=city,
            pix_key=key,
            valor=amount,
            transacao_id=txid,
            ponto_iniciacao_metodo=initiation_method,
            receptor_categoria_code=mcc,
            recebedor_cep=cep,
            info_adicional=info,
            idioma_preferencia=language,
            recebedor_nome_alt=alt_name,
            recebedor_cidade_alt=alt_city
        )
        
        transacao = brcode.Pix(data)
        payload_gerado = transacao.payload()
        
        console.print(payload_gerado)

    except exceptions.GeracaoPayloadError as e:
        console.print(panel("❌ Erro de Validação de Dados", f"Campo: [bold]{e.campo}[/bold]\nMotivo: {e.motivo}"))
        raise typer.Exit(code=1)

    except exceptions.ChavePixInvalidaError as e:
        console.print(panel("❌ Chave PIX Inválida", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ProcessamentoImagemError as e:
        console.print(panel("❌ Erro de Imagem", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ErroDeESError as e:
        console.print(panel("❌ Erro ao Salvar Arquivo", f"{e}\nVerifique o caminho e as permissões."))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(panel("❌ Ocorreu um erro inesperado", f"{e}"))
        raise typer.Exit(code=1)

@app.command(
    help="Gera um QR Code PIX.",
)
def qrcode(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Caminho e nome do arquivo de saída (ex: 'output/pix.png')."),
    key: str = typer.Option(..., "--key", "-k", help="Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória).", prompt=True),
    name: str = typer.Option(..., "--name", "-n", help="Nome do beneficiário.", prompt=True),
    city: str = typer.Option(..., "--city", "-c", help="Cidade do beneficiário (maiúsculas, sem acentos).", prompt=True),
    amount: Optional[float] = typer.Option(None, "--amount", "-a", help="Valor da transação. Ex: 10.50"),
    txid: str = typer.Option("***", "--txid", "-t", help="ID da transação (Transaction ID)."),
    info: Optional[str] = typer.Option(None, "--info", "-i", help="Informações adicionais para o pagador."),
    cep: Optional[str] = typer.Option(None, "--cep", help="CEP do beneficiário (formato XXXXXXXX)."),
    mcc: str = typer.Option("0000", "--mcc", help="Merchant Category Code (Código da Categoria do Comerciante)."),
    initiation_method: Optional[str] = typer.Option(None, "--initiation-method", help="Método de iniciação (ex: '11' para estático, '12' para dinâmico)."),
    language: Optional[str] = typer.Option(None, "--lang", help="Idioma de preferência para dados alternativos (ex: pt_BR, en_US)."),
    alt_name: Optional[str] = typer.Option(None, "--alt-name", help="Nome alternativo do beneficiário (em outro idioma)."),
    alt_city: Optional[str] = typer.Option(None, "--alt-city", help="Cidade alternativa do beneficiário (em outro idioma)."),
    caminho_logo: Optional[str] = typer.Option(None, "--logo", "-l", help="Caminho para um arquivo de imagem (ex: pasta/logo.png)")
):
    try:
        data = models.PixData(
            recebedor_nome=name,
            recebedor_cidade=city,
            pix_key=key,
            valor=amount,
            transacao_id=txid,
            ponto_iniciacao_metodo=initiation_method,
            receptor_categoria_code=mcc,
            recebedor_cep=cep,
            info_adicional=info,
            idioma_preferencia=language,
            recebedor_nome_alt=alt_name,
            recebedor_cidade_alt=alt_city
        )
        
        transacao = brcode.Pix(data)
        if output:
            if transacao.save_qrcode(caminho_arquivo_saida=output):
                console.print(panel("✅ QR Code gerado com sucesso", f"QR Code salvo em: {output}", "green"))
        else:
            imagem_pillow = transacao.qrcode(
                caminho_logo=caminho_logo, 
                cor_qr="black", 
                cor_fundo="white",
                box_size=10,
                border=4
            )
            imagem_pillow.show()

    except exceptions.GeracaoPayloadError as e:
        console.print(panel("❌ Erro de Validação de Dados", f"Campo: [bold]{e.campo}[/bold]\nMotivo: {e.motivo}"))
        raise typer.Exit(code=1)

    except exceptions.ChavePixInvalidaError as e:
        console.print(panel("❌ Chave PIX Inválida", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ProcessamentoImagemError as e:
        console.print(panel("❌ Erro de Imagem", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ErroDeESError as e:
        console.print(panel("❌ Erro ao Salvar Arquivo", f"{e}\nVerifique o caminho e as permissões."))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(panel("❌ Ocorreu um erro inesperado", f"{e}"))
        raise typer.Exit(code=1)
    
@app.command(
    help="Decodifica uma string PIX 'Copia e Cola' e exibe seus dados."
)
def decode(
    payload: str = typer.Argument(..., help="A string do payload BR Code a ser decodificada.")
):
    
    try:
        dados_decodificados = decipher.decode(payload)
        
        tabela_resultados = Table(title="Dados do PIX", show_header=False)
        tabela_resultados.add_column("Campo", style="cyan", no_wrap=True)
        tabela_resultados.add_column("Valor", style="green")

        mapa_nomes = {
            "merchant_name": "Nome do Recebedor",
            "merchant_city": "Cidade do Recebedor",
            "pix_key": "Chave PIX",
            "transaction_amount": "Valor",
            "transaction_id": "ID da Transação (TXID)",
            "merchant_category_code": "Cód. Categoria (MCC)",
            "postal_code": "CEP",
            "country_code": "País",
            "gui": "GUI",
        }

        for chave, nome_amigavel in mapa_nomes.items():
            if chave in dados_decodificados:
                valor = dados_decodificados[chave]
                
                if chave == "transaction_amount":
                    valor_str = f"R$ {valor:.2f}"
                else:
                    valor_str = str(valor)
                    
                tabela_resultados.add_row(nome_amigavel, valor_str)
        
        console.print(tabela_resultados)

    except exceptions.CRCInvalidoError as e:
        console.print(panel("❌ CRC Inválido", f"{e}\nO código pode estar corrompido ou foi alterado."))
        raise typer.Exit(code=1)
    
    except exceptions.DecodificacaoPayloadError as e:
        console.print(panel("❌ Erro de Decodificação", f"{e}\nA string fornecida não parece ser um PIX Copia e Cola válido."))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(panel("❌ Ocorreu um erro inesperado", f"{e}"))
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()