#!/bin/sh
set -eu

PROM_URL="${PROM_URL:-http://127.0.0.1:9090}"
VM_URL="${VM_URL:-http://monitoring-victoriametrics:8428}"

echo "Creating Prometheus snapshot at ${PROM_URL}"
RESP=$(curl -fsS -XPOST "${PROM_URL}/api/v1/admin/tsdb/snapshot")
NAME=$(printf '%s' "$RESP" | sed -n 's/.*"name":"\([^"]*\)".*/\1/p')
if [ -z "$NAME" ]; then
  echo "Snapshot was not created: ${RESP}" >&2
  echo "Recreate monitoring-prometheus with --web.enable-admin-api and retry." >&2
  exit 1
fi
echo "Snapshot: ${NAME}"

VOL=$(docker inspect monitoring-prometheus --format '{{ range .Mounts }}{{ if eq .Destination "/prometheus" }}{{ .Name }}{{ end }}{{ end }}')
NET=$(docker inspect monitoring-victoriametrics --format '{{ range $k, $v := .NetworkSettings.Networks }}{{ $k }}{{ end }}')
if [ -z "$VOL" ] || [ -z "$NET" ]; then
  echo "monitoring-prometheus or monitoring-victoriametrics is not running." >&2
  exit 1
fi

docker run --rm \
  --network "$NET" \
  -v "${VOL}:/prometheus:ro" \
  victoriametrics/vmctl:latest \
  prometheus \
  --prom-snapshot="/prometheus/snapshots/${NAME}" \
  --vm-addr="${VM_URL}" \
  --disable-progress-bar \
  -s

docker exec monitoring-prometheus rm -rf "/prometheus/snapshots/${NAME}"
echo "Import finished and snapshot ${NAME} removed."
