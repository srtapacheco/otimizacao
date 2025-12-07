# Instalação do Frontend

Este projeto é enviado **sem a pasta `node_modules`** para reduzir o tamanho do repositório.
Para rodar o frontend corretamente, siga as instruções abaixo.

---

## 1. Instalar dependências

No diretório `frontend`, execute:

```bash
npm install
```

Esse comando baixa todas as bibliotecas necessárias e recria a pasta `node_modules`, incluindo o executável `vue-cli-service` usado para iniciar a aplicação.

---

## 2. Rodar o servidor de desenvolvimento

Depois da instalação, execute:

```bash
npm run serve
```

Se tudo estiver correto, aparecerá no terminal algo semelhante a:

```
DONE  Compiled successfully in XXXXms

App running at:
- Local:   http://localhost:8080/
- Network: http://192.168.xx.xx:8080/
```

A aplicação pode ser acessada no navegador pelo endereço:

```
http://localhost:8080/
```

---

## 3. Criar o build de produção (opcional)

Caso deseje gerar a versão otimizada:

```bash
npm run build
```

Uma pasta `dist/` será criada com os arquivos finais para deploy.

---

## 4. Observações importantes

* Como o `node_modules` não está no repositório, **npm install é obrigatório** antes de qualquer execução.
* O projeto usa **Vue CLI**, portanto todos os scripts (`serve`, `build`, `lint`) dependem do `vue-cli-service` localizado em `node_modules/.bin`.
* Para rodar diretamente o serviço, também é possível usar:

  ```bash
  npx vue-cli-service serve
  ```
