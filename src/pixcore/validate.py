import re
import uuid

def validar_cpf(cpf: str) -> bool:
    """
    Valida um número de Cadastro de Pessoas Físicas (CPF).

    A função remove caracteres não numéricos, verifica se o CPF tem 11 dígitos,
    descarta CPFs com todos os dígitos iguais e calcula os dois dígitos
    verificadores para garantir a validade do número.

    Args:
        cpf (str): O número de CPF a ser validado, podendo conter ou não
                   caracteres de formatação (ex: '123.456.789-00').

    Returns:
        bool: Retorna `True` se o CPF for válido, e `False` caso contrário.
    """
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    primeiro_digito = 11 - (soma % 11)
    if primeiro_digito >= 10:
        primeiro_digito = 0

    if int(cpf[9]) != primeiro_digito:
        return False
    
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    segundo_digito = 11 - (soma % 11)

    if segundo_digito >= 10:
        segundo_digito = 0

    if int(cpf[10]) != segundo_digito:
        return False
    return True

def validar_cnpj(cnpj: str) -> bool:
    """
    Valida um número de Cadastro Nacional da Pessoa Jurídica (CNPJ).

    A função remove caracteres não numéricos, verifica se o CNPJ possui 14
    dígitos, descarta sequências com todos os dígitos iguais e valida os
    dígitos verificadores com base no algoritmo oficial.

    Args:
        cnpj (str): O número de CNPJ a ser validado, com ou sem formatação
                    (ex: '00.000.000/0001-91').

    Returns:
        bool: Retorna `True` se o CNPJ for válido, e `False` caso contrário.
    """
    cnpj = "".join(re.findall(r'\d', str(cnpj)))

    if len(cnpj) != 14:
        return False

    if cnpj in (c * 14 for c in "0123456789"):
        return False

    cnpj_base = [int(d) for d in cnpj[:12]]
    digitos_verificadores = [int(d) for d in cnpj[12:]]

    pesos_dv1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma_dv1 = sum(num * peso for num, peso in zip(cnpj_base, pesos_dv1))
    
    resto_dv1 = soma_dv1 % 11
    dv1_calculado = 0 if resto_dv1 < 2 else 11 - resto_dv1

    if dv1_calculado != digitos_verificadores[0]:
        return False

    cnpj_com_dv1 = cnpj_base + [dv1_calculado]
    pesos_dv2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma_dv2 = sum(num * peso for num, peso in zip(cnpj_com_dv1, pesos_dv2))

    resto_dv2 = soma_dv2 % 11
    dv2_calculado = 0 if resto_dv2 < 2 else 11 - resto_dv2
    
    if dv2_calculado != digitos_verificadores[1]:
        return False

    return True

def validar_email(email: str) -> bool:
    """
    Verifica se o formato de um endereço de e-mail é sintaticamente válido.

    Utiliza uma expressão regular para checar a estrutura do e-mail (ex:
    usuario@dominio.com). Esta validação não garante que o endereço de
    e-mail realmente exista ou possa receber mensagens.

    Args:
        email (str): A string contendo o e-mail a ser validado.

    Returns:
        bool: Retorna `True` se o formato do e-mail for válido, e `False`
              caso contrário.
    """
    padrao = re.compile(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$')
    if re.match(padrao, email):
        return True
    else:
        return False

def validar_telefone(telefone: str) -> bool:
    """
    Valida um número de telefone brasileiro (fixo ou celular com 9º dígito).

    A função remove caracteres de formatação, trata o código de país '55',
    valida a existência do DDD e verifica as regras de composição do número,
    incluindo a presença do nono dígito para celulares.

    Args:
        telefone (str): O número de telefone a ser validado, com ou sem
                        formatação (ex: '+55 (11) 99999-8888').

    Returns:
        bool: Retorna `True` se o número for um telefone brasileiro válido,
              e `False` caso contrário.
    """
    numeros = re.sub(r'\D', '', telefone)

    if len(numeros) == 12 or len(numeros) == 13:
        if numeros.startswith('55'):
            numeros = numeros[2:]
        else:
            return False

    if not (10 <= len(numeros) <= 11):
        return False

    ddds_validos = {
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24',
        '27', '28', '31', '32', '33', '34', '35', '37', '38', '41', '42', '43',
        '44', '45', '46', '47', '48', '49', '51', '53', '54', '55', '61', '62',
        '63', '64', '65', '66', '67', '68', '69', '71', '73', '74', '75', '77',
        '79', '81', '82', '83', '84', '85', '86', '87', '88', '89', '91', '92',
        '93', '94', '95', '96', '97', '98', '99'
    }
    ddd = numeros[:2]
    if ddd not in ddds_validos:
        return False
    
    numero_real = numeros[2:]

    if len(numero_real) == 9:
        if numero_real[0] != '9':
            return False
    elif len(numero_real) == 8:
        if numero_real[0] == '9':
            return False
    else:
        return False

    return True

def validar_chave_aleatoria(chave_aleatoria: str) -> bool:
    """
    Valida uma Chave Aleatória Pix (EVP) verificando se está no formato UUID.

    Uma chave aleatória do Pix deve ser um Identificador Único Universal (UUID)
    versão 4. Esta função checa se a string fornecida corresponde a esse padrão.

    Args:
        chave_aleatoria (str): A string da chave a ser validada.

    Returns:
        bool: Retorna `True` se a chave for um UUID válido, e `False`
              caso contrário.
    """
    if not isinstance(chave_aleatoria, str):
        return False

    try:
        uuid.UUID(chave_aleatoria)
        return True
    except ValueError:
        return False
