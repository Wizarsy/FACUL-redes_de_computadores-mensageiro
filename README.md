# RC

## registrar cliente

Cliente X envia codigo (01) para o servidor, o servidor cria o id e envia (02 + id) para o cliente x.

## Criar grupo

Cliente X envia (10 + id do X + timestamp da criação do grupo + membros), o servidor cria o id do grupo e notifica todos os membros sobre a criação do grupo, ou seja, adiciona a msg (11 + id do grupo + timestamp da criação do grupo + membros) na fila de cada membro do grupo.

## Conectar cliente

Cliente X envia (03 + id) para o servidor, o servidor verifica existencia do client no db, caso exista ele conecta o cliente começa o processo de verificar msg pendentes.

## Enviar mensagem

Cliente X quer enviar msg para cliente Y/Grupo, cliente X por sua vez envia (05 + id do X + id do Y/id do Grupo + timestamp do envio + msg) para o servidor, ao receber o servidor verifica se cliente Y/Grupo existe e esta conectado, caso sim ele adiciona (06 + id do X + id do Y/id do Grupo + timestamp do envio + msg) na fila de msg do cliente Y/Para cada membro do Grupo.

## Confirmação de entrega de mensagem para o servidor

Ao enviar com sucesso uma msg da fila do cliente Y o servidor sabe que a msg foi entregue.

## Confirmação de entrega de mensagem para o cliente

Para cada msg entregue com sucesso para o cliente Y por parte do servidor, o servidor adicionara (07 + id do Y/id + timestamp de entrega) na fila do cliente X.

## Confirmação de leitura da mensagem pelo cliente

Cliente Y le a msg e envia (08 + id do X/id do grupo + timestamp da leitura) para o servidor, ao receber o servidor adiciona (09 + id do Y + timestamp da leitura) na fila do cliente X/id do grupo

## TODO

- [ ] Resolução de caminho independente do cwd;
- [ ] Graceful Shutdown;
- [ ] Limitação de threads por conexão e fila de requisições.
