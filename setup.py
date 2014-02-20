# -*- coding: utf-8 -*-
"""
    setup

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import re
import os
import ConfigParser
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []

MODULE = 'incoterm_sale_opportunity'
PREFIX = 'openlabs'
MODULE2PREFIX = {
    'incoterm': 'openlabs'
}

for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append(
            '%s_%s >= %s.%s, < %s.%s' % (
                MODULE2PREFIX.get(dep, 'trytond'), dep,
                major_version, minor_version, major_version, minor_version + 1
            )
        )

setup(
    name='%s_%s' % (PREFIX, MODULE),
    version=info.get('version'),
    description='Intercom Sale Opportunity Module for Tryton',
    author='Openlabs Technologies & Consulting (P) Limited',
    author_email='info@openlabs.co.in',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Office/Business',
    ],
    package_dir={'trytond.modules.%s' % (MODULE): '.'},
    packages=[
        'trytond.modules.%s' % (MODULE),
        'trytond.modules.%s.tests' % (MODULE),
    ],
    package_data={
        'trytond.modules.%s' % (MODULE): info.get('xml', [])
        + ['emails/*.html', 'tryton.cfg', 'view/*.xml']
        + info.get('translation', [])
    },
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    %s = trytond.modules.%s
    """
    % (MODULE, MODULE),
    test_suite='tests.suite',
    test_loader='trytond.test_loader:Loader',
)
