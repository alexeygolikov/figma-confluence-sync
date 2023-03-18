from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="figma-confluence-sync",
    version="0.1.0",
    author="Oleksii Golikov",
    description="figma-confluence-sync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexeygolikov/figma-confluence-sync",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Apache License Version 2.0",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=['requests', 'python-dotenv'],
)
