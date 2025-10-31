#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='goalin',
    version='0.1.0',
    description='Productivity tracking service for Linux',
    author='YadavYashvant',
    author_email='',
    url='https://github.com/YadavYashvant/Goalin',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'goalin-daemon=goalin.daemon:main',
            'goalin-gui=goalin.gui:main',
            'goalin-report=goalin.report:main',
            'goalin-setup=goalin.setup_wizard:run_setup_wizard',
        ],
    },
    install_requires=[
        'PyGObject>=3.42.0',
        'python-xlib>=0.31',
        'pytz>=2021.3',
        'google-generativeai>=0.3.0',
    ],
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
    ],
)
