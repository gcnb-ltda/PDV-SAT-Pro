# Homologação da NFC-e direta

O motor implementa geração NFC-e 4.00, chave e DV, XMLDSig RSA-SHA256 com A1,
SOAP 1.2/mTLS, status, autorização síncrona, cancelamento, inutilização,
contingência offline, QR Code v3/CSC, validação XSD e armazenamento atômico.

## Bloqueio intencional

Cada comprador cadastra seus próprios dados em Configuração fiscal e ativação.
O botão de validação confere o A1 e consulta o status da SEFAZ. Somente após
retorno 107 e confirmação de credenciamento a opção de emissão real pode ser
salva. Qualquer mudança nos dados fiscais invalida a liberação anterior.

Não altere manualmente as flags internas. Homologação não é credenciamento.

## Checklist por UF

1. Instalar o pacote XSD vigente do Portal Nacional.
2. Conferir endpoints e URLs de QR Code/consulta da UF.
3. Cadastrar A1, CSC/ID, endereço, código IBGE, CRT, série e numeração.
4. Testar status 107, autorização 100, cancelamento e inutilização.
5. Simular queda de rede e transmissão posterior da emissão tpEmis=9.
6. Conferir XML/protocolo, DANFE NFC-e, QR Code e consulta pública.
7. Validar NT 2025.002 e tabelas IBS/CBS vigentes com o contador.
8. Registrar evidências e aprovação por UF antes de liberar as duas flags.

O catálogo embutido resolve SVRS e SP. As demais UFs falham de forma segura até
que seus endpoints oficiais sejam inseridos no override.
