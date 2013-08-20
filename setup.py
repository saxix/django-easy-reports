#!/usr/bin/env python
import os
import codecs
from setuptools import setup, find_packages
import ereports

RELEASE = ereports.get_version()

base_url = 'https://github.com/saxix/django-concurrency/'
VERSIONMAP = {'final': (ereports.VERSION, 'Development Status :: 5 - Production/Stable'),
              'rc': (ereports.VERSION, 'Development Status :: 4 - Beta'),
              'beta': (ereports.VERSION, 'Development Status :: 4 - Beta'),
              'alpha': ('master', 'Development Status :: 3 - Alpha')}

download_tag, development_status = VERSIONMAP[ereports.VERSION[3]]


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()


def reqs(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return filter(lambda x: not x.startswith('#'),
                  codecs.open(os.path.join(here, *parts), 'r').readlines())


setup(
    name=ereports.NAME,
    version=RELEASE,
    url='https://github.com/saxix/django-easy-reports',
    author='sax',
    author_email='s.apostolico@gmail.com',
    packages=find_packages(),
    include_package_data=True,

    dependency_links=['http://pypi.wfp.org/simple/'],
    install_requires=reqs('ereports/requirements/install.pip'),
    tests_require=reqs('ereports/requirements/testing.pip'),
    test_suite='conftest.runtests',

    description="Django reporting library ",
    long_description=open('README.rst').read(),
    license="MIT License",
    keywords="django",
    classifiers=[
        development_status,
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],

)
