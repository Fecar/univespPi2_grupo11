#!/bin/sh
set -e

echo "Aplicando migracoes..."
flask db upgrade

echo "Iniciando aplicacao..."
exec "$@"
