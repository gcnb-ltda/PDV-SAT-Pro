# PDV SAT Pro

PDV desktop moderno em Python, com produtos, pesquisa por código de barras, carrinho, desconto, múltiplas formas de pagamento, fechamento de venda, estoque e emissão fiscal configurável entre SAT e NFC-e.

Inclui cadastro completo de produtos, edição de quantidade, limite de desconto, cálculo de troco, histórico, backup/restauração, auditoria, central de relatórios, painel gerencial e armazenamento de credenciais no cofre do sistema operacional. Consulte `REQUISITOS.md` e `COBERTURA_REQUISITOS.md`.

## Relatórios

O botão **Relatórios** abre a central com filtros por período, pesquisa e pagamento. Estão disponíveis relatórios de vendas, fechamento de caixa, resumo diário, produtos vendidos, ranking, produtos sem movimentação, posição e mínimo de estoque, movimentações, rentabilidade, descontos, cancelamentos, pagamentos, operadores, documentos e inconsistências fiscais, base fiscal por NCM, clientes, Curva ABC e auditoria. Os resultados podem ser exportados em CSV, XLSX e PDF. O botão **Painel** apresenta indicadores gerenciais dos últimos 30 dias.

## Instalação rápida

O pacote inclui instaladores para Windows, Linux e macOS. Consulte `INSTALACAO.md` ou execute:

- Windows: `install_windows.bat`
- Linux: `./instalar_linux.sh`
- macOS: `instalar_macos.command`

## Executar manualmente

Requer Python 3.11+ (Windows para o SAT físico).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Em Linux/macOS use `source .venv/bin/activate` e `cp .env.example .env`.

O primeiro acesso usa operador `ADMIN`, senha `1234`. Troque em produção.

## Configuração SAT ou NFC-e

Use **Configuração fiscal** na tela principal. O usuário pode selecionar SAT ou NFC-e e cadastrar os dados no próprio sistema.

Para SAT: DLL do fabricante, código de ativação e número de sessão. Para NFC-e: certificado A1, senha, CSC, ID do CSC, CNPJ, IE, UF, ambiente, série e numeração.

## Configuração da impressora

Use o botão **Impressora**, separado da configuração fiscal, para selecionar uma impressora instalada no sistema, definir papel térmico de 58 ou 80 mm, número de vias, cabeçalho, rodapé e impressão automática. O botão **Testar impressão** permite validar o dispositivo. O SAT autoriza o CF-e; a impressora apenas produz o extrato após a venda ser autorizada e gravada.

## SAT real

1. Instale o driver/DLL do fabricante e confirme se Python e DLL têm a mesma arquitetura (normalmente 32 bits).
2. Configure `SAT_MODE=dll`, `SAT_DLL_PATH`, `SAT_ACTIVATION_CODE` e `SAT_NUMBER` no `.env`.
3. Confira os nomes e a assinatura das funções no manual do fabricante. O adapter inclui `ConsultarSAT` e `EnviarDadosVenda`; fabricantes podem variar.
4. Nunca grave o código de ativação no repositório. Restrinja acesso ao `.env`.

O XML enviado no exemplo é deliberadamente simplificado. Antes de produção, gere o CFe conforme a especificação vigente, dados tributários reais, assinatura AC, CNPJ/IE e regras da SEFAZ-SP. Homologue com contador e integrador fiscal.

## NFC-e real

O cadastro e o simulador estão prontos. A autorização real deve ser ligada em `nfce.NfceSefaz` a uma biblioteca ou API fiscal homologada, pois exige XML 4.00, certificado digital, QR Code 2/3, CSC e URLs específicas de cada UF/ambiente. Não use o simulador para emitir documento fiscal válido.

## Atalhos

- `F2`: buscar produto
- `F4`: finalizar venda
- `F8`: cancelar carrinho
- `Enter`: adicionar código digitado

## Testes

```bash
pytest -q
```
