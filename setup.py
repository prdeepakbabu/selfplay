from setuptools import setup, find_packages

setup(
    name='selfplay',
    version='0.3.0',
    description='A multi-bot simulation package with multi-turn conversation, self-play, role-play capabilities, social science experiment simulation, and multi-provider support',
    author='Deepak Babu Piskala',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prdeepakbabu",
    author_email='prdeepak.babu@gmail.com',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'markdown2>=2.4.0',
        'requests>=2.28.0',
        'pyyaml>=6.0',
        'python-dotenv>=1.0.0'
    ],
    extras_require={
        'ui': ['gradio>=4.0.0'],
        'anthropic': ['anthropic>=0.5.0'],
        'google': ['google-generativeai>=0.3.0'],
        'aws': ['boto3>=1.28.0'],
        'socialsim': [
            'datasets>=2.10.0',
            'pandas>=1.3.0',
            'numpy>=1.20.0',
            'scipy>=1.7.0',
            'matplotlib>=3.4.0'
        ],
        'all': [
            'gradio>=4.0.0',
            'anthropic>=0.5.0',
            'google-generativeai>=0.3.0',
            'boto3>=1.28.0',
            'datasets>=2.10.0',
            'pandas>=1.3.0',
            'numpy>=1.20.0',
            'scipy>=1.7.0',
            'matplotlib>=3.4.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'selfplay = selfplay.app:main',
            'selfplay-ui = selfplay.app_gradio:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
