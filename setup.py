from setuptools import setup, find_packages
import os

setup(
    name="autoskill-ai",
    version="1.0.6",
    description="AI agent self-evolution plugin supporting dynamic skill generation, execution and management",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.py', '*.yaml', '*.json', '*.md', '*.safetensors', '*.txt'],
        'templates': ['*.yaml'],
        'core': ['model/**/*'],
    },
    install_requires=[
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "langchain": [
            "langchain>=0.1.0",
            "langchain-openai>=0.1.0",
            "openai>=1.30.0",
        ],
        "ml": [
            "numpy>=1.21.2",
            "pandas>=1.3.3",
            "scikit-learn>=0.24.2",
        ],
        "nlp": [
            "nltk>=3.6.3",
            "transformers>=4.18.0",
        ],
        "deep-learning": [
            "tensorflow>=2.8.0",
            "torch>=1.9.0",
        ],
        "skill-fingerprint": [
            "sentence-transformers>=2.2.0",
        ],
        "all": [
            "autoskill-ai[langchain,ml,nlp,deep-learning,skill-fingerprint]",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)