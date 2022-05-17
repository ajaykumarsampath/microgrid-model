from setuptools import setup, find_packages

setup(
    name='microgrid',
    version='0.0.1',
    description='Package to build microgrid model',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    author='Ajay Kumar',
    author_email='ajaykumarsampath@gmail.com',
    url="https://github.com/ajaykumarsampath/microgrid-model",
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'dacite',
        'pydantic'
    ],
    setup_requires=['flake8'],
    extras_require={  
        "dev": ["check-manifest"],
        "test": [
            "pytest",
            "numpy",
            "scipy",
            "coverage",
            "pytest-cov"
        ],
    },
)
