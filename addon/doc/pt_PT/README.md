# commandHelper

Fornece um método alternativo de execução de scripts para pessoas que têm dificuldade em pressionar combinações complicadas de teclado. 

### Modo de uso 

Pressionar NVDA + h ativa uma camada de comandos do teclado com as seguintes opções: 

* Setas para a esquerda e direita para escolher uma categoria. 
* Cualquer letra de A a Z para saltar para a categoria con essa inicial. 
* Setas para cima e para baixo para seleccionar um pedido da categoria escolhida. 
* Retorno para executar o script. 
* Shift+enter executa o script como se a sua combinação de teclas tivesse sido pressionada duas vezes rapidamente. 
* control+enter executa o script como se a sua combinação de teclas tivesse sido pressionada três vezes. 
* F1 para dizer a tecla de atalho do script seleccionado. 
* Escape deixa os comandos em camada e restaura a funcionalidade normal do teclado.

### Configuração

A combinação de teclas para activar o extra pode ser modificada nas preferências do NVDA> Definir Comandos.

Algumas outras teclas podem ser personalizadas nas preferências do NVDA> Configurações> Ajuda de Comandos.

* Active / desactive o uso da tecla ctrl para entrar no ajuda de comandos.
* Seleccione com que tecla deseja sair do extra.
* Escolha com que tecla o atalho associado a um comando é anunciado.
* Activar / desactivar a gestão do addon através do teclado numérico.

#### Usar a tecla de controlo para activar o Ajuda de comandos

Com esta opção activada, o extra é chamado ao pressionar a tecla de controlo cinco vezes seguidas. Isto pode ser útil para pessoas que tenham dificuldade em pressionar combinações de várias teclas ao mesmo tempo. No entanto, às vezes pode fazer com que o ajuda de comandos seja activado acidentalmente, quando se pressiona a tecla de controlo para outros usos, por exemplo, control + C e control + V para copiar e colar. Para evitar isto, deve reduzir a velocidade de repetição do teclado. Isso é feito no painel de controlo do Windows. Na caixa de diálogo de configurações do plugin, há um botão que leva directamente a essas configurações. Elas também podem ser abertas pressionando a tecla Windows + R e digitando control.exe keyboard na caixa Executar do Windows. No controlo deslizante "Taxa de repetição" deve definir um valor o mais baixo possível. Ao defini-lo como zero, garantimos que não teremos problemas, mas a activação do extra deixará de funcionar mantendo pressionada a tecla de controlo, o que pode ser um inconveniente para alguns utilizadores com mobilidade reduzida, que tenham dificuldade em dar toques rápidos e repetidos no teclado e prefiram, por esse motivo,  ativá-lo dessa forma. Não existe uma configuração universal, cada utilizador deve encontrar a mais adequada para as suas necessidades ou preferências.

#### Teclado numérico

Com esta opção activada, pode usar o extra com as teclas do teclado numérico.

* 4 e 6 para escolher uma categoria.
* 2 e 8 para seleccionar um pedido da categoria escolhida.
* 5 para dizer o atalho correspondente ao comando seleccionado.
* Enter para executar o comando.
* Sinal de mais para executar o comando como se a sua combinação de teclas tivesse sido pressionada duas vezes rapidamente.
* Sinal de menos para executar o comando como se a sua combinação de teclas tivesse sido pressionada três vezes.
* Escape deixa a camada de comando e restaura a funcionalidade normal do teclado.

Nota sobre compatibilidade: O plugin está pronto para funcionar com versões anteriores do NVDA. O mais antigo testado é 2018.1, mas deve funcionar com os mais antigos. No entanto, nenhum suporte futuro será fornecido para problemas específicos que possam surgir nessas versões.