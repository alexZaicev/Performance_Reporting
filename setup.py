from setuptools import setup

setup(
    name='Report Generator',
    version='1.0.1',
    license='MIT',
    description='Performance monitoring report generator for Birmingham City Council',
    author='Aleksej Zaicev',
    author_email='alex.zaicef@gmail.com',
    packages=['src'],
    install_required=['pandas', 'xlrd']
    )
