def format_tlv(id_field: str, value: str) -> str:
    """Formata um campo no formato TLV (Type-Length-Value)."""
    length = str(len(value)).zfill(2)
    return f"{id_field}{length}{value}"

def calculate_crc16(payload: str) -> str:
    """
    Calcula o CRC16-CCITT-FFFF do payload.
    Conforme a referência #1, utiliza o polinômio '1021' (hexa)
    e valor inicial 'FFFF' (hexa). [cite: 88]
    """
    crc = 0xFFFF
    polynomial = 0x1021

    for byte in payload.encode('utf-8'):
        crc ^= (byte << 8)
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
    
    return format(crc & 0xFFFF, 'X').zfill(4)