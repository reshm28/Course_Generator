from setuptools import setup, find_packages

setup(
    name="edhub-course-generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Add your project's dependencies here
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "langgraph>=0.1.0",
        # Add other dependencies as needed
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "pytest-cov>=2.0.0",
            "black>=21.0",
            "isort>=5.0.0",
            "mypy>=0.900",
        ],
    },
)
