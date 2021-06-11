"""
Setup package for the stm_package
"""
import setuptools

with open('requirements.txt', 'r', encoding='utf-8') as rf:
    requirements = [requirement.strip('\n') for requirement in rf.read().split('\n')]
    while '' in requirements:
        requirements.remove('')

with open('README.md', 'r', encoding='utf-8') as df:
    description = df.read()


setuptools.setup(
    name='subtree-metric',
    version='0.2.4',
    author='Kashchikhin Andrej',
    author_email='logerk3@gmail.com',
    description='Subtree Metric for the translation evaluation',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/WhiteJaeger/nlp-metrics',
    project_urls={
        'Bug Tracker': 'https://github.com/WhiteJaeger/nlp-metrics/issues',
        'Web Application': 'https://nlp-metrics.herokuapp.com'
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['subtree_metric'],
    python_requires='>=3.6',
    install_requires=requirements
)
