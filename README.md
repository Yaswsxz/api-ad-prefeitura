# API de Gerenciamento de Usuários - Active Directory

API RESTful para gerenciar a estrutura organizacional e as identidades no Active Directory da Prefeitura de Londrina, com auditoria completa de todas as ações.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Estrutura do Active Directory](#estrutura-do-active-directory)
- [Instalação e Configuração](#instalação-e-configuração)
- [Endpoints da API](#endpoints-da-api)
- [Exemplo de Requisição](#exemplo-de-requisição)
- [Montando a Árvore no AD](#montando-a-árvore-no-ad)
- [Troubleshooting](#troubleshooting)
- [Problemas Conhecidos](#problemas-conhecidos)
- [Auditoria e LGPD](#auditoria-e-lgpd)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fluxo de Contribuição (Git)](#fluxo-de-contribuição-git)
- [Autora](#autora)

## Sobre o Projeto

Automatiza o gerenciamento do Active Directory da prefeitura em dois níveis:

- **Estrutura organizacional (OUs)**: criar e alterar órgãos dentro dos 4 ramos (Direta, Indireta, Terceirizadas, Prepostos), e desincorporar/remover unidades que deixaram de existir.
- **Identidades (Pessoas)**: criar e alterar estagiários, servidores de carreira, comissionados e contas não-humanas (impressoras, sistemas) dentro de cada unidade da Direta.

Além disso: consulta/busca de contas, troca de senha, autenticação, logout, e registro de auditoria completa de tudo isso.

**Divisão de trabalho:** este repositório é mantido por duas pessoas estagiárias. Eu (Yasmin) sou responsável por Criar OU, Alterar/Mover OU, Criar Pessoa e Alterar Pessoa (routers `estrutura` e `identidade`); o restante das operações da API é responsabilidade do outro estagiário.

**Camadas do projeto:** `routers/` (endpoints e validação) → `services/` (regras de negócio) → `core/` (conexão LDAP, config, JWT, logs). Os dados de auditoria ficam num banco SQLite separado do Active Directory.

**Stack:** Python 3.11, FastAPI, ldap3, SQLAlchemy + SQLite, Pydantic, JWT (python-jose), pytest. Versões exatas em `requirements.txt`.

## Estrutura do Active Directory

Em set/2026 a árvore do AD foi reestruturada. O modelo antigo (`CN=Ativos` / `CN=Inativos`, com subsetores soltos como `CODEL`, `CMTU`) foi substituído por uma árvore com 3 troncos, cada um com os mesmos 4 ramos:

```
PML
 ├── Operativos        (estrutura ativa)
 ├── Inoperantes        (espelho 1:1 de Operativos — recebe quem sai de operação)
 └── Desincorporados    (só para OU que deixou de existir de fato — caso raro)
      └── cada um dos 3 acima tem: Direta / Indireta / Terceirizadas / Prepostos
```

Dentro de cada unidade do ramo **Direta** (ex: `Fazenda`, `Educação`), existem 4 subcontainers fixos, criados automaticamente ao criar a unidade: `Estagio`, `Carreira`, `Comissionados`, `NaoHumanos`. Os outros 3 ramos (Indireta, Terceirizadas, Prepostos) não têm essa subdivisão.

**Mapeamento dos setores antigos para os ramos novos** (confirmado com o supervisor):

| Ramo | Unidades |
|---|---|
| Direta | Fazenda, Educação, Planejamento, Procuradoria, Ouvidoria, Secretaria Municipal de Saúde |
| Indireta | CODEL, CMTU, COHAB, ACESF, CAAPSML, FEL, IPPUL, Autarquia Municipal de Saúde (AMS), Sercomtel |
| Terceirizadas | *(nenhuma confirmada ainda)* |
| Prepostos | Cartório do Segundo Ofício |

**Atenção:** os nós da árvore são **containers** (`CN=`), não Organizational Units (`OU=`) — usar `OU=` no lugar de `CN=` gera erro `noSuchObject`.

**Sem DELETE físico de pessoa por padrão:** quando alguém deixa de ser operante, ela é movida da árvore `Operativos` para a mesma posição em `Inoperantes` (nunca apagada). Remoção física só é permitida a partir de `Inoperantes` (pessoa) ou `Desincorporados` (OU), como trava de segurança.

**Atributo `pmlNomeOrgao`:** o nome descritivo do órgão (ex.: "Secretaria Municipal da Fazenda") deveria ficar num atributo customizado chamado `pmlNomeOrgao`. Esse atributo ainda **não foi criado no schema do AD** (precisa de permissão de Schema Admin). Enquanto isso não acontece, a API detecta a ausência automaticamente e usa o atributo padrão `description` no lugar — volta a usar `pmlNomeOrgao` sozinha assim que o schema for estendido, sem precisar alterar código.

## Instalação e Configuração

Requer **Python 3.11**, acesso à rede da prefeitura (ou VPN), e credenciais do AD.

```bash
git clone https://github.com/Yaswsxz/api-ad-prefeitura.git
cd api-ad-prefeitura

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac

py -3.11 -m pip install -r requirements.txt
py -3.11 -m pip install pycryptodome   # necessário para NTLM — ver Troubleshooting
```

Crie um `.env` na raiz (baseado em `.env.example`):

```env
# Active Directory
AD_SERVER=ldap://seu-servidor-ad
AD_DOMAIN=seu-dominio.local
AD_BASE_DN=OU=DESENVOL,DC=seu-dominio,DC=local
AD_SEARCH_BASE=OU=DESENVOL,DC=seu-dominio,DC=local
AD_USER_OU=OU=DESENVOL,DC=seu-dominio,DC=local
AD_BIND_USER=dominio\usuario_servico
AD_BIND_PASSWORD=sua_senha

# Raiz da árvore nova (Operativos/Inoperantes/Desincorporados ficam dentro dela)
AD_PML_BASE=OU=PML,OU=DESENVOL,DC=seu-dominio,DC=local

# Opcional — só para os testes de caminho de sucesso (test_success_path.py).
# Sem isso configurado, esses testes são pulados automaticamente.
TEST_AD_USER=dominio\usuario_teste
TEST_AD_PASSWORD=sua_senha_de_teste

DATABASE_URL=sqlite:///./ad_audit.db
```

`AD_BASE_DN` e `AD_PML_BASE` precisam refletir exatamente a hierarquia real do AD — um caminho incompleto causa `noSuchObject` mesmo com o resto correto.

```bash
py -3.11 -m uvicorn app.main:app --reload   # API em http://localhost:8000
py -3.11 -m pytest tests/ -v                 # rodar os testes
```

## Endpoints da API

**Status** (sem autenticação): `GET /`, `GET /health` (checa AD + banco de auditoria, 200 ou 503), `GET /versao`.

### Estrutura (OU) — prefixo `/estrutura/unidades`

`{ramo_path}` é um de: `direta`, `indireta`, `terceirizada`, `preposto`.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/{ramo_path}` | Cria uma unidade em Operativos e Inoperantes ao mesmo tempo (se Direta, já cria os 4 subcontainers) |
| PATCH | `/{ramo_path}/{nome}` | Altera o nome descritivo (só se a unidade estiver em Operativos) |
| PATCH | `/{ramo_path}/{nome}/desincorporar` | Move a unidade de Operativos para Desincorporados |
| DELETE | `/{ramo_path}/{nome}` | Remove fisicamente — só se já estiver em Desincorporados |

### Identidade (Pessoa) — prefixo `/identidade`

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/humanos` | Cria Estagio/Carreira/Comissionados/NaoHumanos numa unidade da Direta — nasce em Inoperantes, bloqueada |
| PATCH | `/humanos/{login}` | Altera dados — só se já estiver em Operativos |
| DELETE | `/humanos/{login}` | Remove fisicamente — só se já estiver em Inoperantes |

### Ferramentas — prefixo `/usuarios`

Busca, autenticação e utilitários que não dependem da árvore nova.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/login` | Login e geração de token JWT |
| POST | `/auth` | Autentica no AD sem gerar token |
| GET | `/cargos` | Cargos distintos já cadastrados |
| GET | `/candidatos-teste` | Sinaliza possíveis contas de teste (não remove nada) |
| GET | `` | Lista/busca com filtros: `nome`, `cargo`, `email`, `ativo`, `ordenar_por`, `ordem` |
| GET | `/{login}` | Consulta um usuário |
| POST | `/{login}/trocar-senha` | Troca a senha |
| POST | `/{login}/logout` | Registra logout |

### Auditoria — prefixo `/auditoria`

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/login-history` | Logins/logouts — `{"total", "items"}` |
| GET | `/activity-history` | Ações — `{"total", "period_days", "items"}` |
| GET | `/historico/{login}` | Linha do tempo combinada de um usuário |
| GET | `/user-summary/{login}` | Resumo de atividades |
| GET | `/security-report` | Relatório de segurança |

Documentação interativa: `/docs` (Swagger) e `/redoc`.

## Exemplo de Requisição

**Criar uma OU** — `POST /estrutura/unidades/direta`:

```json
{
  "nome": "FAZENDA",
  "pml_nome_orgao": "Secretaria Municipal da Fazenda"
}
```

**Criar uma pessoa** — `POST /identidade/humanos` (nasce em Inoperantes, bloqueada):

```json
{
  "tipo": "Estagio",
  "unidade": "FAZENDA",
  "primeiro_nome": "Joao",
  "ultimo_nome": "Silva",
  "cargo": "Estagiário de TI",
  "email": "joao.silva@londrina.pr.gov.br"
}
```

Resposta (201):

```json
{
  "login": "joao.silva",
  "nome": "Joao Silva",
  "tipo": "Estagio",
  "unidade": "FAZENDA",
  "ativo": false,
  "distinguished_name": "CN=Joao Silva,CN=Estagio,CN=FAZENDA,CN=Direta,CN=Inoperantes,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
  "senha_gerada": "SenhaGerada123!"
}
```

Não-humanos (`"tipo": "NaoHumanos"`) usam `nao_humano_categoria` + `nao_humano_identificador` (ex.: `sistema` + `contas` → login `nhu.sistema.contas`) em vez de nome/sobrenome, e não recebem `senha_gerada`.

## Montando a Árvore no AD

`scripts/criar_estrutura_ad.py` monta o esqueleto completo e as unidades conhecidas, em duas fases:

```bash
py -3.11 scripts\criar_estrutura_ad.py --dry-run          # só mostra o que faria
py -3.11 scripts\criar_estrutura_ad.py --so-esqueleto      # só os containers vazios
py -3.11 scripts\criar_estrutura_ad.py                     # esqueleto + unidades
```

Editar a lista `UNIDADES` no topo do script conforme novos órgãos forem confirmados.

## Troubleshooting

**`ValueError: unsupported hash type MD4`** — falta `pycryptodome` (NTLM depende de MD4, removido do OpenSSL recente). `pip install pycryptodome` e reinicie o servidor.

**`{'result': 32, 'noSuchObject'}`** — caminho (DN) inválido: `.env` incompleto, `OU=` no lugar de `CN=`, ou `AD_PML_BASE` errado.

**`invalid attribute type pmlNomeOrgao`** — atributo customizado ainda não existe no schema do AD. A API já cai automaticamente para `description` nesse caso (ver [Estrutura do Active Directory](#estrutura-do-active-directory)); se o erro persistir, confirme que está rodando a versão mais recente de `estrutura_service.py`.

**`{'result': 64, 'namingViolation'}` ao mover** — *(corrigido)* era `modify_dn` recebendo o caminho completo em vez de só o RDN. Hoje usa `new_superior` corretamente.

**API não reflete mudanças mesmo com `--reload`, ou "Failed to fetch" no Swagger** — quase sempre processo antigo do uvicorn ainda rodando em outro terminal (comum depois de trocar de terminal várias vezes). No Windows: `Get-Process python* | Stop-Process -Force`, depois suba de novo com um terminal só.

**Erro genérico "Internal Server Error"** — veja o traceback no terminal do uvicorn e o `api_ad.log`.

**Pylance sublinhando imports como "could not be resolved"** — o VS Code está apontando pra um interpretador Python diferente do que tem os pacotes instalados. `Ctrl+Shift+P` → "Python: Select Interpreter" → escolhe o do `venv`, e `Ctrl+Shift+P` → "Developer: Reload Window".

## Problemas Conhecidos

**Troca de senha e reabilitação falham silenciosamente sem TLS.** O AD recusa a extensão de troca de senha em conexões sem criptografia. A API já tenta StartTLS automaticamente, mas o controlador de domínio recusa essa negociação — provavelmente por falta de certificado configurado. Ainda não confirmado com o administrador do domínio se dá pra configurar certificado TLS (LDAPS na 636, ou StartTLS na 389).

**Atributo `pmlNomeOrgao` não existe no schema do AD.** Pendente de extensão de schema por quem tem permissão de Schema Admin. Workaround atual: a API usa `description` como substituto (ver acima).

## Auditoria e LGPD

Toda ação é registrada no SQLite: quem fez (`username`), o quê (`action`, `target_user`), quando (`timestamp`), de onde (`ip_address`, `user_agent`), e se deu certo (`status`). O CPF informado na criação de pessoa só fica no banco de auditoria (`ad_audit.db`, fora do Git) — nunca em log ou resposta de erro. Acesso ao servidor e aos endpoints de auditoria deve ser restrito a pessoal autorizado.

## Estrutura do Projeto

```
app/
├── core/          # config, conexão LDAP (com StartTLS), JWT, logs
├── routers/       # estrutura.py, identidade.py, users.py, audit.py
├── schemas/       # estrutura.py, identidade.py, user.py, audit.py
├── services/      # estrutura_service.py, identidade_service.py, ad_service.py
├── audit_service.py
├── database.py
└── main.py        # inclui /, /health, /versao

scripts/
├── criar_estrutura_ad.py   # monta o esqueleto + unidades no AD
├── investigar_ad.py
├── listar_ous.py
└── verificar_env.py

tests/      # test_api.py, test_ad.py, test_success_path.py
```

## Fluxo de Contribuição (Git)

Dois remotos: `origin` (GitHub, espelho público, `main` sem proteção) e `gitlab` (repositório oficial da prefeitura, `main` protegida).

- **GitHub:** push direto, sem branch — `git push origin <branch-local>:main --force` quando precisar sincronizar.
- **GitLab:** branch diária no padrão `correcoes-DD-MM`, criada a partir de `gitlab/main`, com Merge Request pra `main` (obrigatório, já que a branch é protegida).

## Autora

**Yasmin Fernanda de Carvalho**
E-mail: yasmincarvalho.dev06@gmail.com · GitHub: [Yaswsxz](https://github.com/Yaswsxz)
*Estagiária de Desenvolvimento — Prefeitura Municipal de Londrina*

Projeto interno - Prefeitura Municipal de Londrina/PR