#!/usr/bin/env python

import io
import os
import re
from collections import OrderedDict

from setuptools import find_packages, setup


def get_version(package):
    with io.open(os.path.join(package, "__init__.py")) as f:
        pattern = r'^__version__ = [\'"]([^\'"]*)[\'"]'
        return re.search(pattern, f.read(), re.MULTILINE).group(1)


setup(
    name="django-graphene-auth",
    version=get_version("graphql_auth"),
    license="MIT",
    description="Graphql and relay authentication with Graphene for Django.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="ptbang",
    author_email="ptbang@gmail.com",
    maintainer="ptbang",
    url="https://github.com/ptbang/django-graphene-auth",
    project_urls=OrderedDict((("Documentation", "https://django-graphene-auth.readthedocs.io/en/latest/"),)),
    packages=find_packages(exclude=["test*"]),
    install_requires=[
        "Django>=3.2",
        "django-graphql-jwt==0.4.0",
        "django-filter>=23.5",
        "graphene_django>=3.1.6",
        "graphene>=3.3",
        "PyJWT>=2.8.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
    keywords="api graphql rest relay graphene auth jwt",
    zip_safe=False,
    include_package_data=True,
)
