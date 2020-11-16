from setuptools import find_packages, setup

setup(
    name="gp2gp-mesh-s3-uploader",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["boto3~=1.16", "defusedxml~=0.6"],
    entry_points={
        "console_scripts": [
            "sync-mesh-to-s3=gp2gp.synchronizer:main",
        ]
    },
)
