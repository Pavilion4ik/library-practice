# library-practice 

# Installation

Python3 must be already installed

```shell
git clone https://github.com/Pavilion4ik/library-practice.git
cd library-practice
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
set DJANGO_DEBUG=<False to run in DEBUG=False or True for DEBUG=True>
set SECRET_KEY=<your SECRET_KEY>
python manage.py runserver
```

# Features

* Authentication functionality for Driver/User
* Managing books, borrowings, users and payments directly from API
* Powerful admin panel for advanced  managing
