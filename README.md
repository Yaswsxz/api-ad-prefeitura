# API de Gerenciamento de Usuários - Active Directory

API RESTful para gerenciar a estrutura organizacional e as identidades no Active Directory da Prefeitura de Londrina, com auditoria completa de todas as ações.

## Sobre

Dois níveis de gerenciamento:

- **Estrutura (OUs)**: criar/alterar órgãos nos 4 ramos — Direta, Indireta, Terceirizadas, Prepostos.
- **Identidades**: criar/alterar estagiários, servidores de carreira, comissionados e contas não-humanas dentro de cada unidade da Direta.

Mais: busca, autenticação, troca de senha, logout e auditoria completa.

**Camadas:** `routers/` → `services/` → `core/` (LDAP, config, JWT, logs). Auditoria em SQLite, separado do AD.

**Stack:** Python 3.11, FastAPI, ldap3, SQLAlchemy + SQLite, Pydantic, JWT, pytest.

## Estrutura do AD

Árvore com 3 troncos, cada um com os mesmos 4 ramos:

```
PML
 ├── Operativos       (ativo)
 ├── Inoperantes       (espelho — quem sai de operação vai pra cá)
 └── Desincorporados   (só OU que deixou de existir — caso raro)
      └── cada um: Direta / Indireta / Terceirizadas / Prepostos
```

Dentro de cada unidade da **Direta** existem 4 subcontainers fixos, criados automaticamente: `Estagio`, `Carreira`, `Comissionados`, `NaoHumanos`.

Tudo é criado como `organizationalUnit` (`OU=`), não container.

**Sem DELETE de pessoa:** quem sai de operação é movido de `Operativos` pra `Inoperantes` (nunca apagado). Remoção física só a partir de `Inoperantes` (pessoa) ou `Desincorporados` (OU).

**`pmlNomeOrgao`:** atributo customizado sugerido no documento da API, mas ainda não existe no schema do AD. A API detecta isso sozinha e usa `description` como substituto até o schema ser estendido — nada a fazer aqui.

## Instalação

```bash
git clone https://github.com/Yaswsxz/api-ad-prefeitura.git
cd api-ad-prefeitura
python -m venv venv
venv\Scripts\activate          # Windows
py -3.11 -m pip install -r requirements.txt
py -3.11 -m pip install pycryptodome   # necessário pro NTLM
```

`.env` (baseado em `.env.example`):

```env
AD_SERVER=ldap://seu-servidor-ad
AD_DOMAIN=seu-dominio.local
AD_BASE_DN=OU=DESENVOL,DC=seu-dominio,DC=local
AD_SEARCH_BASE=OU=DESENVOL,DC=seu-dominio,DC=local
AD_BIND_USER=dominio\usuario_servico
AD_BIND_PASSWORD=sua_senha
AD_PML_BASE=OU=PML,OU=DESENVOL,DC=seu-dominio,DC=local
DATABASE_URL=sqlite:///./ad_audit.db
```

```bash
py -3.11 -m uvicorn app.main:app --reload   # http://localhost:8000/docs
py -3.11 -m pytest tests/ -v
```

## Endpoints principais

| Prefixo | O que faz |
|---|---|
| `/estrutura/unidades` | Criar/alterar/desincorporar/remover OU |
| `/identidade/humanos` | Criar/alterar/remover pessoa |
| `/usuarios` | Login, busca, troca de senha, logout ("Ferramentas") |
| `/auditoria` | Histórico de login e atividades |

Documentação completa e interativa: `/docs` (Swagger).

## Montando a árvore no AD

```bash
py -3.11 scripts\criar_estrutura_ad.py --dry-run       # só mostra
py -3.11 scripts\criar_estrutura_ad.py --so-esqueleto   # só os containers vazios
py -3.11 scripts\criar_estrutura_ad.py                  # esqueleto + unidades
```

Editar a lista `UNIDADES` no topo do script conforme novos órgãos forem confirmados.

## Problemas conhecidos

- **Troca de senha/reabilitação falha sem TLS** — AD recusa StartTLS no controlador atual; pendente de certificado.
- **`pmlNomeOrgao` não existe no schema** — workaround já aplicado (usa `description`).

## Troubleshooting rápido

| Sintoma | Causa provável |
|---|---|
| `ValueError: unsupported hash type MD4` | falta `pycryptodome` |
| `noSuchObject` | `.env` errado, ou `AD_PML_BASE` incorreto |
| API não reflete mudança / "Failed to fetch" | processo antigo do uvicorn ainda rodando — `Get-Process python* \| Stop-Process -Force` |
| Pylance sublinhando imports | interpretador errado no VS Code — `Ctrl+Shift+P` → Select Interpreter |

## Auditoria e LGPD

Toda ação registrada no SQLite: quem, o quê, quando, de onde, e se deu certo. CPF só fica no banco de auditoria (fora do Git), nunca em log.

## Git

- **GitHub** (`origin`): push direto, sem branch — `git push origin <branch>:main --force`.
- **GitLab** (`gitlab`, oficial, `main` protegida): branch diária `correcoes-DD-MM` a partir de `gitlab/main`, com Merge Request.

## Autora

**Yasmin Fernanda de Carvalho** — Estagiária de Desenvolvimento, Prefeitura Municipal de Londrina
yasmincarvalho.dev06@gmail.com · [GitHub](https://github.com/Yaswsxz)