# Citizen Assist AI — Orientação ao Cidadão

**Global Solution 2026.2 | Pensamento Computacional e Automação com Python**  
**Curso:** Ciência da Computação  
**Integrantes e RM:** Raphaello Caffettani - RM 572334 Lucca Bertolini - RM 569552


## 1. Apresentação

O Citizen Assist AI é um assistente de terminal, desenvolvido em Python, para orientar pessoas que precisam localizar informações básicas sobre serviços públicos. O projeto reúne orientações em linguagem acessível, com referência oficial, data de verificação e informações sobre documentos ou requisitos e canais de atendimento.

**Público atendido:** cidadãos que precisam de orientações simples sobre serviços de saúde, documentos e trabalho.  
**Problema:** as informações sobre serviços públicos estão distribuídas entre diferentes órgãos e portais, dificultando a identificação de fontes confiáveis.  
**Solução:** uma base JSON verificada e um mecanismo de busca por regras, sem dependência de serviços externos de inteligência artificial.

**ODS relacionados:** ODS 3 — Saúde e Bem-Estar; ODS 8 — Trabalho Decente e Crescimento Econômico; ODS 16 — Paz, Justiça e Instituições Eficazes.

## 2. Funcionalidades

- Perguntas em texto livre, com normalização, pontuação e nível de confiança.
- Navegação por três categorias, com orientações numeradas e opção `0` para voltar.
- Respostas com descrição, documentos/requisitos, local de atendimento, URL oficial, data de verificação e aviso de que o assistente não é um canal oficial.
- Sugestão de até duas orientações alternativas quando há mais de um resultado relevante.
- Tratamento de opções fora da faixa, letras, campos vazios e respostas `s/n` inválidas.
- Recusa de perguntas com `@` ou com oito ou mais algarismos, sem salvar esse conteúdo.
- Histórico de atendimentos em JSON, cálculo de indicadores e exportação de CSV.
- Tratamento de arquivo JSON ausente ou inválido, sem encerramento inesperado.

## 3. Organização do código

```text
citizen-assist-ai/
├── README.md
├── main.py
├── orientacao.py
├── base_conhecimento.py
├── assistente.py
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    └── atendimentos.csv
```

O sistema utiliza composição entre três classes:

```text
Assistente
└── base: BaseConhecimento
    └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Atributos principais | Métodos e responsabilidade |
|---|---|---|
| `Orientacao` | `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte`, `verificado_em` | `exibir()`: apresenta os dados e a transparência da fonte. |
| `BaseConhecimento` | `caminho`, `orientacoes` | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()`: interpreta o JSON e localiza orientações. |
| `Assistente` | `nome`, `base`, `historico` | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`: conduz e registra o atendimento. |

O método `main()` cria a base, carrega as orientações e inicia o assistente. O parâmetro `self` em cada classe permite acessar os atributos e chamar métodos do próprio objeto.

## 4. Como executar

**Requisito:** Python 3.10 ou superior. Não é necessário instalar bibliotecas externas.

1. Baixe os arquivos do repositório e mantenha a estrutura das pastas.
2. Abra um terminal na pasta que contém `main.py`.
3. Execute:

   ```bash
   python main.py
   ```

4. No menu, escolha `1` para fazer uma pergunta, `2` para navegar por categoria, `3` para consultar indicadores ou `4` para exportar os atendimentos. A opção `0` retorna ou encerra conforme a tela.

**Exemplos de perguntas:**

```text
Como faço o cartão do SUS?
Como regularizar CPF suspenso?
Onde tiro meu primeiro título de eleitor?
Como acessar a Carteira de Trabalho Digital?
Como solicitar o seguro-desemprego?
```

Ao sair, o programa solicita uma avaliação de facilidade de uso de 1 a 5. Quando houve atendimento na sessão, essa nota é vinculada ao último registro, sem identificação do participante.

## 5. Base de conhecimento

O arquivo `data/base_conhecimento.json` contém **10 orientações**, distribuídas em **3 categorias**, com **no mínimo 3 palavras-chave por registro**. Cada entrada possui os nove campos obrigatórios: `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`.

| ID | Categoria | Orientação | Fonte oficial |
|---:|---|---|---|
| 1 | Saúde | Solicitar Cartão SUS | [Ministério da Saúde](https://www.gov.br/saude/pt-br/acesso-a-informacao/faq/tematicos-e-outros/como-conseguir-o-cartao-sus) |
| 2 | Saúde | Consultar o número do CNS | [Ministério da Saúde](https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao/10-onde-encontro-o-numero) |
| 3 | Saúde | Encontrar uma UBS | [Ministério da Saúde](https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao/2-quais-os-servicos-que) |
| 4 | Documentos | Consultar situação do CPF | [Receita Federal](https://www.gov.br/pt-br/servicos/consultar-cadastro-de-pessoas-fisicas) |
| 5 | Documentos | Regularizar CPF | [Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf) |
| 6 | Documentos | Tirar primeiro título | [Tribunal Superior Eleitoral](https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/autoatendimento-eleitoral) |
| 7 | Documentos | Certidão de quitação eleitoral | [Tribunal Superior Eleitoral](https://www.tse.jus.br/servicos-eleitorais/certidoes/certidoes) |
| 8 | Trabalho | Carteira de Trabalho Digital | [Ministério do Trabalho e Emprego](https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho) |
| 9 | Trabalho | Seguro-desemprego | [Ministério do Trabalho e Emprego](https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego) |
| 10 | Trabalho | Abono salarial | [Ministério do Trabalho e Emprego](https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/abono-salarial) |

**Data de conferência das fontes:** 17/11/2026, registrada no campo `verificado_em` de cada orientação. O acesso à informação oficial pode exigir autenticação, e prazos ou requisitos podem mudar. A consulta deve ser confirmada diretamente no órgão responsável.

## 6. Regra de pontuação e confiança

A busca não gera novas respostas: ela procura a orientação mais adequada dentro do JSON. A função `normalizar()` remove acentos, pontuação e diferenças entre maiúsculas e minúsculas.

| Critério | Pontuação |
|---|---:|
| Uma palavra-chave cadastrada aparece integralmente na pergunta | +3 pontos por palavra-chave encontrada |
| Uma palavra distinta da pergunta, com quatro letras ou mais, aparece no título | +1 ponto por palavra encontrada |
| Pontuação a partir de 6 | Confiança **ALTA** |
| Pontuação entre 3 e 5 | Confiança **MÉDIA** |
| Pontuação abaixo de 3 | Não apresenta orientação; sugere reformulação ou categorias |

A função `buscar()` retorna uma **lista de tuplas** no formato `(pontos, orientacao)`, ordenada por maior pontuação. Em caso de empate, utiliza o identificador do registro como desempate.

**Exemplo:** na pergunta *“Como faço o cartão do SUS?”*, a orientação 1 recebe **3 pontos** por `cartao do sus`, **3 pontos** por `sus` e **1 ponto** pela palavra `cartao` no título, totalizando **7 pontos (confiança ALTA)**. Até duas alternativas relacionadas podem ser mostradas quando alcançam a pontuação mínima.

## 7. Histórico, indicadores e proteção de dados

Cada atendimento concluído é salvo em `data/historico.json` com data, origem (`pergunta` ou `categoria`), pergunta, ID da orientação encontrada, indicação de resultado, avaliação de utilidade, tentativas e tempo em segundos. O cálculo de tempo utiliza `time.time()` e arredondamento para uma casa decimal.

O programa calcula:

- **Respostas encontradas (%):** atendimentos com orientação divididos pelo total de atendimentos.
- **Taxa de acerto / ajudou (%):** respostas marcadas como úteis divididas pelas respostas encontradas que receberam avaliação `s` ou `n`.
- **Tempo médio para encontrar:** média da duração dos atendimentos nos quais uma orientação foi encontrada.
- **Tentativas por atendimento:** média da quantidade de perguntas necessárias até o resultado.
- **Facilidade de uso (1 a 5):** média das notas recebidas ao sair, associadas ao último atendimento da sessão.
- **Dúvidas sem solução:** lista das perguntas para as quais não foi encontrada orientação suficiente.

O botão do menu `4` exporta o arquivo `data/atendimentos.csv` com `csv.DictWriter`, codificação UTF-8 com BOM e separador `;`, adequado para abertura em planilhas em português.

O assistente **não solicita nome, CPF, telefone ou e-mail**. Perguntas com `@` ou oito ou mais algarismos são recusadas antes da busca e não entram no histórico. Informações pessoais eventualmente exigidas por um serviço devem ser fornecidas somente no canal oficial, nunca no programa.

## 8. Verificações de funcionamento e comentários

Foram executados **33 testes automatizados**, todos aprovados, abrangendo o carregamento do JSON, as três classes, normalização, pontuação, entrada inválida, bloqueio de dados pessoais, navegação, histórico, indicadores e exportação CSV.

### Consultas registradas

Foi realizada uma sequência controlada de **10 atendimentos de verificação funcional**, envolvendo consultas por texto e navegação por categoria. Os registros produzidos pelo programa estão em `data/historico.json`, e sua exportação está em `data/atendimentos.csv`.

| Indicador | Resultado da verificação funcional |
|---|---:|
| Atendimentos registrados | 10 |
| Respostas encontradas | 8 (80%) |
| Consultas sem orientação | 2 (20%) |
| Média de tentativas | 1,0 |
| Avaliações pessoais de utilidade | Não coletadas |
| Avaliação de facilidade por usuários | Não coletada |

As consultas sem solução foram **“Onde consigo remédio de graça?”** e **“Como pedir segunda via da conta de luz?”**, pois a base cadastrada não possui orientações correspondentes. Os tempos da execução controlada medem a operação do programa, e não a experiência de leitura de pessoas.

### Comentários

1. **Clareza das respostas:** as orientações localizadas apresentaram documentos ou requisitos, canal de atendimento, fonte oficial e data de verificação, tornando a consulta objetiva.
2. **Facilidade de navegação:** a organização por Saúde, Documentos e Trabalho permite consultar serviços sem precisar formular uma pergunta com palavras-chave exatas.
3. **Limites da cobertura:** perguntas sobre fornecimento de medicamentos e segunda via da conta de energia não foram atendidas pela base atual; a ampliação de orientações é uma oportunidade de melhoria.

### Melhoria aplicada

A busca foi ampliada com a expressão **`vinculos de emprego`** na orientação da Carteira de Trabalho Digital, para reconhecer uma forma adicional de consulta sobre registros profissionais. A alteração foi conferida executando a busca antes e depois da atualização do JSON; após a inclusão, o programa reconheceu a orientação correspondente.

As observações acima são comentários da **verificação funcional do software**. A avaliação com pessoas externas à equipe e seus indicadores de compreensão dependem da realização de atendimentos por participantes.

## 9. Decisão técnica e limitações

A busca por pontuação foi escolhida porque pode ser explicada, testada e conferida diretamente no código. A saída é restrita aos registros da base, diminuindo o risco de oferecer orientações inventadas.

As principais limitações são a dependência de palavras-chave cadastradas, a impossibilidade de responder temas ausentes do JSON e a necessidade de revisão periódica das informações oficiais. A confiança apresentada indica **semelhança textual**, não certeza sobre a situação particular do cidadão nem garantia de que um benefício será concedido.

**Integrações com outras disciplinas:** não foram utilizadas; o projeto foi construído de maneira independente, mantendo a busca por regras como funcionalidade principal.

**Vídeo técnico:** [link do vídeo não listado a inserir após a publicação]
