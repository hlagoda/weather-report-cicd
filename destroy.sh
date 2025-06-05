#!/bin/bash

PROJECT_NAME=$1

if [[ "$#" == 0 ]]; then
    echo "Number of arguments must be 1 and is $#"
    exit 1
fi

terraform -chdir=./workspace destroy -auto-approve