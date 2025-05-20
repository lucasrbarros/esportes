# Sistema de Gestão de Quadras

Este documento descreve a nova funcionalidade de gestão de quadras implementada no sistema de agendamento de jogos esportivos.

## Visão Geral

A nova funcionalidade permite que administradores:

1. Cadastrem e gerenciem quadras físicas com valores específicos por hora
2. Associem jogos a quadras específicas
3. Definam a duração dos jogos
4. Calculem automaticamente o valor por pessoa com base no preço da quadra e número de participantes

## Alterações no Banco de Dados

Para implementar esta funcionalidade, foi necessário adicionar uma nova tabela e campos ao banco de dados. Execute o script SQL contido no arquivo `database_update.sql` para atualizar sua base de dados.

Principais alterações:

- Nova tabela `courts` para armazenar informações das quadras
- Novos campos na tabela `rooms`:
  - `court_id`: referência à quadra selecionada
  - `duration_hours`: duração do jogo em horas
  - `end_time`: horário de término do jogo

## Como Usar

### Gerenciamento de Quadras

1. Na página de administração, clique no botão "Gerenciar Quadras"
2. Utilize o botão "Nova Quadra" para adicionar uma nova quadra
3. Preencha os dados da quadra:
   - Nome
   - Tipo de esporte
   - Preço por hora
   - Capacidade máxima
   - Localização (opcional)
   - Descrição (opcional)
   - Status (ativa/inativa)
4. Para editar uma quadra existente, clique no botão de edição na linha correspondente
5. Para excluir uma quadra, clique no botão de exclusão (só é possível excluir quadras sem reservas futuras)

### Criação/Edição de Jogos com Quadras

1. Ao criar ou editar um jogo, na seção "Dados da Quadra":
   - Selecione uma quadra no dropdown
   - Defina a duração do jogo em horas
   - Observe as informações da quadra e valor total
2. O sistema calculará automaticamente:
   - O valor total com base no preço/hora da quadra e duração
   - O valor por pessoa com base no número máximo de participantes
3. O horário de término do jogo será calculado automaticamente

### Verificação de Disponibilidade

O sistema verifica automaticamente a disponibilidade da quadra no horário selecionado. Não será possível criar ou editar um jogo se houver conflito de horários para a quadra escolhida.

### Relatórios

Na seção de relatórios, foi adicionada uma nova visualização de estatísticas de quadras, mostrando:
- Total de quadras cadastradas
- Quadras mais utilizadas

## Lógica de Cálculo de Valores

- **Valor total do jogo**: Preço por hora da quadra × Duração em horas
- **Valor por pessoa**: Valor total ÷ Número de participantes confirmados

O sistema atualiza automaticamente o valor por pessoa conforme participantes confirmam presença ou cancelam participação.

## Limitações e Considerações

- Uma quadra não pode ter duas reservas no mesmo horário
- Não é possível excluir quadras que possuem jogos agendados no futuro
- O valor mínimo de duração é de 0,5 horas (30 minutos)
- É possível criar jogos sem associar a uma quadra específica