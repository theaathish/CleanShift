from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cleanshift",
    version="1.0.0",
    author="CleanShift Team",
    description="CLI utility to clean and shift C drive content to other drives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "psutil>=5.9.0",
        "rich>=13.0.0",
        "colorama>=0.4.6",
        "pywin32>=306",
    ],
    entry_points={
        "console_scripts": [
            "cleanshift=cleanshift.main:cli",
        ],
    },
)
