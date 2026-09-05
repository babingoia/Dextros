# Dextros 🩸

**Dextros** é um aplicativo desktop/mobile para registro e acompanhamento de dados de controle glicêmico de pacientes diabéticos — um diário glicêmico digital, inspirado nas cartelas de papel que endocrinologistas costumam pedir para os pacientes preencherem manualmente.

> O nome vem de "dextro", como é popularmente chamado no Brasil o teste de glicemia capilar.

Construído em **Python + Kivy/KivyMD**, seguindo princípios de **Clean Architecture**, para rodar tanto em desktop (Windows/Linux/macOS) quanto em Android a partir da mesma base de código.

---

## 📦 Release

**[V0.1 — Primeira versão de Dextros!](https://github.com/babingoia/Dextros/releases/tag/V0.1)** *(pre-release)*

Aplicativo que salva registros de glicemia com data, horário, quantidade de insulina, observações, refeição e exercícios realizados, e os mostra de forma estilizada em dois gráficos diferentes.

📱 [Baixar o APK para Android](https://github.com/babingoia/Dextros/releases/download/V0.1/dextros.apk)

---

## ✨ Funcionalidades

- 📋 **Registro de medições (Cards)**: glicemia, insulina de ação longa (basal) e de ação rápida (bolus), exercício físico (com intensidade), período da refeição associado e observações livres.
- 📊 **Visualização em matriz "Dia × Hora"**: veja todas as medições do dia organizadas por horário, em uma grade rolável.
- 🍽️ **Visualização em matriz "Dia × Refeição"**: acompanhe a glicemia em relação aos períodos de refeição (jejum, pré/pós almoço, pré/pós jantar, etc.).
- 🗑️ **Exclusão de registros** diretamente a partir da matriz, com popup de detalhes.
- 🌓 **Interface responsiva**, com navbar lateral retrátil em telas pequenas e layout expandido em desktop.
- 💾 **Persistência local em JSON**, com escrita atômica (segura contra corrupção de dados em caso de falha).

---

## 🏗️ Arquitetura

O projeto segue uma variação de **Clean Architecture / Ports & Adapters**, organizada em camadas concêntricas onde as dependências sempre apontam para dentro:

```
frameworks  →  adapters  →  usecases  →  core
(Kivy, JSON)   (controllers,  (regras de   (Value Objects,
               gateways,      aplicação)    regras de negócio
               repositórios)                puras)
```

| Camada | Responsabilidade |
|---|---|
| `core/` | Value Objects imutáveis e regras de negócio puras (ex: `Card`, `Glycemia`, `Date`). Não depende de nenhuma outra camada. |
| `usecases/` | Casos de uso da aplicação (ex: `CreateCardUseCase`, geração de matrizes via Template Method). Depende apenas de interfaces (`ICardRepository`, `ICardCreator`). |
| `adapters/` | Controllers, roteador (`IRouter`), parsers e o repositório concreto (`JsonRepository`) — traduzem dados entre o mundo externo e os casos de uso. |
| `frameworks/` | Detalhes concretos de framework: UI em Kivy/KivyMD e persistência em arquivo JSON. |
| `infrastructure/` | Utilitários transversais: logging colorido e resolução de paths multiplataforma (dev / executável / Android). |

📖 Para uma análise técnica completa e aprofundada (todos os módulos, fluxos ponta a ponta, testes e dívidas técnicas conhecidas), veja **[DEXTROS_DOCUMENTACAO_TECNICA.md](./DEXTROS_DOCUMENTACAO_TECNICA.md)**.

---

## 🚀 Como executar

### Opção 1: Instalar o APK (Android)

Baixe o `.apk` diretamente da [página do release V0.1](https://github.com/babingoia/Dextros/releases/tag/V0.1) e instale no seu dispositivo Android (pode ser necessário habilitar "instalar de fontes desconhecidas" nas configurações do sistema, já que o app ainda não está em nenhuma loja de aplicativos).

### Opção 2: Rodar a partir do código-fonte (desktop)

> ⚠️ O projeto ainda não possui um `requirements.txt` publicado. As dependências abaixo foram identificadas por inspeção do código-fonte.

### Pré-requisitos

- Python 3.10 ou superior (o código usa `match/case` e `X | Y` type hints)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/babingoia/Dextros.git
cd Dextros

# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install kivy kivymd pytest hypothesis colorama
```

### Executando o app

```bash
python main.py
```

Na primeira execução, o app cria automaticamente o diretório de dados do usuário e copia um banco de dados de exemplo (`db/cards_populated.json`, com 1001 registros fictícios) para lá.

### Rodando os testes

```bash
pytest
```

---

## 📁 Estrutura do projeto

```
Dextros/
├── main.py                # Composition Root — monta e injeta todas as dependências
├── core/                  # Value Objects e regras de negócio (Card, Glycemia, Date, ...)
├── usecases/               # Casos de uso (criar/deletar card, gerar matrizes)
├── adapters/               # Controllers, roteador, parsers, repositório JSON
├── frameworks/              # UI (Kivy/KivyMD) e implementação do handler JSON
├── infrastructure/           # Logging e resolução de paths
├── db/                       # Bancos de dados JSON (seed e exemplos)
└── tests/                    # Testes unitários e de integração (pytest + hypothesis)
```

---

## 🧪 Testes

O projeto conta com **143 testes** entre unitários e de integração, cobrindo principalmente:

- Todos os Value Objects do domínio (`core/`), incluindo testes baseados em propriedade (`hypothesis`) para `Glycemia`;
- O repositório JSON, com testes de integração reais (arquivo em disco) cobrindo CRUD, JSON corrompido, caracteres especiais/emoji e consistência após múltiplas operações;
- A orquestração dos casos de uso via mocks.

---

## 🗺️ Roadmap

Alguns dos próximos passos planejados (veja [`Planejamento.md`](./Planejamento.md) para a lista completa):

- [ ] Calculadora de insulina rápida (bolus) a partir da glicemia e carboidratos consumidos.
- [ ] Configuração de thresholds de glicemia/insulina, refletidos visualmente nas matrizes.
- [ ] Gráfico de linha com média de glicemia por horário ao longo de X dias.
- [ ] Campo de carboidratos nas refeições.
- [ ] Edição de registros já salvos.
- [ ] Import/export do banco de dados.
- [ ] Testes end-to-end e de UI.

---

## 🩺 Base clínica

Os valores padrão de referência para hipoglicemia e hiperglicemia usados pelo domínio (`Glycemia`) foram definidos com base na diretriz oficial da Sociedade Brasileira de Diabetes: [diretriz.diabetes.org.br/metas-no-tratamento-do-diabetes](https://diretriz.diabetes.org.br/metas-no-tratamento-do-diabetes/).

Os níveis de intensidade de exercício (`leve`, `moderada`, `vigorosa`) seguem o Guia de Atividade Física para a População Brasileira.

> Este aplicativo é uma ferramenta de **registro pessoal** e não substitui orientação médica. Consulte sempre um profissional de saúde para decisões de tratamento.

---

## 📄 Licença

Distribuído sob a **PolyForm Noncommercial License 1.0.0**. Veja [`LICENSE`](./LICENSE) para o texto completo.

Em resumo (isso não substitui a leitura da licença): você pode usar, estudar, modificar e distribuir este código livremente para **qualquer finalidade não-comercial** — uso pessoal, estudo, projetos hobby, organizações educacionais, de pesquisa, de saúde pública ou sem fins lucrativos. **Uso comercial não é permitido** sob esta licença.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! O projeto segue algumas convenções de nomenclatura específicas (arquivos em `snake_case`, classes em `PascalCase`, sufixo `Controller`/`Service` obrigatório nas respectivas camadas) — confira [`documentação.md`](./documentação.md) antes de abrir um PR.
