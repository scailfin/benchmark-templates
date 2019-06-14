from setuptools import setup


install_requires=[
    'future',
    'gitpython',
    'jsonschema',
    'pyyaml>=5.1'
]


tests_require = [
    'coverage>=4.0',
    'coveralls',
    'nose'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
}


setup(
    name='benchmark-templates',
    version='0.1.0',
    description='Workflow Templates for Reproducible Data Analysis Benchmarks',
    keywords='reproducibility benchmarks data analysis',
    license='MIT',
    packages=['benchtmpl'],
    include_package_data=True,
    test_suite='nose.collector',
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires
)
