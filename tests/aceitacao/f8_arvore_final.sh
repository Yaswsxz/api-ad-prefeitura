#!/usr/bin/env bash
# F8 — Árvore final: a matriz completa, ativa, nos DNs previstos; log limpo; cobertura de rotas.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f8
ACE_NAO_PARAR=1

SNAP="$ACE_SAIDA/${ACE_DATA}_arvore-final.tsv"
printf 'ramo\tunidade\tcategoria\thumanos_operativos\tnaohumanos_operativos\n' > "$SNAP"

# ---- AT-F8-01: unidades em Operativos e Inoperantes; nenhuma em Desincorporados ---------------------------------------------
for ramo in direta indireta preposto terceirizada; do
  lista="$(ace_ler_unidades | awk -F'\t' -v r="$ramo" '$1==r{print $2}' | jq -Rsc 'split("\n")|map(select(length>0))')"
  for arvore in operativos inoperantes; do
    ACE_JQ_ARGS=(--argjson e "$lista" --arg a "$arvore")
    ace_teste "AT-F8-01.$ramo.$arvore" GET "/estrutura/unidades/$ramo?arvore=$arvore&limite=1000" 200 "" \
      '[.items[].nome] as $n | ($e|all(. as $u | $n|any(. == $u))) and (.items|all(.arvore==$a))'
  done
  ACE_JQ_ARGS=(--argjson e "$lista")
  ace_teste "AT-F8-01.$ramo.desincorporados" GET "/estrutura/unidades/$ramo?arvore=desincorporados&limite=1000" 200 "" \
    '[.items[].nome] as $n | ($e|all(. as $u | $n|any(. == $u)|not))'
done

# ---- AT-F8-02/03: contas por unidade e categoria (Operativos) e ausência nas outras árvores --------------------------------
while IFS=$'\t' read -r -u 3 ramo unidade cod pml; do
  nh="$(ace_conta humano "$unidade")"; nn="$(ace_conta naohumano "$unidade")"
  ACE_JQ_ARGS=(--argjson n "$nh")
  ace_teste "AT-F8-02.$unidade.humanos" GET "/identidade/humanos?arvore=operativos&ramo=$ramo&unidade=$unidade&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==false and .arvore=="operativos"))'
  ACE_JQ_ARGS=(--argjson n "$nn")
  ace_teste "AT-F8-02.$unidade.naohumanos" GET "/identidade/naohumanos?arvore=operativos&ramo=$ramo&unidade=$unidade&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==false and .arvore=="operativos"))'
  if [ "$ramo" = direta ]; then
    for cat in estagio carreira comissionado; do
      ACE_JQ_ARGS=(--arg c "$cat")
      ace_teste "AT-F8-02.$unidade.$cat" GET "/identidade/humanos?arvore=operativos&ramo=$ramo&unidade=$unidade&categoria=$cat&limite=1000" 200 "" \
        '.total==2 and (.items|all(.categoria==$c))'
      printf '%s\t%s\t%s\t2\t-\n' "$ramo" "$unidade" "$cat" >> "$SNAP"
    done
    printf '%s\t%s\t%s\t-\t%s\n' "$ramo" "$unidade" "NaoHumanos" "$nn" >> "$SNAP"
  else
    printf '%s\t%s\t%s\t%s\t%s\n' "$ramo" "$unidade" "-" "$nh" "$nn" >> "$SNAP"
  fi
  for arvore in inoperantes desincorporados; do
    for rota in humanos naohumanos; do
      ace_teste "AT-F8-03.$unidade.$arvore.$rota" GET "/identidade/$rota?arvore=$arvore&ramo=$ramo&unidade=$unidade&limite=1000" "200|404" "" '(.total // 0)==0'
    done
  done
done 3< <(ace_ler_unidades)

# ---- AT-F8-04: o DN de cada uma das 72 contas ---------------------------------------------------------------------------------
while IFS=$'\t' read -r -u 3 tipo ramo unidade categoria login nome tipo_nh cpf; do
  dn="$(ace_dn Operativos "$ramo" "$unidade" "$categoria" "$nome")"
  ACE_JQ_ARGS=(--arg dn "$dn")
  ace_teste "AT-F8-04.$login" GET "$(ace_rota_ident "$tipo")/$login" 200 "" \
    '.arvore=="operativos" and .bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
done 3< <(ace_ler_identidades)

# ---- AT-F8-08: isolamento: a base Humanos só tem humanos e a NaoHumanos só não humanos --------------------------
tot_h="$(ace_ler_identidades | awk -F'\t' '$1=="humano"{n++} END{print n+0}')"
tot_n="$(ace_ler_identidades | awk -F'\t' '$1=="naohumano"{n++} END{print n+0}')"
ACE_JQ_ARGS=(--argjson n "$tot_h")
ace_teste AT-F8-08.humanos GET "/identidade/humanos?arvore=operativos&limite=1000" 200 "" \
  '.total==$n and ([.items[].distinguished_name|ascii_downcase|test(",ou=humanos,ou=operativos,")]|all) and ([.items[].login|test("^nhu[.]")]|any|not)'
ACE_JQ_ARGS=(--argjson n "$tot_n")
ace_teste AT-F8-08.naohumanos GET "/identidade/naohumanos?arvore=operativos&limite=1000" 200 "" \
  '.total==$n and ([.items[].distinguished_name|ascii_downcase|test(",ou=naohumanos,ou=operativos,")]|all) and ([.items[].login|test("^nhu[.]")]|all)'

# ---- AT-F8-05: varredura do log desde a marca de início -------------------------------------------------------------------------
off="$(ace_marca log_bytes)"; off="${off:-0}"
trecho() { ace_log_desde "$off"; }
erros_ad="$(trecho | grep -a 'AD_ERRO')"
n19="$(printf '%s
' "$erros_ad" | grep -a -c 'codigo_ldap=19 ')"
n32="$(printf '%s
' "$erros_ad" | grep -a -c 'codigo_ldap=32 ')"
total_erros="$(printf '%s
' "$erros_ad" | grep -a -c 'AD_ERRO')"
outros=$((total_erros - n19 - n32))
ruins="$(trecho | grep -a -c -E 'INCONSISTENTE|AUDITORIA_' || true)"
esp19="$(cat "$ACE_SAIDA"/${ACE_DATA}_f*.tsv | awk -F'	' '$9=="SUBSTITUIDO"{n++} END{print n+0}')"
esp32="$(cat "$ACE_SAIDA"/${ACE_DATA}_f8.tsv | awk -F'	' '$2 ~ /^AT-F8-03/ && $6==404{n++} END{print n+0}')"
oks="$(trecho | grep -c 'AD_OK' || true)"
escritas="$(cat "$ACE_SAIDA"/${ACE_DATA}_f*.tsv | awk -F'\t' '$9=="OK" && $11!="-"{n++} END{print n+0}')"
ace_registrar_manual AT-F8-05.erros "log sem INCONSISTENTE, AUDITORIA_ nem AD_ERRO inesperado" "0" "$((ruins + outros))" "$([ "$((ruins + outros))" = 0 ] && echo OK || echo FALHA)" "AD_ERRO por código: $n19 do 19 (substituídos), $n32 do 32 (404 do AT-F8-03), $outros de outros"
ace_registrar_manual AT-F8-05.constraint "AD_ERRO 19 = recusas de login já usado (SUBSTITUIDO)" "$esp19" "$n19" "$([ "$n19" = "$esp19" ] && echo OK || echo FALHA)" ""
ace_registrar_manual AT-F8-05.nosuchobject "AD_ERRO 32 = listagens em árvore sem a unidade (404 do AT-F8-03)" "$esp32" "$n32" "$([ "$n32" = "$esp32" ] && echo OK || echo FALHA)" ""
ace_registrar_manual AT-F8-05.ad_ok "linhas AD_OK >= escritas bem-sucedidas" ">= $escritas" "$oks" "$([ "$oks" -ge "$escritas" ] && echo OK || echo FALHA)" ""

# ---- AT-F8-06: instantâneo ----------------------------------------------------------------------------------------------------------
linhas="$(($(wc -l < "$SNAP") - 1))"
ace_registrar_manual AT-F8-06 "instantâneo da árvore final gravado" "arquivo" "$linhas linhas em $(basename "$SNAP")" OK ""

# ---- AT-F8-07: cobertura de rotas (OpenAPI x chamadas executadas) ------------------------------------------------------------------
COB="$ACE_SAIDA/${ACE_DATA}_cobertura.tsv"
printf 'metodo\trota\texecucoes\tresultado\n' > "$COB"
ace_chamar GET /openapi.json
EXEC="$(cat "$ACE_SAIDA"/${ACE_DATA}_f*.tsv | awk -F'\t' '$3!="-" && $6!="-"{split($4,a,"?"); print $3" "a[1]}')"
lacunas=0; total=0
while IFS=$'\t' read -r metodo rota; do
  [ -n "$metodo" ] || continue
  re="^${metodo} $(printf '%s' "$rota" | sed -E 's/\{[^}]+\}/[^\/]+/g')$"
  n="$(printf '%s\n' "$EXEC" | grep -Ec "$re" || true)"
  total=$((total + 1))
  if [ "$n" -gt 0 ]; then r=OK; else r=LACUNA; lacunas=$((lacunas + 1)); fi
  printf '%s\t%s\t%s\t%s\n' "$metodo" "$rota" "$n" "$r" >> "$COB"
done < <(printf '%s' "$ACE_CORPO" | jq -r '.paths|to_entries[]|.key as $p|.value|keys[]|[ascii_upcase,$p]|@tsv')
ace_registrar_manual AT-F8-07 "toda rota da API foi exercitada ($total rotas/métodos)" "0 lacunas" "$lacunas lacunas" "$([ "$lacunas" = 0 ] && echo OK || echo FALHA)" ""

ace_resumo
