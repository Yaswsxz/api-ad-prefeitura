"""
AD em memória para os testes de serviço: nenhuma rede, nenhum Active Directory.

Imita só o que a API usa: busca (com os filtros que os serviços montam), add, modify,
modify_dn (levando os filhos junto), delete e a guarda da raiz. Falhas são injetadas por
operação (`falhas[(operacao, n)]`), por atributo ausente do schema (`sem_schema`) e por falta
de TLS (`sem_tls`).
"""
import re
from typing import Optional

from ldap3 import BASE, LEVEL

from app.core.arvore import (
    HUMANO, NAO_HUMANO, OUS_INTERNAS_DIRETA, Arvore, Categoria, Ramo, TipoIdentidade,
    dn_arvore, dn_container, dn_ramo, dn_tipo, dn_unidade, rdn_cn,
)
from app.core.contexto import Contexto
from app.core.erros_ad import Codigo, ErroAD
from app.core.raiz import componentes_dn, garantir_dentro

CTX = Contexto(operador="operador-teste", ip="127.0.0.1", user_agent="pytest")

FILTRO_PESSOA = "(&(objectCategory=person)(objectClass=user))"


def erro_ad(codigo: str = Codigo.AD_PERMISSAO_NEGADA, status: int = 502) -> ErroAD:
    return ErroAD("falha simulada", codigo=codigo, status_code=status)


class ADFalso:
    def __init__(self):
        self.objs: dict[str, dict] = {}          # DN em minúsculas -> {"dn", "classe", "attrs"}
        self.ops: list[tuple] = []               # operações que deram certo
        self.filtros: list[str] = []             # filtros recebidos nas buscas
        self.auditoria: list[tuple] = []         # (acao, alvo, detalhes)
        self.falhas: dict[tuple[str, int], Exception] = {}
        self.sem_schema: set[str] = set()
        self.sem_tls = False
        self._chamadas: dict[str, int] = {}
        self.response: list[dict] = []
        self.result: dict = {"result": 0}
        for arvore in Arvore:
            self._criar_ou(dn_arvore(arvore), {})
            for tipo in TipoIdentidade:
                self._criar_ou(dn_tipo(arvore, tipo), {})
                for ramo in Ramo:
                    self._criar_ou(dn_ramo(arvore, ramo, tipo), {})

    # --- montar o cenário ---------------------------------------------------

    def _criar_ou(self, dn: str, attrs: dict) -> str:
        self.objs[dn.lower()] = {"dn": dn, "classe": "ou", "attrs": {"ou": componentes_dn(dn)[0][1], **attrs}}
        return dn

    def unidade(self, arvore: Arvore, ramo: Ramo, nome: str, **pml) -> str:
        """A unidade nos dois lados (Humanos e NaoHumanos); devolve o DN do lado Humanos."""
        for tipo in (NAO_HUMANO, HUMANO):
            dn = self._criar_ou(dn_unidade(arvore, ramo, nome, tipo), {"ou": nome, **pml})
            if tipo is HUMANO and ramo is Ramo.DIRETA:
                for interna in OUS_INTERNAS_DIRETA:
                    self._criar_ou(f"OU={interna},{dn}", {"ou": interna})
        return dn

    def espelhar(self, ramo: Ramo, nome: str, **pml) -> None:
        """A unidade em Operativos e em Inoperantes, como a API cria."""
        for arvore in (Arvore.OPERATIVOS, Arvore.INOPERANTES):
            self.unidade(arvore, ramo, nome, **pml)

    def conta(self, arvore: Arvore, ramo: Ramo, unidade: str, login: str, *, nome: Optional[str] = None,
              categoria: Optional[Categoria] = None, uac: int = 512, **pml) -> str:
        nome = nome or login
        tipo = NAO_HUMANO if login.startswith("nhu.") else HUMANO
        dn = f"{rdn_cn(nome)},{dn_container(arvore, ramo, unidade, categoria, tipo)}"
        self.objs[dn.lower()] = {"dn": dn, "classe": "user", "attrs": {
            "sAMAccountName": login, "cn": nome, "userAccountControl": uac, **pml}}
        return dn

    # --- consultar o resultado ----------------------------------------------

    def da(self, login: str) -> Optional[dict]:
        return next((o for o in self.objs.values()
                     if o["classe"] == "user" and o["attrs"]["sAMAccountName"] == login), None)

    def dn(self, login: str) -> str:
        return self.da(login)["dn"]

    def uac(self, login: str) -> int:
        return self.da(login)["attrs"]["userAccountControl"]

    def pml(self, dn: str) -> dict:
        return {k: v for k, v in self.objs[dn.lower()]["attrs"].items() if k.startswith("pml")}

    def instantaneo(self) -> dict:
        """Cópia do estado, para provar que uma operação não deixou rastro."""
        return {k: (o["dn"], dict(o["attrs"]), o.get("senha")) for k, o in self.objs.items()}

    def tipos_de_operacao(self) -> list[str]:
        return [op[0] for op in self.ops]

    def atributos_gravados(self) -> list[tuple]:
        """Nomes dos atributos de cada `modify` bem-sucedido, na ordem."""
        return [op[2] for op in self.ops if op[0] == "modify"]

    # --- a conexão ---------------------------------------------------------------

    def _tentar(self, operacao: str) -> None:
        n = self._chamadas[operacao] = self._chamadas.get(operacao, 0) + 1
        if (operacao, n) in self.falhas:
            raise self.falhas[(operacao, n)]

    def _exigir_schema(self, nomes) -> None:
        for nome in nomes:
            if nome in self.sem_schema:
                raise erro_ad(Codigo.AD_SCHEMA_INCOMPLETO)

    def add(self, dn, object_class=None, attributes=None, controls=None):
        garantir_dentro(dn, "add")
        self._tentar("add")
        attrs = dict(attributes or {})
        classes = {str(c).lower() for c in attrs.pop("objectClass", [])}
        self._exigir_schema(attrs)
        if dn.lower() in self.objs:
            raise erro_ad(Codigo.JA_EXISTE, 409)
        self.objs[dn.lower()] = {"dn": dn, "classe": "user" if "user" in classes else "ou", "attrs": attrs}
        self.ops.append(("add", dn))

    def modify(self, dn, changes, controls=None):
        garantir_dentro(dn, "modify")
        self._tentar("modify")
        self._exigir_schema(changes)
        if "unicodePwd" in changes and self.sem_tls:
            raise erro_ad(Codigo.AD_TLS_INDISPONIVEL, 503)
        objeto = self.objs[dn.lower()]
        for atributo, [(_, valores)] in changes.items():
            if atributo == "unicodePwd":
                objeto["senha"] = valores[0].decode("utf-16-le").strip('"')
            elif valores:
                objeto["attrs"][atributo] = valores[0]
            else:
                objeto["attrs"].pop(atributo, None)
        self.ops.append(("modify", dn, tuple(changes)))

    def modify_dn(self, dn, relative_dn, delete_old_dn=True, new_superior=None, controls=None):
        garantir_dentro(dn, "modify_dn (origem)")
        if new_superior:
            garantir_dentro(new_superior, "modify_dn (destino)")
        self._tentar("modify_dn")
        novo = f"{relative_dn},{new_superior}"
        if novo.lower() in self.objs:
            raise erro_ad(Codigo.JA_EXISTE, 409)
        antigo = dn.lower()
        for chave in [k for k in self.objs if k == antigo or k.endswith("," + antigo)]:
            objeto = self.objs.pop(chave)
            objeto["dn"] = objeto["dn"][:len(objeto["dn"]) - len(dn)] + novo
            self.objs[objeto["dn"].lower()] = objeto
        self.ops.append(("modify_dn", dn, new_superior))

    def delete(self, dn, controls=None):
        garantir_dentro(dn, "delete")
        self._tentar("delete")
        if any(k.endswith("," + dn.lower()) for k in self.objs):
            raise erro_ad(Codigo.OU_NAO_VAZIA, 409)
        del self.objs[dn.lower()]
        self.ops.append(("delete", dn))

    def unbind(self):
        pass

    def search(self, search_base, search_filter, search_scope="SUBTREE", attributes=None,
               paged_size=None, paged_cookie=None, **_):
        garantir_dentro(search_base, "search")
        self.filtros.append(search_filter)
        self.response = [
            {"dn": o["dn"], "type": "searchResEntry",
             "attributes": {n: [o["attrs"][n]] for n in (attributes or []) if n in o["attrs"]}}
            for o in self.objs.values()
            if self._no_escopo(o["dn"], search_base, search_scope) and self._casa(o, search_filter)
        ]
        self.result = {"result": 0}
        return True

    @staticmethod
    def _no_escopo(dn: str, base: str, escopo: str) -> bool:
        alvo, raiz = componentes_dn(dn), componentes_dn(base)
        if escopo == BASE:
            return alvo == raiz
        if escopo == LEVEL:
            return len(alvo) == len(raiz) + 1 and alvo[1:] == raiz
        return len(alvo) >= len(raiz) and alvo[len(alvo) - len(raiz):] == raiz

    @staticmethod
    def _casa(o: dict, filtro: str) -> bool:
        attrs = o["attrs"]
        if filtro == "(objectClass=*)":
            return True
        if filtro == FILTRO_PESSOA:
            return o["classe"] == "user"
        if filtro == "(objectClass=organizationalUnit)":
            return o["classe"] == "ou"
        if m := re.fullmatch(r"\(distinguishedName=(.+)\)", filtro):
            return o["dn"].lower() == m[1].lower()
        if m := re.fullmatch(r"\(&\(objectCategory=person\)\(objectClass=user\)\(sAMAccountName=(.+)\)\)", filtro):
            return o["classe"] == "user" and attrs["sAMAccountName"].lower() == m[1].lower()
        if m := re.fullmatch(r"\(&\(objectClass=organizationalUnit\)\(ou=(.+)\)\)", filtro):
            return o["classe"] == "ou" and attrs.get("ou", "").lower() == m[1].lower()
        if m := re.fullmatch(r"\(\|\(cn=(.+)\)\(ou=(.+)\)\)", filtro):
            return m[1].lower() in (attrs.get("cn", "").lower(), attrs.get("ou", "").lower())
        raise AssertionError(f"filtro não previsto pelo AD falso: {filtro}")


def semear_identidades(ad: ADFalso) -> ADFalso:
    """Cenário padrão dos testes de identidade (as OUs de cada categoria já existem)."""
    for ramo, nome in ((Ramo.DIRETA, "FAZENDA"), (Ramo.DIRETA, "EDUCACAO"), (Ramo.INDIRETA, "CODEL")):
        ad.espelhar(ramo, nome)
    op, ino = Arvore.OPERATIVOS, Arvore.INOPERANTES
    ad.conta(op, Ramo.DIRETA, "FAZENDA", "ana.lima", categoria=Categoria.CARREIRA, pmlCpf="1")
    ad.conta(op, Ramo.DIRETA, "FAZENDA", "bia.souza", categoria=Categoria.ESTAGIO, uac=66050)  # bloqueada + senha não expira
    ad.conta(op, Ramo.DIRETA, "FAZENDA", "nhu.sistema.contas", nome="sistemacontas", pmlNaoHumanoTipo="bot")
    ad.conta(ino, Ramo.DIRETA, "FAZENDA", "caio.rocha", categoria=Categoria.CARREIRA, uac=514)
    ad.conta(op, Ramo.INDIRETA, "CODEL", "duda.reis")
    ad.ops.clear()
    return ad
