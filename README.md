# API de Gerenciamento de Usuários - Active Directory

API RESTful desenvolvida para gerenciar usuários no Active Directory da Prefeitura de Londrina, com foco em automação, segurança e auditoria completa.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Endpoints da API](#endpoints-da-api)
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

---

## Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| CRUD de Usuários | Criar, listar, buscar, atualizar e remover usuários no AD |
| Gerenciamento de Senhas | Troca de senha com geração automática |
| Controle de Contas | Habilitar e desabilitar usuários |
| Autenticação | Login e logout com registro de tentativas |
| Auditoria Completa | Registro de todas as ações no SQLite |
| Documentação Automática | Swagger UI e Redoc |

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
│  (core/) - Conexão LDAP, configurações     │
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

### 2. Crie e ative um ambiente virtual (opcional)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências (usando Python 3.11)

```bash
py -3.11 -m pip install -r requirements.txt
```

### 4. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:

```env
# Active Directory
AD_SERVER=ldap://seu-servidor-ad
AD_DOMAIN=seu-dominio.local
AD_BASE_DN=DC=seu-dominio,DC=local
AD_USER_OU=OU=Usuarios,DC=seu-dominio,DC=local
AD_BIND_USER=svc_api@seu-dominio.local
AD_BIND_PASSWORD=sua_senha

# Banco de Dados
DATABASE_URL=sqlite:///./ad_audit.db
```

### 5. Execute a API (sempre com Python 3.11)

```bash
py -3.11 -m uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

---

## Endpoints da API

### Usuários (prefixo: `/usuarios`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/usuarios` | Lista todos os usuários |
| GET | `/usuarios/{login}` | Busca um usuário específico |
| POST | `/usuarios` | Cria um novo usuário |
| PUT | `/usuarios/{login}` | Atualiza dados do usuário |
| DELETE | `/usuarios/{login}` | Remove um usuário |
| POST | `/usuarios/{login}/trocar-senha` | Troca a senha |
| POST | `/usuarios/{login}/habilitar` | Ativa a conta |
| POST | `/usuarios/{login}/desabilitar` | Desativa a conta |
| POST | `/usuarios/auth` | Autentica um usuário |
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
│   ├── core/               # Configurações e utilidades
│   │   ├── config.py       # Variáveis de ambiente
│   │   ├── generators.py   # Geradores de login/senha
│   │   └── ldap_connection.py  # Conexão com AD
│   ├── routers/            # Endpoints
│   │   ├── users.py        # Rotas de usuários
│   │   └── audit.py        # Rotas de auditoria
│   ├── schemas/            # Validação de dados
│   │   └── user.py         # Schemas Pydantic
│   ├── services/           # Lógica de negócio
│   │   └── ad_service.py   # Integração com AD
│   ├── audit_service.py    # Serviço de auditoria
│   ├── database.py         # Modelos SQLAlchemy
│   └── main.py             # Ponto de entrada
├── .env                    # Configurações (não versionar)
├── .env.example            # Template de configurações
├── .gitignore              # Arquivos ignorados
├── README.md               # Documentação
└── requirements.txt        # Dependências
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