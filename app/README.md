# Spotly - Local Development & Deployment Guide

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- Docker & Docker Compose (for deployment)

---

## 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Check if Poetry is available:

```bash
poetry --version
```

If Poetry is not found, add it to your PATH:

1. Open your bash configuration:
   ```bash
   nano ~/.bashrc
   ```
2. Add this line at the end:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
3. Save and reload:
   ```bash
   source ~/.bashrc
   ```

---

## 2. Clone the Repository

```bash
git clone https://github.com/team-gamma-devs/spotly.git
cd spotly
```

---

## 3. Install Dependencies

```bash
poetry install --no-root
```

---

## 4. Environment Variables

Create a .env file in the project root with the following variables:

```env
SECRET_KEY= # Generate with: openssl rand -hex 32
RESEND_API_KEY= # Your Resend API key or email service key
MONGO_INITDB_ROOT_USERNAME= # MongoDB username
MONGO_INITDB_ROOT_PASSWORD= # MongoDB password
MONGODB_URL=mongodb://USERNAME:PASSWORD@mongo:27017 # Use the above credentials
```

---

## 5. Activate Poetry Virtual Environment

```bash
source $(poetry env activate)
```

---

## 6. Run the Application (Development)

```bash
uvicorn app.main:app --reload
```

---

## 7. Deployment with Docker Compose

### Install Docker & Docker Compose

Follow [official Docker instructions](https://docs.docker.com/engine/install/) or use:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker & Compose
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify installation:
```bash
sudo docker run hello-world
```

---

### Build & Run Containers

```bash
docker compose build --no-cache
docker compose up -d
```

The app will now be running on your server.

---