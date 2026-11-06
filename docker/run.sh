#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
image="${RLE_IMAGE:-rle-noc:gem5-20.0.0.3}"
command="${1:-help}"
if (($#)); then shift; fi

case "$command" in
    build)
        exec docker build --build-arg "BUILD_JOBS=${BUILD_JOBS:-2}" \
            -t "$image" -f "$project_dir/Dockerfile" "$@" "$project_dir"
        ;;
    smoke|train|shell)
        if ! docker image inspect "$image" >/dev/null 2>&1; then
            printf 'Cannot access image %s. Check Docker access, then run: bash docker/run.sh build\n' "$image" >&2
            exit 1
        fi
        results_base="${RLE_RESULTS_DIR:-$project_dir/outputs}"
        run_dir="$results_base/$command-$(date -u +%Y%m%dT%H%M%SZ)-$$"
        mkdir -p "$run_dir"
        run_dir="$(cd -- "$run_dir" && pwd)"
        docker image inspect --format '{{.Id}}' "$image" > "$run_dir/image-id.txt"
        printf 'Results: %s\n' "$run_dir"
        run_options=(--rm --init --user "$(id -u):$(id -g)"
            --mount "type=bind,source=$run_dir,target=/results")
        if [[ "$command" == shell ]]; then
            exec docker run "${run_options[@]}" -it "$image" shell "$@"
        fi
        # pipefail preserves simulator/container errors while retaining the log.
        docker run "${run_options[@]}" "$image" "$command" "$@" 2>&1 | tee "$run_dir/run.log"
        ;;
    help|--help|-h)
        cat <<'USAGE'
Run from any directory:
  bash docker/run.sh build
  bash docker/run.sh smoke
  bash docker/run.sh smoke --routing west_first
  bash docker/run.sh train qlearning --episodes 2 --seed 0
  bash docker/run.sh train sarsa --episodes 50 --seed 0
  bash docker/run.sh train expected-sarsa --episodes 50 --seed 0
  bash docker/run.sh shell

Environment: BUILD_JOBS=2, RLE_IMAGE=rle-noc:gem5-20.0.0.3,
             RLE_RESULTS_DIR=<project>/outputs
USAGE
        ;;
    *)
        printf 'Unknown command: %s. Use: bash docker/run.sh help\n' "$command" >&2
        exit 2
        ;;
esac
