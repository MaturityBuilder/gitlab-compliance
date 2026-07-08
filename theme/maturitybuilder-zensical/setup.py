from setuptools import find_packages, setup

setup(
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={
        "maturitybuilder_zensical": [
            "mkdocs_theme.yml",
            "main.html",
            "assets/**/*",
            "partials/**/*",
        ],
    },
    include_package_data=True,
)
