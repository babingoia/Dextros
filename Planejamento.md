# ANOTACOES
    -> Eu tenho que reciclar os botões do datehourmatrix. Então a minha data precisa ter info pra botões.
    -> O card_creator então passa o template dos widgets em forma de dict e a matrix passa os dados.

# Tasks pequenas

-> Arrumar a ordem de carregamento das coisas.
-> Tirar o sistema manual de eventos e usar o EventDispatcher do Kivy.
-> Modularizar as funções do draw_self do DateHourMatrix
-> Otimizar a DateHourMatrix.

-> Tirar a manipulação de cache do CardWidget
-> Botar Docstring em tudo.
-> Desacoplar os dados do datepicker e simplificar, jogando na main view.

-> Transformar o widget do card em um botão alterável
-> Criar a função do alterar card do card creator.

-> Adicionar configurações de tamanho padronizadas pros kv.
-> Adicionar um sistema pro SessionCache não ficar salvando e puxando do json toda hora.

# Tasks Maiores
-> Atualizar as classes de domínio
    *Data:

    *Horário: Carrega uma constante de todos os horários do dia e daquele dextro e valida o formato. Útil pra deixar formatado
    de que jeito os horários vão aparecer na view depois.

    *Refeição: carrega refições pré-definidas que depois vão ser mostradas em um picker e pode receber quantidade de
    carboidratos consumida.
    
    *Dextro: carrega o próprio valor, validação, e estado: se é normal, hipoglicemia ou hiperglicemia.
    
    *Insulina Rápida:

    *Insulina Lenta:

    *Exercício:

    *Observação: 
-> Adicionar testes

# Objetivos

-> Calculadora que leva a fórmula da pessoa para calcular quantidade de insulina rápida 
a partir do dextro e da quantidade de carboidratos consumida.

-> Gráfico em linha que mostra a média de dextro por horário em determinada quantidade de
dias.

-> Gráfico que mostra a quantidade de insulina rápida que a pessoa tá tomando por média de refeição.

-> Gráfico que mostra a quantidade de insulina rápida em comparação com a insulina lenta por dia.

-> Gráfico que mostra a média de: dextro, insulina rápida, carboidratos por refeição em determinado período de dias.