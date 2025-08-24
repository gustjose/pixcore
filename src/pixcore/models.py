from . import validate
from . import exceptions
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class PixData:
    """
    Representa e valida todos os dados para a geração de um BR Code Pix.

    Esta dataclass serve como um contêiner estruturado para os campos
    obrigatórios e opcionais do padrão EMV® QRCPS, aplicando validações
    automáticas na inicialização do objeto para garantir a conformidade
    e integridade dos dados.

    Attributes:
        recebedor_nome (str): Nome do recebedor/comerciante. Deve ter entre 3 e 25 bytes.
        recebedor_cidade (str): Cidade do recebedor/comerciante. Deve ter entre 3 e 15 bytes.
        pix_key (str): Chave Pix do recebedor (e-mail, CPF/CNPJ, celular ou chave aleatória). Máximo de 77 caracteres.
        valor (Optional[float]): O valor da transação. Se for `None` ou `0`, o QR Code será gerado com valor aberto,
                                 permitindo que o pagador insira o valor.
        transacao_id (str): Identificador da transação (TXID). Deve ser alfanumérico com até 25 caracteres.
                            O padrão '***' indica que não é utilizado um TXID específico.
        ponto_iniciacao_metodo (Optional[str]): Define se o QR Code é estático ('11') ou dinâmico ('12').
                                                Se `None`, o campo não é incluído no payload.
        receptor_categoria_code (str): Código da Categoria do Comerciante (MCC). Padrão: "0000".
        recebedor_cep (Optional[str]): CEP do comerciante. Deve conter exatamente 8 dígitos numéricos.
        info_adicional (Optional[str]): Campo de texto livre para informações adicionais (não usado diretamente
                                        na geração padrão do BR Code, mas útil para o sistema).
        idioma_preferencia (Optional[str]): Idioma para dados alternativos (ex: "pt_BR").
        recebedor_nome_alt (Optional[str]): Nome alternativo do recebedor (em outro idioma).
        recebedor_cidade_alt (Optional[str]): Cidade alternativa do recebedor (em outro idioma).

    Raises:
        exceptions.GeracaoPayloadError: Se qualquer um dos campos não atender às regras
                                        de validação (ex: comprimento, formato).
        exceptions.ChavePixInvalidaError: Se o formato da chave Pix não for reconhecido como válido.

    Examples:
        Criando uma instância válida de PixData:
        >>> dados_validos = PixData(
        ...     recebedor_nome="EMPRESA MODELO",
        ...     recebedor_cidade="SAO PAULO",
        ...     pix_key="123e4567-e89b-12d3-a456-426655440000",
        ...     valor=10.50,
        ...     transacao_id="TXID12345"
        ... )
    """

    recebedor_nome: str
    recebedor_cidade: str
    pix_key: str
    valor: Optional[float] = None
    transacao_id: str = "***"
    ponto_iniciacao_metodo: Optional[str] = None
    receptor_categoria_code: str = "0000"
    recebedor_cep: Optional[str] = None
    info_adicional: Optional[str] = None
    idioma_preferencia: Optional[str] = None
    recebedor_nome_alt: Optional[str] = None
    recebedor_cidade_alt: Optional[str] = None

    def __post_init__(self):
        """
        Executa a validação dos dados após a inicialização do objeto.

        Este método é chamado automaticamente pelo dataclass e centraliza todas
        as regras de negócio para garantir a integridade dos dados do PIX.
        """
        if not self.recebedor_nome or len(self.recebedor_nome.encode('utf-8')) > 25 or len(self.recebedor_nome) < 3:
            raise exceptions.GeracaoPayloadError(campo='recebedor_nome', motivo="O nome do recebedor (recebedor_nome) é obrigatório e deve ter entre 3 e 25 bytes.")
            
        if not self.recebedor_cidade or len(self.recebedor_cidade.encode('utf-8')) > 15 or len(self.recebedor_cidade) < 3:
            raise exceptions.GeracaoPayloadError('recebedor_cidade', "A cidade do recebedor (recebedor_cidade) é obrigatória e deve ter entre 3 e 15 bytes.")

        if self.transacao_id != '***' and not re.match(r'^[a-zA-Z0-9]{1,25}$', self.transacao_id):
            raise exceptions.GeracaoPayloadError('transacao_id', "O ID da Transação (transacao_id) deve ser alfanumérico com até 25 caracteres.")

        if not self.pix_key or len(self.pix_key) > 77: 
            raise exceptions.GeracaoPayloadError('pix_key', "A chave Pix (pix_key) é obrigatória e deve ter até 77 caracteres.")
        elif self.tipo_chave() == "Tipo Desconhecido":
            raise exceptions.ChavePixInvalidaError(self.pix_key,"O formato da chave Pix (pix_key) não é reconhecido.")
            
        if self.valor is not None and self.valor <= 0:
            raise exceptions.GeracaoPayloadError('valor', "O valor (valor), se presente, deve ser positivo.")
            
        if self.recebedor_cep and not re.match(r'^\d{8}$', self.recebedor_cep):
            raise exceptions.GeracaoPayloadError('recebedor_cep', "O CEP (recebedor_cep) deve conter 8 dígitos numéricos.")
        
    def tipo_chave(self) -> str:
        """
        Identifica o tipo da chave Pix com base em seu formato.

        A verificação é feita em uma ordem específica para evitar falsos positivos
        (ex: um CPF ser confundido com um telefone).

        Returns:
            str: O tipo da chave (ex: "CPF", "Email", "Tipo Desconhecido").
        """
        chave = self.pix_key

        if validate.validar_chave_aleatoria(chave):
            return "Chave Aleatória (EVP)"
        elif '@' in chave and validate.validar_email(chave):
            return "Email"
        elif validate.validar_telefone(chave):
            return "Telefone"
        elif validate.validar_cpf(chave):
            return "CPF"  
        elif validate.validar_cnpj(chave):
            return "CNPJ"
        else:
            return "Tipo Desconhecido"