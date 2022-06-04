from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name="tuckboxes",
    version=version,
    entry_points={
        'console_scripts': [
            "tuckboxes = tuckboxes.tuckboxes:main"
        ],
    },
    packages=find_packages(exclude=['tests']),
    install_requires=["reportlab>=3.4.0",
                      "Pillow>=4.1.0",
                      "numpy",
                      "click"],
    url='http://domtabs.sandflea.org',
    include_package_data=True,
    author="Peter Gorniak",
    author_email="sumpfork@mailmight.net",
    description="Tuckbox Generation for Board- and Cardgames",
    keywords=['boardgame', 'cardgame', 'tuckboxes'],
    long_description=""
)
