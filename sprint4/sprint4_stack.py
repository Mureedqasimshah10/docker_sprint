from aws_cdk import (
    Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as lambda_, 
    RemovalPolicy, 
    aws_events as events_,
    aws_events_targets as targets_,
    aws_cloudwatch as cloudwatch_,
    aws_iam as iam_,
    aws_sns as sns_,
    aws_cloudwatch_actions as cw_actions_,
    aws_sns_subscriptions as subscriptions_,
    aws_dynamodb as dynamodb_,
    aws_codedeploy as codedeploy_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from resources import constants as constants

class Sprint4Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create lambda functions
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html
        lambda_role = self.create_role()

        WHLambda = self.create_lambda("WH_Functions", "WHLambda.lambda_handler", "./resources", lambda_role)
        DBLambda = self.create_lambda("DB_Functions", "DBLambda.lambda_handler", "./resources", lambda_role)
        APILambda = self.create_lambda("API_Functions", "APILambda.lambda_handler", "./resources", lambda_role)

        # create table
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Table.html 
        DBTable = self.create_table(constants.ALARM_TABLE_NAME)

        # set environment variable
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        tname = DBTable.table_name
        DBLambda.add_environment(key="Alarm_Table", value=tname)

        # scheduling the lambda function
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events/Schedule.html
        schedule = events_.Schedule.rate(Duration.minutes(constants.SCHEDULE_TIME_CONSTANT)) # for every 60th minute
        target = targets_.LambdaFunction(handler=WHLambda)

        # create a Cloudwatch Event rule
        rule = events_.Rule(self, "LambdaEventRule",
            schedule=schedule,
            targets=[target]
        )
        
        # create an SNS Topic to send email notification
        # https://docs.aws.amazon.com/cdks/api/v1/python/aws_cdk.aws_sns/Topic.html
        topic = sns_.Topic(self, "AlarmNotification")


        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns_subscriptions/EmailSubscription.html
        topic.add_subscription(subscriptions_.EmailSubscription(constants.SNS_EMAIL_ADDRESS))


        # create Lambda Subscription - to send alarm data into DynamoDB table
        topic.add_subscription(subscriptions_.LambdaSubscription(DBLambda))


        ##################################################################################################################
        #                   Sprint #03 Stack Start - Lamnda Auto Deployment Configuration and Rollback                   #
        ##################################################################################################################


        #Step:01 Get the metric
        WHLambdaDurationMetric = WHLambda.metric("Duration", period=Duration.minutes(constants.SCHEDULE_TIME_CONSTANT))
        WHLambdaInvocationMetric = WHLambda.metric("Invocations", period=Duration.minutes(constants.SCHEDULE_TIME_CONSTANT))

        #Step:02 Create Alarms for metric
        durationAlarm = cloudwatch_.Alarm(self, "WHLambdaAlarmfor_Duration",
            comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=1,
            metric=WHLambdaDurationMetric,
            )

        invocationAlarm = cloudwatch_.Alarm(self, "WHLambdaAlarmfor_Invocation",
            comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=1,
            metric=WHLambdaInvocationMetric,
            )

        # add SNS action to topic
        durationAlarm.add_alarm_action(cw_actions_.SnsAction(topic))
        invocationAlarm.add_alarm_action(cw_actions_.SnsAction(topic))
        
        # create Lambda deployment configuration and rollback
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Alias.html#aws_cdk.aws_lambda.Alias
        version = WHLambda.current_version
        alias = lambda_.Alias(self, "Lambda_Alias_Pipeline"+construct_id,
            alias_name= "Prod_Alias_Pipeline"+construct_id,
            version=version
        )

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_codedeploy/LambdaDeploymentGroup.html
        deployment_group = codedeploy_.LambdaDeploymentGroup(self, "QasimLambda_BG_Deployment",
            alias = alias,
            alarms = [durationAlarm, invocationAlarm],
            deployment_config = codedeploy_.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE
        )

        
        ##################################################################################################################
        #                                   Sptint #4 Stack Start - API Gateway Integration                              #
        ##################################################################################################################
        
        
        # create table
        URLTable = self.create_API_table(constants.API_TABLE_NAME)

        # set environment variable
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        apitname = URLTable.table_name
        APILambda.add_environment(key="URL_TABLE", value=apitname)
        WHLambda.add_environment(key="URL_TABLE", value=apitname)

        #Define API

        # create REST API Gateway integrated with `APILambda backend`
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_apigateway/LambdaRestApi.html
        api = apigateway_.LambdaRestApi(self, id = "QasimAPI",
                handler= APILambda,
                proxy=False,
                endpoint_configuration= apigateway_.EndpointConfiguration(
                types= [apigateway_.EndpointType.REGIONAL]
            )
        )

        # define API Gateway permissions to invoke  APIlambda
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html?highlight=grant%20invoke#aws_cdk.aws_lambda.Function.grant_invoke
        APILambda.grant_invoke(iam_.ServicePrincipal("apigateway.amazonaws.com"))

        # add resource and methods
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Resource.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/IResource.html#aws_cdk.aws_apigateway.IResource.add_method
        root = api.root.add_resource("root")       # path to resource
        root.add_method("POST")                    # POST: (Create) /root      
        root.add_method("GET")                     # GET: (Read) /root
        root.add_method("DELETE")                  # DELETE: /root
        root.add_method("PUT")                     # PUT: (Update) /root


        ##################################################################################################################


        # loop into the list of URL
        for url in constants.MY_URLS_VAR:
            # creating Metric for Availability and Latency
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Metric.html

            availMetric = cloudwatch_.Metric(metric_name=constants.URL_MONITOR_NAME_AVAILABILITY,
            namespace=constants.URL_MONITOR_NAMESPACE,
            dimensions_map={"URL" : url},
            period=Duration.minutes(constants.SCHEDULE_TIME_CONSTANT)
            )

            latenMetric = cloudwatch_.Metric(metric_name=constants.URL_MONITOR_NAME_LATENCY,
            namespace=constants.URL_MONITOR_NAMESPACE,
            dimensions_map={"URL" : url},
            period=Duration.minutes(constants.SCHEDULE_TIME_CONSTANT)
            )

            # define threshold and create Alarms for Availability and Latency metric
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Alarm.html
            availAlarm = cloudwatch_.Alarm(self, "AvailabilityAlarmfor_"+url,
            comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=1,
            metric=availMetric
            )

            latenAlarm = cloudwatch_.Alarm(self, "LatencyAlarmfor_"+url,
            comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=0.4,
            evaluation_periods=1,
            metric=latenMetric
            )

            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch_actions/SnsAction.html
            availAlarm.add_alarm_action(cw_actions_.SnsAction(topic))
            latenAlarm.add_alarm_action(cw_actions_.SnsAction(topic))

        # Removal policy to destroy services
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/RemovalPolicy.html#aws_cdk.core.RemovalPolicy
        WHLambda.apply_removal_policy(RemovalPolicy.DESTROY)
        DBLambda.apply_removal_policy(RemovalPolicy.DESTROY)
        APILambda.apply_removal_policy(RemovalPolicy.DESTROY)
        durationAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
        invocationAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
        topic.apply_removal_policy(RemovalPolicy.DESTROY)
        api.apply_removal_policy(RemovalPolicy.DESTROY)

    # input parameters: id, handler, path and role
    # return values: Lambda function
    def create_lambda(self, id_, handler, path, myRole):
        return lambda_.Function(self, id_,
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler=handler,
        code=lambda_.Code.from_asset(path),
        role=myRole,
        timeout=Duration.seconds(600),
        )

    # input parameters: None
    # return values: dynamo_db table
    def create_table(self, id_):
        return dynamodb_.Table(self, id_,
            removal_policy=RemovalPolicy.DESTROY,
            partition_key= dynamodb_.Attribute(name= "MetricName", type= dynamodb_.AttributeType.STRING),
            sort_key= dynamodb_.Attribute(name= "Timestamp", type= dynamodb_.AttributeType.STRING)
        )

    def create_API_table(self, id_):
        return dynamodb_.Table(self, id_,
            removal_policy=RemovalPolicy.DESTROY,
            partition_key= dynamodb_.Attribute(name= "linkID", type= dynamodb_.AttributeType.STRING)
        )

    # creating role for policies
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/ManagedPolicy.html
    # input parameters: None
    # return values: lambda_role
    def create_role(self):
        return iam_.Role(self, "Role",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
                ]
            )
            