# setup.py

import pathlib
from setuptools import setup, find_packages

setup(
    name='concepts',
    version='0.10.dev0',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Formal Concept Analysis with Python',
    keywords='fca complete lattice graph join meet galois',
    license='MIT',
    url='https://github.com/xflr6/concepts',
    project_urls={
        'Documentation': 'https://concepts.readthedocs.io',
        'Changelog': 'https://concepts.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/xflr6/concepts/issues',
        'CI': 'https://github.com/xflr6/concepts/actions',
        'Coverage': 'https://codecov.io/gh/xflr6/concepts',
    },
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.6',
    install_requires=[
        'bitsets~=0.7',
        'graphviz~=0.7',
    ],
    extras_require={
        'dev': ['tox>=3', 'flake8', 'pep8-naming', 'wheel', 'twine'],
        'test': ['pytest>=5.2', 'pytest-cov'],
        'docs': ['sphinx>=1.8', 'sphinx-autodoc-typehints', 'sphinx-rtd-theme'],
    },
    long_description=pathlib.Path('README.rst').read_text(encoding='utf-8'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
