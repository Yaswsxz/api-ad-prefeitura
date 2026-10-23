#!/usr/bin/env bash
# F1 — Unidades (4 ramos): criar, consultar, listar, alterar e os negativos.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f1

while IFS=$'\t' read -r -u 3 ramo nome cod pml; do
  rota="/estrutura/unidades/$ramo"; ramo_ou="$(ace_ramo_ou "$ramo")"
  # AT-F1-01 criar (se já existe, "já existia")
  ace_chamar GET "$rota/$nome"
  if [ "$ACE_STATUS" = 200 ]; then
    ace_ja_existia "AT-F1-01.$nome" POST "$rota" "unidade já existia"
  else
    ACE_JQ_ARGS=(--arg nome "$nome" --arg ramo "$ramo" --arg pml "$pml"
      --arg dno "$(ace_dn_unidade Operativos Humanos "$ramo" "$nome")" --arg dni "$(ace_dn_unidade Inoperantes Humanos "$ramo" "$nome")"
      --arg dnno "$(ace_dn_unidade Operativos NaoHumanos "$ramo" "$nome")" --arg dnni "$(ace_dn_unidade Inoperantes NaoHumanos "$ramo" "$nome")")
    ace_teste "AT-F1-01.$nome" POST "$rota" 201 "$(jq -nc --arg n "$nome" --arg p "$pml" '{nome:$n,pml_nome_orgao:$p}')" \
      ".nome==\$nome and .ramo==\$ramo and (.distinguished_name_operativos|ascii_downcase)==(\$dno|ascii_downcase) and (.distinguished_name_inoperantes|ascii_downcase)==(\$dni|ascii_downcase)
       and (.distinguished_name_operativos_nao_humanos|ascii_downcase)==(\$dnno|ascii_downcase) and (.distinguished_name_inoperantes_nao_humanos|ascii_downcase)==(\$dnni|ascii_downcase) and $ACE_F_AVISOS"
  fi
done 3< <(ace_ler_unidades)

# AT-F1-02 consultar uma unidade: existe nas duas árvores
while IFS=$'\t' read -r -u 3 ramo nome cod pml; do
  ACE_JQ_ARGS=(--arg nome "$nome")
  ace_teste "AT-F1-02.$nome" GET "/estrutura/unidades/$ramo/$nome" 200 "" \
    '.nome==$nome and (.arvores|sort)==["inoperantes","operativos"] and ((.distinguished_names|keys)==["inoperantes","operativos"])
     and ((.distinguished_names_nao_humanos|keys)==["inoperantes","operativos"])
     and ([.distinguished_names[]|ascii_downcase|test(",ou=humanos,ou=")]|all) and ([.distinguished_names_nao_humanos[]|ascii_downcase|test(",ou=naohumanos,ou=")]|all)'
done 3< <(ace_ler_unidades)

# AT-F1-03 listar por ramo, nas duas árvores
for ramo in direta indireta preposto terceirizada; do
  lista="$(ace_ler_unidades | awk -F'\t' -v r="$ramo" '$1==r{print $2}' | jq -Rsc 'split("\n")|map(select(length>0))')"
  n="$(printf '%s' "$lista" | jq length)"
  for arvore in operativos inoperantes; do
    ACE_JQ_ARGS=(--argjson esperados "$lista" --argjson n "$n" --arg arvore "$arvore")
    ace_teste "AT-F1-03.$ramo.$arvore" GET "/estrutura/unidades/$ramo?arvore=$arvore&limite=1000" 200 "" \
      '([.items[].nome] as $nomes | $esperados | all(. as $u | $nomes | any(. == $u))) and .total>=$n and (.items|all(.arvore==$arvore))'
  done
done

# AT-F1-04 paginação
ace_teste AT-F1-04 GET "/estrutura/unidades/direta?limite=1&deslocamento=1" 200 "" '(.items|length)==1 and .limite==1 and .deslocamento==1 and .total>=3'

# AT-F1-05 alterar (pml_nome_orgao); com PML_GRAVAR=false o aviso é o resultado esperado
while IFS=$'\t' read -r -u 3 ramo nome cod pml; do
  ACE_JQ_ARGS=(--arg nome "$nome")
  ace_teste "AT-F1-05.$nome" PATCH "/estrutura/unidades/$ramo/$nome" 200 "$(jq -nc --arg p "$pml (revisada)" '{pml_nome_orgao:$p}')" \
    ".nome==\$nome and $ACE_F_AVISOS"
done 3< <(ace_ler_unidades)

# Negativos
ACE_A=sim ace_teste AT-F1-06 POST /estrutura/unidades/direta 409 '{"nome":"CULTURA"}' '.codigo=="CONFLITO" and (.mensagem|test("Já existe"))'
ACE_A=sim ace_teste AT-F1-07 POST /estrutura/unidades/indireta 409 '{"nome":"CULTURA"}' '.codigo=="CONFLITO" and (.mensagem|test("Já existe"))'
ace_teste AT-F1-08 POST /estrutura/unidades/direta 422 '{"nome":"ESTAGIO"}' '.codigo=="VALIDACAO"'
ace_teste AT-F1-09.virgula POST /estrutura/unidades/direta 422 '{"nome":"A,OU=B"}' '.codigo=="VALIDACAO"'
ace_teste AT-F1-09.curto POST /estrutura/unidades/direta 422 '{"nome":"X"}' '.codigo=="VALIDACAO"'
ace_teste AT-F1-10 GET /estrutura/unidades/direta/NAOEXISTE 404 "" '.codigo=="NAO_ENCONTRADO"'
ACE_A=sim ace_teste AT-F1-11 PATCH /estrutura/unidades/direta/NAOEXISTE 404 '{"pml_nome_orgao":"Qualquer coisa"}' '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F1-12 GET /estrutura/unidades/inexistente 404 "" '.codigo=="NAO_ENCONTRADO"'

ace_resumo
