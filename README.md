# API de Gerenciamento de Usuários - Active Directory

API RESTful desenvolvida para gerenciar usuários no Active Directory da Prefeitura de Londrina, com foco em automação, segurança e auditoria completa.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura](#arquitetura)
- [Estrutura do Active Directory](#estrutura-do-active-directory)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Endpoints da API](#endpoints-da-api)
- [Exemplo de Requisição](#exemplo-de-requisição)
- [Solução de Problemas (Troubleshooting)](#solução-de-problemas-troubleshooting)
- [Auditoria e LGPD](#auditoria-e-lgpd)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Autora](#autora)

---

## Sobre o Projeto

Esta API foi desenvolvida para automatizar e centralizar o gerenciamento de usuários no Active Directory da Prefeitura de Londrina. Ela permite:

- Criar, editar, remover e consultar usuários
- Trocar senhas (automáticas ou personalizadas)
- Habilitar e desabilitar contas
- Autenticar usuários no AD
- Auditoria completa de todas as ações (LGPD)
- **Logs detalhados para facilitar diagnósticos**
- **Autenticação com JWT para segurança das rotas**
- **Testes automatizados para garantir estabilidade**

---

## Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| CRUD de Usuários | Criar, listar, buscar, atualizar e remover usuários no AD |
| Gerenciamento de Senhas | Troca de senha com geração automática |
| Controle de Contas | Habilitar e desabilitar usuários (move entre containers Ativos/Inativos) |
| Autenticação | Login e logout com registro de tentativas |
| Auditoria Completa | Registro de todas as ações no SQLite |
| Documentação Automática | Swagger UI e Redoc |
| **Logs Detalhados** | **Registro de todas as operações em arquivo e console** |
| **Autenticação JWT** | **Proteção das rotas com token de acesso** |
| **Testes Automatizados** | **Validação contínua da API com pytest** |

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.115.0 | Framework web |
| LDAP3 | 2.9.1 | Comunicação com Active Directory |
| SQLAlchemy | 2.0.52 | ORM para banco de dados |
| SQLite | - | Banco de dados local (auditoria) |
| Pydantic | 2.9.2 | Validação de dados |
| Uvicorn | 0.30.6 | Servidor ASGI |
| **python-jose** | **3.5.0** | **JWT (autenticação)** |
| **passlib** | **1.7.4** | **Hash de senhas** |
| **pytest** | **9.1.1** | **Testes automatizados** |
| **pycryptodome** | **-** | **Suporte a hash MD4/NTLM exigido pelo `ldap3` em builds recentes do Python (ver Troubleshooting)** |

---

## Arquitetura

A API segue o padrão de arquitetura em camadas:

```
┌─────────────────────────────────────────────┐
│          CAMADA DE APRESENTAÇÃO             │
│  (routers/) - Endpoints e validação        │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│          CAMADA DE NEGÓCIO                  │
│  (services/) - Regras de negócio           │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│       CAMADA DE INFRAESTRUTURA             │
│  (core/) - Conexão LDAP, configurações,    │
│            logs, autenticação JWT          │
└─────────────────────────────────────────────┘
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
┌──────────────────┐     ┌──────────────────────┐
│ Active Directory │     │  SQLite (Auditoria)  │
│    (LDAP)        │     │  - login_history     │
│                  │     │  - activity_history  │
└──────────────────┘     └──────────────────────┘
```

---

## Estrutura do Active Directory

A API opera dentro da seguinte hierarquia no AD da prefeitura (domínio `DC=londrina,DC=pr,DC=gov,DC=br`):

```
OU=DESENVOL
└── OU=PML
    ├── CN=Ativos                  (container)
    │   ├── CN=CODEL               (container - subsetor)
    │   ├── CN=CMTU                (container - subsetor)
    │   ├── CN=Planejamento        (container - subsetor)
    │   ├── CN=Ouvidoria           (container - subsetor)
    │   ├── CN=Saude               (container - subsetor)
    │   └── CN=Sercontel           (container - subsetor)
    └── CN=Inativos                (container)
        ├── CN=CODEL
        ├── CN=CMTU
        ├── CN=Planejamento
        ├── CN=Ouvidoria
        ├── CN=Saude
        └── CN=Sercontel
```

**Pontos importantes:**

- `Ativos`, `Inativos` e os subsetores (`CODEL`, `CMTU`, etc.) são **containers** (`CN=`), **não** Organizational Units (`OU=`). Usar `OU=` no lugar de `CN=` para esses objetos gera erro `noSuchObject`.
- Ao criar um usuário, o campo `subcontainer` do payload **precisa** ser um dos nomes reais listados acima — qualquer outro valor (inclusive o exemplo padrão do Swagger, `"ContainerA"`) causa falha na criação.
- Para investigar a estrutura real do AD a qualquer momento (ex: se novos subsetores forem criados), use um script simples com `ldap3`:

```python
from ldap3 import Server, Connection, SUBTREE

server = Server("cegonha.londrina.pr.gov.br")
conn = Connection(server, user="pmldomain\\<usuario_servico>", password="<senha>", auto_bind=True)

conn.search(
    search_base="OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
    search_filter="(objectClass=*)",
    search_scope=SUBTREE,
    attributes=["objectClass", "name"],
)

for entry in conn.entries:
    print(entry.entry_dn, "| classes:", list(entry.objectClass))

conn.unbind()
```

---

## Pré-requisitos

Antes de começar, você vai precisar ter instalado:

- Python **3.11** (ou superior, mas com suporte confirmado para 3.11)
- Acesso à rede da Prefeitura de Londrina (ou VPN)
- Credenciais do Active Directory
- Git (para clonar o repositório)

⚠️ **Importante:** Este projeto é compatível e foi testado com **Python 3.11**. Para evitar erros de instalação (como do `pydantic-core`), utilize a versão 3.11 no comando `py -3.11`.

---

## Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/Yaswsxz/api-ad-prefeitura.git
cd api-ad-prefeitura
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências (usando Python 3.11)

```bash
py -3.11 -m pip install -r requirements.txt
```

Se o `requirements.txt` ainda não incluir o `pycryptodome`, instale manualmente (necessário para autenticação NTLM no LDAP — ver [Troubleshooting](#solução-de-problemas-troubleshooting)):

```bash
py -3.11 -m pip install pycryptodome
```

### 4. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:

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

# Banco de Dados
DATABASE_URL=sqlite:///./ad_audit.db
```

**Atenção:** `AD_BASE_DN`, `AD_ATIVOS_BASE` e `AD_INATIVOS_BASE` precisam refletir exatamente a hierarquia real do AD (ver [Estrutura do Active Directory](#estrutura-do-active-directory)). Um caminho incorreto ou incompleto causa erro `noSuchObject` mesmo que o restante da configuração esteja certo.

### 5. Execute a API (sempre com Python 3.11)

```bash
py -3.11 -m uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

### 6. Rodar os testes automatizados

```bash
py -3.11 -m pytest tests/ -v
```

---

## Endpoints da API

### Usuários (prefixo: `/usuarios`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/usuarios` | Lista todos os usuários (protegido por JWT) |
| GET | `/usuarios/{login}` | Busca um usuário específico (protegido por JWT) |
| POST | `/usuarios` | Cria um novo usuário (protegido por JWT) |
| PUT | `/usuarios/{login}` | Atualiza dados do usuário (protegido por JWT) |
| DELETE | `/usuarios/{login}` | Remove um usuário (protegido por JWT) |
| POST | `/usuarios/{login}/trocar-senha` | Troca a senha (protegido por JWT) |
| POST | `/usuarios/{login}/habilitar` | Ativa a conta (protegido por JWT) |
| POST | `/usuarios/{login}/desabilitar` | Desativa a conta (protegido por JWT) |
| POST | `/usuarios/auth` | Autentica um usuário |
| POST | `/usuarios/{login}/logout` | Registra logout |
| **POST** | **`/usuarios/login`** | **Login e geração de token JWT** |

### Auditoria (prefixo: `/auditoria`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/auditoria/login-history` | Histórico de logins e logouts |
| GET | `/auditoria/activity-history` | Histórico de ações |
| GET | `/auditoria/user-summary/{login}` | Resumo de atividades por usuário |
| GET | `/auditoria/security-report` | Relatório de segurança |

### Documentação Interativa

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

---

## Exemplo de Requisição

### Criar usuário — `POST /usuarios`

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

**Campos obrigatórios:** `primeiro_nome`, `ultimo_nome`, `subcontainer`.
`subcontainer` deve ser um dos setores reais existentes no AD (ver [Estrutura do Active Directory](#estrutura-do-active-directory)) — usar um valor inexistente (como o exemplo padrão do Swagger, `"ContainerA"`) resulta em erro `noSuchObject`.

**Resposta esperada (201):**

```json
{
  "login": "joao.silva",
  "nome_completo": "Joao Silva",
  "email": "joao.silva@londrina.pr.gov.br",
  "cargo": "Analista Administrativo",
  "ativo": false,
  "distinguished_name": "CN=Joao Silva,CN=CODEL,CN=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
  "senha_gerada": "SenhaGerada123!"
}
```

> Novos usuários são criados com a conta **desabilitada** por padrão (`ativo: false`), e habilitados posteriormente pelo endpoint `/usuarios/{login}/habilitar`.

---

## Solução de Problemas (Troubleshooting)

### Erro: `ValueError: unsupported hash type MD4`

**Causa:** o `ldap3` usa autenticação NTLM, que depende do algoritmo MD4. Builds recentes do Python/OpenSSL removeram suporte nativo a MD4 por ser considerado obsoleto, e a biblioteca de fallback (`pycryptodome`) não está instalada.

**Solução:**
```bash
pip install pycryptodome
```
Reinicie o servidor (`Ctrl+C` e rode `uvicorn` de novo) após instalar.

### Erro: `{'result': 32, 'description': 'noSuchObject', ...}`

**Causa:** o caminho (DN) usado na operação não existe no AD. As causas mais comuns:
- Variáveis do `.env` (`AD_BASE_DN`, `AD_ATIVOS_BASE`, `AD_INATIVOS_BASE`) com caminho incompleto, na ordem errada, ou usando `OU=` em vez de `CN=` para containers.
- Campo `subcontainer` não enviado no request, ou enviado com um valor que não existe no AD (ex: o placeholder `"ContainerA"` do Swagger).

**Como investigar:** rode o script de listagem da árvore do AD (ver [Estrutura do Active Directory](#estrutura-do-active-directory)) para confirmar os caminhos reais e comparar com o `.env`.

### A API não reflete mudanças no código, mesmo com `--reload`

**Causa:** processos antigos do `uvicorn` continuam rodando em segundo plano e ocupando a porta 8000, fazendo o Swagger conversar com uma versão desatualizada do servidor.

**Como verificar:**
```powershell
netstat -ano | findstr :8000
```
Se aparecer mais de um processo (`LISTENING`), há instâncias duplicadas.

**Solução:**
```powershell
taskkill /F /IM python.exe
```
Depois, confirme que a porta está livre (`netstat -ano | findstr :8000` deve retornar vazio) e suba o servidor novamente com um único terminal.

### O erro retornado é genérico (`"Internal Server Error"`, sem detalhes)

Isso indica uma exceção não tratada pelo código (fora do bloco `except LDAPException`). Consulte o **traceback completo no terminal onde o `uvicorn` está rodando** — ele aponta o arquivo e a linha exata da falha.

---

## Auditoria e LGPD

Todas as ações realizadas na API são registradas automaticamente no SQLite, garantindo:

| Requisito LGPD | Como é atendido |
|----------------|-----------------|
| Rastreabilidade | Toda ação é registrada |
| Quem fez o quê | `username` + `action` + `target_user` |
| Quando | `timestamp` |
| De onde | `ip_address` + `user_agent` |
| Sucesso ou falha | `status` (SUCCESS/FAILED) |

---

## Estrutura do Projeto

```
ApiTeste/
├── app/
│   ├── core/                     # Configurações e utilidades
│   │   ├── config.py             # Variáveis de ambiente
│   │   ├── generators.py         # Geradores de login/senha
│   │   ├── ldap_connection.py    # Conexão com AD
│   │   ├── auth.py               # Autenticação JWT
│   │   └── logging_config.py     # Logs detalhados
│   ├── routers/                  # Endpoints
│   │   ├── users.py              # Rotas de usuários
│   │   └── audit.py              # Rotas de auditoria
│   ├── schemas/                  # Validação de dados
│   │   └── user.py               # Schemas Pydantic
│   ├── services/                 # Lógica de negócio
│   │   └── ad_service.py         # Integração com AD
│   ├── audit_service.py          # Serviço de auditoria
│   ├── database.py               # Modelos SQLAlchemy
│   └── main.py                   # Ponto de entrada
├── scripts/                      # Scripts auxiliares (investigação/diagnóstico do AD)
├── tests/                        # Testes automatizados
│   └── test_api.py               # Testes da API
├── .env                          # Configurações (não versionar)
├── .env.example                  # Template de configurações
├── .gitignore                    # Arquivos ignorados
├── README.md                     # Documentação
└── requirements.txt              # Dependências
```

---

## Autora

**Yasmin Fernanda de Carvalho**
E-mail: yasmincarvalho.dev06@gmail.com
GitHub: [Yaswsxz](https://github.com/Yaswsxz)

*Estagiária de Desenvolvimento - Prefeitura Municipal de Londrina*

---

## Licença

Projeto interno - Prefeitura Municipal de Londrina/PR