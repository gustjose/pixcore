class PixCoreError(Exception):
    """Exceção base para todos os erros da biblioteca PixCore."""
    pass

class ChavePixInvalidaError(PixCoreError):
    """Levantado quando uma chave Pix é considerada inválida."""
    def __init__(self, chave: str, motivo: str):
        self.chave = chave
        self.motivo = motivo
        mensagem = f"A chave Pix '{chave}' é inválida. Motivo: {motivo}"
        super().__init__(mensagem)

    def __str__(self):
        return f"Validação da chave Pix falhou: {self.motivo} (chave: {self.chave[:15]}...)"

class GeracaoPayloadError(PixCoreError):
    """Levantado quando ocorre um erro na geração do payload BRCode."""
    def __init__(self, campo: str, motivo: str):
        self.campo = campo
        self.motivo = motivo
        mensagem = f"Erro ao gerar payload. Campo '{campo}': {motivo}"
        super().__init__(mensagem)

    def __str__(self):
        return f"Não foi possível gerar o payload: {self.motivo} (campo: {self.campo})"
    
class ProcessamentoImagemError(PixCoreError):
    """Levantado quando há um erro ao processar uma imagem (ex: logo)."""
    def __init__(self, caminho_imagem: str, motivo: str):
        self.caminho_imagem = caminho_imagem
        self.motivo = motivo
        super().__init__(f"Erro ao processar imagem '{caminho_imagem}': {motivo}")

class ErroDeESError(PixCoreError):
    """Levantado para erros de Entrada/Saída, como falhas ao salvar arquivos."""
    def __init__(self, caminho_arquivo: str, motivo: str):
        self.caminho_arquivo = caminho_arquivo
        self.motivo = motivo
        super().__init__(f"Erro de E/S no arquivo '{caminho_arquivo}': {motivo}")