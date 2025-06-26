# ADN-YSC-Portal-Backend

## 🚀 Setup Instructions (FastAPI + Docker)
Follow these steps to get the **ADN YSC Portal Backend** running locally.

### ✅ Prerequisites
Ensure the following are installed:
* [Docker & Docker Compose](https://docs.docker.com/get-docker/)
* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)

### 📦 1. Clone the Repository

```bash
git clone https://github.com/mwiks-dev/ADN-YSC-Portal-Backend.git
cd ADN-YSC-Portal-Backend
```

### ⚙️ 2. Environment Variables
```bash 
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 🐳 3. Start the App with Docker

> Make sure no other service is using port **3306** (MySQL) or change it in `docker-compose.yml`.

```bash
sudo docker compose up -d --build --remove-orphans
```
This will:

* Build the FastAPI app
* Start the database (MySQL)
* Launch the API server

### 🌐 4. Access the API

Once running, open:
* **API base**: `http://localhost:8000`
* **Interactive Docs (Swagger)**: `http://localhost:8000/docs`
* **ReDoc**: `http://localhost:8000/redoc`


### 🐍 Optional: Run Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload
```

By default, this runs on `http://127.0.0.1:8000`.

### 🧪 Testing & Development

* Use Swagger UI for interactive testing
* Keep code organized in `controllers/`, `models/`, and `type/` folders
