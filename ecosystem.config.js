module.exports = {
    apps: [
        {
            name: "fastapi-app",
            script: "/home/adnyouth/virtualenv/python/main/3.12/bin/uvicorn",
            args: "main:app --host 127.0.0.1 --port 5000",
            interpreter: "none",
            cwd: "/home1/adnyouth/python/main",
            watch: false,
            autorestart: true,
            env: {
                PATH: "/home/adnyouth/virtualenv/python/main/3.12/bin:/usr/local/bin:/usr/bin:/bin",
                PYTHONPATH: "/home1/adnyouth/python/main",
                VIRTUAL_ENV: "/home/adnyouth/virtualenv/python/main/3.12",
            },
        },
    ],
};