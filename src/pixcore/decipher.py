from . import constants as const
from . import utils
from . import exceptions
from typing import Dict, Any

def _parse_merchant_account_info(payload: str) -> Dict[str, str]:
    """Analisa o campo aninhado Merchant Account Information (ID 26)."""
    data = {}
    for sub_id, _, sub_value in utils.parse_tlv(payload):
        if sub_id == const.ID_GUI:
            data['gui'] = sub_value
        elif sub_id == const.ID_PIX_KEY:
            data['pix_key'] = sub_value
    return data

def _parse_additional_data_field(payload: str) -> Dict[str, str]:
    """Analisa o campo aninhado Additional Data Field (ID 62)."""
    data = {}
    for sub_id, _, sub_value in utils.parse_tlv(payload):
        if sub_id == const.ID_TRANSACTION_ID:
            data['transaction_id'] = sub_value
    return data

def _parse_language_template(payload: str) -> Dict[str, str]:
    """Analisa o campo aninhado Merchant Information Language Template (ID 64)."""
    data = {}
    for sub_id, _, sub_value in utils.parse_tlv(payload):
        if sub_id == const.ID_LANGUAGE_PREFERENCE:
            data['language_preference'] = sub_value
        elif sub_id == const.ID_MERCHANT_NAME_ALT:
            data['merchant_name_alt'] = sub_value
        elif sub_id == const.ID_MERCHANT_CITY_ALT:
            data['merchant_city_alt'] = sub_value
    return data


def decode(payload: str) -> Dict[str, Any]:
    """
    Decodifica um payload completo do BR Code Pix, validando seu CRC16.

    Args:
        payload (str): A string completa do "Copia e Cola" do Pix.

    Returns:
        Dict[str, Any]: Um dicionário com os dados do Pix decodificados de forma estruturada.

    Raises:
        exceptions.CRCInvalidoError: Se o checksum CRC16 do payload for inválido.
        exceptions.DecodificacaoPayloadError: Se o payload for malformado.
    """
    if len(payload) < 8 or payload[-8:-4] != f"{const.ID_CRC16}04":
        raise exceptions.DecodificacaoPayloadError("Formato do campo CRC16 inválido ou ausente.")

    payload_to_check = payload[:-8]
    received_crc = payload[-4:]
    
    expected_crc = utils.calculate_crc16(payload_to_check + f"{const.ID_CRC16}04")

    if received_crc.upper() != expected_crc.upper():
        raise exceptions.CRCInvalidoError(esperado=expected_crc, recebido=received_crc)

    data_payload = payload_to_check
    decoded_data: Dict[str, Any] = {}

    for id_field, _, value in utils.parse_tlv(data_payload):
        match id_field:
            case const.ID_PAYLOAD_FORMAT_INDICATOR:
                decoded_data['payload_format_indicator'] = value
            case const.ID_POINT_OF_INITIATION_METHOD:
                decoded_data['point_of_initiation_method'] = value
            case const.ID_MERCHANT_CATEGORY_CODE:
                decoded_data['merchant_category_code'] = value
            case const.ID_TRANSACTION_CURRENCY:
                decoded_data['transaction_currency'] = value
            case const.ID_TRANSACTION_AMOUNT:
                decoded_data['transaction_amount'] = float(value)
            case const.ID_COUNTRY_CODE:
                decoded_data['country_code'] = value
            case const.ID_MERCHANT_NAME:
                decoded_data['merchant_name'] = value
            case const.ID_MERCHANT_CITY:
                decoded_data['merchant_city'] = value
            case const.ID_POSTAL_CODE:
                decoded_data['postal_code'] = value
            case const.ID_MERCHANT_ACCOUNT_INFORMATION:
                decoded_data.update(_parse_merchant_account_info(value))
            case const.ID_ADDITIONAL_DATA_FIELD_TEMPLATE:
                decoded_data.update(_parse_additional_data_field(value))
            case const.ID_MERCHANT_INFO_LANGUAGE_TEMPLATE:
                decoded_data.update(_parse_language_template(value))
    
    return decoded_data