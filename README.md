
> SkipQ Pegasus Python: Sprint 4 Project

# Serverless Public API Gate with CRUD Operations for Web Health Application !

[![Linux](https://svgshare.com/i/Zhy.svg)](#) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](#) [![Generic badge](https://img.shields.io/badge/version-3.8.10-blue)](#)

## Overview

This project is extenssion of the Sprint3 and it is about building a public server-less CRUD API Gateway endpoint for the web crawler to create, read, update and delete the target URLs list in DynamoDB database table DynamoDB is a fully managed NoSQL database service that provides fast performance with seamless scalability.

### Learning Objectives

The core objectives are listed as follows:

* Create and populate a URL table in DynamoDB.
* Implement CRUD REST commands on DynamoDB entries.
* Create Lambda handler to process API Gateway requests.
* Create public server-less REST API Gateway endpoint.
* Use CI/CD to automate multiple deployment stages (prod vs beta).
* Extend tests in each stage to cover the CRUD operations and DynamoDB read/write time.
* Manage README files and run-books in markdown on GitHub.

### End Goal

The end goal of this sprint is to build a public serverless API Gateway endpoint using CRUD operations for the application so that clients can create, read, update, and delete items from a DynamoDB table.

### TECHNOLOGIES USED

* [AWS CI/CD CodePipeline](https://aws.amazon.com/codepipeline/)
* [AWS API Gateway](https://aws.amazon.com/api-gateway/)
* [AWS CodeBuild](https://aws.amazon.com/codebuild/)
* [AWS CloudWatch](https://aws.amazon.com/cloudwatch/)
* [AWS Github](https://github.com/aws)


> The full procedure to setup AWS and RUN the Sprint3 is given in next step.

## Gettin Started - Environment Setup

1. First install Windows Subsystem for Linux (WSL). For  this, download WSL.exe file from Google. I faced error in installtion using `wsl --install` command so I used `wsl.exe --install -d Ubuntu-20.04` commad to install it correctly.
2. Dwnloaded VS Code and setup remote WSL from windows
3. Download python3
4. Donwload awscliv2.zip file from given path and install AWS. If you download it directly from google, there will be issue of path.
6. Download and install NVM and NPM
7. Check versions of all to be sure that softwares are installed corrrectly.

## Project Deployment - How to Run

1. Oopen the ubuntu terminal and clone the git repository using `git clone "forked-repo-github-url"`
2. Confirm that your working directory is `Sprint4`
3. Activate the virtual environment using command `source .venv/bin/activate`
4. Configure the aws using `aws configure` and add your email and username to global configuration using command

    ```sh
    git config --global user.email "your-email.gmail.com"
    ```
    and
    ```sh
    git config --global user.name "your-name"
    ```
5. Edit commands in `pipelines_.ShellStep` to add path of your directory.

    ```sh
    cd RootFolderName/ProjectFolderName/
    ```
6. Run `pip install -r requirements.txt` to install all required packages
7. Push changes to github.

    ```sh
    git commit -m "commit message"
    ```
    and 
    ```sh
    git push
    ```
8. Synth and Deploy the project on Consile using `cdk synth` and `cdk deploy`.


## AWS Console Output

* Go to the AWS Console and monitore logs of WHLambda function for Availability and Latency.
* Go to the AWS Console and monitore logs of DBLambda function for records (if you print them).
* Go to the AWS DynamoDB database and check the item tables for records.
* Go to the AWS CodePipeline and check the deployment of all stages.


## Useful commands

 * `cdk ls`     list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `source .venv/bin/activate`        activate virtual environment
 * `pip install -r requirements.txt`  install requirements


> For a more in-depth getting started guide, visit the [Getting Started](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) page in the AWS docs.