from setuptools import setup

setup(
    name='PY Harvest Website Emails',
    version='0.0.1',
    py_modules=['scripts/main'],
    install_requires=[
        'Click',
        'requests==2.26.0',
        'beautifulsoup4==4.10.0',
        'selenium==4.8.2',
        'webdriver-manager==3.8.5'
    ],
    entry_points={
        'console_scripts': [
            'harvest-website-emails = scripts.main:cli',
        ],
    },
)
