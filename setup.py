from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentic-tdd",
    version="0.1.0",
    author="Pietro Dibello",
    author_email="pietro.dibello@example.com",
    description="Multi-Agent Test-Driven Development CLI Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xpepper/agentic-tdd",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.0.300",
        "langchain-openai>=0.0.5",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "GitPython>=3.1.30",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "isort>=5.10",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-tdd=agentic_tdd.cli:main",
        ],
    },
)