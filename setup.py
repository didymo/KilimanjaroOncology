from setuptools import find_namespace_packages, setup

setup(
    name="KilimanjaroOncology",
    version="0.1",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    url="",
    license="",
    author="Ashley Maher",
    author_email="ashley.maher@didymodesigns.com.au",
    description="Kilimanjaro Oncology Data Management System",
    include_package_data=True,
    package_data={
        "app": ["csv_files/*.CSV", "csv_files/*.csv", "database/*.sql"],
    },
    install_requires=[
        # Only external dependencies should be listed here
        # Standard library modules shouldn't be included
    ],
    entry_points={  # Assumes there's a main() function in
        "console_scripts": [  # kilimanjaro_oncology/main.py
            "KilimanjaroOncology=kilimanjaro_oncology.main:main",
        ],
    },
    python_requires=">=3.6",
)
