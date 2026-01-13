# setup.py
from setuptools import setup, find_packages

setup(
    name="ptlab2",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'Django==4.2.7',
        'psycopg2-binary==2.9.9',
        'gunicorn==21.2.0',
        'whitenoise==6.6.0',
        'dj-database-url==2.0.0',
        'pandas==2.0.3',
        'numpy==1.24.3',
    ],
    python_requires='>=3.11,<3.12',
)