# Deploying yehor-inq.com

Target architecture, once this is done:

```
                 ┌─────────────────────────────────────────┐
                 │   system nginx (apt, NOT in Docker)      │
                 │   listens on 80/443 for ALL domains      │
Internet ──443──▶│                                          │
                 │   yehor-inq.com        ──▶ 127.0.0.1:8001│──▶ gunicorn (Docker: web)
                 │   crossword.yehor-inq.com ─▶ 127.0.0.1:8081│──▶ crossword's container
                 └─────────────────────────────────────────┘
```

Right now crossword's own docker-compose nginx binds `0.0.0.0:80`/`:443`
directly, so there is no room for a second project to also bind those
ports. The fix is to stop letting *any* per-project container touch
80/443, and instead run a single system-level nginx that fans requests out
by `server_name`. This only requires remapping crossword's nginx container
to a localhost-only port — its app containers are untouched.

This is a change to a live service — do it in a low-traffic window and
keep the old `docker-compose.yml` around so you can revert the port
mapping instantly if something looks wrong.

## 0. One-time host prep

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl enable --now nginx
```

## 1. Free up 80/443 from crossword

On the crossword project (wherever its `docker-compose.yml` lives):

1. Back it up: `cp docker-compose.yml docker-compose.yml.bak`.
2. In the `nginx` service's `ports:`, change:
   ```yaml
   ports:
     - "80:80"
     - "443:443"
   ```
   to:
   ```yaml
   ports:
     - "127.0.0.1:8081:80"
   ```
   (drop the 443 mapping — TLS termination moves to the host nginx).
3. If crossword's `nginx.conf` has an `ssl_certificate` / `listen 443`
   server block, comment it out — it no longer receives HTTPS traffic
   directly, host nginx does. Reload it with `docker compose up -d`.
4. Verify: `curl -I http://127.0.0.1:8081` should return crossword's
   response. `sudo ss -tlnp | grep -E ':80|:443'` should now show only
   host nginx.
5. Add a host nginx site for it, e.g.
   `/etc/nginx/sites-available/crossword.yehor-inq.com.conf`:
   ```nginx
   server {
       listen 80;
       server_name crossword.yehor-inq.com;
       location / {
           proxy_pass http://127.0.0.1:8081;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   ```bash
   sudo ln -s /etc/nginx/sites-available/crossword.yehor-inq.com.conf /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   sudo certbot --nginx -d crossword.yehor-inq.com
   ```
   (If crossword already had a Let's Encrypt cert issued on the host from
   before it moved into Docker, certbot will just renew/reuse it.)

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
  default to `yehor-inq.com` in `.env.example`, adjust if you also want
  `www`.
- Leave `SECURE_SSL_ENABLED=1` — nginx redirects to HTTPS once certbot has
  run (step 3). If you want to smoke-test over plain HTTP first, set it to
  `0` temporarily.

```bash
mkdir -p media
docker compose up -d --build
docker compose logs -f web   # watch migrate/collectstatic, Ctrl-C when it settles
```

`web` now listens on `127.0.0.1:8001` only (see `docker-compose.yml`).

## 3. Host nginx + TLS for yehor-inq.com

```bash
sudo cp deploy/nginx/yehor-inq.com.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/yehor-inq.com.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d yehor-inq.com -d www.yehor-inq.com
```

Certbot edits the `listen 80` block in place to add `listen 443 ssl` +
redirect. Confirm `https://yehor-inq.com` loads.

## 4. DNS / Cloudflare

- Add `A` records for `yehor-inq.com` and `www` pointing at the server's
  IP (orange-cloud/proxied as you prefer).
- Once the origin has a valid Let's Encrypt cert, set Cloudflare SSL/TLS
  mode to **Full (strict)** for the zone so Cloudflare↔origin traffic is
  also encrypted and verified.

## 5. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable   # if not already
```
Nothing else needs to be open — both app containers (8001, 8081) are
bound to `127.0.0.1` only.

## 6. Auto-deploy on push to main

`.github/workflows/deploy.yml` SSHes into the server and runs
`deploy/deploy.sh` (git reset to `origin/main`, `docker compose up -d
--build`), then purges the whole Cloudflare cache via the API — all
triggered by a push to `main`.

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
