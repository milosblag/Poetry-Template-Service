import os
import multiprocessing

# Gunicorn config variables
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8000")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")

# Gunicorn settings
max_requests = 1000
max_requests_jitter = 50
keepalive = 5
timeout = 120
graceful_timeout = 30

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores

if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)

# Bind
if bind_env:
    bind = bind_env
else:
    bind = f"{host}:{port}"

# For debugging and testing
log_data = {
    "loglevel": use_loglevel,
    "workers": web_concurrency,
    "bind": bind,
}
print(log_data)

# Gunicorn configuration
loglevel = use_loglevel
workers = web_concurrency
bind = bind
keepalive = keepalive
errorlog = "-"
accesslog = "-" 