# run_ck_on_list.sh
# Requisito: ter top1000_java.csv no mesmo diretório e o JAR do CK pronto.

CK_JAR="./ck/target/ck-*-jar-with-dependencies.jar"
LIST="top1000_java.csv"
OUTROOT="./results"
THREADS=1 

mkdir -p "$OUTROOT"

if [ ! -f "$LIST" ]; then
  echo "Coloque top1000_java.csv no diretório e rode novamente."
  exit 1
fi

# função para processar 1 repo
process_repo() {
  full_name="$1"   # ex: spring-projects/spring-boot
  owner=$(echo "$full_name" | cut -d'/' -f1)
  repo=$(echo "$full_name" | cut -d'/' -f2)
  target_dir="./clones/${owner}_${repo}"
  out_dir="${OUTROOT}/${owner}_${repo}"

  mkdir -p "$(dirname "$target_dir")"
  if [ ! -d "$target_dir/.git" ]; then
    echo "Clonando $full_name ..."
    git clone --depth 1 "https://github.com/${full_name}.git" "$target_dir" || { echo "Clone falhou: $full_name"; return; }
  else
    echo "Repositório já clonado: $full_name"
  fi

  # Verifica se há arquivos .java
  java_count=$(find "$target_dir" -name "*.java" | wc -l)
  if [ "$java_count" -eq 0 ]; then
    echo "Nenhum arquivo Java encontrado em $full_name. Pulando."
    return
  fi

  mkdir -p "$out_dir"
  echo "Rodando CK em $full_name -> $out_dir"
  java -jar $CK_JAR "$target_dir" false 0 false "$out_dir" "build/" "target/" || { echo "CK falhou para $full_name"; return; }
  echo "OK: $full_name"
}

# lê CSV completo pulando header
# tail -n +2 "$LIST" | cut -d',' -f1 | while IFS= read -r fullname; do
#   process_repo "$fullname"
# done

# le somente 1 repo
# tail -n +2 "$LIST" | cut -d',' -f1 | head -n 1 | while IFS= read -r fullname; do
#   process_repo "$fullname"
# done

# lê CSV pulando header e tenta até achar um repo com arquivos Java
tail -n +2 "$LIST" | cut -d',' -f1 | while IFS= read -r fullname; do
  owner=$(echo "$fullname" | cut -d'/' -f1)
  repo=$(echo "$fullname" | cut -d'/' -f2)
  target_dir="./clones/${owner}_${repo}"

  # Clona se necessário
  if [ ! -d "$target_dir/.git" ]; then
    echo "Clonando $fullname ..."
    git clone --depth 1 "https://github.com/${fullname}.git" "$target_dir" || { echo "Clone falhou: $fullname"; continue; }
  fi

  # Verifica se há arquivos .java
  java_count=$(find "$target_dir" -name "*.java" | wc -l)
  if [ "$java_count" -eq 0 ]; then
    echo "Nenhum arquivo Java em $fullname. Excluindo clone..."
    rm -rf "$target_dir"
    continue
  fi

  # Se chegou aqui, tem arquivos Java
  echo "Repo com Java encontrado: $fullname"
  process_repo "$fullname"
  break  # sai do loop após processar um repo válido
done
