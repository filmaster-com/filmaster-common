import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='filmaster-common',
    version='0.1',
    packages=['film_common'],
    install_requires=[
        'pytz',
        'jsonrpclib',
    ],
    include_package_data=True,
    long_description=README,
    url='https://github.com/filmaster-com/filmaster-common',
    author='filmaster.tv',
    author_email='dev@filmaster.tv',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
