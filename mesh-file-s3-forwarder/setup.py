from setuptools import find_packages, setup

setup(
    name="gp2gp-mesh-file-s3-forwarder",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["boto3~=1.16", "defusedxml~=0.6"],
    entry_points={
        "console_scripts": [
            "forward-mesh-files-to-s3=gp2gp.main:main",
        ]
    },
)
