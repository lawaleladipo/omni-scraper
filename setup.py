from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="omni-scraper",
    version="0.3.0",
    description="Async OSINT toolkit with Intelligence X leaks, Tor crawler, Shodan, and scraping.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lawaleladipo/omni-scraper",
    author="Olawale Oladipo",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[x.strip() for x in open("requirements.txt") if x.strip()],
    entry_points={
        "console_scripts": [
            "omni-scraper=omni_scraper.cli:cli",
        ]
    },
)
