# API Gerenciador de Usuários - Active Directory

API REST em **FastAPI** para a prefeitura gerenciar contas de funcionários/estagiários
diretamente no **Active Directory**, via protocolo **LDAP** (funciona com qualquer versão
do AD, incluindo a de 2006/Windows Server 2003).

## Funcionalidades

| Operação | Método | Rota |
|---|---|---|
| Listar/buscar usuários | GET | `/usuarios?nome=joao` |
| Consultar um usuário | GET | `/usuarios/{login}` |
| Criar usuário | POST | `/usuarios` |
| Atualizar usuário | PUT | `/usuarios/{login}` |
| Remover usuário | DELETE | `/usuarios/{login}` |
| Trocar senha | POST | `/usuarios/{login}/trocar-senha` |
| Desabilitar usuário | POST | `/usuarios/{login}/desabilitar` |
| Habilitar usuário | POST | `/usuarios/{login}/habilitar` |

## Como rodar localmente

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
copy .env.example .env       # Windows
cp .env.example .env         # Linux/Mac
# edite o .env com os dados reais do seu Active Directory

# 4. Rodar a API
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`.
Documentação interativa (Swagger) automática em `http://localhost:8000/docs`.

## Sobre a conexão com o AD

- Para **apenas ler** dados (listar/buscar), uma conexão LDAP simples (porta 389) já funciona.
- Para **criar, trocar senha ou desabilitar** contas, o Active Directory **exige** uma conexão
  criptografada — use `ldaps://` (porta 636) no `.env`. Se o seu controlador de domínio
  ainda não tem LDAPS habilitado, isso precisa ser configurado no servidor (certificado no DC)
  antes dessas operações funcionarem.
- A conta de serviço (`AD_BIND_USER`) usada pela API precisa ter permissão delegada no AD
  para criar/alterar objetos de usuário na OU configurada (`AD_USER_OU`).

## Geração automática de login e senha

- Login: `primeiro.ultimo` (minúsculo, sem acentos), conforme padrão definido.
- Senha: 8 caracteres aleatórios, com maiúscula, minúscula, número e símbolo
  (atende à política de complexidade padrão do AD).

## Estrutura do projeto

```
ad-api/
├── app/
│   ├── main.py                 # ponto de entrada da aplicação
│   ├── core/
│   │   ├── config.py           # configurações via .env
│   │   ├── ldap_connection.py  # conexão com o AD
│   │   └── generators.py       # geração de login/senha
│   ├── schemas/
│   │   └── user.py             # modelos Pydantic (entrada/saída)
│   ├── services/
│   │   └── ad_service.py       # regras de negócio + chamadas LDAP
│   └── routers/
│       └── users.py            # rotas da API
├── requirements.txt
├── .env.example
└── README.md
```

## Próximos passos sugeridos

- Adicionar autenticação na própria API (ex: JWT) para que só usuários autorizados
  da prefeitura possam chamá-la — hoje as rotas estão abertas.
- Testar a conexão LDAPS com o controlador de domínio real antes de ir para produção.
- Conectar o frontend (HTML/CSS/JS) que você já tinha planejado a estas rotas.
