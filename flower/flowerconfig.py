import os

from dotenv import load_dotenv

from modeling_system_backend.settings import BASE_DIR

load_dotenv(f"{BASE_DIR}/.env")

broker_url = os.environ.get("BROKER_URL")

port = os.environ.get("FLOWER_PORT")

logging = "info"

persistent = True

state_save_interval = 10

basic_auth = [f"{os.environ.get('FLOWER_LOGIN')}:{os.environ.get('FLOWER_PASSWORD')}"]  # Или "user:password"
url_prefix = os.environ.get("FLOWER_PREFIX")

# Уведомления (например, если хотите Telegram-бота)
# flower_events = True
