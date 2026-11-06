FROM ubuntu:18.04@sha256:152dc042452c496007f07ca9127571cb9c29697f42acbfad72324b2bb2e43c98

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/results/.matplotlib

# Use the legacy toolchain shipped with this gem5 release, including Python 2.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates git m4 scons zlib1g-dev \
    python python-dev python-six python-numpy python-matplotlib \
    libgoogle-perftools-dev \
    && rm -rf /var/lib/apt/lists/*

ARG GEM5_COMMIT=fa70478413e4650d0058cbfe81fd5ce362101994
WORKDIR /home/tungthanhle/gem5
RUN git clone --depth 1 --branch v20.0.0.3 https://github.com/gem5/gem5.git . \
    && test "$(git rev-parse HEAD)" = "$GEM5_COMMIT"

# Merge the project's complete source directories into the complete upstream
# checkout. Keep upstream-only build files, ext/, build_opts/ and system/.
COPY src/ src/
COPY configs/ configs/
COPY util/ util/

ARG BUILD_JOBS=2
RUN mkdir -p /opt/rle-noc \
    && git diff --no-ext-diff > /opt/rle-noc/project-overlay.diff \
    && git status --short > /opt/rle-noc/project-overlay-status.txt \
    && scons --ignore-style build/NULL/gem5.opt \
        PROTOCOL=Garnet_standalone -j "$BUILD_JOBS"

# Preserve the original absolute paths without changing the host source files.
COPY interconnect-routing-gym/example/ interconnect-routing-gym/example/
COPY docker/ /opt/rle-noc/
COPY LICENSE /opt/rle-noc/PROJECT-LICENSE
RUN python /opt/rle-noc/prepare_image.py \
    && dpkg-query -W > /opt/rle-noc/packages.txt \
    && mkdir -p /results \
    && chmod 1777 /results \
    && chmod +x /opt/rle-noc/entrypoint.sh

LABEL org.opencontainers.image.title="RLE-NOC reproduction environment" \
    org.opencontainers.image.description="gem5 20.0.0.3, Garnet_standalone and the RLE-NOC routing modifications"

ENTRYPOINT ["/opt/rle-noc/entrypoint.sh"]
CMD ["smoke"]
