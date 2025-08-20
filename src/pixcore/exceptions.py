"""
Módulo de Exceções Personalizadas para a Biblioteca PixCore.

Este módulo define uma hierarquia de exceções customizadas para lidar com
erros específicos que podem ocorrer durante a geração e processamento de
códigos Pix, como validação de chaves, geração de payload e manipulação
de arquivos.
"""

class PixCoreError(Exception):
    """
    Exceção base para todos os erros controlados da biblioteca PixCore.

    Todas as outras exceções personalizadas neste módulo herdam desta classe,
    permitindo que os usuários capturem erros específicos ou genéricos da
    biblioteca com um único bloco `except`.
    """
    pass

class ChavePixInvalidaError(PixCoreError):
    """
    Levantada quando uma chave Pix não passa nos critérios de validação.

    Isso pode ocorrer por formato incorreto, checksum inválido ou outros
    problemas de integridade da chave fornecida.

    :ivar chave: A chave Pix que foi considerada inválida.
    :ivar motivo: A descrição do motivo pelo qual a chave falhou na validação.
    """
    def __init__(self, chave: str, motivo: str):
        self.chave: str = chave
        self.motivo: str = motivo
        mensagem = f"A chave Pix '{chave}' é inválida. Motivo: {motivo}"
        super().__init__(mensagem)

    def __str__(self) -> str:
        chave_parcial = f"{self.chave[:15]}..." if len(self.chave) > 15 else self.chave
        return f"Validação da chave Pix falhou: {self.motivo} (chave: '{chave_parcial}')"

class GeracaoPayloadError(PixCoreError):
    """
    Levantada durante a montagem do payload BRCode se um campo for inválido.

    Indica que um dos campos obrigatórios ou opcionais do payload não pôde
    ser processado, seja por tamanho excedido, formato incorreto ou valor
    inadequado.

    :ivar campo: O nome ou ID do campo que causou o erro.
    :ivar motivo: A explicação do erro (ex: 'tamanho excedido', 'formato inválido').
    """
    def __init__(self, campo: str, motivo: str):
        self.campo: str = campo
        self.motivo: str = motivo
        mensagem = f"Erro ao gerar payload. Campo '{campo}': {motivo}"
        super().__init__(mensagem)

    def __str__(self) -> str:
        return f"Não foi possível gerar o payload: {self.motivo} (campo: {self.campo})"
    
class ProcessamentoImagemError(PixCoreError):
    """
    Levantada quando ocorre um erro ao processar um arquivo de imagem.

    Comumente usada para erros ao tentar abrir, redimensionar ou incorporar
    um logo no QR Code, como em casos de arquivo não encontrado ou formato
    de imagem não suportado.

    :ivar caminho_imagem: O caminho do arquivo de imagem que falhou.
    :ivar motivo: O motivo específico do erro.
    """
    def __init__(self, caminho_imagem: str, motivo: str):
        self.caminho_imagem: str = caminho_imagem
        self.motivo: str = motivo
        super().__init__(f"Erro ao processar imagem '{caminho_imagem}': {motivo}")

class ErroDeESError(PixCoreError):
    """
    Levantada para erros de Entrada/Saída (I/O) relacionados a arquivos.

    Ocorre quando a biblioteca tenta ler ou, mais comumente, salvar um arquivo
    (como a imagem do QR Code) e encontra um problema no sistema de arquivos,
    como falta de permissão ou disco cheio.

    :ivar caminho_arquivo: O caminho do arquivo onde a operação de E/S falhou.
    :ivar motivo: A descrição do erro (ex: 'permissão negada').
    """
    def __init__(self, caminho_arquivo: str, motivo: str):
        self.caminho_arquivo: str = caminho_arquivo
        self.motivo: str = motivo
        super().__init__(f"Erro de E/S no arquivo '{caminho_arquivo}': {motivo}")