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




