module.exports = {
  apps: [{
    name: 'price-forecast-api',
    script: 'uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    cwd: 'C:\\Users\\Mischelle\\price-forecast-api',
    interpreter: 'python',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
