#!/bin/bash

# Please ensure that you have the correct AWS credentials configured
# Enter the name of the stack, the parameters file name, the template name, then changeset condition, and finally the region name.

if [ $# -ne 4 ]; then
    echo "Enter stack name, parameters file name, template file name to create, set changeset value (true or false), and enter region name. "
    exit 0
else
    STACK_NAME=$1
    PARAMETERS_FILE_NAME=$2
    TEMPLATE_FILE=$3
    # CHANGESET_MODE=$4
    REGION=$4
fi

if [[ $TEMPLATE_FILE != *.yaml ]]; then
    echo "CloudFormation template $TEMPLATE_FILE does not exist. Make sure the extension is *.yaml and not (*.yml)"
    exit 0
fi

aws cloudformation deploy \
    --stack-name "$STACK_NAME" \
    --template-file "$TEMPLATE_FILE" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides file://"$PARAMETERS_FILE_NAME" \
    --region "$REGION"
