#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 [de|fr|it|all] [seed]" >&2
  exit 2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}"
PARENT_DIR="$(cd "${APP_DIR}/.." && pwd)"
GENERATOR_CONFIG_DIR="${APP_DIR}/config"
LOCAL_CONFIG_DIR="${PARENT_DIR}/sites/app/config"
SEED_ARG="${2:-}"

build_one() {
  local lang="$1"
  local source_config="${LOCAL_CONFIG_DIR}/${lang}.json"
  local target_config="${GENERATOR_CONFIG_DIR}/config.json"

  if [[ ! -f "${source_config}" ]]; then
    echo "Missing config file: ${source_config}" >&2
    exit 1
  fi

  echo "[build_local_review_site] language=${lang}"
  cp "${source_config}" "${target_config}"
  (
    cd "${APP_DIR}"
    if [[ -n "${SEED_ARG}" ]]; then
      uv run python3 build.py --seed "${SEED_ARG}"
    else
      uv run python3 build.py
    fi
  )
}

case "$1" in
  de|fr|it)
    build_one "$1"
    ;;
  all)
    build_one de
    build_one fr
    build_one it
    ;;
  *)
    usage
    ;;
esac
