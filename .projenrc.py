"""
Script that generates read-only boilerplate files.

Files that are managed with this project-scaffolding script
are read-only. They must not be changed manually! Instead,
modify this script and regenerate them.

Some files managed by this script are:
- .gitignore
- setup.cfg
- setup.py
- pyproject.toml
- MANIFEST.in

If you're confused/curious about why we use this file to manage other files,
you can learn about the tool here: https://github.com/phitoduck/phito-projen
"""

import json

from phito_projen import PythonPackage
from phito_projen.components.templatized_file import TemplatizedFile
from projen import Project

repo = Project(name="awscdk-minecraft")

metaflow_cdk_package = PythonPackage(
    parent=repo,
    name="awscdk-minecraft",
    outdir="awscdk-minecraft",
    module_name="cdk_minecraft",
    version="0.0.0",
    install_requires=[
        "aws-cdk-lib >=2.45.0, <3.0.0",
        "constructs >=10.0.5, <11.0.0",
    ],
)

vscode_settings_kwargs = dict(
    project=repo,
    file_path=".vscode/example-settings.json",
    make_comment_fn=lambda line: f"// {line}",
    supports_comments=True,
    template_body=json.dumps(
        {
            "restructuredtext.confPath": "",
            "autoDocstring.customTemplatePath": "./.vscode/python-docstring-template.mustache",
            "python.linting.pylintEnabled": True,
            "python.linting.pylintArgs": ["--rcfile=./linting/.pylintrc"],
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": ["--line-length=112"],
            "python.linting.flake8Enabled": True,
            "python.linting.flake8Args": [
                "--config==./linting/.flake8",
                "--max-line-length=112",
            ],
            "editor.formatOnSave": True,
        },
        indent=4,
    ),
)

vscode_settings_json = TemplatizedFile(**vscode_settings_kwargs)
vscode_settings_kwargs["is_sample"] = True
vscode_settings_kwargs["file_path"] = ".vscode/settings.json"
sample_vscode_settings_json = TemplatizedFile(**vscode_settings_kwargs)

repo.gitignore.add_patterns(
    "venv",
    "*cache*",
    ".env",
    "metaflow-repos",
    ".metaflow",
    "**cdk.out/",
    "**cdk.context.json",
    ".vscode",
    "!.vscode/python-docstring-template.mustache",
    "!.vscode/example-settings.json",
)

# generate/update boilerplate project files in this repository
repo.synth()
