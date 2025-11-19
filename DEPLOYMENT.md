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

### Step 1: Verify User Has Shell Access

On your **server**, check if the SSH user has shell access:

```bash
# Check current user's shell
grep "^$USER:" /etc/passwd

# The line should end with /bin/bash, NOT /usr/sbin/nologin or /bin/false
```

If it shows `/usr/sbin/nologin` or `/bin/false`, enable shell access:

```bash
# Enable bash shell for your user (requires sudo)
sudo usermod -s /bin/bash your-username

# Or use a different user that already has shell access
grep "/bin/bash" /etc/passwd
```

### Step 2: Generate SSH Key on Server

On your **server** (this is simpler than generating locally):

```bash
# Generate key pair
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/github_deploy_key -N ""

# Add public key to authorized_keys
cat ~/github_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Display the private key to copy to GitHub
cat ~/github_deploy_key

# After copying to GitHub, remove the key files for security
rm ~/github_deploy_key ~/github_deploy_key.pub
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

### Verify New Version is Running

After deployment, verify the new code is active:

```bash
# On your server, check the current git commit
cd /path/to/daily-tutor-bot
git log -1 --oneline

# Compare with what's on GitHub main branch
# They should match after deployment

# Check when containers were created
docker-compose ps
# Look at the "Created" column - should be recent

# Verify containers are running
docker-compose ps | grep "Up"
```

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

### Check specific commit is deployed:
```bash
# On server
cd /path/to/daily-tutor-bot
git rev-parse HEAD  # Get current commit hash

# Compare with GitHub
# https://github.com/shawnsquire/daily-tutor-bot/commits/main
```

## Troubleshooting

### "This account is currently not available"
This means the SSH user doesn't have shell access enabled.

**Fix:**
```bash
# On your server, check the user's shell
grep "^$USER:" /etc/passwd

# If it shows /usr/sbin/nologin or /bin/false, enable bash:
sudo usermod -s /bin/bash your-username

# Verify the change
grep "^$USER:" /etc/passwd  # Should now show /bin/bash
```

After fixing, update the `SSH_USER` secret in GitHub if you changed to a different user.

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
