#!/usr/bin/env bash
# Biblioteca da campanha de aceitação (docs/testes/especificacao-testes.md).
# Executada com bash + curl + jq. NUNCA imprime nem grava token, segredo ou senha_inicial.
# Uso: cada fase faz `source lib.sh`, `ace_inicio fN`, roda testes com ace_teste e termina com ace_resumo.

set -u
set +x

ACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACE_RAIZ="$(cd "$ACE_DIR/../.." && pwd)"
ACE_MASSA="$ACE_DIR/massa"
ACE_SAIDA="$ACE_RAIZ/docs/testes/execucoes"
ACE_LOGS="$ACE_RAIZ/logs"

# O log da API é uma sequência só: os arquivos virados (api_ad-AAAA-MM-DD.NNN.log, em ordem
# alfabética = cronológica) e depois o corrente (api_ad.log). Virar o arquivo só move bytes do fim de um para o
# seguinte, sem mudar a sequência: os offsets da marca continuam valendo mesmo se a rotação ocorrer no meio da campanha.
ace_log_cat() { local f; for f in "$ACE_LOGS"/api_ad-*.log "$ACE_LOGS/api_ad.log"; do [ -f "$f" ] && cat "$f"; done; return 0; }
ace_log_bytes() { ace_log_cat | wc -c; }
ace_log_desde() { ace_log_cat | tail -c +$(( ${1:-0} + 1 )); }   # ace_log_desde OFFSET
ACE_ADMIN="Supervisor de Testes"
ACE_DATA="${ACEITACAO_DATA:-$(date +%F)}"
ACE_MARCA="$ACE_SAIDA/marca.txt"

_env() { grep -E "^$1=" "$ACE_RAIZ/.env" | tail -1 | cut -d= -f2- | tr -d '\r"'; }
ACE_PML_BASE="$(_env AD_PML_BASE)"

# Destino: a API atrás do nginx, em HTTPS. O certificado vem da Infraestrutura e é emitido para o nome do
# servidor (NGINX_SERVER_NAME do .env): o curl resolve esse nome para 127.0.0.1 só nesta chamada (--resolve), sem DNS, e o
# certificado é conferido normalmente. Sem NGINX_SERVER_NAME usa https://localhost. Porta: HTTPS_PORT do .env (padrão 443).
# ACEITACAO_URL substitui o destino; ACEITACAO_CACERT (opcional) indica a CA, se o sistema não a confia. A campanha escreve no
# AD: só se aceita localhost, 127.0.0.1 ou o nome do próprio servidor, sempre resolvido para 127.0.0.1.
_porta_https="${HTTPS_PORT:-$(_env HTTPS_PORT)}"
_nome_servidor="${NGINX_SERVER_NAME:-$(_env NGINX_SERVER_NAME)}"; [ "$_nome_servidor" = "_" ] && _nome_servidor=""
ACE_URL="${ACEITACAO_URL:-https://${_nome_servidor:-localhost}${_porta_https:+:$_porta_https}}"
_resto="${ACE_URL#*://}"; _hostport="${_resto%%/*}"; _host="${_hostport%%:*}"
case "$_hostport" in *:*) _porta="${_hostport##*:}";; *) _porta=""; esac
[ -n "$_porta" ] || { case "$ACE_URL" in https://*) _porta=443;; *) _porta=80;; esac; }
ACE_CURL_TLS=()
if [ "$_host" = localhost ] || [ "$_host" = 127.0.0.1 ]; then :
elif [ -n "$_nome_servidor" ] && [ "$_host" = "$_nome_servidor" ]; then ACE_CURL_TLS+=(--resolve "$_host:$_porta:127.0.0.1")
else echo "destino não permitido: $ACE_URL (só localhost, 127.0.0.1 ou NGINX_SERVER_NAME)" >&2; exit 2; fi
ACE_CACERT="${ACEITACAO_CACERT:-}"
[ -z "$ACE_CACERT" ] || ACE_CURL_TLS+=(--cacert "$ACE_CACERT")
ACE_PML_GRAVAR="$(_env PML_GRAVAR | tr 'A-Z' 'a-z')"
ACE_PML_GRAVAR="${ACEITACAO_PML_GRAVAR:-${ACE_PML_GRAVAR:-true}}"
ACE_RETOMADA="${ACEITACAO_RETOMADA:-0}"

# Filtro jq sobre o campo `avisos`: com PML_GRAVAR=false o aviso é o resultado esperado.
if [ "$ACE_PML_GRAVAR" = "false" ]; then ACE_F_AVISOS='(.avisos|length)>0'; else ACE_F_AVISOS='(.avisos|length)==0'; fi

ACE_N=0; ACE_OKS=0; ACE_FALHAS=0; ACE_JA=0; ACE_SUBST=0
ACE_JQ_ARGS=()
ACE_A=nao

# ---------------------------------------------------------------------------------------------
# Início de fase, token e pré-voo
# ---------------------------------------------------------------------------------------------

ace_inicio() {   # ace_inicio f2   [sem-previoo]
  ACE_FASE="$1"
  ACE_EXEC="$(date -u +%FT%TZ)"
  command -v curl >/dev/null && command -v jq >/dev/null || { echo "faltam curl/jq" >&2; exit 2; }
  mkdir -p "$ACE_SAIDA"
  ACE_TSV="$ACE_SAIDA/${ACE_DATA}_${ACE_FASE}.tsv"
  [ -f "$ACE_TSV" ] || printf 'execucao\tid\tmetodo\trota\tesperado\tobtido\trequest_id\tms\tresultado\taudita\tescreveu\tnota\n' > "$ACE_TSV"
  ACE_HDR="$ACE_SAIDA/.hdr.$$"
  trap 'rm -f "$ACE_HDR"' EXIT
  echo "== Fase ${ACE_FASE} | $ACE_EXEC | PML_GRAVAR=$ACE_PML_GRAVAR | retomada=$ACE_RETOMADA =="
  ace_token
  if [ "${2:-}" != "sem-prevoo" ]; then
    ace_chamar GET /health/detalhes
    if [ "$ACE_STATUS" != 200 ]; then echo "PRÉ-VOO FALHOU: /health/detalhes devolveu $ACE_STATUS" >&2; exit 2; fi
  fi
}

ace_token() {
  local id corpo resp
  id="$(_env API_CLIENT_ID)"
  [ -n "$id" ] && [ -s "$ACE_RAIZ/segredo_cliente_api.txt" ] || { echo "faltam API_CLIENT_ID ou segredo_cliente_api.txt" >&2; exit 2; }
  # o segredo entra no JSON por --rawfile e segue ao curl por stdin: nunca aparece em argumento
  corpo="$(jq -nc --arg i "$id" --rawfile s "$ACE_RAIZ/segredo_cliente_api.txt" \
           '{client_id:$i, client_secret:($s|rtrimstr("\n")|rtrimstr("\r"))}')"
  resp="$(printf '%s' "$corpo" | curl -sS --max-time 30 "${ACE_CURL_TLS[@]}" -H 'Content-Type: application/json' \
          --data-binary @- "$ACE_URL/auth/token" 2>&1)" || true
  ACE_TOKEN="$(printf '%s' "$resp" | jq -r '.access_token // empty' 2>/dev/null)"
  unset corpo resp
  [ -n "$ACE_TOKEN" ] || { echo "não foi possível obter o token (API no ar? credenciais?)" >&2; exit 2; }
}

# ---------------------------------------------------------------------------------------------
# Chamada HTTP (curl). O token e o corpo vão por um arquivo de configuração em descritor (-K <(...)).
# ---------------------------------------------------------------------------------------------

ace_chamar() {   # ace_chamar MÉTODO ROTA [CORPO]  -> ACE_STATUS ACE_CORPO ACE_RID ACE_MS
  local metodo="$1" rota="$2" corpo="${3:-}" cfg resp ultima bearer
  case "$rota" in /*) ;; *) echo "rota inválida: $rota" >&2; exit 2;; esac
  bearer="${ACE_BEARER-__padrao__}"; [ "$bearer" = "__padrao__" ] && bearer="$ACE_TOKEN"
  cfg="url = \"$ACE_URL$rota\"
request = \"$metodo\"
header = \"Content-Type: application/json\""
  [ -n "$bearer" ] && cfg+=$'\n'"header = \"Authorization: Bearer $bearer\""
  [ "$metodo" != GET ] && cfg+=$'\n'"header = \"X-Administrador: $ACE_ADMIN\""
  [ -n "${ACE_EXTRA_HEADER:-}" ] && cfg+=$'\n'"header = \"$ACE_EXTRA_HEADER\""
  [ -n "$corpo" ] && cfg+=$'\n'"data-raw = $(printf '%s' "$corpo" | jq -Rs .)"
  resp="$(curl -sS --max-time 180 "${ACE_CURL_TLS[@]}" -D "$ACE_HDR" -w $'\n%{http_code} %{time_total}' -K <(printf '%s\n' "$cfg") 2>&1)" || true
  ultima="${resp##*$'\n'}"
  ACE_CORPO="${resp%$'\n'*}"
  ACE_STATUS="${ultima%% *}"
  ACE_MS="$(awk -v t="${ultima##* }" 'BEGIN{printf "%d", t*1000}')"
  ACE_RID="$(awk 'tolower($1)=="x-request-id:"{gsub(/\r/,"",$2); print $2}' "$ACE_HDR" 2>/dev/null | tail -1)"
  case "$ACE_STATUS" in [0-9][0-9][0-9]) ;; *) ACE_STATUS=000;; esac
  unset cfg resp
}

ace_hdr() { awk -v n="$(printf '%s' "$1" | tr 'A-Z' 'a-z'):" 'tolower($1)==n{sub(/^[^:]*:[ \t]*/,""); gsub(/\r/,""); print}' "$ACE_HDR" | tail -1; }

ace_corpo_seguro() {
  if printf '%s' "$ACE_CORPO" | jq -e . >/dev/null 2>&1; then
    printf '%s' "$ACE_CORPO" | jq -c 'del(.senha_inicial, .senha_nova, .access_token)' | cut -c1-300
  else
    echo "<resposta não JSON, ${#ACE_CORPO} bytes>"
  fi
}

# Ação auditada que uma escrita bem-sucedida deve ter gerado (para a conciliação da F7).
ace_acao() {   # ace_acao MÉTODO ROTA STATUS
  case "$3" in 2??) ;; *) echo -; return;; esac
  case "$1 $2" in
    "POST /estrutura/unidades/"*/desincorporar) echo DESINCORPORAR_OU;;
    "POST /estrutura/unidades/"*/reincorporar)  echo REINCORPORAR_OU;;
    "POST /estrutura/unidades/"*)               echo CREATE_OU;;
    "PATCH /estrutura/unidades/"*)              echo UPDATE_OU;;
    "POST /identidade/humanos")                 echo CREATE_HUMANO;;
    "POST /identidade/naohumanos")              echo CREATE_NAO_HUMANO;;
    "PATCH /identidade/"*)                      echo UPDATE_IDENTIDADE;;
    "DELETE /identidade/"*)                     echo DELETE_IDENTIDADE;;
    "POST /identidade/"*/desbloquear)           echo UNBLOCK_IDENTIDADE;;
    "POST /identidade/"*/bloquear)              echo BLOCK_IDENTIDADE;;
    "POST /identidade/"*/destituir)             echo DESTITUIR_IDENTIDADE;;
    "POST /identidade/"*/ativar)                echo ATIVAR_IDENTIDADE;;
    "POST /identidade/"*/transferir)            echo TRANSFERIR_IDENTIDADE;;
    "POST /identidade/"*/redefinir-senha)       echo REDEFINIR_SENHA;;
    *) echo -;;
  esac
}

# ---------------------------------------------------------------------------------------------
# Teste = chamada + verificações + registro
# ---------------------------------------------------------------------------------------------

ace_registrar() {   # id metodo rota esperado obtido rid ms resultado audita escreveu nota
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ACE_EXEC" "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" \
    "$(printf '%s' "${11}" | tr '\t\n\r' '   ')" >> "$ACE_TSV"
  ACE_N=$((ACE_N + 1))
  case "$8" in
    OK) ACE_OKS=$((ACE_OKS + 1));;
    JA_EXISTIA) ACE_JA=$((ACE_JA + 1));;
    SUBSTITUIDO) ACE_SUBST=$((ACE_SUBST + 1));;
    *) ACE_FALHAS=$((ACE_FALHAS + 1));;
  esac
  if [ "$8" != OK ]; then printf '%-11s %s  %s %s  %s\n' "$8" "$1" "$2" "$3" "${11}" | cut -c1-260; fi
  if [ $((ACE_N % 25)) -eq 0 ]; then echo "   … $ACE_N testes ($ACE_OKS ok)"; fi
}

# ace_teste ID MÉTODO ROTA ESPERADO [CORPO] [FILTRO_JQ] [NOTA] [CABEÇALHO:VALOR]
#   ESPERADO aceita alternativas separadas por | (ex.: "404|200").
#   ACE_JQ_ARGS=(--arg x y) entrega variáveis ao filtro. ACE_A=sim marca negativo que chega ao serviço.
ace_teste() {
  local id="$1" metodo="$2" rota="$3" esperado="$4" corpo="${5:-}" filtro="${6:-}" nota="${7:-}" cab="${8:-}"
  local res=OK escreveu=- audita="$ACE_A" nome valor got
  ace_chamar "$metodo" "$rota" "$corpo"
  if [ "${ACE_DESCOBRIR:-0}" = 1 ] && [ "$metodo" = POST ] && [ "$ACE_STATUS" = 409 ] && [ "$(printf "%s" "$ACE_CORPO" | jq -r .codigo 2>/dev/null)" = AD_CONFLITO ]; then
    res=SUBSTITUIDO; audita=sim; nota="recusado pelo AD (login/UPN já usado fora do PML): trocar na massa"
    printf '%s\t%s\n' "$id" "$rota" >> "$ACE_SAIDA/${ACE_DATA}_substituidos.tsv"
  elif [[ "|$esperado|" != *"|$ACE_STATUS|"* ]]; then
    res=FALHA; nota="esperado $esperado, obtido $ACE_STATUS; $(ace_corpo_seguro)"
  elif [ -n "$filtro" ] && ! printf '%s' "$ACE_CORPO" | jq -e "${ACE_JQ_ARGS[@]}" "$filtro" >/dev/null 2>&1; then
    res=FALHA; nota="verificação falhou: $filtro; $(ace_corpo_seguro)"
  elif [ -n "$cab" ]; then
    nome="${cab%%:*}"; valor="${cab#*:}"
    got="$(ace_hdr "$nome")"
    if [ -z "$got" ] || [[ "$got" != *"$valor"* ]]; then res=FALHA; nota="cabeçalho $nome ausente ou sem '$valor'"; fi
  fi
  if [ "$res" = OK ]; then
    escreveu="$(ace_acao "$metodo" "$rota" "$ACE_STATUS")"
    [ "$escreveu" != - ] && audita=sim
  fi
  ace_registrar "$id" "$metodo" "$rota" "$esperado" "$ACE_STATUS" "${ACE_RID:--}" "$ACE_MS" "$res" "$audita" "$escreveu" "$nota"
  ACE_JQ_ARGS=(); ACE_A=nao
  [ "$res" = FALHA ] && ace_parar
  return 0
}

ace_neg() { ACE_A=sim; ace_teste "$@"; }          # negativo que chega ao serviço (gera linha FAILED na auditoria)

ace_ja_existia() {   # ace_ja_existia ID MÉTODO ROTA NOTA
  ace_registrar "$1" "$2" "$3" "-" "-" "-" 0 JA_EXISTIA nao - "$4"
}

ace_registrar_manual() {   # ace_registrar_manual ID DESCRIÇÃO esperado obtido OK|FALHA nota
  ace_registrar "$1" "-" "$2" "$3" "$4" "-" 0 "$5" nao - "${6:-}"
  [ "$5" = FALHA ] && [ "${ACE_NAO_PARAR:-0}" != 1 ] && ace_parar
  return 0
}

ace_parar() {
  echo "-- FASE INTERROMPIDA no teste acima. Estado a conferir antes de repetir (ida e volta pode ter ficado pela metade). --" >&2
  ace_resumo
  exit 1
}

ace_resumo() {
  echo "== Fase ${ACE_FASE}: $ACE_N testes | $ACE_OKS aprovados | $ACE_JA já existiam | $ACE_SUBST substituídos | $ACE_FALHAS falhas =="
  [ "$ACE_FALHAS" -eq 0 ]
}

# ---------------------------------------------------------------------------------------------
# Massa
# ---------------------------------------------------------------------------------------------

ace_ler_unidades()    { tail -n +2 "$ACE_MASSA/unidades.tsv" | tr -d '\r'; }
ace_ler_identidades() { tail -n +2 "$ACE_MASSA/identidades.tsv" | tr -d '\r'; }

ace_ramo_ou() { case "$1" in direta) echo Direta;; indireta) echo Indireta;; preposto) echo Prepostos;; terceirizada) echo Terceirizadas;; esac; }
ace_cat_ou()  { case "$1" in estagio) echo Estagio;; carreira) echo Carreira;; comissionado) echo Comissionados;; esac; }
ace_rota_ident() { case "$1" in humano) echo /identidade/humanos;; *) echo /identidade/naohumanos;; esac; }

# DN esperado de uma identidade:
#   ace_dn ARVORE(Operativos|Inoperantes|Desincorporados) RAMO UNIDADE CATEGORIA NOME
# O lado vem do nome: conta não humana tem nome minúsculo sem espaço (^[a-z0-9]+$); humano tem sempre dois nomes.
#   humano da Direta:  CN=…,OU=<Categoria>,OU=<UNIDADE>,OU=Direta,OU=Humanos,OU=<Árvore>,<PML>
#   demais humanos:    CN=…,OU=<UNIDADE>,OU=<Ramo>,OU=Humanos,OU=<Árvore>,<PML>
#   não humano:        CN=…,OU=<UNIDADE>,OU=<Ramo>,OU=NaoHumanos,OU=<Árvore>,<PML>
ace_dn() {
  local arvore="$1" ramo="$2" unidade="$3" cat="$4" nome="$5" lado=Humanos interna=""
  [[ "$nome" =~ ^[a-z0-9]+$ ]] && lado=NaoHumanos
  if [ "$lado" = Humanos ] && [ "$ramo" = direta ]; then interna="OU=$(ace_cat_ou "$cat"),"; fi
  printf 'CN=%s,%sOU=%s,OU=%s,OU=%s,OU=%s,%s' "$nome" "$interna" "$unidade" "$(ace_ramo_ou "$ramo")" "$lado" "$arvore" "$ACE_PML_BASE"
}

# DN de uma unidade: ace_dn_unidade ARVORE LADO(Humanos|NaoHumanos) RAMO UNIDADE
ace_dn_unidade() {
  printf 'OU=%s,OU=%s,OU=%s,OU=%s,%s' "$4" "$(ace_ramo_ou "$3")" "$2" "$1" "$ACE_PML_BASE"
}

# Quantas contas da massa atendem ao filtro: ace_conta TIPO UNIDADE [CATEGORIA]
ace_conta() {
  ace_ler_identidades | awk -F'\t' -v t="$1" -v u="$2" -v c="${3:-}" '$1==t && $3==u && (c=="" || $4==c){n++} END{print n+0}'
}

# Campo da massa: ace_campo LOGIN COLUNA(ramo|unidade|categoria|nome|tipo|tipo_nh|cpf)
ace_campo() {
  local col
  case "$2" in tipo) col=1;; ramo) col=2;; unidade) col=3;; categoria) col=4;; nome) col=6;; tipo_nh) col=7;; cpf) col=8;; esac
  ace_ler_identidades | awk -F'\t' -v l="$1" -v c="$col" '$5==l{print $c; exit}'
}

ace_tipo_de() { case "$1" in nhu.*) echo naohumano;; *) echo humano;; esac; }

# Marca de início (AT-F0-09): posição do log e instante UTC, para varreduras e conciliação.
ace_marca() { [ -f "$ACE_MARCA" ] && sed -n "s/^$1=//p" "$ACE_MARCA" | tr -d '\r'; }
