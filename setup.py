from setuptools import setup, find_packages

setup(
    name="autonomous_defense_firm",
    version="0.1.0",
    description="AI-powered autonomous criminal defense firm for Tennessee",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'autodef-firm=autonomous_defense_firm.cli:main',
        ],
    },
    python_requires='>=3.8',
)
