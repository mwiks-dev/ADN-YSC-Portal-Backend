module.exports = {
    apps: [
        {
            name: "fastapi-app",
            script: "/home1/adnyouth/virtualenv/backend/3.12/bin/uvicorn",
            args: "main:app --host 127.0.0.1 --port 5000 --reload",
            interpreter: "none",
            cwd: "/home1/adnyouth/backend",
            watch: false,
            autorestart: true,
            env: {
                PATH: "/home1/adnyouth/virtualenv/backend/3.12/bin:/usr/local/bin:/usr/bin:/bin",
                PYTHONPATH: "/home1/adnyouth/backend",
                VIRTUAL_ENV: "/home1/adnyouth/virtualenv/backend/3.12",
            },
        },
    ],
};