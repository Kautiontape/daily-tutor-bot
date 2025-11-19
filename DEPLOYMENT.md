# Automated Deployment Setup

This guide will help you set up automated deployment so that pushes to the `main` branch automatically update your production server.

## How It Works

1. You push code to the `main` branch on GitHub
2. GitHub Actions triggers the deployment workflow
3. The workflow SSHs into your server
4. Pulls latest code, rebuilds Docker images, and restarts containers

## Prerequisites

- A server running your Daily Tutor Bot with Docker and Docker Compose
- SSH access to your server
- Git repository cloned on your server

## Setup Instructions

### Step 1: Generate SSH Key (if you don't have one)

On your **local machine** or in a secure location:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key
```

This creates two files:
- `~/.ssh/github_deploy_key` (private key - keep secret!)
- `~/.ssh/github_deploy_key.pub` (public key)

### Step 2: Add Public Key to Your Server

Copy the public key to your server:

```bash
ssh-copy-id -i ~/.ssh/github_deploy_key.pub your-username@your-server-ip
```

Or manually add it to `~/.ssh/authorized_keys` on your server:

```bash
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `SSH_HOST` | Your server's IP or domain | `123.45.67.89` or `bot.example.com` |
| `SSH_USER` | SSH username on your server | `ubuntu` or `root` |
| `SSH_PRIVATE_KEY` | Contents of the private key file | Copy entire contents of `~/.ssh/github_deploy_key` |
| `SSH_PORT` | SSH port (optional, defaults to 22) | `22` or `2222` |
| `DEPLOY_PATH` | Full path to project on server | `/home/ubuntu/daily-tutor-bot` |

#### How to Copy Private Key:

```bash
cat ~/.ssh/github_deploy_key
```

Copy everything including the `-----BEGIN` and `-----END` lines.

### Step 4: Prepare Your Server

On your **production server**:

1. **Clone the repository** (if not already done):
   ```bash
   cd /home/your-username  # or wherever you want it
   git clone https://github.com/shawnsquire/daily-tutor-bot.git
   cd daily-tutor-bot
   ```

2. **Create the `.env` file** with your production credentials:
   ```bash
   cp .env.example .env
   nano .env  # Add your actual credentials
   ```

3. **Create the external volume** (if not already exists):
   ```bash
   docker volume create daily_tutor_bot_postgres_data
   ```

4. **Initial start** (manual first time):
   ```bash
   docker-compose up -d
   ```

5. **Optional: Make deploy script executable**:
   ```bash
   chmod +x deploy.sh
   ```

### Step 5: Test the Deployment

Make a small change to your code, commit, and push to main:

```bash
git add .
git commit -m "Test automated deployment"
git push origin main
```

Go to your GitHub repository → Actions tab to watch the deployment progress.

## Manual Deployment

If you need to manually deploy on the server, you can either:

**Option 1: Use the deploy script**
```bash
cd /path/to/daily-tutor-bot
./deploy.sh
```

**Option 2: Run commands manually**
```bash
cd /path/to/daily-tutor-bot
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Monitoring

### Check if deployment succeeded:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f app
```

### View recent deployment logs:
```bash
docker-compose logs --tail=50 app
```

## Troubleshooting

### Deployment fails with "Permission denied"
- Make sure the public key is in `~/.ssh/authorized_keys` on the server
- Check file permissions: `chmod 600 ~/.ssh/authorized_keys`
- Verify SSH user has permission to access the deploy path

### Deployment fails with "Git pull failed"
- SSH into your server and check for merge conflicts
- Make sure the server's git user is configured
- May need to run `git reset --hard origin/main` on server if local changes exist

### Containers fail to start
- Check logs: `docker-compose logs`
- Verify `.env` file exists and has correct values
- Make sure the postgres volume exists: `docker volume ls`

### Database connection errors
- Ensure postgres container is running: `docker-compose ps`
- Check database credentials in `.env` match docker-compose.yml
- Verify the postgres volume is mounted correctly

## Security Notes

- Never commit the private SSH key to the repository
- Use GitHub Secrets for all sensitive data
- Consider using a dedicated deployment user with limited permissions
- Regularly rotate SSH keys
- Monitor deployment logs for suspicious activity

## Files Created

- `.github/workflows/deploy.yml` - GitHub Actions workflow
- `deploy.sh` - Optional manual deployment script
- `DEPLOYMENT.md` - This documentation

## Next Steps

After successful deployment:
1. Monitor logs to ensure bot is working correctly
2. Test bot functionality on Telegram
3. Set up monitoring/alerting for production issues
4. Consider adding a staging environment for testing before production
