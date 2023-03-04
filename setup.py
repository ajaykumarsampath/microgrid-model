from setuptools import setup, find_packages

"""
with open('requirements.txt') as f:
    required = f.read().splitlines()
"""

setup(
    name='microgrid',
    version='0.0.1',
    description='Package to build microgrid model',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    author='Ajay Kumar',
    author_email='ajaykumarsampath@gmail.com',
    license='MIT',
    keywords='microgird model, energy management system',
    url="https://github.com/ajaykumarsampath/microgrid-model",
    python_requires=">=3.8",
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'dacite',
        'pydantic',
        'cvxpy',
        'cylp',
    ],
    setup_requires=['flake8'],
    extras_require={  
        "dev": ["check-manifest"],
        "test": [
            "pytest",
            "numpy",
            "scipy",
            "coverage",
            "pytest-cov",
            "cvxpy",
            "cylp"
        ],
    },
)
