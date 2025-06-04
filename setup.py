from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eu-ai-act-compliance-checker",
    version="1.0.0",
    author="EU AI Act Compliance Team",
    author_email="compliance@example.com",
    description="MCP Server & Gradio App for EU AI Act Compliance Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/eu-ai-act-compliance-checker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers", 
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Legal",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "cloud": [
            "modal>=0.50.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eu-ai-act-checker=app:main",
        ],
    },
    include_package_data=True,
    keywords="eu ai act, compliance, mcp, gradio, legal tech, ai regulation",
    project_urls={
        "Bug Reports": "https://github.com/your-username/eu-ai-act-compliance-checker/issues",
        "Source": "https://github.com/your-username/eu-ai-act-compliance-checker",
        "Documentation": "https://github.com/your-username/eu-ai-act-compliance-checker/wiki",
    },
) 