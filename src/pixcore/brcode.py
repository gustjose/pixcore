from . import constants as const
from . import utils
from .models import PixData
from PIL import Image
import qrcode

class Pix:
    def __init__(self, pix_data: PixData):
        self.pix_data = pix_data

    def _build_merchant_account_info(self) -> str:
        gui = utils.format_tlv(const.ID_GUI, const.GUI_BR_BCB_PIX)
        pix_key = utils.format_tlv(const.ID_PIX_KEY, self.pix_data.pix_key)
        
        value = f"{gui}{pix_key}"
        
        return utils.format_tlv(const.ID_MERCHANT_ACCOUNT_INFORMATION, value)

    def _build_additional_data(self) -> str:
        txid = utils.format_tlv(const.ID_TRANSACTION_ID, self.pix_data.transacao_id)
        return utils.format_tlv(const.ID_ADDITIONAL_DATA_FIELD_TEMPLATE, txid)

    def _build_language_template(self) -> str:
        parts = []
        if self.pix_data.idioma_preferencia:
            parts.append(utils.format_tlv(const.ID_LANGUAGE_PREFERENCE, self.pix_data.idioma_preferencia))
        if self.pix_data.recebedor_nome_alt:
            parts.append(utils.format_tlv(const.ID_MERCHANT_NAME_ALT, self.pix_data.recebedor_nome_alt))
        if self.pix_data.recebedor_cidade_alt:
            parts.append(utils.format_tlv(const.ID_MERCHANT_CITY_ALT, self.pix_data.recebedor_cidade_alt))
        
        if not parts:
            return ""

        return utils.format_tlv(const.ID_MERCHANT_INFO_LANGUAGE_TEMPLATE, "".join(parts))

    def payload(self) -> str:
        """Gera o payload completo do BR Code no formato TLV."""
        payload_parts = [
            utils.format_tlv(const.ID_PAYLOAD_FORMAT_INDICATOR, const.PAYLOAD_FORMAT_INDICATOR_VALUE),
        ]

        if self.pix_data.ponto_iniciacao_metodo:
            payload_parts.append(utils.format_tlv(const.ID_POINT_OF_INITIATION_METHOD, self.pix_data.ponto_iniciacao_metodo))

        payload_parts.extend([
            self._build_merchant_account_info(),
            utils.format_tlv(const.ID_MERCHANT_CATEGORY_CODE, self.pix_data.receptor_categoria_code),
            utils.format_tlv(const.ID_TRANSACTION_CURRENCY, const.TRANSACTION_CURRENCY_BRL),
        ])

        if self.pix_data.valor:
            amount_str = f"{self.pix_data.valor:.2f}"
            payload_parts.append(utils.format_tlv(const.ID_TRANSACTION_AMOUNT, amount_str))

        payload_parts.extend([
            utils.format_tlv(const.ID_COUNTRY_CODE, const.COUNTRY_CODE_BR),
            utils.format_tlv(const.ID_MERCHANT_NAME, self.pix_data.recebedor_nome),
            utils.format_tlv(const.ID_MERCHANT_CITY, self.pix_data.recebedor_cidade),
        ])

        if self.pix_data.recebedor_cep:
            payload_parts.append(utils.format_tlv(const.ID_POSTAL_CODE, self.pix_data.recebedor_cep))

        payload_parts.extend([
            self._build_additional_data(),
            self._build_language_template()
        ])
        
        payload = "".join(filter(None, payload_parts))
        
        crc = utils.calculate_crc16(payload + const.ID_CRC16 + "04")
        payload += utils.format_tlv(const.ID_CRC16, crc)
        
        return payload
    
    def qrcode(self, caminho_logo: str = None, cor_qr: str = "black", cor_fundo: str = "white") -> Image.Image:
        """
        Gera e retorna um objeto de imagem (Pillow) do QR Code.
        """
        payload_str = self.payload()
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(payload_str)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color=cor_qr, back_color=cor_fundo).convert('RGB')

        if caminho_logo:
            try:
                logo = Image.open(caminho_logo)
                tamanho_max_logo = int(img_qr.size[0] * 0.25)
                logo.thumbnail((tamanho_max_logo, tamanho_max_logo))
                
                pos_x = (img_qr.size[0] - logo.size[0]) // 2
                pos_y = (img_qr.size[1] - logo.size[1]) // 2
                
                img_qr.paste(logo, (pos_x, pos_y), mask=logo)
            except FileNotFoundError:
                print(f"Aviso: Logo não encontrado em '{caminho_logo}'. Gerando sem logo.")
            except Exception as e:
                print(f"Aviso: Erro ao processar o logo: {e}. Gerando sem logo.")
                
        return img_qr
    
    def save_qrcode(self, caminho_arquivo_saida: str, caminho_logo: str = None, cor_qr: str = "black", cor_fundo: str = "white"):
        """
        Gera e salva a imagem do QR Code diretamente em um arquivo.
        """
        imagem_qr = self.qrcode(caminho_logo=caminho_logo, cor_qr=cor_qr, cor_fundo=cor_fundo)
        imagem_qr.save(caminho_arquivo_saida)
        print(f"QR Code salvo com sucesso em: {caminho_arquivo_saida}")