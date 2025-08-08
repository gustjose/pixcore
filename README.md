# PixCore

<p align="center">
  <img src="https://raw.githubusercontent.com/gustjose/pixcore/refs/heads/main/docs/assets/banner-white.png" alt="logo do projeto" width="700">
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/pyversions/pixcore?style=for-the-badge" alt="Python Versions">
  <img src="https://img.shields.io/pypi/v/pixcore?style=for-the-badge&color=blue" alt="PyPI Version">
  <img src="https://img.shields.io/pypi/l/pixcore?style=for-the-badge&color=green" alt="License">
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
- **Zero Dependências Externas (Exceto Pillow e qrcode):** Leve e fácil de integrar em qualquer projeto.
- **Totalmente Testada:** Cobertura de testes para garantir a confiabilidade na geração dos códigos.

---

## Instalação

Você pode instalar o PixCore diretamente do PyPI:

```bash
pip install pixcore
```
## Guia de Uso Rápido

Usar o PixCore é um processo de apenas dois passos:

1. Crie uma instância de PixData com as informações do recebedor.
2. Use um objeto Pix para gerar o payload ou o QR Code.

### Exemplo 1: Gerando um QR Code com Valor e Logo

```Python
from pixcore.models import PixData
from pixcore.brcode import Pix

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
from pixcore.models import PixData
from pixcore.brcode import Pix

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

## 📚 Documentação

Para um guia completo sobre todos os campos, validações e funcionalidades, acesse a nossa documentação oficial.

[Link para documentação.](https://gustjose.github.io/pixcore/)

## 🤝 Contribuições

Contribuições são muito bem-vindas! Se você tem ideias para melhorias, novas funcionalidades ou encontrou algum bug, sinta-se à vontade para:

    1. Abrir uma Issue para discutir o que você gostaria de mudar.
    2. Fazer um Fork do projeto e enviar um Pull Request com suas alterações.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

