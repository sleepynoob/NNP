#!/bin/bash
required_packages=("colorlog, black, isort, ruff, pre-commit, sphinx, sphix_rtd_theme")

python_version=$(echo $(python -V | awk -F'.' '{print $2}'))

echo "Checking default Python version..."
if [[ "$python_version" -lt 10 ]]; then
	echo "The default Python interpreter located at $(which python)) has a version < 10"
	read -p "Enter the path to a Python interpreter with a version > 10: " python_path
	if [[ -z "$python_path" ]]; then
		echo "No suitable Python interpreter were provided. Aborting installation..."
		exit 1
	else
	echo "No check will be run on the provided path..."
	fi
else
	python_path=$(which python)
fi

printf "Choose an installation type:\n0: automatic\n1: semi-automatic\n"
read -p "Installation type: " install_type

printf "You have chosen a"

if [[ "$install_type" -eq 0 ]]; then
	printf "n automatic installation\nPlease wait...\n"
	env_name="nnp-mv"
elif [[ "$install_type" -eq 1 ]]; then
	printf " semi-automatic installation\n"
	read -p "Enter the name of the virtual environment, keep empty for the default one 'nnp-mv': " env_name
	if [[ -z "$env_name" ]]; then
		env_name="nnp-mv"
	fi
else
	printf "n invalid installation type: $install_type. Aborting...\n"
	exit 1
fi

virtualenv -p $python_path $env_name # Python version >= 3.10 required
echo "Python environment '$env_name' succesfully created"

install_req=false

if [[ "$install_type" -eq 0 ]]; then
	install_req=true
elif [[ "$install_type" -eq 1 ]]; then
	read -p "Should the requirements be installed from requirements.txt ? (y/ANY): " install_req_input
	if [[ "$install_req_input" == "y" || "$install_req_input" == "Y" ]]; then
		install_req=true
	else
		install_req=false
	fi
fi

if $install_req; then
	echo "The requirements will be installed..."
	source $env_name/bin/activate
	pip install -r requirements.txt
	echo "The requirements have been succesfully installed"
	deactivate
else
	echo "The requirements will not be installed..."
	echo "In order to run the project, the following Python packages need to be installed :"
	printf "%s\n" "${required_packages[@]}"
fi

echo "Installation is done"

strreplace="PYTHONINTERPRETER"

interpreterpath="$env_name/bin/python"

sed -i "s|$strreplace|$interpreterpath|g" "nnp-comp.py"
sed -i "s|$strreplace|$interpreterpath|g" "nnp-exec.py"

echo "To activate the Python environment, run 'source $env_name/bin/activate' from the project directory ($(cd "$(dirname "$0")" && pwd))"
