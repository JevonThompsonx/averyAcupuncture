# Avery Acupuncture — static site image
# Base pinned by digest (stack convention): nginx:1.27-alpine.
# Digest: docker.io/library/nginx@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10
FROM nginx@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10

# Server config (listen 8080, cache + gzip headers, security headers)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# The site itself. .dockerignore keeps build context clean.
COPY . /usr/share/nginx/html/

EXPOSE 8080

# nginx:alpine ships busybox wget, so a real liveness probe is possible.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:8080/healthz || exit 1
