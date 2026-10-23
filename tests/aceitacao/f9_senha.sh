#!/usr/bin/env bash
# F9 — Senha: redefinir-senha, tamanho_senha em ativar e redefinir, política por tipo.
# Roda DEPOIS de F0-F5 (usa contas já ativas) e ANTES de reexecutar F7/F8, que passam a contar as ações da F9.
# Só muda senhas das contas da massa; as duas contas descartáveis (criar, ativar, redefinir, destituir, remover) não ficam.
# ATENÇÃO: não é reexecutável às cegas. Se parar no meio, confira se franklin.tavora e nhu.outro.teste ficaram no AD.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f9

CLASSES='test("[A-Z]") and test("[a-z]") and test("[0-9]") and test("[!@#$%&*]")'
SENHAS=(); HUM=0; NHU=0; DESCARTAVEIS=(franklin.tavora nhu.outro.teste)
LOG_INICIO="$(ace_log_bytes)"
INICIO="${ACE_EXEC%Z}"
MOTIVO="teste de redefinicao"

for l in "${DESCARTAVEIS[@]}"; do
  ace_chamar GET "$(ace_rota_ident "$(ace_tipo_de "$l")")/$l"
  [ "$ACE_STATUS" = 404 ] || { echo "a conta descartável $l já existe (ou erro $ACE_STATUS): confira o AD antes de rodar a F9" >&2; exit 2; }
done

guardar() {   # guarda a senha da última resposta (só em memória, para a varredura de vazamento)
  SENHAS+=("$(printf '%s' "$ACE_CORPO" | jq -r '.senha_nova // .senha_inicial')")
}

# redefinir ID LOGIN TAMANHO BLOQUEADA(true|false) [DN]  -> 200, senha com o tamanho e as 4 classes, sem cache
redefinir() {
  local id="$1" login="$2" n="$3" bloq="$4" dn="${5:-}" rota corpo filtro
  rota="$(ace_rota_ident "$(ace_tipo_de "$login")")"
  if [ "$n" = - ]; then corpo="$(jq -nc --arg m "$MOTIVO" '{motivo:$m}')"; n=12
  else corpo="$(jq -nc --arg m "$MOTIVO" --argjson n "$n" '{motivo:$m,tamanho_senha:$n}')"; fi
  filtro='.login==$login and .arvore=="operativos" and .bloqueada==$b and (.avisos|length)==0 and (.senha_nova|length)==$n and (.senha_nova|'"$CLASSES"')'
  [ -n "$dn" ] && filtro+=' and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
  ACE_JQ_ARGS=(--arg login "$login" --argjson b "$bloq" --argjson n "$n" --arg dn "$dn")
  ace_teste "$id" POST "$rota/$login/redefinir-senha" 200 "$corpo" "$filtro" "" "Cache-Control:no-store"
  guardar
  # só conta as redefinições que deram certo (ace_teste para a fase se falhar)
  if [ "$(ace_tipo_de "$login")" = humano ]; then HUM=$((HUM + 1)); else NHU=$((NHU + 1)); fi
}

dn_da() { local l="$1"; ace_dn Operativos "$(ace_campo "$l" ramo)" "$(ace_campo "$l" unidade)" "$(ace_campo "$l" categoria)" "$(ace_campo "$l" nome)"; }

# ---- AT-F9-01..03: humanos nos 4 ramos; tamanhos 12 (padrão), 8, 20 e 64 ------------------------------------------------------
redefinir AT-F9-01.padrao   fagundes.varela - false "$(dn_da fagundes.varela)"
redefinir AT-F9-02.tam8     fagundes.varela 8  false
redefinir AT-F9-02.tam20    fagundes.varela 20 false
redefinir AT-F9-02.tam64    fagundes.varela 64 false
for l in ralph.emerson mikhail.lermontov ivan.gontcharov; do
  redefinir "AT-F9-03.$l" "$l" - false "$(dn_da "$l")"
done

# ---- AT-F9-04: não humanos nos 4 ramos (grava a flag "senha não expira" antes da senha, se faltar) --------------------------
for l in nhu.bot.cult nhu.bot.habi nhu.bot.tabe nhu.bot.limp; do
  redefinir "AT-F9-04.$l" "$l" - false "$(dn_da "$l")"
done

# ---- AT-F9-05: o bloqueio não muda (ida e volta) -------------------------------------------------------------------------------
ACE_JQ_ARGS=(--arg login fagundes.varela)
ace_teste AT-F9-05.bloquear POST /identidade/humanos/fagundes.varela/bloquear 200 "" '.login==$login and .bloqueada==true'
redefinir AT-F9-05.bloqueada fagundes.varela - true "$(dn_da fagundes.varela)"
ACE_JQ_ARGS=(--arg login fagundes.varela)
ace_teste AT-F9-05.desbloquear POST /identidade/humanos/fagundes.varela/desbloquear 200 "" '.login==$login and .bloqueada==false'
ace_teste AT-F9-05.get GET /identidade/humanos/fagundes.varela 200 "" '.bloqueada==false and .arvore=="operativos"'

# ---- AT-F9-06: validação (não chega ao serviço) --------------------------------------------------------------------------------
V='.codigo=="VALIDACAO"'
ace_teste AT-F9-06.tam7      POST /identidade/humanos/fagundes.varela/redefinir-senha 422 '{"motivo":"teste de redefinicao","tamanho_senha":7}' "$V"
ace_teste AT-F9-06.tam65     POST /identidade/humanos/fagundes.varela/redefinir-senha 422 '{"motivo":"teste de redefinicao","tamanho_senha":65}' "$V"
ace_teste AT-F9-06.sem-motivo POST /identidade/humanos/fagundes.varela/redefinir-senha 422 '{}' "$V"
ace_teste AT-F9-06.motivo-curto POST /identidade/naohumanos/nhu.bot.cult/redefinir-senha 422 '{"motivo":"ab"}' "$V"
ace_teste AT-F9-06.ativar-tam7 POST /identidade/humanos/fagundes.varela/ativar 422 '{"instrumento":"Portaria 400/2026 - teste","tamanho_senha":7}' "$V"
ace_teste AT-F9-06.ativar-tam65 POST /identidade/naohumanos/nhu.bot.cult/ativar 422 '{"instrumento":"Portaria 400/2026 - teste","tamanho_senha":65}' "$V"

# ---- AT-F9-07: negativos que chegam ao serviço (A) ------------------------------------------------------------------------------
CORPO="{\"motivo\":\"$MOTIVO\"}"
ACE_A=sim ace_teste AT-F9-07.inexistente  POST /identidade/humanos/ninguem.aqui/redefinir-senha 404 "$CORPO" '.codigo=="NAO_ENCONTRADO"'
ACE_A=sim ace_teste AT-F9-07.tipo-trocado POST /identidade/naohumanos/fagundes.varela/redefinir-senha 404 "$CORPO" '.codigo=="NAO_ENCONTRADO"'
ACE_A=sim ace_teste AT-F9-07.tipo-trocado2 POST /identidade/humanos/nhu.bot.cult/redefinir-senha 404 "$CORPO" '.codigo=="NAO_ENCONTRADO"'

# ---- AT-F9-08: descartáveis — ativar com tamanho, redefinir, destituir e remover ------------------------------------------------
ACE_JQ_ARGS=(--arg l franklin.tavora)
ace_teste AT-F9-08.humano.criar POST /identidade/humanos 201 \
  '{"ramo":"direta","unidade":"CULTURA","categoria":"estagio","login":"franklin.tavora","nome_completo":"Franklin Távora"}' \
  '.login==$l and .arvore=="inoperantes" and .bloqueada==true'
ACE_JQ_ARGS=(--arg l nhu.outro.teste)
ace_teste AT-F9-08.naohumano.criar POST /identidade/naohumanos 201 \
  '{"ramo":"direta","unidade":"CULTURA","login":"nhu.outro.teste","nome":"outroteste","pml_nao_humano_tipo":"outro"}' \
  '.login==$l and .arvore=="inoperantes" and .bloqueada==true'

# em Inoperantes só se ativa; redefinir é recusado (A)
ACE_A=sim ace_teste AT-F9-08.humano.redefinir-inoperante POST /identidade/humanos/franklin.tavora/redefinir-senha 409 "$CORPO" '.codigo=="CONFLITO"'
ACE_A=sim ace_teste AT-F9-08.naohumano.redefinir-inoperante POST /identidade/naohumanos/nhu.outro.teste/redefinir-senha 409 "$CORPO" '.codigo=="CONFLITO"'

ativar() {   # ativar ID LOGIN TAMANHO
  local id="$1" login="$2" n="$3" rota
  rota="$(ace_rota_ident "$(ace_tipo_de "$login")")"
  ACE_JQ_ARGS=(--arg login "$login" --argjson n "$n")
  ace_teste "$id" POST "$rota/$login/ativar" 200 \
    "$(jq -nc --argjson n "$n" '{instrumento:"Portaria 401/2026 - ativacao de teste",tamanho_senha:$n}')" \
    '.login==$login and .arvore=="operativos" and .bloqueada==false and (.senha_inicial|length)==$n and (.senha_inicial|'"$CLASSES"') and '"$ACE_F_AVISOS" \
    "" "Cache-Control:no-store"
  guardar
}
ativar AT-F9-08.humano.ativar    franklin.tavora 20
ativar AT-F9-08.naohumano.ativar nhu.outro.teste 8

redefinir AT-F9-08.humano.redefinir    franklin.tavora 16 false
redefinir AT-F9-08.naohumano.redefinir nhu.outro.teste 16 false

for l in "${DESCARTAVEIS[@]}"; do
  rota="$(ace_rota_ident "$(ace_tipo_de "$l")")"
  ACE_JQ_ARGS=(--arg login "$l")
  ace_teste "AT-F9-08.$l.destituir" POST "$rota/$l/destituir" 200 '{"instrumento":"Portaria 402/2026 - destituicao de teste"}' \
    '.login==$login and .arvore=="inoperantes" and .bloqueada==true and '"$ACE_F_AVISOS"
  ace_teste "AT-F9-08.$l.remover" DELETE "$rota/$l?motivo=inclusao+indevida" 204 ""
  ace_teste "AT-F9-08.$l.get" GET "$rota/$l" 404 "" '.codigo=="NAO_ENCONTRADO"'
done

# ---- AT-F9-09: as senhas não vazam (log da API e auditoria) -----------------------------------------------------------------
n_log="$(ace_log_desde "$LOG_INICIO" | grep -F -c -f <(printf '%s\n' "${SENHAS[@]}"))"
ace_chamar GET "/auditoria/activity-history?days=2&limit=1000"
n_aud="$(printf '%s' "$ACE_CORPO" | grep -F -c -f <(printf '%s\n' "${SENHAS[@]}"))"
res=OK; [ "${n_log:-1}" = 0 ] && [ "${n_aud:-1}" = 0 ] || res=FALHA
ace_registrar_manual AT-F9-09 "senhas não vazam (${#SENHAS[@]} senhas verificadas)" "0 no log e 0 na auditoria" "${n_log} no log e ${n_aud} na auditoria" "$res" ""
unset SENHAS

# ---- AT-F9-10: a auditoria registra a redefinição (motivo, tamanho, troca) e a política por tipo ----------------------------
LINHAS="$(printf '%s' "$ACE_CORPO" | jq -c --arg m "$INICIO" '.items[]|select(.action=="REDEFINIR_SENHA" and .status=="SUCCESS" and .timestamp>=$m)')"
tot="$(printf '%s\n' "$LINHAS" | grep -c .)"
det() { printf '%s\n' "$LINHAS" | jq -r "select((.details // \"{}\")|fromjson?|$1)|1" | wc -l; }
n_hum="$(det '.troca_obrigatoria==true')"; n_nhu="$(det '.troca_obrigatoria==false')"
n_cam="$(det '(.motivo=="'"$MOTIVO"'") and (.tamanho_senha|type=="number")')"
ESP=$((HUM + NHU))
r=OK; [ "$tot" = "$ESP" ] && [ "$n_hum" = "$HUM" ] && [ "$n_nhu" = "$NHU" ] && [ "$n_cam" = "$ESP" ] || r=FALHA
ace_registrar_manual AT-F9-10 "auditoria: REDEFINIR_SENHA com motivo/tamanho; troca só em humanos" \
  "$ESP linhas ($HUM com troca, $NHU sem)" "$tot linhas ($n_hum com troca, $n_nhu sem, $n_cam com motivo e tamanho)" "$r" ""

echo
echo "CONFERÊNCIA MANUAL (AT-F9-11, no AD, pelo responsável): pwdLastSet/\"usuário deve alterar a senha no próximo logon\" e"
echo "\"senha nunca expira\" não são visíveis pela API. Depois desta fase: em uma conta humana da massa (ex.: fagundes.varela)"
echo "a troca no próximo logon deve estar marcada; em uma não humana (ex.: nhu.bot.cult) a senha nunca expira (UAC 66048)."

ace_resumo
