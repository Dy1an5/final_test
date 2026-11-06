#!/usr/bin/env bash
set -euo pipefail

cd /home/tungthanhle/gem5
mkdir -p /results/m5out /results/Tables /results/Rewards_Hist /results/Figures
export MPLCONFIGDIR=/results/.matplotlib

for metadata in build-info.json packages.txt project-overlay.diff project-overlay-status.txt; do
    cp "/opt/rle-noc/$metadata" "/results/$metadata"
done

case "${1:-smoke}" in
    smoke|train)
        exec python /opt/rle-noc/experiment.py "$@"
        ;;
    shell)
        shift
        exec bash "$@"
        ;;
    *)
        exec "$@"
        ;;
esac
