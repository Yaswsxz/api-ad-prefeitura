# API de Identidades no Active Directory (PML)

---

## Nome do Sistema/Módulo

API de Gestão de Identidades no Active Directory da Prefeitura de Londrina.

## Propósito

A Prefeitura mantém no Active Directory (AD) as identidades de **pessoas** (humanos: servidores de carreira, comissionados e
estagiários) e de **contas técnicas** (não humanos: robôs, impressoras, serviços). A estrutura organizacional (órgãos da
Administração Direta e Indireta, empresas terceirizadas e prepostos) e a vida funcional dessas identidades (admissão,
destituição, transferência, bloqueio) busca ser refletidas no AD de forma padronizada, auditável e segura por meio deste projeto.

Esta API é um serviço REST de **administração** do AD,  destinado a ser consumido por um front-end/sistema de administração back-office. 
A API oferece **operações de nível de negócio** — "criar unidade da Administração Direta", "ativar
servidor", "destituir estagiário", "desincorporar unidade" — e cuida dos detalhes: onde cada objeto fica na árvore, bloqueio e
habilitação de contas, senha inicial, atributos de registro e trilha de auditoria, evitando assim a granularidade de operações LDAP.

**Proposta de valor**

- Os sistemas integrados não demandam conhececimento de LDAP ou a estrutura convencionada da árvore, ficando ao encargo da API preservar e impor o modelo.
- **Identidade nunca é excluída**: ao sair de operação é movido para o local análogo em `Inoperantes` de modo que a remoção física só
  existe para inclusão indevida ou duplicada e preservando assim "a memória" da estrutura.
- **Humanos e não humanos são isolados no topo da árvore**: existe uma base LDAP apenas de identidades destinadas a humanos (`OU=Humanos,OU=Operativos,...`),
  o que simplifica os realms exclusivamente humanos no Keycloak.
- **Contenção**: nada se lê nem se escreve fora de `OU=<RAIZ>,DC=londrina,DC=pr,DC=gov,DC=br`, onde convivem objetos de produção.
- **Auditoria completa** de toda escrita, em duas fases (a intenção é gravada antes de alterações no AD), nenhuma senha exposta em log.

## Secretaria/Órgão Gestor

Secretaria Municipal de Planejamento, Orçamento e Tecnologia

## Gestor na Secretaria/Órgão

Não há.

## Fornecedores

Diretoria de Tecnologia da Informação - DTI.

---

## Funcionalidades principais

**Estrutura (unidades/OUs), nos 4 ramos** — Direta, Indireta, Terceirizadas, Prepostos:
- criar unidade (nos dois espelhos, `Operativos` e `Inoperantes`, e nos dois lados, `Humanos` e `NaoHumanos`);
- consultar e listar unidades (paginado, por árvore); alterar o nome do órgão;
- **desincorporar** (bloqueia as contas e move a unidade para `Desincorporados`) e **reincorporar** (restaura e desbloqueia).

**Identidades humanas e não humanas:**
- criar (uma conta nasce **bloqueada e sem senha**, em `Inoperantes`), consultar e listar com filtros, alterar atributos `pml*`;
- **ativar/admitir** (define a senha inicial, move para `Operativos` e habilita), **destituir** (documenta o ato, bloqueia e move
  para `Inoperantes`), **transferir** (entre unidades, categorias e ramos) e bloquear/desbloquear no lugar;
- **redefinir a senha** (a API gera, com tamanho configurável; humano troca no próximo logon, não humano tem senha sem expiração;
  a senha é devolvida **uma única vez**);
- remover fisicamente (somente em `Inoperantes`, com motivo).

**Transversais:**
- autenticação do cliente por chave própria (`POST /auth/token`, token JWT de curta duração, limite de tentativas);
- auditoria: histórico de logins e de atividades, linha do tempo por login, resumo e relatório de segurança;
- erros em corpo único (`codigo`, `mensagem`, `detalhes`) com `request_id`; cabeçalho opcional `X-Administrador`;
- saúde (`/health` público e estático; `/health/detalhes` autenticado) e versão.

## Linguagens/Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| API REST | FastAPI, Starlette, uvicorn, Pydantic v2 e pydantic-settings |
| Active Directory | ldap3 (LDAPS; TLS 1.0 legado com certificado do DC fixado), pycryptodome |
| Autenticação | python-jose (JWT), PBKDF2-SHA256 para o segredo do cliente |
| Auditoria | SQLAlchemy 2 + SQLite |
| Testes | pytest (AD em memória); campanha de aceitação em bash + curl + jq |
| Plataforma | Active Directory, Git/GitLab, Docker e Docker Compose (imagem `python:3.12-slim`) |

## Arquitetura

### Camadas

```mermaid
flowchart TB
    cliente["<b>Cliente</b><br/>front-end / sistema de administração"]

    subgraph api["API — FastAPI (um processo uvicorn)"]
        direction TB
        routers["<b>routers/</b><br/>rotas HTTP, autenticação JWT,<br/>validação de entrada (schemas Pydantic),<br/>erro único com request_id"]
        services["<b>services/</b><br/>regras de negócio das unidades e das identidades,<br/>ordem das escritas, compensação em falha parcial,<br/>auditoria em duas fases"]
        ldap["<b>core/ldap_connection</b><br/>única camada que fala com o AD:<br/>guarda de raiz em toda operação (OU=DESENVOL),<br/>escape de filtros e DNs, erros do AD interpretados"]
        routers --> services --> ldap
    end

    ad[("<b>Active Directory</b><br/>LDAPS, TLS com certificado fixado<br/>fonte de verdade das identidades")]
    sqlite[("<b>SQLite</b><br/>logs/ad_audit.db<br/>trilha de auditoria")]
    arquivos["<b>Arquivos em logs/</b><br/>api_ad.log, uvicorn.log,<br/>contingência mensal (.jsonl)"]

    cliente -- "HTTPS + Bearer token" --> routers
    ldap -- "LDAP (leitura e escrita)" --> ad
    services -- "intenção e resultado" --> sqlite
    services -. "log e contingência" .-> arquivos
```

| Camada | Responsabilidade | Não faz |
|---|---|---|
| `routers/` | Receber a requisição, autenticar, validar o formato e devolver o corpo de resposta ou o erro padronizado | Regra de negócio; falar com o AD |
| `services/` | Decidir o que fazer: checar pré-condições, executar a sequência de escritas, desfazer o que for preciso e registrar a auditoria | Chamar o `ldap3` diretamente: toda operação passa pela conexão |
| `core/ldap_connection` | Executar toda operação LDAP, validando o DN contra a raiz e transformando o erro do AD em erro de domínio | Conhecer regras de negócio |

| Pasta | Conteúdo |
|---|---|
| `app/routers/` | Rotas: `auth`, `estrutura`, `identidade`, `audit` (e `/`, `/health`, `/versao` em `main.py`) |
| `app/schemas/` | Modelos de entrada e saída (validação de nomes, logins, datas, categorias) |
| `app/services/` | `estrutura_service` (unidades), `identidade_service` (consulta, criação, alteração, bloqueio, remoção), `identidade_ciclo` (ativar, destituir, transferir, redefinir senha), `base_ad` (operações comuns) |
| `app/core/` | `arvore` (único lugar com os nomes das OUs fixas e a montagem/leitura de DNs), `raiz` (contenção), `ldap_connection`, `erros_ad`, `tls`, `atributos`, `regras`, `config`, `auth`, `limite`, `rotacao`, `logging_config` |
| `app/audit_service.py`, `app/database.py` | Auditoria em duas fases e modelos do SQLite |
| `config/` | `regras.toml` (atributos alteráveis e tipos de não humano) e `tls/` (certificado público fixado do DC) |
| `tests/` | Testes com dublês (`pytest`; AD em memória, nenhum acesso ao AD) |
| `tests/aceitacao/` | Campanha de aceitação por `curl` contra a API e o AD de desenvolvimento: fases `f0`…`f9`, massa em `massa/*.tsv` e `README.md` |
| `docs/` | Diagrama da árvore do AD (`arvore-ad.svg`) e especificação e relatórios dos testes de aceitação (`testes/`) |

### A árvore do AD

```
<AD_PML_BASE>  (hoje OU=PML,OU=DESENVOL,...)
 ├── Operativos        estrutura ativa
 ├── Inoperantes       espelho de Operativos: sair de operação implica ser movido para este ponto
 └── Desincorporados   unidades que deixaram o quadro (com todo o conteúdo)
        em cada uma das três:
        ├── Humanos
        │     ├── Direta ── <UNIDADE> ── Estagio | Carreira | Comissionados
        │     └── Indireta | Terceirizadas | Prepostos ── <UNIDADE>   (humanos direto na unidade)
        └── NaoHumanos
              └── Direta | Indireta | Terceirizadas | Prepostos ── <UNIDADE>   (sem categorias)
```

Diagrama: [`docs/arvore-ad.svg`](docs/arvore-ad.svg). Regras principais:

- Todos nós de seperação lógica são `organizationalUnit` (`OU=`); o nome da unidade (maiúsculas) é **único em toda a árvore**.
- A unidade existe nos dois lados (`Humanos` e `NaoHumanos`) de cada árvore; as categorias só existem em `Humanos/Direta`.
- Desativar = mover para o caminho análogo em `Inoperantes`. Desincorporar move **os dois lados** da unidade e bloqueia as
  contas; o espelho em `Inoperantes` permanece.
- A API cria os nós fixos que faltarem (`Humanos`, `NaoHumanos` e os ramos); a OU de cada árvore tem de existir.
- Não há remoção de OU.

### Contenção e segurança

- **TLS obrigatório**: o controlador atual só fala TLS 1.0 (RSA 1024, SHA-1); a limitação foi aceita e o
  certificado do DC é **fixado** (`config/tls/cegonha.pem`), conferido antes de qualquer credencial.
- **Cliente único** autenticado por chave. O administrador humano pode ser
  informado em `X-Administrador` e é registrado **sem verificação**.
- Senhas: geradas pela API, devolvidas uma única vez com `Cache-Control: no-store`, **nunca** em log nem auditoria.

### Dados e auditoria

- **AD**: fonte de verdade das identidades e da estrutura.
- **SQLite** (`logs/ad_audit.db`): trilha de auditoria. Cada escrita no AD é auditada em **duas fases**: a
  intenção (`INICIADA`) é gravada antes; se não puder ser gravada, a operação **não ocorre**; o resultado (`SUCCESS`, `FAILED`
  ou `INCONSISTENTE`) é gravado depois, e se isso falhar o fato vai para um arquivo de contingência.
- **Operações compostas** têm pré-validação, compensação em falha parcial e marca `INCONSISTENTE` quando a compensação também falha.
- **Atributos de registro `pml*`** (instrumento e data dos atos, CPF, tipo de não humano): ainda **não existem no schema do AD**;
  a extensão está pendente junto à Gerência de Infraestrutura. Enquanto isso as operações que os gravam falham com
  `AD_SCHEMA_INCOMPLETO` — ou, só em desenvolvimento, `PML_GRAVAR=false` pula a gravação e avisa na resposta.

## Documentação

### Pré-requisitos e instalação

Python 3.12, acesso de rede ao controlador de domínio e uma conta de serviço do AD. As permissões que faltarem aparecem como
`AD_PERMISSAO_NEGADA` e a linha `AD_ERRO` do log indica qual solicitar (ver "Logs e auditoria").

```bash
git clone https://gitlab.londrina.pr.gov.br/GRDS-1/estagio-id/pml-api-active-directory.git
cd pml-api-active-directory
python -m venv .venv
source .venv/bin/activate      # Linux/WSL  (Windows: .venv/Scripts/activate)
python -m pip install -r requirements.txt
```

### Configuração (`.env`)

Copie `.env.example` para `.env` e preencha (o arquivo nunca é versionado). A lista completa e os comentários estão em
`.env.example`. As principais:

| Chave | Para que serve |
|---|---|
| `JWT_SECRET_KEY`, `API_CLIENT_ID`, `API_CLIENT_SECRET_HASH` | **Obrigatórias**: a API não sobe sem elas. `docker compose run --rm gerar-segredos` (ou `python -m app.core.segredo`) gera o segredo do cliente, o hash e o `JWT_SECRET_KEY` ([Primeira instalação](#primeira-instalação)) |
| `AD_SERVER`, `AD_BIND_USER`, `AD_BIND_PASSWORD`, `AD_UPN_SUFIXO` | Conexão e conta de serviço da API no AD (segredos só no `.env`) |
| `AD_PML_BASE` | Raiz da sub-árvore da API; tem de estar dentro de `OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br`, senão a API não sobe |
| `AD_TLS_LEGADO`, `AD_TLS_CERT_FIXADO`, `AD_TLS_CA_FILE` | TLS: `ldaps://`, TLS 1.0 do DC atual e certificado fixado (`config/tls/cegonha.pem`) |
| `AD_ALLOW_INSECURE` | Só desenvolvimento, enquanto o DC recusar TLS; proibido com `AMBIENTE=prod` |
| `AMBIENTE` | `dev` ou `prod`; `prod` proíbe `AD_ALLOW_INSECURE` e `PML_GRAVAR=false` |
| `PML_GRAVAR` | Temporária: `false` pula a gravação dos `pml*` enquanto o schema não existe |
| `API_REGRAS_FILE` | Atributos alteráveis por `PATCH` e tipos de não humano (padrão `config/regras.toml`) |
| `LOG_DIR`, `LOG_MAX_BYTES`, `API_LOG_FILE`, `DATABASE_URL`, `AUDITORIA_CONTINGENCIA_FILE` | Logs e auditoria; padrão tudo em `logs/` |
| `CORS_ALLOW_ORIGINS`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `AUTH_MAX_FALHAS`, `AUTH_JANELA_SEGUNDOS` | CORS, validade do token e limite de falhas em `/auth/token` |

### Executar e testar

```bash
python -m uvicorn app.main:app --reload     # http://localhost:8000/docs  (Swagger)
python -m pytest -q                          # testes com AD em memória: nenhum acesso ao AD
python -m pytest -m integration              # opt-in: handshake TLS real com o DC, sem bind
```

### Execução em container (Docker Compose)

A imagem é `python:3.12-slim` com o código dentro; **configuração, logs e `.env` ficam no host**.

#### Primeira instalação

```bash
cp .env.example .env                              # 1. o arquivo nunca vai para a imagem nem para o Git
docker compose run --rm gerar-segredos            # 2. imprime o segredo do cliente, o hash e o JWT_SECRET_KEY
```

O passo 2 usa a própria imagem da API (a primeira execução a constrói; numa instalação já existente que recebeu código novo,
rode antes `docker compose build`, senão o comando usa a imagem antiga e não imprime nada), **sem rede e sem ler o `.env`**, e
remove o container ao sair. A saída tem esta forma:

```
SEGREDO DO CLIENTE (entregue ao cliente; não é mostrado de novo):
  <segredo aleatório>

Cole no .env:
  API_CLIENT_SECRET_HASH='pbkdf2_sha256$600000$...$...'
  JWT_SECRET_KEY=<chave aleatória>
```

3. **Cole as duas linhas** `API_CLIENT_SECRET_HASH` e `JWT_SECRET_KEY` no `.env` (o hash fica entre aspas simples, porque contém `$`)
   e defina `API_CLIENT_ID` (o nome do cliente, livre).
4. **Entregue o segredo em claro ao cliente agora** (o front-end o envia com o `client_id` em `POST /auth/token`). Ele só existe no
   terminal: não é gravado em arquivo nem em log, e o `.env` guarda apenas o hash. Se for perdido, gere outro (passo 2) e troque o hash.
5. Preencha o restante do `.env` (`AD_*`, `AD_PML_BASE`, TLS do DC; ver "Configuração") e coloque `fullchain.crt` e `fullchain.key`
   em `./.certs` (ver "HTTPS e certificados").
6. Suba a pilha e confira:

```bash
mkdir -p logs && chown "$(id -u):$(id -g)" logs   # a pasta de logs precisa ser gravável pelo API_UID/API_GID
docker compose up -d --build            # https://<NGINX_SERVER_NAME>/docs (HTTPS pelo nginx)
curl https://<NGINX_SERVER_NAME>/health # {"status":"ok"}
```

**Trocar o segredo do cliente** (rotação): rode `docker compose run --rm gerar-segredos` de novo, troque `API_CLIENT_SECRET_HASH`
no `.env` (e o `JWT_SECRET_KEY`, se quiser invalidar os tokens emitidos), reinicie com `docker compose restart api` e entregue o
novo segredo ao cliente; o anterior deixa de valer. Fora de container, o mesmo comando é `python -m app.core.segredo` (com o venv ativo).

#### Dia a dia

```bash
docker compose logs -f api              # cópia do console; os arquivos completos estão em logs/
docker compose down                     # para (logs/ e auditoria permanecem no host)
docker compose run --rm testes          # pytest dentro da imagem (AD em memória)
```

| Volume / entrada | No host (padrão) | No container | Observação |
|---|---|---|---|
| Configuração | `./config` (`API_CONFIG_DIR`) | `/app/config` (somente leitura) | `regras.toml` e o certificado fixado do DC (`tls/cegonha.pem`) |
| Logs e auditoria | `./logs` (`API_LOGS_DIR`) | `/app/logs` | `api_ad*.log`, `uvicorn.log`, `ad_audit.db`, contingência; nada é apagado |
| Ambiente | `.env` (`API_ENV_FILE`) | `/app/.env` (somente leitura) | lido pela própria API, como fora do container; o Compose não o injeta (interpolaria o `$` do hash do segredo e o corromperia) |
| Certificados HTTPS | `./.certs` (`API_CERTS_DIR`) | `/etc/nginx/certs` do nginx (somente leitura) | `fullchain.crt` e `fullchain.key`, fornecidos pela CA; nunca vão ao Git nem à imagem |
| Configuração do nginx | `./config/nginx` (`NGINX_CONF_DIR`) | `/etc/nginx/templates` do nginx (somente leitura) | `default.conf.template`, com as variáveis do Compose |
| Logs do nginx | `./logs/nginx` | `/var/log/nginx` do nginx | `acesso-AAAA-MM-DD.log` (um por dia) e `error.log`; nada é apagado |

**Podman** (alternativa ao Docker, sem daemon próprio): os mesmos arquivos servem. No Windows, inicie a máquina uma vez
(`podman machine start`) e use `podman compose up -d --build` no lugar de `docker compose ...` (o `podman compose` delega
ao `docker-compose` instalado). A base é referenciada por nome completo (`docker.io/library/python:3.12-slim`), o que evita o
aviso de *short-name* do Podman. Em Podman **rootless** o uid do container não é o do host: use `API_UID=0` (o root do
container é o seu usuário) ou `userns_mode: "keep-id"`; na máquina **rootful** do Windows e no Docker o padrão `1000` funciona.

Variáveis do Compose (todas opcionais, com os padrões de produção; lista comentada no fim do `.env.example`): `HTTPS_BIND`,
`HTTPS_PORT` e `HTTP_PORT` (onde o nginx é publicado; padrão `0.0.0.0:443` e `:80`), `API_CERTS_DIR`, `NGINX_SERVER_NAME`,
`HSTS_MAX_AGE`, `API_UID`/`API_GID` (dono dos arquivos de log), `API_ENV_FILE`, `API_CONFIG_DIR`, `API_LOGS_DIR`,
`API_IMAGE_TAG` e `TZ` (o log vira por dia local). Exemplos:

```bash
API_ENV_FILE=prod.env API_LOGS_DIR=/var/log/pml-api docker compose up -d     # outro .env e outra pasta de logs
HTTPS_BIND=127.0.0.1 HTTPS_PORT=8443 HTTP_PORT=8080 REDIRECT_PORT=:8443 docker compose up -d   # desenvolvimento, portas altas e só local
```

Pontos de atenção:
- No container, deixe `LOG_DIR`, `API_LOG_FILE`, `DATABASE_URL` e `AUDITORIA_CONTINGENCIA_FILE` **vazios** no `.env` (caminhos do host não valem lá dentro).
- **IP do cliente** (auditoria e limite de login): o nginx é a borda e **sobrescreve** o `X-Forwarded-For` com o IP real; como só
  ele alcança a API, o `uvicorn` confia no cabeçalho (`FORWARDED_ALLOW_IPS=*`). Se um balanceador for posto na frente do nginx, o
  IP visto será o do balanceador, a menos que ele seja configurado para repassar o IP (`real_ip` no nginx).
- **SQLite** em volume exige disco local (ext4/WSL2); em NFS/SMB o bloqueio de arquivo não é confiável.
- **Um container, um processo**: a rotação de logs vale para um único `uvicorn`; não use `--workers` nem réplicas.
- O `json-file` do Docker limita só a cópia do console (`max-size`); os arquivos de `logs/` não são apagados.
- **TLS 1.0 com o DC na imagem Debian**: o handshake foi verificado na imagem (Podman) e funciona sem ajuste. Para repetir:
  `docker compose run --rm testes python -m pytest -m integration tests/test_tls_dc.py`. Se um dia falhar (imagem base nova com
  política mais estrita), descomente `OPENSSL_CONF` no `docker-compose.yml`
  (usa o `config/openssl-legado.cnf`, com `MinProtocol = TLSv1` e `CipherString = ALL:@SECLEVEL=0`); vale só para o serviço da API, e a relaxação é a mesma já aceita para o canal com o AD.

### HTTPS (nginx) e certificados

Só o **nginx** é publicado no host. Ele termina o TLS (1.2 e 1.3, cifras do perfil "intermediário" da Mozilla, sem *tickets* de
sessão), redireciona o HTTP para o HTTPS e repassa à API pela rede interna do Compose; **a API não tem porta publicada**. Imagem:
`nginxinc/nginx-unprivileged` (oficial, roda sem root). Cabeçalhos de segurança (HSTS por variável, `nosniff`, `no-referrer`) e
`X-Request-ID` (o mesmo valor nos logs do nginx e da API). A configuração está em `config/nginx/default.conf.template`.

**Certificados.** O nginx lê `fullchain.crt` (certificado do servidor + intermediários, nesta ordem) e `fullchain.key` (chave sem
senha) de `./.certs`. Em produção os arquivos vêm da CA, pela Infraestrutura. O `.certs/` está no `.gitignore` e no `.dockerignore`:
**chaves nunca vão ao Git nem à imagem**.

**Atualizar o certificado** (sem recarga automática, por escolha): copie os novos `fullchain.crt` e `fullchain.key` para `./.certs`
e reinicie o nginx (`docker compose restart nginx`) ou a pilha. Certificado vencido derruba a confiança dos clientes até a troca;
sem certificado válido o nginx não sobe (veja
`docker compose logs nginx`).


### Endpoints

Todas as rotas, exceto `/`, `/health` e `/auth/token`, exigem `Authorization: Bearer <token>`. Corpos, regras e códigos de erro de
cada rota estão no Swagger (`/docs`).

| Prefixo | O que faz |
|---|---|
| `POST /auth/token` | Emite o token do cliente (`client_id` e segredo no corpo) |
| `/estrutura/unidades/{ramo}` | Listar e criar unidades; `/{nome}`: consultar, alterar, `desincorporar`, `reincorporar` |
| `/identidade/humanos` e `/identidade/naohumanos` | Listar e criar; `/{login}`: consultar, alterar (`PATCH`), `bloquear`, `desbloquear`, `ativar`, `destituir`, `transferir`, `redefinir-senha`, remover (`DELETE`) |
| `/auditoria/...` | `login-history`, `activity-history`, `historico/{login}`, `user-summary/{username}`, `security-report` |
| `/`, `/health`, `/health/detalhes`, `/versao` | Status; `/health` é público e não toca no AD |

`{ramo}` ∈ `direta`, `indireta`, `terceirizada`, `preposto`.

### Logs e auditoria

Tudo fica em `logs/` (chave `LOG_DIR`; fora do Git) e **nada é apagado**:

| Arquivo | O que é |
|---|---|
| `logs/api_ad.log` | Log da aplicação (corrente). Vira ao mudar o dia ou ao passar de `LOG_MAX_BYTES` (50 MB) para `api_ad-AAAA-MM-DD.NNN.log` |
| `logs/uvicorn.log` | Acessos e erros do servidor, com a mesma política |
| `logs/ad_audit.db` | Trilha de auditoria (SQLite); a API nunca apaga linhas |
| `logs/auditoria_contingencia-AAAA-MM.jsonl` | Fatos que não puderam ser gravados no banco depois de o AD mudar (um arquivo por mês) |
| `logs/teste/` | Escrita dos testes automáticos |

Compactar ou arquivar o que já virou é rotina operacional, fora da API. Para o `ad_audit.db`, copie periodicamente com
`sqlite3 ad_audit.db ".backup 'destino.db'"` para fora do diretório de trabalho. Cada falha do AD vira uma linha `AD_ERRO ...`
no log, com o código LDAP e a permissão provável a solicitar; cole essa linha para interpretação.

### Auditoria e LGPD

Toda ação de escrita fica registrada: quem (cliente e, se informado, o administrador), o quê, quando, de onde e se deu certo.
Senhas nunca são auditadas nem registradas em log. O CPF é um campo comum e pode constar da auditoria.

### Campanha de aceitação (AD real)

`tests/aceitacao/` executa, com `curl`, todas as rotas contra a API por HTTPS (nginx; destino pelo `.env`, ver `tests/aceitacao/README.md`), que fala com o AD de desenvolvimento
(10 unidades e 72 contas, mantidas ao final). Cada fase (F0 a F9) roda **só com autorização do responsável**; a especificação e
os resultados estão em [`docs/testes/`](docs/testes/). Antes de uma campanha nova, o conteúdo antigo das três árvores sob
`OU=PML` precisa estar limpo. Detalhes em [`tests/aceitacao/README.md`](tests/aceitacao/README.md).

### Problemas conhecidos

- **Canal com o DC fraco** — TLS 1.0, RSA 1024, SHA-1; limitação aceita. O certificado fixado vence em
  **20/09/2027**: ao renovar, substituir `config/tls/cegonha.pem`.
- **Atributos `pml*` ainda não existem no schema** — ver "Dados e auditoria".
- **Limite de login em memória**: o limite de falhas em `/auth/token` vale por processo.
- **Rotação de logs para um processo**: com vários workers do uvicorn seria preciso um rotador externo.

### Troubleshooting rápido

| Sintoma | Causa provável |
|---|---|
| `ValueError: unsupported hash type MD4` | falta `pycryptodome` (está no `requirements.txt`) |
| A API não sobe, `Field required` | faltam `JWT_SECRET_KEY`, `API_CLIENT_ID` ou `API_CLIENT_SECRET_HASH` no `.env` |
| A API não sobe, "fora de OU=DESENVOL" | `AD_PML_BASE` fora da raiz permitida |
| `AD_TLS_INDISPONIVEL` | o DC recusou o TLS (veja `AD_TLS_LEGADO` e `AD_SERVER=ldaps://...`) |
| `AD_CERTIFICADO_NAO_CONFERE` | o DC apresentou outro certificado que o fixado em `AD_TLS_CERT_FIXADO` (renovado?) |
| `AD_PERMISSAO_NEGADA` | falta permissão à conta da API; use a linha `AD_ERRO` do log para pedir à Infraestrutura |
| `AD_SCHEMA_INCOMPLETO` | atributo `pml*` ausente no schema (a extensão é feita pela Infraestrutura; ver "Dados e auditoria") |
| `NAO_ENCONTRADO` (noSuchObject) | `.env` errado, `AD_PML_BASE` incorreto ou a unidade não existe |
| API não reflete mudança / "Failed to fetch" | processo antigo do uvicorn ainda rodando; encerre-o e suba de novo |
| Container: `permission denied` em `/app/logs` | a pasta `logs/` do host não é gravável por `API_UID:API_GID` (veja `id -u` e `chown`) |
| Container não sobe ou `.env` virou pasta | o `.env` (ou o arquivo de `API_ENV_FILE`) tem de existir **antes** do `up` (`cp .env.example .env`); no Docker, montar um arquivo inexistente cria uma pasta com esse nome |
| Aviso do Compose `variable "..." is not set` | o `.env` tem um `$` (hash do segredo); é só o Compose lendo o arquivo para interpolar e não afeta a API, que lê o arquivo sozinha. O hash gerado por `gerar-segredos` já sai entre aspas simples, e então o aviso não aparece; se colou sem aspas, ponha-as |
| Container: porta em uso | outro processo já usa 443/80; pare-o ou mude `HTTPS_PORT`/`HTTP_PORT` (e `REDIRECT_PORT`) |
| nginx não sobe (`cannot load certificate`) | falta ou está inválido `.certs/fullchain.crt`/`.certs/fullchain.key` (peça o PEM à Infraestrutura) |
| `curl: (60)` ou `unable to get local issuer certificate` | o cliente não confia na CA, ou o `fullchain.crt` só tem o certificado do servidor, sem o intermediário da CA: peça à Infraestrutura o arquivo com a cadeia completa. Para testar assim mesmo sem desligar a verificação, aponte `--cacert` (ou `ACEITACAO_CACERT`) para o próprio `fullchain.crt` |
| nginx `Permission denied` em `/var/log/nginx` | `logs/nginx` precisa ser gravável pelo uid 101 do nginx (`mkdir -p logs/nginx && chown 101 logs/nginx`) |
| Container `unhealthy` | `docker compose logs api`: `.env` incompleto (`Field required`) ou `AD_PML_BASE` inválido |
| Pylance sublinhando imports | interpretador errado no VS Code — `Ctrl+Shift+P` → Select Interpreter |

## Implantação

* <definir>.londrina.pr.gov.br (testes)
* <definir>.londrina.pr.gov.br (produção)

A API foi validada contra o AD de desenvolvimento (`OU=DESENVOL`). Antes de produção: extensão do schema com os atributos `pml*`
(Infraestrutura), `AMBIENTE=prod` com `PML_GRAVAR=true`, entrega do segredo do cliente ao front-end, HTTPS entre o front-end e a
API e atualização do certificado fixado quando o do DC for renovado.

## Autores

* **Ricardo Faggion** — Analista de Sistemas - Prefeitura de Londrina (concepção, arquitetura, revisão de código e commits evolutivos)
* **Yasmin Fernanda de Carvalho** — Estagiária (Unicesumar-Londrina) na Prefeitura de Londrina (contribuições no repositório)
* **Augusto Henrique Carreiro Zardo** — Estagiário (UEPG-PR) na Prefeitura de Londrina (contribuições no repositório)
