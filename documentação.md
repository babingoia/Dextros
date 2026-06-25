# Domínio
## Como descrever um domínio
    -> Qual o domínio?
    -> Para que serve esse domínio?
    -> Quais decisões precisaram ser tomadas?
    -> Porque essa decisão foi tomada.

## Presentation
Responsável tanto pela parte lógica quanto construção da tela. É o nível mais abstrato pois não se importa com tecnologia
utilizada. Isso é importante para uma futura expansão de projeto web onde tanto a view quanto os controllers precisariam ser
trocados. Portanto organiza tudo isso pela tecnologia utilizada.

### UI
Responsável pela parte de visualização da tecnologia. Gerencia properties, eventos, estrutura da apresentação e widgets
personalizados. Separa portanto a lógica da apresentação da apresentação em si, comunicando-se por properties e eventos. 

### Controllers
Atua como mediator entre o Core e a UI, traduzindo mudanças entre uma camada e outra. Se comunica interpretando eventos da UI e chamdas de ferramentas da infraestructure para baixo acoplamento entre as camadas.

## Infrastructure
Guarda ferramental de uso transversal e utilitário da aplicação. Portanto pode ser utilizada em qualquer domínio da aplicação, mas de forma reativa a esses mesmos domínios.

## Core
Responsável pela lógica de negócios da aplicação; validação de value objects; tipagem específica; estruturas de dados. Não deve
conhecer nenhuma das outras camadas.


# Estrutura intra-domínio

## kivy
Guarda toda a infraestrutura de apresentação do kivy. Escolhido principalmente pelo potencial de densenvolvimento de aplicativo 
mobile e executável ao mesmo tempo.

### ui
#### widgets
Guarda todos os widgets específicos do projeto.

##### creators
Classes especializadas na criação de widgets específicos do projeto.

##### graphs
Widgets especializados na criação de gráficos complexos do projeto.

##### pickers
Widgets especializados da classe picker do kivy.


## core
### value_objects
Estrutura que guarda todos os value_objects da aplicação.


# Convenções
## Arquivos e Classes
    -> Arquivos nomeados sempre em letra minúscula e com espaços em forma de underscore.
    -> Classes nomeadas em letra maiúscula sem espaço.
    -> Main.py sem underscore.
    -> Toda classe e arquivo em controller precisa ter o sufixo controller.
    -> Toda classe e arquvo em infrastructure precisa ter o sufixo service.

    -> Nomes de variáveis e docstrings em inglês.


# Arquivos do Projeto
## MainView.kv (UI)
Estrutura de componentes da main view.


## MainView.py
Gerencia a janela principal do app capturando eventos, extraindo dados inseridos e definindo properties.

### Eventos

"on_save_request": Evento chamado à partir do click do botão de salvar.

### Properties

"available_time": Propriedade de lista que mostra os horários no spinner.
"actual_time": Propriedade de texto que define o texto de spinner de horários.
"date_display": Propriedade de texto que define a data sendo mostrada na tela.

### Métodos Públicos

"on_save_request(*args)": Método chamado por evento para ser sobrescrito.
"get_data() -> dict[str,str]": Retorna um dicionário com todas as informações "text" da página.
