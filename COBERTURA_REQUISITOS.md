# Cobertura dos requisitos

## Implementado nesta versão

- Produtos: cadastro, consulta, alteração, inativação, código de barras, descrição, preço, unidade, estoque, NCM e CFOP (`RF01`–`RF03`).
- Venda: carrinho, quantidade editável, remoção, totais, desconto limitado, pagamentos, dinheiro e troco (`RF04`–`RF10`).
- Fiscal: seleção SAT/NFC-e, cadastro protegido, validação de produção, simuladores de homologação, adapter SAT por DLL e persistência do retorno (`RF11`–`RF15`, `RF20`).

## Módulo de relatórios — escopo incorporado

Os requisitos `RF21` a `RF50` foram incorporados formalmente ao produto e constituem o próximo módulo funcional do PDV. Eles abrangem:

- relatórios de vendas, caixa, produtos, estoque, rentabilidade, descontos e cancelamentos (`RF21`–`RF34`);
- documentos fiscais, inconsistências, tributos, clientes, Curva ABC e auditoria (`RF35`–`RF40`);
- filtros, exportação em PDF/CSV/XLSX, impressão, totalização, permissões, rastreabilidade, atualização, paginação e agendamento (`RF41`–`RF49`);
- painel gerencial com indicadores e gráficos (`RF50`).

### Situação de cobertura

| Faixa | Situação | Observação |
|---|---|---|
| RF21–RF40 | Implementado com ressalvas | Central contém os 20 relatórios. Caixa sem suprimentos/sangrias, cancelamentos e tributos exibem apenas dados efetivamente registrados; tributos usam base por NCM até integração do retorno fiscal detalhado. |
| RF41–RF44 | Implementado | Filtros, ordenação, totais e exportação CSV/XLSX/PDF disponíveis. PDF pode ser impresso pelo visualizador do sistema. |
| RF45–RF46 | Implementado | Perfis ADMIN/GERENTE restringem relatórios sensíveis; exportações registram empresa, CNPJ, operador, data, hora e filtros. A autenticação corporativa pode substituir o perfil local em implantação multiusuário. |
| RF47 | Implementado | Relatórios consultam diretamente as transações confirmadas na base SQLite. |
| RF48 | Implementado | Ordenação, pesquisa e paginação de 100 registros por página disponíveis. |
| RF49 | Implementado | Agendamentos diários, semanais ou mensais exportam CSV/XLSX/PDF ao iniciar o PDV quando vencidos. |
| RF50 | Implementado | Painel apresenta faturamento, vendas, ticket médio e ranking de produtos dos últimos 30 dias. |

Um requisito marcado como planejado não deve ser considerado concluído apenas por estar presente na especificação. Sua conclusão exige código, testes automatizados e critérios de aceite.
- Estoque e histórico: validação pré-fiscal, baixa transacional e consulta das vendas (`RF16`–`RF19`).
- Cliente na nota: CPF/CNPJ opcional, normalização, validação, inclusão no XML SAT, encaminhamento ao adaptador NFC-e e armazenamento no histórico (`RF51`).
- Impressão: configuração independente do emissor fiscal, seleção da impressora do sistema, papel 58/80 mm, vias, cabeçalho, rodapé, teste e impressão automática após a confirmação da venda (`RF52`–`RF54`).
- Plataforma e operação: builds Windows x64/x86, macOS Universal e Linux AppImage; dados no diretório do usuário; operação local; logs rotativos com redação; backup/restauração; leitor USB tipo teclado e testes no CI (`RNF01`, `RNF03`, `RNF05`–`RNF10`, `RNF12`–`RNF20`).

## Critérios que exigem homologação ou ensaio externo

- `RNF02`: validar visualmente em monitores a partir de 1024 × 768.
- `RNF04`: executar ensaio com base real de 100 mil produtos e hardware-alvo.
- `RF14` em produção: SAT exige DLL/documentação do fabricante; NFC-e exige provedor fiscal ou implementação SEFAZ por UF, certificado, CSC e homologação.
- `RNF20`: emissão fiscal deve permanecer em homologação até aprovação fiscal e contábil.

## Segurança

Credenciais são armazenadas pelo cofre nativo do sistema via `keyring`: Windows Credential Locker, macOS Keychain ou Secret Service no Linux. Logs não incluem certificado, senha, CSC ou código SAT. Nenhuma credencial é incorporada aos instaladores.
