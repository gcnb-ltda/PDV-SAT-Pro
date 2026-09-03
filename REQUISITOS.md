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
| RF21 | O sistema deve emitir relatório de vendas por período, operador, caixa, produto e forma de pagamento. |
| RF22 | O sistema deve apresentar relatório de fechamento de caixa com saldo inicial, suprimentos, sangrias, vendas, cancelamentos, descontos e saldo final. |
| RF23 | O sistema deve gerar resumo diário contendo faturamento, quantidade de vendas, ticket médio e quantidade de itens vendidos. |
| RF24 | O sistema deve listar os produtos vendidos, com quantidades, valores brutos, descontos e valores líquidos. |
| RF25 | O sistema deve classificar os produtos mais vendidos por quantidade e por faturamento. |
| RF26 | O sistema deve identificar produtos sem movimentação de venda dentro de um período informado. |
| RF27 | O sistema deve apresentar a posição atual do estoque, incluindo unidade, quantidade, custo estimado e valor potencial de venda. |
| RF28 | O sistema deve listar produtos abaixo ou próximos do estoque mínimo configurado. |
| RF29 | O sistema deve apresentar as movimentações de estoque, incluindo entradas, saídas, ajustes, cancelamentos, data e responsável. |
| RF30 | O sistema deve calcular faturamento, custo, lucro bruto e margem por produto, categoria ou período. |
| RF31 | O sistema deve relacionar os descontos concedidos por venda, item, operador, motivo e período. |
| RF32 | O sistema deve listar vendas e itens cancelados, incluindo motivo, operador, data e documento fiscal relacionado. |
| RF33 | O sistema deve consolidar os valores recebidos por forma de pagamento, incluindo dinheiro, PIX, cartão, voucher e outras modalidades cadastradas. |
| RF34 | O sistema deve comparar vendas, descontos, cancelamentos e ticket médio por operador. |
| RF35 | O sistema deve listar documentos SAT e NFC-e autorizados, rejeitados, cancelados ou pendentes. |
| RF36 | O sistema deve identificar documentos fiscais com erro de emissão, transmissão, autorização ou retorno. |
| RF37 | O sistema deve consolidar os tributos informados nos documentos fiscais por período, produto e categoria tributária. |
| RF38 | O sistema deve apresentar vendas por cliente, frequência de compras, ticket médio e data da última compra. |
| RF39 | O sistema deve gerar a Curva ABC dos produtos por participação no faturamento, quantidade ou margem. |
| RF40 | O sistema deve emitir relatório de auditoria das alterações de configurações, cadastros, estoque, descontos, cancelamentos e ações administrativas. |
| RF41 | Os relatórios devem oferecer filtros aplicáveis por período, caixa, operador, produto, categoria, forma de pagamento e situação fiscal. |
| RF42 | O sistema deve permitir exportar relatórios nos formatos PDF, CSV e XLSX. |
| RF43 | O sistema deve permitir imprimir relatórios em formato A4 e, quando aplicável, em impressora térmica. |
| RF44 | Os relatórios devem apresentar totais, subtotais e indicadores consolidados compatíveis com os filtros selecionados. |
| RF45 | A visualização, impressão e exportação de relatórios sensíveis devem respeitar as permissões do usuário autenticado. |
| RF46 | Cada relatório exportado deve identificar a empresa, a data e hora de geração, o usuário responsável e os filtros utilizados. |
| RF47 | Os relatórios devem consultar os dados confirmados mais recentes disponíveis no banco de dados. |
| RF48 | Relatórios extensos devem disponibilizar paginação, ordenação e pesquisa nos resultados. |
| RF49 | O sistema deve permitir configurar o agendamento de relatórios recorrentes. |
| RF50 | O sistema deve apresentar painel gerencial com indicadores e gráficos de faturamento, ticket médio, vendas, estoque e situação fiscal. |
| RF51 | O sistema deve permitir informar opcionalmente o CPF ou CNPJ do cliente, validar o documento, incluí-lo no SAT ou NFC-e e armazená-lo no histórico da venda. |

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
- Os requisitos RF21 a RF50 definem o módulo de relatórios e devem ser validados com dados de teste antes da liberação operacional.
