function copyToClipboard(text, buttonElement) {
  navigator.clipboard.writeText(text).then(function() {
    const originalText = buttonElement.innerText;
    buttonElement.innerText = 'Copiado!';
    setTimeout(function() {
      buttonElement.innerText = originalText;
    }, 2000);
  }, function(err) {
    console.error('Erro ao copiar texto: ', err);
  });
}