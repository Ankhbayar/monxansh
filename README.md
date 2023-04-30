Мон Ханш
========

Монголын Банкнуудын ханш татагч widget. Монгол банкны албан ханшийг харуулаж байгаа.


# Prepare Development Environgment

```console
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
# Run App

```console
gunicorn main:app --reload
```