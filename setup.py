from setuptools import setup, find_packages

setup(
    name='microgrid',
    version='0.0.1',
    description='Package to build microgrid model',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    extras_require={  
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
)