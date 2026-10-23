#!/usr/bin/env bash
# Gera docs/testes/resultados-AAAA-MM-DD.md a partir dos TSVs da campanha. Só lê arquivos do projeto.
# Para cada ID vale a ÚLTIMA execução (uma fase repetida substitui a anterior).
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
SAIDA="$RAIZ/docs/testes/execucoes"
DATA="${ACEITACAO_DATA:-$(date +%F)}"
MD="$RAIZ/docs/testes/resultados-$DATA.md"
MARCA="$SAIDA/marca.txt"

env_val() { grep -E "^$1=" "$RAIZ/.env" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r"'; }
tsvs=("$SAIDA"/${DATA}_f[0-9].tsv)
[ -e "${tsvs[0]}" ] || { echo "nenhum TSV de $DATA em $SAIDA" >&2; exit 1; }

# última linha de cada ID, por fase (arquivo)
ultimas() { awk -F'\t' 'NR>1 && $2 ~ /^AT-/{r[$2]=$0; if(!($2 in o)){o[$2]=++n}} END{for(i in r) print o[i]"\t"r[i]}' "$1" | sort -n | cut -f2-; }

{
echo "# Resultados da campanha de aceitação — $DATA"
echo
echo "| | |"
echo "|---|---|"
echo "| **Especificação** | [especificacao-testes.md](especificacao-testes.md) |"
echo "| **Commit do executor** | \`$(git -C "$RAIZ" rev-parse --short HEAD 2>/dev/null)\` |"
echo "| **API / AD** | \`http://127.0.0.1:8000\` → \`$(env_val AD_SERVER)\` (LDAPS, TLS 1.0, certificado fixado) |"
echo "| **\`PML_GRAVAR\`** | \`$(env_val PML_GRAVAR)\` (com \`false\`, o \`avisos\` dos \`pml*\` é o resultado esperado) |"
echo "| **Início da campanha (UTC)** | $(sed -n 's/^instante_utc=//p' "$MARCA" 2>/dev/null | tr -d '\r') |"
echo

echo "## Resumo por fase"
echo
echo "| Fase | Testes | Aprovados | Já existiam | Substituídos | Falhas | Tempo das chamadas |"
echo "|---|---:|---:|---:|---:|---:|---:|"
tot=0; aprov=0; ja=0; subs=0; fal=0
for f in "${tsvs[@]}"; do
  nome="$(basename "$f" .tsv | sed "s/^${DATA}_//")"
  linha="$(ultimas "$f" | awk -F'\t' '{n++; if($9=="OK")o++; else if($9=="JA_EXISTIA")j++; else if($9=="SUBSTITUIDO")s++; else x++; ms+=$8} END{printf "%d %d %d %d %d %d", n, o, j, s, x, ms/1000}')"
  set -- $linha
  printf '| %s | %s | %s | %s | %s | %s | %s s |\n' "${nome^^}" "$1" "$2" "$3" "$4" "$5" "$6"
  tot=$((tot + $1)); aprov=$((aprov + $2)); ja=$((ja + $3)); subs=$((subs + $4)); fal=$((fal + $5))
done
printf '| **Total** | **%s** | **%s** | **%s** | **%s** | **%s** | |\n' "$tot" "$aprov" "$ja" "$subs" "$fal"
echo

echo "## Conciliação da auditoria (F7)"
echo
if [ -f "$SAIDA/${DATA}_conciliacao.tsv" ]; then
  echo "| Ação | Esperado | Observado | Resultado |"; echo "|---|---:|---:|---|"
  tail -n +2 "$SAIDA/${DATA}_conciliacao.tsv" | awk -F'\t' '{printf "| %s | %s | %s | %s |\n", $1,$2,$3,$4}'
else echo "_F7 ainda não executada._"; fi
echo

echo "## Cobertura de rotas (F8)"
echo
if [ -f "$SAIDA/${DATA}_cobertura.tsv" ]; then
  echo "| Método | Rota | Execuções | Resultado |"; echo "|---|---|---:|---|"
  tail -n +2 "$SAIDA/${DATA}_cobertura.tsv" | awk -F'\t' '{printf "| %s | `%s` | %s | %s |\n", $1,$2,$3,$4}'
else echo "_F8 ainda não executada._"; fi
echo

echo "## Árvore final (F8)"
echo
if [ -f "$SAIDA/${DATA}_arvore-final.tsv" ]; then
  echo "| Ramo | Unidade | OU / categoria | Humanos | Não humanos |"; echo "|---|---|---|---:|---:|"
  tail -n +2 "$SAIDA/${DATA}_arvore-final.tsv" | awk -F'\t' '{printf "| %s | %s | %s | %s | %s |\n", $1,$2,$3,$4,$5}'
else echo "_F8 ainda não executada._"; fi
echo

echo "## Falhas e desvios"
echo
achou=0
for f in "${tsvs[@]}"; do
  ruins="$(ultimas "$f" | awk -F'\t' '$9!="OK" && $9!="JA_EXISTIA" && $9!="SUBSTITUIDO"{gsub(/[|]/,"/",$12); printf "| %s | %s %s | %s | %s | %s |\n", $2,$3,$4,$5,$6,$12}')"
  if [ -n "$ruins" ]; then
    [ "$achou" = 0 ] && { echo "| ID | Chamada | Esperado | Obtido | Nota |"; echo "|---|---|---|---|---|"; achou=1; }
    printf '%s\n' "$ruins" | sed 's/|\([^|]*\)$/|\1/'
  fi
done
[ "$achou" = 0 ] && echo "Nenhuma falha registrada na última execução de cada teste."
echo

echo "## Conclusão"
echo
if [ "$fal" = 0 ] && ! grep -q 'FALHA\|LACUNA' "$SAIDA/${DATA}_conciliacao.tsv" "$SAIDA/${DATA}_cobertura.tsv" 2>/dev/null; then
  echo "**Aprovada**: $aprov de $tot testes aprovados (+ $ja que já existiam), conciliação da auditoria sem diferença e todas as rotas exercitadas."
else
  echo "**Pendente**: há falhas, divergências de conciliação ou rotas sem teste. Veja as seções acima."
fi
echo

[ -f "$RAIZ/docs/testes/ocorrencias-$DATA.md" ] && { cat "$RAIZ/docs/testes/ocorrencias-$DATA.md"; echo; }

echo "## Detalhe dos testes"
echo
for f in "${tsvs[@]}"; do
  nome="$(basename "$f" .tsv | sed "s/^${DATA}_//")"
  echo "<details><summary>Fase ${nome^^}</summary>"
  echo
  echo "| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |"
  echo "|---|---|---|---|---|---:|---|"
  ultimas "$f" | awk -F'\t' '{printf "| %s | %s %s | %s | %s | %s | %s | %s |\n", $2,$3,$4,$5,$6,$9,$8,$7}'
  echo
  echo "</details>"
  echo
done
} > "$MD"

echo "Relatório gerado: $MD"
