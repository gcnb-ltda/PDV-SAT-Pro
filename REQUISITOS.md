# Requisitos do PDV SAT Pro

Este documento define os requisitos funcionais e não funcionais do software. A presença de um requisito nesta especificação não significa, por si só, que sua implementação esteja concluída. A validação deve ser feita por testes e critérios de aceite próprios.

## Requisitos funcionais

| Código | Requisito |
|---|---|
| RF01 | O sistema deve permitir o cadastro, a consulta, a alteração e a inativação de produtos. |
| RF02 | O sistema deve armazenar código de barras, descrição, preço, unidade, estoque, NCM e CFOP de cada produto. |
| RF03 | O sistema deve localizar produtos por código de barras ou por parte da descrição. |
| RF04 | O sistema deve permitir adicionar produtos ao carrinho de venda. |
| RF05 | O sistema deve permitir alterar a quantidade dos itens durante a venda. |
| RF06 | O sistema deve permitir remover itens do carrinho antes da finalização. |
| RF07 | O sistema deve calcular automaticamente subtotal, descontos e valor total da venda. |
| RF08 | O sistema deve permitir aplicar descontos em valor monetário, respeitando limites configurados. |
| RF09 | O sistema deve aceitar pagamentos em dinheiro, PIX, cartão de débito e cartão de crédito. |
| RF10 | O sistema deve calcular o troco em pagamentos realizados em dinheiro. |
| RF11 | O sistema deve permitir selecionar SAT ou NFC-e como modelo de emissão fiscal. |
| RF12 | O sistema deve permitir cadastrar e atualizar o código de ativação e a DLL do equipamento SAT. |
| RF13 | O sistema deve permitir cadastrar certificado A1, senha, CSC, ID do CSC, série, ambiente e numeração da NFC-e. |
| RF14 | O sistema deve enviar os dados da venda ao emissor fiscal selecionado e registrar seu retorno. |
| RF15 | O sistema deve registrar a chave, protocolo ou identificação do documento fiscal emitido. |
| RF16 | O sistema deve impedir a conclusão da venda quando não houver estoque suficiente. |
| RF17 | O sistema deve reduzir automaticamente o estoque após a conclusão da venda. |
| RF18 | O sistema deve permitir cancelar uma venda em andamento antes de sua finalização. |
| RF19 | O sistema deve armazenar o histórico de vendas, incluindo data, itens, pagamento, total e documento fiscal. |
| RF20 | O sistema deve funcionar em modo de homologação ou simulação para testes sem validade fiscal. |

## Requisitos não funcionais

| Código | Requisito |
|---|---|
| RNF01 | O sistema deve ser compatível com Windows x64, Windows x86, Linux x86_64 e macOS Universal. |
| RNF02 | A interface deve ser responsiva e adequada a resoluções a partir de 1024 × 768 pixels. |
| RNF03 | As operações comuns da interface devem responder em até dois segundos em condições normais. |
| RNF04 | A pesquisa local de produtos deve retornar resultados em até um segundo para uma base de até 100 mil produtos. |
| RNF05 | O sistema deve operar localmente quando não houver conexão com a internet, exceto em serviços fiscais que exijam comunicação externa. |
| RNF06 | O banco de dados local deve preservar a consistência das vendas por meio de transações atômicas. |
| RNF07 | Uma falha durante a gravação da venda não deve gerar baixa parcial de estoque. |
| RNF08 | Senhas, códigos SAT, CSC e senhas de certificados não devem aparecer abertamente na interface. |
| RNF09 | Dados fiscais sensíveis devem ser armazenados com proteção compatível com o sistema operacional. |
| RNF10 | Certificados digitais e credenciais não devem ser incluídos no código-fonte, nos instaladores ou nos registros de diagnóstico. |
| RNF11 | O sistema deve validar os campos fiscais obrigatórios antes de habilitar a emissão em produção. |
| RNF12 | A arquitetura deve manter interface, regras de negócio, persistência e integração fiscal em componentes separados. |
| RNF13 | A substituição do emissor SAT por NFC-e não deve exigir alterações no módulo de vendas. |
| RNF14 | O sistema deve registrar erros técnicos e retornos fiscais com data e contexto suficientes para auditoria. |
| RNF15 | Os registros de diagnóstico não devem armazenar senhas, certificados ou códigos de ativação completos. |
| RNF16 | O sistema deve disponibilizar rotinas de backup e restauração da base local. |
| RNF17 | Os instaladores devem verificar ou incluir todas as dependências necessárias à execução. |
| RNF18 | O sistema deve manter compatibilidade com leitores de código de barras que operem como teclado USB. |
| RNF19 | As funções principais devem possuir testes automatizados executados antes da geração dos instaladores. |
| RNF20 | Alterações relacionadas à emissão fiscal devem ser versionadas e validadas em ambiente de homologação antes da implantação em produção. |

## Convenções

- `RF`: requisito funcional.
- `RNF`: requisito não funcional.
- Alterações nesta especificação devem ser versionadas no mesmo repositório do software.
- Requisitos fiscais devem ser homologados antes do uso em produção.
