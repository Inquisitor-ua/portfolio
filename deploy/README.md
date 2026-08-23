# Deploying yehor-inq.com

This project is deployed as a plain Docker Compose stack (`db` + `web`)
with **no ports published to the host**. It's reached through the shared
**nginx-proxy** stack (a separate repo, `../nginx-proxy` on the server),
which is the single process on the server listening on 80/443 and fanning
requests out to every project — `crossword`, `splitbot`, and this one — by
`server_name`, over a shared external Docker network called `edge`.
See `../nginx-proxy/README.md` for the full picture, including the
Cloudflare Origin CA certificate setup (Cloudflare terminates TLS for
visitors, then re-encrypts to this origin — no Let's Encrypt/certbot
needed here).

nginx-proxy's `conf.d/portfolio.conf` routes `yehor-inq.com` /
`www.yehor-inq.com` to this project's `portfolio-web` container by name,
and serves `/media/` directly from this repo's `media/` directory, which
nginx-proxy mounts read-only from `../portfolio/media`. Static assets
don't need that — WhiteNoise serves them from inside gunicorn.

## 1. One-time server prep (only if not already done for another project)

```bash
docker network create edge
```

If `../nginx-proxy` isn't deployed yet on this server, set it up first —
see its README (Cloudflare Origin CA cert, `docker compose up -d`).

## 2. Deploy this project

```bash
sudo mkdir -p /srv/portfolio && sudo chown $USER:$USER /srv/portfolio
git clone git@github.com:<you>/portfolio.git /srv/portfolio
cd /srv/portfolio
cp .env.example .env
```

Edit `.env`:
- `SECRET_KEY` — generate with `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `POSTGRES_PASSWORD` — a strong random password
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `WAGTAILADMIN_BASE_URL` — already
  default to `yehor-inq.com` in `.env.example`, adjust if needed.
- Leave `SECURE_SSL_ENABLED=1` — nginx-proxy always terminates TLS and
  forwards `X-Forwarded-Proto: https`, so Django's HTTPS-only flags
  (redirect, secure cookies, HSTS) should stay on from the start.

```bash
mkdir -p media
docker compose up -d --build
docker compose logs -f web   # watch migrate/collectstatic, Ctrl-C when it settles
```

`web` (container name `portfolio-web`) publishes no host ports — it's only
reachable by name on the `edge` network, which is exactly what
nginx-proxy's `portfolio.conf` expects.

## 3. Point nginx-proxy at it

On the server, in `../nginx-proxy`:

```bash
git pull
docker compose up -d   # picks up conf.d/portfolio.conf + the new media volume mount
```

If nginx-proxy was already running and only `conf.d/` changed (no volume
changes), `docker compose restart nginx` or `docker exec edge-nginx nginx -s reload`
is enough — but the media volume mount requires recreating the container,
which `docker compose up -d` handles automatically when it detects the
compose file changed.

Confirm: `curl -H "Host: yehor-inq.com" http://127.0.0.1` from the server,
then check `https://yehor-inq.com` through the real domain.

## 4. DNS / Cloudflare

- Add `A` records for `yehor-inq.com` and `www` pointing at the server's
  IP, proxied (orange cloud) through Cloudflare.
- SSL/TLS mode should already be **Full (strict)** for the zone (shared
  with crossword/splitbot) — see `../nginx-proxy/README.md`.

## 5. Auto-deploy on push to main

`.github/workflows/deploy.yml` SSHes into the server and runs
`deploy/deploy.sh` (git reset to `origin/main`, `docker compose up -d
--build`), then purges the whole Cloudflare cache via the API — all
triggered by a push to `main`. This only rebuilds/restarts the `portfolio`
stack itself; it does not touch nginx-proxy, so a `conf.d/portfolio.conf`
change still needs a manual `git pull` + `docker compose up -d` in
`../nginx-proxy` as in step 3.

Create a low-privilege deploy user (or reuse the one you cloned the repo
as) that is in the `docker` group and owns `/srv/portfolio`:

```bash
sudo usermod -aG docker $USER   # log out/in for it to take effect
```

Generate a dedicated SSH key pair for GitHub Actions (don't reuse your
personal key):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/gh_deploy -N ""
cat ~/.ssh/gh_deploy.pub >> ~/.ssh/authorized_keys   # on the server, for the deploy user
```

In the GitHub repo → **Settings → Secrets and variables → Actions**, add:

| Secret | Value |
|---|---|
| `SSH_HOST` | server IP or hostname |
| `SSH_USER` | the deploy user |
| `SSH_PRIVATE_KEY` | contents of `~/.ssh/gh_deploy` (private key) |
| `SSH_PORT` | only if not 22 |
| `APP_DIR` | only if not `/srv/portfolio` |
| `CF_ZONE_ID` | Cloudflare → yehor-inq.com → Overview → API section, "Zone ID" |
| `CF_API_TOKEN` | a token scoped to **Zone → Cache Purge → Edit** for this zone only (My Profile → API Tokens → Create Token) |

Push to `main` and watch the **Actions** tab — it should SSH in, rebuild,
restart the stack, and purge Cloudflare's cache.
