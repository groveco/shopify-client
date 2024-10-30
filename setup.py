from setuptools import setup, find_packages

setup(
    name="shopify-client",
    version="0.1.0",
    description="Python client for Shopify REST and GraphQL API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Anton Shutsik",
    author_email="shutikanton@gmail.com",
    url="https://github.com/groveco/shopify-client.git",
    packages=["shopify_client"],
    install_requires=[
        "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "flake8",
            "black",
            "sphinx",
            "pre-commit"
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Documentation": "https://github.com/groveco/shopify-client",
        "Source": "https://github.com/groveco/shopify-client",
        "Tracker": "https://github.com/groveco/shopify-client/issues",
    },
)
