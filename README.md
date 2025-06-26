# ADN-YSC-Portal-Backend
A backend API built with FastAPI for the ADN YSC Portal. This service handles data operations, user management, and API endpoints for the ADN YSC Youth platform.

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
If applicable, copy and configure your .env file
```bash
cp config/.env
```
Edit your config/.env with your local settings

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

### 📦 Project Structure
ADN-YSC-Portal-Backend/
│
├── config/          # Configuration files
├── controllers/     # FastAPI routers and business logic
├── models/          # SQLAlchemy or Pydantic models
├── type/            # Type definitions (schemas)
├── main.py          # App entry point
├── requirements.txt # Python dependencies
└── docker-compose.yml

## 🤝 Collaboration Guidelines
To keep development clean and organized, please follow these collaboration steps:
### 🔀 1. Clone the Repository
```bash
# Clone the main repo directly
git clone https://github.com/mwiks-dev/ADN-YSC-Portal-Backend.git
cd ADN-YSC-Portal-Backend
```

### 🌱 2. Create a New Working Branch
Always create a new branch for your feature or bug fix:
```bash
git checkout -b feature/your-feature-name
```
Example:
```bash
git checkout -b fix/login-redirect
```

### 💻 3. Make Changes and Commit
Make your changes, then commit with a clear message:
```bash
git add .
git commit -m "Add feature to handle user session timeout"
```

### 📤 4. Push to Your Branch
```bash
git push origin feature/your-feature-name
```

### 🚀 5. Open a Pull Request (PR)
Go to the [GitHub repo](https://github.com/mwiks-dev/ADN-YSC-Portal-Backend) and open a **Pull Request**:
* Select your branch as the source
* Select `master` as the target
* Add a clear description of what your PR does
* Request a review

### ✅ 6. Pull Latest Before Starting New Work
To avoid conflicts, always pull the latest changes from `master` before creating a new branch:
```bash
git checkout master
git pull origin master
```

### 🧹 7. Keep Your Branch Up to Date (Optional but Recommended)
If your PR stays open for a while:
```bash
git checkout feature/your-feature-name
git pull origin main --rebase
```
