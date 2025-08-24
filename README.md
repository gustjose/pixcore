# PixCore

<p align="center">
  <img src="https://raw.githubusercontent.com/gustjose/pixcore/refs/heads/main/docs/assets/banner-white.png" alt="logo do projeto" width="700">
</p>

<p align="center">
    <a href="https://github.com/gustjose/pixcore/releases/latest"><img src="https://img.shields.io/github/v/release/gustjose/pixcore?sort=date&display_name=release&style=for-the-badge&logo=github&logoColor=%23fff&labelColor=%2320201e&color=%234e6879" alt="Github Releases"></a>
  <a href="https://pypi.org/project/pixcore/"><img src="https://img.shields.io/pypi/v/pixcore?style=for-the-badge&logo=pypi&logoColor=%23fff&labelColor=%2320201e&color=%234e6879" alt="PyPI Version"></a>
  <a href="https://github.com/gustjose/pixcore/blob/main/LICENSE"><img src="https://img.shields.io/github/license/gustjose/pixcore?style=for-the-badge&labelColor=%2320201e&color=%234e6879" alt="License"></a>
</p>

Uma biblioteca Python robusta e intuitiva para a geração de QR Codes e payloads "Copia e Cola" do Pix, seguindo as especificações do Banco Central do Brasil.

O **PixCore** foi projetado para ser simples de usar, mas poderoso o suficiente para cobrir todos os campos e customizações necessárias, desde transações simples até casos de uso mais complexos com dados adicionais e logos personalizados.

## Principais Funcionalidades

- **Geração de Payload (BR Code):** Crie a string "Copia e Cola" no formato TLV (Type-Length-Value) pronta para ser usada.
- **Criação de QR Code:** Gere imagens de QR Code (PNG) a partir dos dados do Pix.
- **Validação de Dados:** A classe `PixData` valida automaticamente os campos para garantir a conformidade com o padrão do BACEN (ex: tamanho dos campos, formatos, etc.).
- **Customização Flexível:**
    - Defina valor fixo ou permita que o pagador insira o valor.
    - Adicione um logo customizado no centro do QR Code.
    - Personalize as cores do QR Code.
    - Inclua campos opcionais como CEP, dados em outro idioma e método de iniciação (QR estático/dinâmico).
- **Totalmente Testada:** Cobertura de testes para garantir a confiabilidade na geração dos códigos.
- **Interface de Linha de Comando (CLI)**: Utilize todas as funcionalidades diretamente do seu terminal, sem escrever código Python.
- **Decodificação de Payload**: Analise e valide uma string "Copia e Cola" existente para inspecionar seus dados.
- **Geração em Lote via CSV**: Crie múltiplos QR Codes a partir de um arquivo CSV, ideal para cobranças em massa.
- **Gerenciamento de Configurações**: Salve seus dados padrão (nome, cidade, chave) para agilizar o uso da CLI.

---

## Instalação

Você pode instalar o PixCore diretamente do PyPI:

```bash
pip install pixcore
```
## Uso como Biblioteca Python

Usar o PixCore é um processo de apenas dois passos:

1. Crie uma instância de PixData com as informações do recebedor.
2. Use um objeto Pix para gerar o payload ou o QR Code.

A biblioteca utiliza um sistema de exceções customizadas (ex: ChavePixInvalidaError, GeracaoPayloadError) para permitir um tratamento de erros preciso e robusto em sua aplicação.

### Exemplo 1: Gerando um QR Code com Valor e Logo

```Python
from pixcore import PixData
from pixcore import Pix

# 1. Defina os dados da cobrança Pix
dados_pix = PixData(
    recebedor_nome="Empresa Exemplo LTDA",
    recebedor_cidade="SAO PAULO",
    pix_key="a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  # Chave aleatória (EVP)
    valor=99.90,
    transacao_id="PedidoXPTO123"
)

# 2. Crie a instância principal do Pix
gerador_pix = Pix(dados_pix)

# 3. Gere e salve a imagem do QR Code
gerador_pix.save_qrcode(
    "meu_pix_qr.png",
    caminho_logo="caminho/para/seu/logo.png",
    cor_qr="#004AAD" # Cor customizada
)

# (Opcional) Obtenha a string "Copia e Cola"
payload = gerador_pix.payload()
print("\nPayload (Copia e Cola):")
print(payload)
```
### Exemplo 2: QR Code sem valor definido (pagador decide o valor)

Para gerar um QR Code onde o pagador pode digitar o valor, simplesmente omita o parâmetro valor ao criar o PixData.

```Python
from pixcore import PixData
from pixcore import Pix

dados_doacao = PixData(
    recebedor_nome="ONG BEM MAIOR",
    recebedor_cidade="RIO DE JANEIRO",
    pix_key="ajude@ongbemmaior.org", # Chave tipo e-mail
    transacao_id="DOACAO" # O ID da transação é obrigatório
)

pix_doacao = Pix(dados_doacao)
pix_doacao.save_qrcode("qr_code_doacao.png")
```
---

## Uso via Linha de Comando (CLI)

O PixCore também é uma poderosa ferramenta de linha de comando que permite gerar QR Codes e payloads sem precisar escrever nenhum código.

### Comandos Principais

#### 1. Gerar um QR Code e salvar em arquivo

Use o comando qrcode com a opção -o (output) para salvar a imagem.

```Bash
pixcore qrcode -k "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d" \
               -n "Empresa Exemplo LTDA" \
               -c "SAO PAULO" \
               -a 99.90 \
               --txid "PedidoXPTO123" \
               -o "meu_pix_qr.png"
```
- **Dica**: Se você omitir a opção `-o`, o QR Code será exibido no visualizador de imagens padrão do seu sistema.

#### 2. Gerar apenas o payload "Copia e Cola"

Use o comando payload para obter a string que pode ser usada em aplicativos de banco.
```Bash
pixcore payload -k "seu-email@exemplo.com" -n "Seu Nome" -c "SUA CIDADE" -a 19.99
```

#### 3. Decodificar um código Pix existente

Com o comando decode, você pode validar um payload e ver seus dados de forma organizada.

```Bash
pixcore decode "00020126580014br.gov.bcb.pix0136a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d520400005303986540599.905802BR5918Empresa Exemplo LTDA6009SAO PAULO62150511Pedido1236304ABCD"
```

#### 4. Gerar QR Codes em Lote a partir de um CSV

O comando lote processa um arquivo CSV e gera um QR Code para cada linha. O CSV deve conter as colunas valor e txid.

```Bash
# Exemplo de conteúdo do arquivo 'cobrancas.csv':
# valor,txid
# 10.50,cliente001
# 25.00,cliente002

pixcore lote "cobrancas.csv" "qrcodes_gerados/" --name "Minha Empresa" --key "meu-cnpj" --city "CIDADE"
```

#### 5. Configurar valores padrão

Para evitar digitar seu nome, cidade ou chave Pix toda vez, use o comando config set.

```Bash
pixcore config set name "Empresa Exemplo LTDA"
pixcore config set city "SAO PAULO"
pixcore config set key "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
```

- Para ver as configurações salvas, use `pixcore config show`.

---

## 📚 Documentação

Para um guia completo sobre todos os campos, validações e funcionalidades, acesse a nossa documentação oficial.

[Link para documentação.](https://gustjose.github.io/pixcore/)

## 🤝 Contribuições

Contribuições são muito bem-vindas! Se você tem ideias para melhorias, novas funcionalidades ou encontrou algum bug, sinta-se à vontade para:

    1. Abrir uma Issue para discutir o que você gostaria de mudar.
    2. Fazer um Fork do projeto e enviar um Pull Request com suas alterações.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

