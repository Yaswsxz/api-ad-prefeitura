# API de Gerenciamento de Usuários - Active Directory

API RESTful desenvolvida para gerenciar usuários no Active Directory da Prefeitura de Londrina, com foco em automação, segurança e auditoria completa.

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
- [Gestão de Setores e Consistência](#gestão-de-setores-e-consistência)
- [Solução de Problemas (Troubleshooting)](#solução-de-problemas-troubleshooting)
- [Problemas Conhecidos](#problemas-conhecidos)
- [Auditoria e LGPD](#auditoria-e-lgpd)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Autora](#autora)

## Sobre o Projeto

Esta API foi desenvolvida para automatizar e centralizar o gerenciamento de usuários no Active Directory da Prefeitura de Londrina. Ela permite:

- Criar, editar, remover e consultar usuários
- Trocar senhas (automáticas ou personalizadas)
- Habilitar e desabilitar contas, preservando o setor do usuário
- Transferir usuários entre setores sem alterar o status ativo/inativo
- Detectar e corrigir inconsistências entre o status real da conta e a pasta onde está armazenada
- Identificar e remover contas de teste, sempre com revisão manual antes da remoção
- Autenticar usuários no AD
- Auditoria completa de todas as ações (LGPD)

## Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| CRUD de Usuários | Criar, listar, buscar, atualizar e remover usuários no AD |
| Gerenciamento de Senhas | Troca de senha com geração automática |
| Controle de Contas | Habilitar e desabilitar usuários, preservando o subcontainer (setor) de origem |
| Transferência de Setor | Move um usuário entre setores sem alterar seu status ativo/inativo |
| Validação de Setores | Impede criar ou transferir usuário para um setor que não existe no AD |
| Detecção de Inconsistências | Encontra usuários cujo status real diverge da pasta onde estão guardados |
| Correção em Lote | Corrige automaticamente as inconsistências detectadas |
| Identificação de Contas de Teste | Sinaliza contas suspeitas de serem teste (nunca remove sozinha) |
| Remoção em Lote | Remove apenas os logins explicitamente confirmados pelo operador |
| Autenticação | Login e logout com registro de tentativas |
| Auditoria Completa | Registro de todas as ações no SQLite, incluindo CPF e tipo de vínculo |
| Documentação Automática | Swagger UI e Redoc |

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
| python-jose | 3.5.0 | JWT (autenticação) |
| passlib | 1.7.4 | Hash de senhas |
| pytest | 9.1.1 | Testes automatizados |
| pycryptodome | - | Suporte a hash MD4/NTLM exigido pelo `ldap3` em builds recentes do Python (ver Troubleshooting) |

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
- Ao criar ou transferir um usuário, o campo `subcontainer`/`novo_subcontainer` **precisa** ser um dos nomes reais existentes no AD. A API valida isso automaticamente contra o AD em tempo real (não depende de lista fixa no código) — consulte `GET /usuarios/setores` para ver os valores aceitos no momento.
- Novos setores criados diretamente no AD já são reconhecidos pela API automaticamente, sem precisar alterar código.

## Pré-requisitos

Antes de começar, você vai precisar ter instalado:

- Python **3.11** (ou superior, mas com suporte confirmado para 3.11)
- Acesso à rede da Prefeitura de Londrina (ou VPN)
- Credenciais do Active Directory
- Git (para clonar o repositório)

⚠️ **Importante:** Este projeto é compatível e foi testado com **Python 3.11**. Para evitar erros de instalação (como do `pydantic-core`), utilize a versão 3.11 no comando `py -3.11`.

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

**Atenção:** `AD_BASE_DN`, `AD_ATIVOS_BASE` e `AD_INATIVOS_BASE` precisam refletir exatamente a hierarquia real do AD (ver [Estrutura do Active Directory](#estrutura-do-active-directory)). Um caminho incorreto ou incompleto causa erro `noSuchObject` mesmo que o restante da configuração esteja correto.

### 5. Execute a API (sempre com Python 3.11)

```bash
py -3.11 -m uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

### 6. Rodar os testes automatizados

```bash
py -3.11 -m pytest tests/ -v
```

## Endpoints da API

### Usuários (prefixo: `/usuarios`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/usuarios/setores` | Lista os setores (subcontainers) reais existentes dentro de Ativos |
| GET | `/usuarios/inconsistencias` | Detecta usuários com status divergente da pasta onde estão |
| POST | `/usuarios/inconsistencias/corrigir` | Corrige automaticamente as inconsistências detectadas |
| GET | `/usuarios/candidatos-teste` | Sinaliza possíveis contas de teste (não remove nada) |
| POST | `/usuarios/deletar-lote` | Remove apenas os logins explicitamente informados |
| GET | `/usuarios` | Lista/busca usuários |
| GET | `/usuarios/{login}` | Consulta um usuário pelo login |
| POST | `/usuarios` | Cria um novo usuário |
| PUT | `/usuarios/{login}` | Atualiza dados do usuário (cargo, tipo, email, telefone) |
| DELETE | `/usuarios/{login}` | Remove um usuário do AD |
| POST | `/usuarios/{login}/trocar-senha` | Troca a senha de um usuário |
| POST | `/usuarios/{login}/desabilitar` | Desativa a conta e move para Inativos |
| POST | `/usuarios/{login}/habilitar` | Reativa a conta e move para Ativos |
| POST | `/usuarios/{login}/transferir-setor` | Move o usuário para outro setor, mantendo o status atual |
| POST | `/usuarios/auth` | Autentica um usuário no AD |
| POST | `/usuarios/{login}/logout` | Registra logout |

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
`subcontainer` deve ser um dos setores reais existentes no AD — consulte `GET /usuarios/setores` para a lista atualizada. Um valor inexistente (como o placeholder padrão do Swagger, `"ContainerA"`) resulta em erro `422` antes mesmo de tentar criar o usuário.

`tipo` (`efetivo`/`estagiario`) é salvo permanentemente no cadastro (atributo `description` no AD) e pode ser consultado ou atualizado depois. `cpf` não é salvo no AD, mas fica registrado no histórico de auditoria da criação.

**Resposta esperada (201):**

```json
{
  "login": "joao.silva",
  "nome_completo": "Joao Silva",
  "email": "joao.silva@londrina.pr.gov.br",
  "cargo": "Analista Administrativo",
  "tipo": "efetivo",
  "ativo": false,
  "distinguished_name": "CN=Joao Silva,CN=CODEL,CN=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
  "senha_gerada": "SenhaGerada123!"
}
```

> Novos usuários são criados com a conta **desabilitada** por padrão (`ativo: false`).

## Gestão de Setores e Consistência

### Transferir usuário entre setores

`POST /usuarios/{login}/transferir-setor?novo_subcontainer=Saude` move o usuário para outro setor sem alterar seu status atual (quem está em Ativos permanece em Ativos, quem está em Inativos permanece em Inativos). A API identifica sozinha em qual dos dois o usuário está hoje.

### Detectar e corrigir inconsistências

Um usuário é considerado inconsistente quando o status real da conta (`userAccountControl`) não bate com a pasta onde está guardado — por exemplo, uma conta desabilitada que continua fisicamente dentro de `Ativos`.

```
GET  /usuarios/inconsistencias           → lista os casos encontrados
POST /usuarios/inconsistencias/corrigir  → move cada um para a pasta correta
```

### Identificar e remover contas de teste

Esse fluxo é sempre em duas etapas separadas — a API nunca decide sozinha o que apagar:

```
GET  /usuarios/candidatos-teste  → sugere contas suspeitas (email placeholder "string",
                                     nome/login contendo "teste"/"test")
POST /usuarios/deletar-lote      → remove SOMENTE os logins que você revisou e confirmou
```

```json
{
  "logins": ["usuario.teste", "exemplo.silva"]
}
```

## Solução de Problemas (Troubleshooting)

### Erro: `ValueError: unsupported hash type MD4`

**Causa:** o `ldap3` usa autenticação NTLM, que depende do algoritmo MD4. Builds recentes do Python/OpenSSL removeram suporte nativo a MD4, e a biblioteca de fallback (`pycryptodome`) não está instalada.

**Solução:**
```bash
pip install pycryptodome
```
Reinicie o servidor após instalar.

### Erro: `{'result': 32, 'description': 'noSuchObject', ...}`

**Causa:** o caminho (DN) usado na operação não existe no AD — variáveis do `.env` incompletas/na ordem errada, `OU=` usado no lugar de `CN=`, ou `subcontainer` inexistente.

**Como investigar:** consulte `GET /usuarios/setores`, ou rode o script de listagem da árvore do AD (ver [Estrutura do Active Directory](#estrutura-do-active-directory)).

### Erro: `{'result': 64, 'description': 'namingViolation', ...}` ao mover/desabilitar/habilitar usuário

**Causa (corrigida):** a função de mover usuário usava `conn.modify_dn(dn_atual, novo_dn_completo)`, passando o caminho inteiro no lugar onde o `ldap3` espera apenas o novo nome (RDN). O AD tentava interpretar o caminho completo como um único atributo de nome e recusava a operação.

**Solução aplicada:** o `modify_dn` agora usa o parâmetro `new_superior` para indicar o destino, e passa somente `CN={nome}` como novo RDN. Essa correção afeta todas as operações que movem usuário: desabilitar, habilitar, transferir setor e corrigir inconsistências.

### A API não reflete mudanças no código, mesmo com `--reload`

**Causa:** processos antigos do `uvicorn` continuam rodando em segundo plano na porta 8000.

**Como verificar:**
```powershell
netstat -ano | findstr :8000
```

**Solução:**
```powershell
taskkill /F /IM python.exe
```
Confirme que a porta está livre e suba o servidor novamente em um único terminal.

### O erro retornado é genérico (`"Internal Server Error"`, sem detalhes)

Indica uma exceção não tratada pelo código. Consulte o **traceback completo no terminal onde o `uvicorn` está rodando**.

## Problemas Conhecidos

### `habilitar` e `trocar-senha` retornam `unwillingToPerform` (código 53)

Ao reabilitar uma conta ou trocar a senha de um usuário já existente, o AD recusa a operação com `{'result': 53, 'description': 'unwillingToPerform', ...}`, mesmo com dados válidos. **Desabilitar** e **criar usuário** (que também define senha) funcionam normalmente com a mesma conexão e o mesmo usuário de serviço.

**Hipótese mais provável:** a conta de serviço configurada em `AD_BIND_USER` pode ter permissão delegada no AD para desabilitar/mover contas, mas não para reabilitá-las ou redefinir senha de contas existentes — uma restrição de segurança comum, definida do lado do administrador do domínio, não do código da API.

**Próximo passo:** confirmar com o administrador do AD se a conta de serviço tem as permissões delegadas de **"Reset Password"** e **"Enable/Disable Account"** completas na OU `PML`.

## Auditoria e LGPD

Todas as ações realizadas na API são registradas automaticamente no SQLite, garantindo:

| Requisito LGPD | Como é atendido |
|----------------|-----------------|
| Rastreabilidade | Toda ação é registrada |
| Quem fez o quê | `username` + `action` + `target_user` |
| Quando | `timestamp` |
| De onde | `ip_address` + `user_agent` |
| Sucesso ou falha | `status` (SUCCESS/FAILED) |

O CPF informado na criação de um usuário é registrado apenas no banco de auditoria local (`ad_audit.db`, presente no `.gitignore`), nunca impresso em log de console ou incluído em respostas de erro. O acesso ao servidor onde a API roda, e a qualquer endpoint de auditoria, deve ser restrito a pessoal autorizado.

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
├── scripts/                      # Scripts auxiliares de investigação/diagnóstico do AD
│   ├── listar_ous.py
│   ├── criar_usuario_manual.py
│   ├── verificar_env.py
│   └── migrar_users_para_ativos.py
├── tests/                        # Testes automatizados (pytest)
│   ├── test_api.py
│   └── test_ad.py
├── .env                          # Configurações (não versionar)
├── .env.example                  # Template de configurações
├── .gitignore                    # Arquivos ignorados
├── README.md                     # Documentação
└── requirements.txt              # Dependências
```

## Autora

**Yasmin Fernanda de Carvalho**
E-mail: yasmincarvalho.dev06@gmail.com
GitHub: [Yaswsxz](https://github.com/Yaswsxz)

*Estagiária de Desenvolvimento - Prefeitura Municipal de Londrina*

## Licença

Projeto interno - Prefeitura Municipal de Londrina/PR