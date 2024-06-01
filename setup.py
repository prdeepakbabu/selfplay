from setuptools import setup, find_packages

setup(
    name='selfplay',
    version='0.1.0',
    description='A multi-bot simulation package with multi-turn conversation and self-play and role-play capabilities',
    author='Deepak Babu Piskala',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prdeepakbabu",
    author_email='prdeepak.babu@gmail.com',
    packages=find_packages(),
    install_requires=[
        'openai',
        'markdown2',
        'requests',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'selfplay = selfplay.app:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)