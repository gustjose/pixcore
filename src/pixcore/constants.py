# ==============================================================================
# IDs de Campos (Tags) do Payload Principal do BR Code (EMV® MPM)
# Organizados em ordem numérica.
# ==============================================================================
ID_PAYLOAD_FORMAT_INDICATOR = "00"
ID_POINT_OF_INITIATION_METHOD = "01"
ID_MERCHANT_ACCOUNT_INFORMATION = "26"
ID_MERCHANT_CATEGORY_CODE = "52"
ID_TRANSACTION_CURRENCY = "53"
ID_TRANSACTION_AMOUNT = "54"
ID_COUNTRY_CODE = "58"
ID_MERCHANT_NAME = "59"
ID_MERCHANT_CITY = "60"
ID_POSTAL_CODE = "61"
ID_ADDITIONAL_DATA_FIELD_TEMPLATE = "62"
ID_CRC16 = "63"
ID_MERCHANT_INFO_LANGUAGE_TEMPLATE = "64"

# ==============================================================================
# IDs de Sub-campos (Sub-Tags)
# ==============================================================================

ID_GUI = "00" 
ID_PIX_KEY = "01" 

ID_TRANSACTION_ID = "05"

ID_LANGUAGE_PREFERENCE = "00"
ID_MERCHANT_NAME_ALT = "01"
ID_MERCHANT_CITY_ALT = "02"

# ==============================================================================
# Valores Fixos e Padrões
# ==============================================================================
PAYLOAD_FORMAT_INDICATOR_VALUE = "01"
GUI_BR_BCB_PIX = "BR.GOV.BCB.PIX"
COUNTRY_CODE_BR = "BR"
TRANSACTION_CURRENCY_BRL = "986"