# This is a "Justfile". "just" is a task-runner similar to "make", but much less frustrating.
# There is a VS Code extension for just that provides syntax highlighting.
#
# Execute any commands in this file by running "just <command name>", e.g. "just install".

set dotenv-load := true

AWS_PROFILE := "mlops-club"
AWS_REGION := "us-west-2"

CDK_PLATFORM_DIR := "awscdk-minecraft"
CDK_DEPLOYER_DIR := "awscdk-minecraft-server-deployer"
FRONTEND_DIR := "minecraft-platform-frontend"
BACKEND_DIR := "minecraft-platform-backend-api"
RESOURCES_DIR := CDK_PLATFORM_DIR + "/src/cdk_minecraft/resources"
STATIC_SITE_BUILD_OUTPUT_DIR := RESOURCES_DIR + "/minecraft-platform-frontend-static"


# install the project's python packages and other useful
install: require-venv
    # install useful VS Code extensions
    which code && code --install-extension njpwerner.autodocstring || echo "skipping install of autodocstring"
    which code && code --install-extension kokakiwi.vscode-just || echo "skipping install of vscode-just"
    cp .vscode/example-settings.json settings.json || echo ".vscode/settings.json already present"
    # install python packages not belonging to any particular package in this repo,
    # but important for development
    python -m pip install \
        pre-commit \
        phitoduck-projen \
        black \
        pylint \
        flake8 \
        mypy
    # install the minecraft-deployment package as an "editable" package
    python -m pip install -e {{CDK_PLATFORM_DIR}}[all]
    # install pre-commit hooks to protect the quality of code committed by contributors
    pre-commit install
    # # install git lfs for downloading rootski CSVs and other large files in the repo
    # git lfs install


cdk-deploy: #require-venv
    cd {{CDK_PLATFORM_DIR}} \
    && \
        AWS_PROFILE={{AWS_PROFILE}} \
        AWS_ACCOUNT_ID=$(just get-aws-account-id) \
        CDK_DEFAULT_REGION={{AWS_REGION}} \
        AWS_REGION={{AWS_REGION}} \
        cdk deploy \
            --all \
            --diff \
            --profile {{AWS_PROFILE}} \
            --require-approval any-change \
            --region {{AWS_REGION}} \
            --app "python app.py"

cdk-diff: #require-venv
    cd {{CDK_PLATFORM_DIR}} \
    && \
        AWS_PROFILE={{AWS_PROFILE}} \
        AWS_ACCOUNT_ID=$(just get-aws-account-id) \
        CDK_DEFAULT_REGION={{AWS_REGION}} \
        AWS_REGION={{AWS_REGION}} \
        cdk diff \
            --profile {{AWS_PROFILE}} \
            --region {{AWS_REGION}} \
            --app "python3 app.py"

cdk-destroy: #require-venv
    cd {{CDK_PLATFORM_DIR}} \
    && \
        AWS_PROFILE={{AWS_PROFILE}} \
        AWS_ACCOUNT_ID=`just get-aws-account-id` \
        CDK_DEFAULT_REGION={{AWS_REGION}} \
        cdk destroy --all --diff --profile {{AWS_PROFILE}} --region {{AWS_REGION}} --app "python3 app.py"

# generate CloudFormation from the code in "{{CDK_PLATFORM_DIR}}"
cdk-synth: require-venv #login-to-aws
    cd {{CDK_PLATFORM_DIR}} && \
        AWS_PROFILE={{AWS_PROFILE}} \
        AWS_ACCOUNT_ID=$(just get-aws-account-id) \
        CDK_DEFAULT_REGION={{AWS_REGION}} \
        AWS_REGION={{AWS_REGION}} \
        cdk synth --all --profile mlops-club --app "python3 app.py"

open-aws:
    #!/bin/bash
    MLOPS_CLUB_SSO_START_URL="https://d-926768adcc.awsapps.com/start"
    open $MLOPS_CLUB_SSO_START_URL

# Ensure that an "mlops-club" AWS CLI profile is configured. Then go through an AWS SSO
# sign in flow to get temporary credentials for that profile. If this command finishes successfully,
# you will be able to run AWS CLI commands against the MLOps club account using '--profile mlops-club'
# WARNING: this login only lasts for 8 hours
login-to-aws:
    #!/bin/bash
    MLOPS_CLUB_AWS_PROFILE_NAME="mlops-club"
    MLOPS_CLUB_AWS_ACCOUNT_ID="630013828440"
    MLOPS_CLUB_SSO_START_URL="https://d-926768adcc.awsapps.com/start"
    MLOPS_CLUB_SSO_REGION="us-west-2"

    # TODO: make this check work so we can uncomment it. It will make it so we only have to
    # open our browser if our log in has expired or we have not logged in before.
    # skip if already logged in
    # aws sts get-caller-identity --profile ${MLOPS_CLUB_AWS_PROFILE_NAME} | cat | grep 'UserId' > /dev/null \
    #     && echo "[mlops-club] ✅ Logged in with aws cli" \
    #     && exit 0

    # configure an "[mlops-club]" profile in aws-config
    echo "[mlops-club] Configuring an AWS profile called '${MLOPS_CLUB_AWS_PROFILE_NAME}'"
    aws configure set sso_start_url ${MLOPS_CLUB_SSO_START_URL} --profile ${MLOPS_CLUB_AWS_PROFILE_NAME}
    aws configure set sso_region ${MLOPS_CLUB_SSO_REGION} --profile ${MLOPS_CLUB_AWS_PROFILE_NAME}
    aws configure set sso_account_id ${MLOPS_CLUB_AWS_ACCOUNT_ID} --profile ${MLOPS_CLUB_AWS_PROFILE_NAME}
    aws configure set sso_role_name AdministratorAccess --profile ${MLOPS_CLUB_AWS_PROFILE_NAME}
    aws configure set region ${MLOPS_CLUB_SSO_REGION} --profile ${MLOPS_CLUB_AWS_PROFILE_NAME}

    # login to AWS using single-sign-on
    aws sso login --profile ${MLOPS_CLUB_AWS_PROFILE_NAME} \
    && echo '' \
    && echo "[mlops-club] ✅ Login successful. AWS CLI commands will now work by adding the '--profile ${MLOPS_CLUB_AWS_PROFILE_NAME}' 😃" \
    && echo "             Your '${MLOPS_CLUB_AWS_PROFILE_NAME}' profile has temporary credentials using this identity:" \
    && echo '' \
    && aws sts get-caller-identity --profile ${MLOPS_CLUB_AWS_PROFILE_NAME} | cat

# certain boilerplate files like setup.cfg, setup.py, and .gitignore are "locked";
# you can modify their contents by editing the .projenrc.py file in the root of the repo.
update-boilerplate-files: require-venv
    python .projenrc.py

# throw an error if a virtual environment isn't activated;
# add this as a requirement to other targets that you want to ensure always run in
# some kind of activated virtual environment
require-venv:
    #!/usr/bin/env python
    import sys
    from textwrap import dedent

    def get_base_prefix_compat():
        """Get base/real prefix, or sys.prefix if there is none."""
        return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

    def in_virtualenv():
        return get_base_prefix_compat() != sys.prefix

    if not in_virtualenv():
        print(dedent("""\
            ⛔️ ERROR: 'just' detected that you have not activated a python virtual environment.

            Science has shown that installing python packages (e.g. 'pip install pandas')
            without a virtual environment increases likelihood of getting ulcers and COVID. 🧪👩‍🔬

            To resolve this error, please activate a virtual environment by running
            whichever of the following commands apply to you:

            ```bash
            # create a (virtual) copy of the python just for this project
            python -m venv ./venv/

            # activate that copy of python (now 'which python' points to your new virtual copy)
            source ./venv/bin/activate

            # re-run whatever 'just' command you just tried to run, for example
            just install
            ```

            -- Sincerely, The venv police 👮 🐍
        """))

        sys.exit(1)

    print("[mlops-club] ✅ Virtual environment is active")

# print the AWS account ID of the current AWS_PROFILE to stdout
get-aws-account-id:
    #!/usr/bin/env python3
    import json
    import subprocess

    args = ["aws", "sts", "get-caller-identity", "--profile", "{{AWS_PROFILE}}"]
    proc = subprocess.run(args, capture_output=True)

    aws_cli_response = json.loads(proc.stdout)
    print(aws_cli_response["Account"])

# run quality checks and autoformatters against your code
lint: require-venv
    pre-commit run --all-files

# Create a pip-installable package for this project that can be published to PyPI.
# Gather all necessary source files and build artifacts such as the frontend website
# to include in the final package binary.
build-python-package: clean
    #!/bin/bash

    # fail on first error
    set -e

    export BUILD_DIR="build_/{{CDK_PLATFORM_DIR}}"
    mkdir -p "${BUILD_DIR}"

    # build the frontend into static files
    cd {{FRONTEND_DIR}} && docker-compose up && cd ..
    mkdir -p {{STATIC_SITE_BUILD_OUTPUT_DIR}}
    cp -r {{FRONTEND_DIR}}/build/ {{STATIC_SITE_BUILD_OUTPUT_DIR}}/

    # 'cp -r' copies the actual contents of symlinks, so after this
    # command is run, the copied folder won't have any symlinks, but
    # real copies of the files.
    cp -r "{{CDK_PLATFORM_DIR}}/src" "$BUILD_DIR/"
    cp "{{CDK_PLATFORM_DIR}}/setup.cfg" "$BUILD_DIR/"
    cp "{{CDK_PLATFORM_DIR}}/setup.py" "$BUILD_DIR/"
    cp "{{CDK_PLATFORM_DIR}}/pyproject.toml" "$BUILD_DIR/"
    cp "{{CDK_PLATFORM_DIR}}/MANIFEST.in" "$BUILD_DIR/"
    cp "{{CDK_PLATFORM_DIR}}/README.md" "$BUILD_DIR/"

    python -m pip install build
    cd "${BUILD_DIR}" && echo `pwd` && \
        python -m build --wheel

    cd ../../
    mv ${BUILD_DIR}/build/ .
    mv ${BUILD_DIR}/dist/ .


publish-python-package-test:
    twine upload \
        --repository-url "https://test.pypi.org/legacy/" \
        --username "${TEST_PYPI__TWINE_USERNAME}" \
        --password "${TEST_PYPI__TWINE_PASSWORD}" \
        --verbose \
        dist/*

publish-python-package-prod:
    twine upload \
        --repository-url "https://upload.pypi.org/legacy/" \
        --username "${TWINE_USERNAME}" \
        --password "${TWINE_PASSWORD}" \
        --verbose \
        dist/*

clean:
    rm -rf {{STATIC_SITE_BUILD_OUTPUT_DIR}}   || echo "no static site built"
    rm -rf ./dist/       **/dist/             || echo "no matches found for **/dist/"
    rm -rf .projen/      **/.projen/          || echo "no matches found for **/.projen/"
    rm -rf ./build/      **/build/            || echo "no matches found for **/build/"
    rm -rf ./build_/      **/build_/            || echo "no matches found for **/build/"
    rm -rf ./cdk.out/    **/cdk.out/          || echo "no matches found for **/cdk.out/"
    rm -rf ./.DS_Store/  **/.DS_Store         || echo "no matches found for **/.DS_Store"
    rm -rf ./.mypy_cache/ **/.mypy_cache      || echo "no matches found for **/.mypy_cache"
    rm -rf ./.pytest_cache/ **/.pytest_cache  || echo "no matches found for **/*.pytest_cache"
    rm -rf ./test/       **/test              || echo "no matches found for **/test"
    rm -rf ./.coverage/  **/.coverage         || echo "no matches found for **/.coverage"
    rm -rf ./.ipynb_checkpoints/ **/.ipynb_checkpoints || echo "no matches found for **/.ipynb_checkpoints"
    rm -rf ./.pyc/       **/*.pyc             || echo "no matches found for **/*.pyc"
    rm -rf ./__pycache__/ **/__pycache__      || echo "no matches found for **/__pycache__"
    rm -rf ./*.egg-info/ **/*.egg-info        || echo "no matches found for **/*.egg-info"
    rm cdk.context.json  **/*cdk.context.json || echo "no matches found for cdk.context.json"

release-to-pypi: clean build-python-package publish-python-package-test publish-python-package-prod
