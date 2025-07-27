from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class PixData:
    """
    Representa todos os dados para a geração de um BR Code PIX,
    incluindo campos obrigatórios e opcionais do padrão EMV®.
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
        
        if not self.recebedor_nome or len(self.recebedor_nome.encode('utf-8')) > 25:
            raise ValueError("O nome do recebedor (recebedor_nome) é obrigatório e deve ter até 25 bytes.")
            
        if not self.recebedor_cidade or len(self.recebedor_cidade.encode('utf-8')) > 15:
            raise ValueError("A cidade do recebedor (recebedor_cidade) é obrigatória e deve ter até 15 bytes.")

        if self.transacao_id != '***' and not re.match(r'^[a-zA-Z0-9]{1,25}$', self.transacao_id):
            raise ValueError("O ID da Transação (transacao_id) deve ser alfanumérico com até 25 caracteres.")

        if not self.pix_key or len(self.pix_key) > 77:
            raise ValueError("A chave Pix (pix_key) é obrigatória e deve ter até 77 caracteres.")

        if self.valor is not None and self.valor <= 0:
            raise ValueError("O valor (valor), se presente, deve ser positivo.")
            
        if self.recebedor_cep and not re.match(r'^\d{8}$', self.recebedor_cep):
            raise ValueError("O CEP (recebedor_cep) deve conter 8 dígitos numéricos.")