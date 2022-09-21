import boto3

class CloudwatchPutMetric:
    def __init__(self):
        # Creating Cloudwatch client
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html
        self.client = boto3.client('cloudwatch')

    # input parameters: nameSpace, metricName, dimensionsPair, value
    # return values: None
    def put_data(self, nameSpace, metricName, dimensionsPair, value):
        response = self.client.put_metric_data(
                Namespace=nameSpace,
                MetricData=[
                    {
                        'MetricName': metricName,
                        'Dimensions': dimensionsPair,
                        'Value': value, #availability or latency
                    },
                ]        
        )