Application Setup Guide
=======================

This guide provides step-by-step instructions to set up and run the application.

------------------------------------------------------------
1. Virtual Environment Setup
------------------------------------------------------------

Activate the existing virtual environment, or create a new one if it does not exist.

Create a virtual environment:
    python3 -m venv venv

Activate the virtual environment:

- Windows (PowerShell):
    .\venv\Scripts\activate

- Mac/Linux:
    source venv/bin/activate


------------------------------------------------------------
2. Verify Python & pip Installation
------------------------------------------------------------

Check if Python and pip are installed. If not, install them.

Mac/Linux:
    brew install python
    sudo apt install python3
    python3 -m venv venv
    pip install virtualenv


------------------------------------------------------------
3. Database Setup
------------------------------------------------------------

Ensure the database service is running and properly configured in Django.

Mac:
    brew services start mysql

Check the database configuration in your Django settings.py.


------------------------------------------------------------
4. Install Project Dependencies
------------------------------------------------------------

Install all required packages:
    pip install -r requirements.txt


------------------------------------------------------------
5. Django Setup
------------------------------------------------------------

Run the following commands to prepare and launch the application:
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver


------------------------------------------------------------
6. Asynchronous Task Setup
------------------------------------------------------------

Install Redis

Mac:
    redis-server --version
    brew install redis
    brew services start redis
    redis-server
    redis-cli ping

Windows:
    1. Download Redis from the official website.
    2. Start Redis:
        redis-server
    3. Verify Redis is running:
        redis-cli ping


------------------------------------------------------------
7. Celery Configuration
------------------------------------------------------------

Check that Celery is properly configured to use Redis as the broker.

In settings.py:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'

Start the Celery worker:
    celery -A HRMS worker --loglevel=info

To enable event tracking:
    celery -A HRMS worker --loglevel=info -E


------------------------------------------------------------
Once all the above steps are completed, your HRMS application should be fully operational.
------------------------------------------------------------

