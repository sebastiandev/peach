import re
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


setup(
    name='python-peach',
    packages=['peach'],
    version=get_version('peach'),
    description='A Lightweight framework for building restful apis',
    author='Sebastian Packmann',
    author_email='devsebas@gmail.com',
    url='https://github.com/sebastiandev/peach',
    download_url='https://github.com/sebastiandev/peach/archive/0.1.tar.gz',
    keywords=['flask', 'falcon', 'python', 'api', 'framework', 'restful'],
    install_requires=[
        'marshmallow',
        'webargs'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Framework :: Falcon',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
