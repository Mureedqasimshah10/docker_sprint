from aws_cdk import (
    Stack,
    pipelines as pipeline_,
    aws_codebuild as codebuild_,
    aws_codepipeline_actions as actions_,
)
import aws_cdk as cdk
from constructs import Construct
from sprint4.pipeline_stage import QasimOutputStage

class QasimPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Access the CommitId of a GitHub source in the synth
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/CodePipelineSource.html
        # Create Secret Token
        # https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/create-secret.html
        source = pipeline_.CodePipelineSource.git_hub("mureedqasim2022skipq/Pegasus_Python", "main",
            authentication = cdk.SecretValue.secrets_manager("qasimtokenNew"),
            trigger = actions_.GitHubTrigger('POLL'))
        
        synth = pipeline_.ShellStep("Synth", input=source,
                commands=[
                    'cd mureed/docker_sprint/',
                    'pip install -r requirements.txt',
                    'npm install -g aws-cdk',
                    'cdk synth'],
                primary_output_directory = 'mureed/docker_sprint/cdk.out',)

        # Output build Artifact
        mypipeline = pipeline_.CodePipeline(self, "MureedPipeline", synth=synth, docker_enabled_for_self_mutation=True)

        unit_test = pipeline_.ShellStep("Unit Testing",
            commands=[
                'cd mureed/docker_sprint/',
                'pip install -r requirements.txt',
                'pip install -r requirements-dev.txt',
                'pytest'],
        )

        pyresttest = pipeline_.CodeBuildStep("QasimPyresttest",
            commands=[],
            build_environment= codebuild_.BuildEnvironment(
                build_image= codebuild_.LinuxBuildImage.from_asset(self, "Image", directory="./docker-image").from_docker_registry(name="docker:dind"),
                privileged=True
            ),
            partial_build_spec=codebuild_.BuildSpec.from_object(
                {
                    "version": 0.2,
                    "phases": {
                        "install": {
                            "commands": [
                                "nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2 &",
                                "timeout 15 sh -c \"until docker info; do echo .; sleep 1; done\""
                            ]
                        },
                        "pre_build": {
                            "commands": [
                                "cd mureed/docker_sprint/docker-image",
                                "docker build -t qasim-api ."
                            ]
                        },
                        "build": {
                            "commands": [
                                "docker images",
                                "docker run qasim-api"
                            ]
                        }
                    }
                }
            ),
        )

        alpha = QasimOutputStage(self, "QasimPyrestStage")
        prod = QasimOutputStage(self, "QasimProdStage")

        mypipeline.add_stage(stage=alpha, pre=[unit_test], post=[pyresttest])
        mypipeline.add_stage(stage=prod, pre=[pipeline_.ManualApprovalStep("PromoteToProd")])
