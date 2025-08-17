import typer
from typing import Optional
from . import brcode, models
from . import exceptions
from rich.console import Console
from rich.panel import Panel
from rich_pixels import Pixels

console = Console()
app = typer.Typer(
    help="CLI para gerar payloads e QR Codes PIX com a biblioteca Pixcore."
)

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

@app.command()
def payload(
    key: str = typer.Option(..., "--key", "-k", help="Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória)."),
    name: str = typer.Option(..., "--name", "-n", help="Nome do beneficiário."),
    city: str = typer.Option(..., "--city", "-c", help="Cidade do beneficiário (maiúsculas, sem acentos)."),
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

    except exceptions.ErroGeracaoPayloadError as e:
        console.print(panel("❌ Erro de Validação de Dados", f"Campo: [bold]{e.campo}[/bold]\nMotivo: {e.motivo}"))
        raise typer.Exit(code=1)

    except exceptions.ChavePixInvalidaError as e:
        console.print(panel("❌ Chave PIX Inválida", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ErroProcessamentoImagemError as e:
        console.print(panel("❌ Erro de Imagem", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ErroDeESError as e:
        console.print(panel("❌ Erro ao Salvar Arquivo", f"{e}\nVerifique o caminho e as permissões."))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(panel("❌ Ocorreu um erro inesperado", f"{e}"))
        raise typer.Exit(code=1)

@app.command()
def qrcode(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Caminho e nome do arquivo de saída (ex: 'output/pix.png')."),
    key: str = typer.Option(..., "--key", "-k", help="Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória)."),
    name: str = typer.Option(..., "--name", "-n", help="Nome do beneficiário."),
    city: str = typer.Option(..., "--city", "-c", help="Cidade do beneficiário (maiúsculas, sem acentos)."),
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
        if output:
            if transacao.save_qrcode(caminho_arquivo_saida=output):
                console.print(panel("✅ QR Code gerado com sucesso", f"QR Code salvo em: {output}", "green"))
        else:
            imagem_pillow = transacao.qrcode()
            pixels = Pixels.from_image(imagem_pillow)
            
            console.print(
                Panel(
                    pixels,
                    title="[bold green]Escaneie o QR Code PIX[/bold green]",
                    border_style="green",
                    padding=0,
                    expand=False
                )
            )

    except exceptions.ErroGeracaoPayloadError as e:
        console.print(panel("❌ Erro de Validação de Dados", f"Campo: [bold]{e.campo}[/bold]\nMotivo: {e.motivo}"))
        raise typer.Exit(code=1)

    except exceptions.ChavePixInvalidaError as e:
        console.print(panel("❌ Chave PIX Inválida", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ErroProcessamentoImagemError as e:
        console.print(panel("❌ Erro de Imagem", f"{e}"))
        raise typer.Exit(code=1)

    except exceptions.ErroDeESError as e:
        console.print(panel("❌ Erro ao Salvar Arquivo", f"{e}\nVerifique o caminho e as permissões."))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(panel("❌ Ocorreu um erro inesperado", f"{e}"))
        raise typer.Exit(code=1)
    
if __name__ == "__main__":
    app()