from setuptools import setup, find_packages

setup(
    name='selfplay',
<<<<<<< HEAD
    version='0.1.0',
    description='A multi-bot simulation package with multi-turn conversation and self-play and role-play capabilities',
=======
    version='0.2.0',
    description='A multi-bot simulation package with multi-turn conversation, self-play, role-play capabilities, and multi-provider support',
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
    author='Deepak Babu Piskala',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prdeepakbabu",
    author_email='prdeepak.babu@gmail.com',
    packages=find_packages(),
    install_requires=[
<<<<<<< HEAD
        'openai',
        'markdown2',
        'requests',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'selfplay = selfplay.app:main',
=======
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
        'all': [
            'gradio>=4.0.0',
            'anthropic>=0.5.0',
            'google-generativeai>=0.3.0',
            'boto3>=1.28.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'selfplay = selfplay.app:main',
            'selfplay-ui = selfplay.app_gradio:main',
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
<<<<<<< HEAD
)
=======
)
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
