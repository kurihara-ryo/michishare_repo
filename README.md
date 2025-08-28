# Michishare
旅行プラン共有アプリ（Django）

## 開発起動
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
