import toml
from setuptools import find_packages, setup


def get_version():
    with open("pyproject.toml", "r") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["tool"]["semantic_release"]["version"]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="klingon_tools",
    version=get_version(),
    author="David Hooton",
    author_email="klingon_tools+david@hooton.org",
    description="A set of utilities for running and logging shell commands in "
    "a user-friendly manner.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djh00t/klingon_tools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "openai",
        "gitpython",
        "requests",
        "httpx",
        "windows-curses; platform_system == 'Windows'",
        "pyyaml",
        "ruamel.yaml",
        "pre-commit",
        "psutil",
        "tabulate",
        "packaging",
    ],
    entry_points={
        "console_scripts": [
            "push=klingon_tools.push:main",
            "gh-actions-update=klingon_tools.gh_actions_update:main",
            "pr-title-generate=klingon_tools.entrypoints:gh_pr_gen_title",
            "pr-summary-generate=klingon_tools.entrypoints:gh_pr_gen_summary",
            "pr-context-generate=klingon_tools.entrypoints:gh_pr_gen_context",
            "pr-body-generate=klingon_tools.entrypoints:gh_pr_gen_body",
        ],
    },
    include_package_data=True,
    data_files=[("", ["CHANGELOG.md", "README.md"])],
)
