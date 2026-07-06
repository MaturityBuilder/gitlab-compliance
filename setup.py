from setuptools import setup

setup(
    name="gitlab-docs",
    version="1.0.7",
    description="A tool that generates documentation from GitLab CI YAML",
    license="MIT",
    packages=["src"],
    package_dir={"": "."},
    author="Charlie Smith",
    author_email="me@charlieasmith.co.uk",
    keywords=["documentation", "gitlab-ci", "gitlab"],
    url="https://github.com/MaturityBuilder/gitlab-docs",
)
