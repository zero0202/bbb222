import os
from pathlib import Path

TOKEN = os.getenv("1423900079:AAGW__3wRFANjB8tU87w72Gny4pOl5Q5h58")
admin_id = int(os.getenv(615399265))
db_user = os.getenv("anonimchat")
db_pass = os.getenv("zero+2003")
# lp_token = os.getenv("LIQPAY_TOKEN")
host = os.getenv("104.196.100.114")

I18N_DOMAIN = 'anonim_chat_uzbot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'