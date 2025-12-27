# OpenPoke Deployment Guide

This guide explains how to deploy OpenPoke to a Virtual Private Server (VPS) using Docker.

## Prerequisites

1.  **A VPS**: DigitalOcean Droplet, Hetzner Cloud, AWS Lightsail, etc.
    - OS: Ubuntu 22.04 or 24.04 (recommended)
    - Specs: 2GB RAM minimum (for building Next.js)
2.  **Domain Name** (Optional but recommended for SSL/Twilio): e.g., `my-assistant.com`

## 1. Prepare the VPS

SSH into your VPS and install Docker & Docker Compose:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker compose version
```

## 2. Copy Files

Copy your project files to the VPS. You can use `scp` or `git`.

**Option A: Git (Recommended)**
Push your code to a private GitHub repo, then clone it on the VPS.

**Option B: SCP (Direct Copy)**
Run this from your local machine:

```bash
scp -r /path/to/openpoke root@YOUR_VPS_IP:/root/openpoke
```

## 3. Configure Environment

1.  SSH into the VPS and go to the project folder:
    ```bash
    cd /root/openpoke
    ```
2.  Create/Edit your `.env` file:
    ```bash
    cp .env.example .env
    nano .env
    ```
3.  **Important**: Update `NEXT_PUBLIC_FRONTEND_URL` in `.env` if you have a domain:
    ```bash
    NEXT_PUBLIC_FRONTEND_URL=https://your-domain.com
    ```
    If using IP only:
    ```bash
    NEXT_PUBLIC_FRONTEND_URL=http://YOUR_VPS_IP
    ```

## 4. Configure Caddy (SSL)

If you have a domain, update `Caddyfile` to automatically get HTTPS certificates.

Edit `Caddyfile`:

```caddy
your-domain.com {
    handle /api/v1/* {
        reverse_proxy backend:8001
    }

    handle {
        reverse_proxy frontend:3000
    }
}
```

_Replace `your-domain.com` with your actual domain._

If you are using just an IP address, keep the default `:80` configuration.

## 5. Start the App

Run Docker Compose:

```bash
docker compose up -d --build
```

- `-d`: Detached mode (runs in background)
- `--build`: Forces rebuilding the images

## 6. Verify

- Open your browser to `http://YOUR_VPS_IP` (or your domain).
- Check logs if something is wrong:
  ```bash
  docker compose logs -f
  ```

## 7. Update Twilio

If you are using SMS:

1.  Go to Twilio Console.
2.  Update the Webhook URL for your phone number to:
    `https://your-domain.com/api/v1/sms/webhook`
    (Or `http://YOUR_VPS_IP/api/v1/sms/webhook` if not using SSL)

## Data Persistence

- **Conversation Logs**: Stored in `server/data` (mapped to host folder).
- **Auth Tokens**: Stored in Docker volume `openpoke_config`.

To back up your data, back up the `server/data` folder and the contents of the `openpoke_config` volume.
