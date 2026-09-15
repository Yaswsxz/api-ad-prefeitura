# API de Gerenciamento de Usuários - Active Directory

API RESTful para gerenciar usuários no Active Directory da Prefeitura de Londrina, com auditoria completa de todas as ações.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Instalação e Configuração](#instalação-e-configuração)
- [Endpoints da API](#endpoints-da-api)
- [Exemplo de Requisição](#exemplo-de-requisição)
- [Setores e Consistência](#setores-e-consistência)
- [Troubleshooting](#troubleshooting)
- [Problemas Conhecidos](#problemas-conhecidos)
- [Auditoria e LGPD](#auditoria-e-lgpd)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Autora](#autora)

## Sobre o Projeto

Automatiza o gerenciamento de usuários no AD da prefeitura: criar, editar, remover e consultar contas; trocar senhas; habilitar/desabilitar e transferir entre setores; detectar e corrigir inconsistências de status; identificar contas de teste (sempre com revisão manual antes de remover); autenticar usuários; e registrar auditoria completa de tudo isso.

**Camadas do projeto:** `routers/` (endpoints e validação) → `services/` (regras de negócio) → `core/` (conexão LDAP, config, JWT, logs). Os dados de auditoria ficam num banco SQLite separado do Active Directory.

**Stack:** Python 3.11, FastAPI, ldap3, SQLAlchemy + SQLite, Pydantic, JWT (python-jose), pytest. Versões exatas em `requirements.txt`.

## Estrutura do Active Directory

A API opera dentro de `OU=DESENVOL > OU=PML`, que contém os containers `CN=Ativos` e `CN=Inativos` — cada um com os mesmos subsetores dentro (`CODEL`, `CMTU`, `Planejamento`, `Ouvidoria`, `Saude`, `Sercontel`).

**Atenção:** esses subsetores são **containers** (`CN=`), não Organizational Units (`OU=`) — usar `OU=` no lugar de `CN=` gera erro `noSuchObject`. O campo `subcontainer` precisa ser um dos nomes reais já existentes; consulte `GET /usuarios/setores` para a lista atualizada (a API valida contra o AD em tempo real, então setores novos já são reconhecidos automaticamente).

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
AD_ATIVOS_BASE=CN=Ativos,OU=PML,OU=DESENVOL,DC=seu-dominio,DC=local
AD_INATIVOS_BASE=CN=Inativos,OU=PML,OU=DESENVOL,DC=seu-dominio,DC=local
AD_SEARCH_BASE=OU=DESENVOL,DC=seu-dominio,DC=local
AD_USER_OU=OU=DESENVOL,DC=seu-dominio,DC=local
AD_BIND_USER=dominio\usuario_servico
AD_BIND_PASSWORD=sua_senha

# Opcional — só para os testes de caminho de sucesso (test_success_path.py).
# Sem isso configurado, esses testes são pulados automaticamente.
TEST_AD_USER=dominio\usuario_teste
TEST_AD_PASSWORD=sua_senha_de_teste

DATABASE_URL=sqlite:///./ad_audit.db
```

`AD_BASE_DN`, `AD_ATIVOS_BASE` e `AD_INATIVOS_BASE` precisam refletir exatamente a hierarquia real do AD (ver acima) — um caminho incompleto causa `noSuchObject` mesmo com o resto correto.

```bash
py -3.11 -m uvicorn app.main:app --reload   # API em http://localhost:8000
py -3.11 -m pytest tests/ -v                 # rodar os testes
```

## Endpoints da API

**Status** (sem autenticação): `GET /`, `GET /health` (checa AD + banco de auditoria, 200 ou 503), `GET /versao`.

### Usuários — prefixo `/usuarios`

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/setores` | Setores reais existentes dentro de Ativos |
| GET | `/cargos` | Cargos distintos já cadastrados |
| GET | `/inconsistencias` | Usuários com status divergente da pasta onde estão |
| POST | `/inconsistencias/corrigir` | Corrige as inconsistências detectadas |
| GET | `/candidatos-teste` | Sinaliza possíveis contas de teste (não remove nada) |
| POST | `/deletar-lote` | Remove os logins explicitamente informados |
| GET | `` | Lista/busca com filtros: `nome`, `cargo`, `setor`, `email`, `ativo`, `ordenar_por`, `ordem` |
| GET | `/{login}` | Consulta um usuário |
| POST | `` | Cria um usuário |
| PUT | `/{login}` | Atualiza cargo, tipo, email, telefone |
| DELETE | `/{login}` | Remove um usuário |
| POST | `/{login}/trocar-senha` | Troca a senha |
| POST | `/{login}/desabilitar` | Desativa e move para Inativos |
| POST | `/{login}/habilitar` | Reativa e move para Ativos |
| POST | `/{login}/transferir-setor` | Move para outro setor, mantendo o status |
| POST | `/auth` | Autentica no AD sem gerar token |
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

`POST /usuarios` (campos obrigatórios: `primeiro_nome`, `ultimo_nome`, `subcontainer` — este último precisa ser um valor real, veja `GET /usuarios/setores`):

```json
{
  "primeiro_nome": "Joao",
  "ultimo_nome": "Silva",
  "cpf": "12345678900",
  "cargo": "Analista Administrativo",
  "tipo": "efetivo",
  "email": "joao.silva@londrina.pr.gov.br",
  "subcontainer": "CODEL"
}
```

Resposta (201) — a conta é criada **desabilitada** por padrão, e a senha só é aplicada de verdade se a conexão suportar TLS (ver [Problemas Conhecidos](#problemas-conhecidos)):

```json
{
  "login": "joao.silva",
  "nome_completo": "Joao Silva",
  "ativo": false,
  "distinguished_name": "CN=Joao Silva,CN=CODEL,CN=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
  "senha_gerada": "SenhaGerada123!"
}
```

`tipo` (`efetivo`/`estagiario`) fica salvo no AD (`description`). `cpf` não vai pro AD, só para a auditoria.

## Setores e Consistência

- **Transferir setor**: `POST /usuarios/{login}/transferir-setor?novo_subcontainer=Saude` — mantém o status atual (Ativos ↔ Inativos não muda).
- **Inconsistências**: um usuário é inconsistente quando `userAccountControl` não bate com a pasta onde está (ex: desabilitado mas ainda em `Ativos`). `GET /usuarios/inconsistencias` lista, `POST /usuarios/inconsistencias/corrigir` resolve.
- **Contas de teste**: sempre em duas etapas — `GET /usuarios/candidatos-teste` sugere, `POST /usuarios/deletar-lote` remove só o que você confirmar (`{"logins": ["usuario.teste"]}`).

## Troubleshooting

**`ValueError: unsupported hash type MD4`** — falta `pycryptodome` (NTLM depende de MD4, removido do OpenSSL recente). `pip install pycryptodome` e reinicie o servidor.

**`{'result': 32, 'noSuchObject'}`** — caminho (DN) inválido: `.env` incompleto, `OU=` no lugar de `CN=`, ou `subcontainer` inexistente. Confira `GET /usuarios/setores`.

**`{'result': 64, 'namingViolation'}` ao mover/desabilitar/habilitar** — *(corrigido)* era `modify_dn` recebendo o caminho completo em vez de só o RDN. Hoje usa `new_superior` corretamente.

**API não reflete mudanças mesmo com `--reload`** — processo antigo do uvicorn ainda rodando: `netstat -ano | findstr :8000`, depois `taskkill /F /IM python.exe`.

**Erro genérico "Internal Server Error"** — veja o traceback no terminal do uvicorn e o `api_ad.log`.

## Problemas Conhecidos

**Troca de senha e reabilitação falham silenciosamente sem TLS.** O AD recusa a extensão de troca de senha em conexões sem criptografia. A API já tenta StartTLS automaticamente, mas o controlador de domínio de testes (Windows Server 2003) recusa essa negociação — provavelmente por falta de certificado configurado. Não é problema de permissão da conta de serviço, como se suspeitava antes.

**Próximo passo:** confirmar com o administrador do domínio se dá pra configurar certificado TLS (LDAPS na 636, ou StartTLS na 389). Ainda não confirmado se o AD de produção tem o mesmo problema.

## Auditoria e LGPD

Toda ação é registrada no SQLite: quem fez (`username`), o quê (`action`, `target_user`), quando (`timestamp`), de onde (`ip_address`, `user_agent`), e se deu certo (`status`). O CPF informado na criação de usuário só fica no banco de auditoria (`ad_audit.db`, fora do Git) — nunca em log ou resposta de erro. Acesso ao servidor e aos endpoints de auditoria deve ser restrito a pessoal autorizado.

## Estrutura do Projeto

```
app/
├── core/          # config, conexão LDAP (com StartTLS), JWT, logs
├── routers/       # users.py, audit.py
├── schemas/       # user.py, audit.py
├── services/      # ad_service.py
├── audit_service.py
├── database.py
└── main.py        # inclui /, /health, /versao

scripts/    # scripts auxiliares de investigação/diagnóstico do AD
tests/      # test_api.py, test_ad.py, test_success_path.py
```

## Autora

**Yasmin Fernanda de Carvalho**
E-mail: yasmincarvalho.dev06@gmail.com · GitHub: [Yaswsxz](https://github.com/Yaswsxz)
*Estagiária de Desenvolvimento — Prefeitura Municipal de Londrina*

Projeto interno - Prefeitura Municipal de Londrina/PR