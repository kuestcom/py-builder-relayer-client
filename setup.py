import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kuest-py-builder-relayer-client",
    version="2.0.6",
    author="Kuest Engineering",
    author_email="engineering@kuest.com",
    maintainer="Kuest Engineering",
    maintainer_email="engineering@kuest.com",
    description="Wallet-only Python client for the Kuest relayer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kuestcom/py-builder-relayer-client",
    install_requires=[
        "eth-account>=0.13.7",
        "eth-abi>=5.0.0",
        "eth-utils>=6.0.0",
        "hexbytes>=1.3.1",
        "python-dotenv>=1.2.2",
        "requests>=2.34.2",
        "kuest-py-builder-signing-sdk>=2.0.2",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/kuestcom/py-builder-relayer-client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
)
