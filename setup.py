from setuptools import setup, find_packages

setup(
    name="rpi-hid-keyboard",
    version="0.1.1",
    description="Generic USB HID Keyboard Bridge for RPi Gadgets",
    author="Breeze833",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "hid-keyboard-daemon=rpi_hid.cli:main",
        ],
    },
)
