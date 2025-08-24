import typer
import os
import csv
from typing import Optional
from . import brcode, models
from . import exceptions
from . import decipher
from . import config_manager
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
    """Exibe a versão do programa e encerra."""
    if value:
        console.print(f"PixCore CLI Versão: [cyan][b]{__version__}")
        raise typer.Exit()
    
def help_callback(value: bool):
    """Exibe a tela de ajuda customizada e encerra."""
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
    table_comandos.add_row(
        "lote", 
        "Gera múltiplos QR Codes PIX a partir de um arquivo CSV."
    )
    table_comandos.add_row(
        "config", 
        "Gerencia as configurações padrão da aplicação."
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
    """Cria um painel formatado para exibição de mensagens."""
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
    key: str = typer.Option(None, "--key", "-k", help="Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória)."),
    name: str = typer.Option(None, "--name", "-n", help="Nome do beneficiário."),
    city: str = typer.Option(None, "--city", "-c", help="Cidade do beneficiário (maiúsculas, sem acentos)."),
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
    """
    Gera e exibe o payload PIX no formato 'Copia e Cola' (BR Code TLV).

    Este comando monta a string de pagamento completa, que pode ser copiada e colada
    em um aplicativo de banco para efetuar o pagamento. É a base para a geração
    do QR Code.

    Se os dados essenciais (chave, nome, cidade) não forem fornecidos através das
    opções ou de um arquivo de configuração, o comando solicitará interativamente
    que sejam digitados.

    Exemplos de uso:

    - Gerar um payload com valor definido:
        $ pixcore payload --key "seu-email@exemplo.com" --name "Nome Completo" --city "SAO PAULO" --amount 19.99

    - Gerar um payload com valor aberto (a ser digitado pelo pagador):
        $ pixcore payload -k "12345678900" -n "Nome Completo" -c "SAO PAULO" --txid "PEDIDO123"
    """
    try:
        config = config_manager.read_config()
        
        final_key = key or config.get('default', 'key', fallback=None)
        if not final_key:
            final_key = typer.prompt("Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória)")
        
        final_name = name or config.get('default', 'name', fallback=None)
        if not final_name:
            final_name = typer.prompt("Nome do beneficiário")

        final_city = city or config.get('default', 'city', fallback=None)
        if not final_city:
            final_city = typer.prompt("Cidade do beneficiário (maiúsculas, sem acentos)")

        data = models.PixData(
            recebedor_nome=final_name,
            recebedor_cidade=final_city,
            pix_key=final_key,
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
    key: str = typer.Option(None, "--key", "-k", help="Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória)."),
    name: str = typer.Option(None, "--name", "-n", help="Nome do beneficiário."),
    city: str = typer.Option(None, "--city", "-c", help="Cidade do beneficiário (maiúsculas, sem acentos)."),
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
    """
    Gera um QR Code PIX, salvando em arquivo ou exibindo na tela.

    Este comando cria a imagem do QR Code a partir dos dados fornecidos. Possui dois
    modos de operação:

    1.  Padrão: Se a opção '--output' não for usada, a imagem do QR Code será
        aberta no visualizador de imagens padrão do seu sistema operacional.

    2.  Salvar em arquivo: Ao usar a opção '--output', a imagem é salva no
        caminho especificado. O formato é inferido pela extensão do arquivo (ex: .png).

    É possível customizar o QR Code, por exemplo, adicionando um logo no centro.

    Exemplos de uso:

    - Gerar e exibir um QR Code simples na tela:
        $ pixcore qrcode -k "chave-pix" -n "Nome" -c "CIDADE" -a 50.00

    - Salvar um QR Code com logo em um arquivo específico:
        $ pixcore qrcode -k "chave-pix" -n "Nome" -c "CIDADE" -a 123.45 --logo "logo.png" --output "pix_pagamento.png"
    """
    try:
        config = config_manager.read_config()

        final_key = key or config.get('default', 'key', fallback=None)
        if not final_key:
            final_key = typer.prompt("Chave PIX (CPF/CNPJ, e-mail, celular ou aleatória)")

        final_name = name or config.get('default', 'name', fallback=None)
        if not final_name:
            final_name = typer.prompt("Nome do beneficiário")

        final_city = city or config.get('default', 'city', fallback=None)
        if not final_city:
            final_city = typer.prompt("Cidade do beneficiário (maiúsculas, sem acentos)")

        data = models.PixData(
            recebedor_nome=final_name,
            recebedor_cidade=final_city,
            pix_key=final_key,
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
            output_dir = os.path.dirname(output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            if transacao.save_qrcode(caminho_arquivo_saida=output, caminho_logo=caminho_logo):
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
    """
    Decodifica um payload PIX ('Copia e Cola') e exibe seus dados de forma legível.

    Este comando é útil para verificar a integridade e o conteúdo de um código PIX.
    Ele recebe a string do payload, valida seu código de verificação (CRC16) e, se
    válido, extrai e exibe todas as informações em uma tabela organizada, como nome
    do recebedor, valor, chave e cidade.

    Exemplo de uso:

    - Decodificar um payload recebido:
        $ pixcore decode "00020126580014br.gov.bcb.pix0136..."
    """
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

@app.command(
    help="Gera múltiplos QR Codes PIX a partir de um arquivo CSV."
)
def lote(
    arquivo_csv: str = typer.Argument(..., help="Caminho para o arquivo CSV com os dados."),
    diretorio_saida: str = typer.Argument(..., help="Diretório onde os QR Codes serão salvos."),
    key: str = typer.Option(None, "--key", "-k", help="Chave PIX padrão (usada se não especificada no CSV)."),
    name: str = typer.Option(None, "--name", "-n", help="Nome do beneficiário padrão (usado se não especificado no CSV)."),
    city: str = typer.Option(None, "--city", "-c", help="Cidade padrão do beneficiário (usada se não especificada no CSV)."),
):
    """
    Processa um arquivo CSV para gerar múltiplos QR Codes PIX de uma só vez.

    Este comando é ideal para casos de uso que exigem a geração de cobranças em massa.
    Ele lê um arquivo CSV, onde cada linha representa um PIX a ser gerado, e salva
    os QR Codes resultantes em um diretório de saída.

    O arquivo CSV deve conter, no mínimo, as colunas: `valor` e `txid`.
    Outras colunas como `chave`, `nome`, `cidade`, `info_adicional`, `cep` e `mcc`
    podem ser incluídas para sobrescrever os valores padrão. Se `chave`, `nome` ou `cidade`
    não estiverem no CSV, serão usados os valores passados como opção ou do arquivo de configuração.

    Os arquivos de imagem gerados serão nomeados com o valor da coluna 'txid' de cada linha
    (ex: `[txid].png`).

    Exemplo de uso:

    - Gerar QR Codes a partir de 'cobrancas.csv' e salvar na pasta 'qrcodes/':
        $ pixcore lote "cobrancas.csv" "qrcodes/" --name "Minha Empresa" --city "RIO DE JANEIRO" --key "meu-cnpj"
    """
    try:
        config = config_manager.read_config()
        os.makedirs(diretorio_saida, exist_ok=True)

        with open(arquivo_csv, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            console.rule(f'Geração em Lote - [cyan]{arquivo_csv}', style='blue')
            console.print('')
            
            for i, row in enumerate(reader):
                linha_num = i + 2
                try:
                    final_key = row.get('chave') or key or config.get('default', 'key', fallback=None)
                    final_name = row.get('nome') or name or config.get('default', 'name', fallback=None)
                    final_city = row.get('cidade') or city or config.get('default', 'city', fallback=None)
                    
                    amount_str = row.get('valor')
                    txid = row.get('txid')

                    if not all([final_key, final_name, final_city, amount_str, txid]):
                        console.print(panel(f"⚠️ Linha {linha_num} Ignorada", "Dados essenciais (chave, nome, cidade, valor, txid) estão faltando."))
                        continue
                    
                    try:
                        amount = float(amount_str.replace(',', '.'))
                    except (ValueError, TypeError):
                        console.print(panel(f"⚠️ Linha {linha_num} Ignorada", f"Valor '[bold]{amount_str}[/]' é inválido."))
                        continue

                    info = row.get('info_adicional')
                    cep = row.get('cep')
                    mcc = row.get('mcc', '0000')

                    data = models.PixData(
                        recebedor_nome=final_name,
                        recebedor_cidade=final_city,
                        pix_key=final_key,
                        valor=amount,
                        transacao_id=txid,
                        receptor_categoria_code=mcc,
                        recebedor_cep=cep,
                        info_adicional=info,
                    )
                    
                    transacao = brcode.Pix(data)
                    nome_arquivo = f"{txid}.png"
                    caminho_arquivo = os.path.join(diretorio_saida, nome_arquivo)
                    
                    if transacao.save_qrcode(caminho_arquivo_saida=caminho_arquivo):
                        console.print(f"  ✅ [green]Sucesso:[/] QR Code para txid '[bold]{txid}[/]'")
                    
                except Exception as e:
                    console.print(panel(f"❌ Erro na Linha {linha_num}", f"Não foi possível gerar o QR Code para txid '[bold]{txid}[/]'.\nMotivo: {e}"))

        console.print('')
        console.print(panel("✅ Geração em lote concluída!", f"QR Codes salvos em: [cyan]{diretorio_saida}", "green"))

    except FileNotFoundError:
        console.print(panel("❌ Arquivo não encontrado", f"O arquivo [bold]{arquivo_csv}[/] não foi encontrado."))
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(panel("❌ Ocorreu um erro inesperado no processamento em lote", f"{e}"))
        raise typer.Exit(code=1)

# ==============================================================================
# App de Configurações
# ==============================================================================

config_app = typer.Typer(
    help="Gerencia as configurações padrão da aplicação.",
    add_completion=False
)
app.add_typer(config_app, name="config")

def help_callback_config(value: bool):
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
        "set",
        "Define um valor de configuração. Ex: 'pixcore config set name \"Meu Nome\"'"
    )
    table_comandos.add_row(
        "show",
        "Mostra todas as configurações salvas."
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
        "--help", 
        "-h", 
        "Mostra esta mensagem de ajuda detalhada."
    )
    
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

    console.print("Para ajuda sobre um comando específico, use: [b][yellow]pixcore config [NOME_DO_COMANDO] --help[/]\n")
    raise typer.Exit()

@config_app.callback(invoke_without_command=True)
def main_config_app(
    ctx: typer.Context,
    help: Optional[bool] = typer.Option(
        None,
        "--help", "-h",
        callback=help_callback_config,
        is_eager=True,
        help="Mostra a mensagem de ajuda customizada.",
    )
):
    if ctx.invoked_subcommand is None:
        help_callback_config(True)

@config_app.command("set", help="Define um valor de configuração. Ex: 'pixcore config set name \"Meu Nome\"'")
def config_set(
    key: str = typer.Argument(..., help="A chave de configuração (ex: name, city, key)."),
    value: str = typer.Argument(..., help="O valor a ser salvo."),
):
    """
    Define e salva um par chave/valor na configuração padrão da aplicação.

    Use este comando para salvar valores que você usa com frequência, como seu nome,
    cidade ou chave PIX principal. Uma vez salvas, essas configurações serão usadas
    como padrão em outros comandos, evitando que você precise digitá-las toda vez.

    As chaves de configuração válidas são: 'name', 'city' e 'key'.

    Exemplos de uso:

    - Salvar seu nome padrão:
        $ pixcore config set name "Meu Nome Completo"

    - Salvar sua chave PIX principal:
        $ pixcore config set key "minha-chave-aleatoria"
    """
    chaves_validas = ["name", "city", "key"]
    if key not in chaves_validas:
        console.print(Panel(f"❌ Chave '[bold red]{key}[/]' inválida. Use uma das seguintes: {chaves_validas}", expand=False))
        raise typer.Exit(code=1)

    config_manager.set_value('default', key, value)
    console.print(Panel(f"✅ Configuração '[cyan]{key}[/]' salva como '[green]{value}[/]'.", expand=False))

@config_app.command("show", help="Mostra todas as configurações salvas.")
def config_show():
    """
    Exibe as configurações atuais salvas em uma tabela.

    Este comando lê o arquivo de configuração e mostra os valores padrão que estão
    sendo utilizados pela aplicação. É útil para verificar quais dados estão
    configurados antes de gerar novos códigos PIX.

    Exemplo de uso:

    - Ver as configurações salvas:
        $ pixcore config show
    """
    configs = config_manager.get_config_as_dict()
    if not configs or 'default' not in configs:
        console.print("[yellow]Nenhuma configuração salva encontrada.[/yellow]")
        return

    table = Table(title="Configurações Salvas")
    table.add_column("Chave", style="cyan")
    table.add_column("Valor", style="green")

    for key, value in configs['default'].items():
        table.add_row(key, value)
    
    console.print(table)

if __name__ == "__main__":
    app()