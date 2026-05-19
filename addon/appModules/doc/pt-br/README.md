# Bruno API Client Accessibility

Complemento para NVDA que melhora a acessibilidade no Bruno API Client em campos que não expõem corretamente o texto através do IAccessible2 (IA2).

## Visão Geral

Bruno é um cliente de API utilizado para testes de requisições, parâmetros, headers e análise de respostas.

Alguns campos de texto do Bruno — especialmente a barra de URL — utilizam elementos `textarea` ocultos (`mousetrap`) que capturam entrada do teclado, mas não expõem corretamente seu conteúdo para APIs de acessibilidade.

Por causa disso, o NVDA não consegue de forma confiável:
- anunciar caracteres apagados
- acompanhar movimentação do cursor
- ler conteúdo existente ao focar o campo
- reportar alterações de texto corretamente

Este complemento fornece uma camada mínima de acessibilidade apenas para esses campos específicos.

Campos normais que já expõem conteúdo corretamente via IA2 continuam sendo tratados nativamente pelo NVDA.

---

# Problema de Acessibilidade

Os campos afetados do Bruno:
- retornam texto vazio através de `makeTextInfo()`
- não expõem valor utilizável via IA2
- mantêm o conteúdo real dentro do estado interno do React, e não no DOM acessível

Sem este complemento, o NVDA pode:
- falhar ao anunciar caracteres apagados
- parar de anunciar texto após edições
- informar que o campo está vazio
- perder feedback de navegação do cursor

---

# O que o Complemento Faz

O complemento mantém uma memória interna mínima apenas para campos mousetrap do Bruno confirmados como inacessíveis.

Ele fornece:
- anúncio de caracteres digitados
- anúncio de backspace/delete
- feedback de navegação com setas esquerda/direita
- anúncio correto do conteúdo ao focar o campo
- rastreamento estável do cursor durante re-renderizações do React

O complemento só é ativado quando a recuperação de texto via IA2 é confirmada como indisponível.

Se o Bruno corrigir a acessibilidade em versões futuras, o tratamento nativo do NVDA volta a ter prioridade automaticamente.

---

# Escopo

Este complemento possui escopo propositalmente reduzido e não tenta substituir o comportamento nativo de edição de texto do NVDA.

O complemento:
- não implementa um editor customizado
- não substitui o comportamento nativo de seleção de texto
- não interfere em campos editáveis normais
- não altera globalmente o comportamento do NVDA

Atalhos nativos de seleção e comandos padrão de edição continuam funcionando normalmente através do Bruno e do NVDA.

---

# Notas Técnicas

O Bruno frequentemente recria seus componentes Electron/React durante a edição.

Por causa disso:
- objetos do NVDA podem ser recriados entre teclas
- o estado do cursor pode se tornar inválido
- a identidade do campo pode mudar dinamicamente

O complemento utiliza um estado sombra leve para preservar:
- conteúdo textual
- posição do cursor

apenas para textareas mousetrap inacessíveis.

---

# Compatibilidade

Testado com:
- NVDA 2025.3.3
- NVDA 2026.1.1

A compatibilidade com outras versões pode variar.

---

# Uso

Instale o complemento e utilize o Bruno normalmente.

Ao editar campos inacessíveis suportados, o NVDA anunciará corretamente:
- caracteres digitados
- caracteres apagados
- navegação do cursor
- conteúdo do campo ao receber foco

Nenhuma configuração adicional é necessária.