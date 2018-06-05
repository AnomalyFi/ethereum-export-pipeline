from troposphere import Template, Parameter, Ref
from troposphere.datapipeline import Pipeline, PipelineTag, PipelineObject, ObjectField, ParameterObject, \
    ParameterObjectAttribute

from ethereumetl.templates.config import EXPORT_JOBS


def generate_export_pipeline_template(output):
    t = Template()

    # CloudFormation version
    t.add_version('2010-09-09')

    t.add_description('Ethereum ETL Export CloudFormation Stack')

    # Parameters

    S3Bucket = t.add_parameter(Parameter(
        "S3Bucket",
        Description="S3 bucket where CSV files will be uploaded",
        Type="String",
        Default="example.com"
    ))

    Command = t.add_parameter(Parameter(
        "Command",
        Description="Shell command that will be executed on workers",
        Type="String",
        Default="cd /home/ec2-user/ethereum-etl && bash -x export_all.sh -s $1 -e $2 -b $3 -i /home/ec2-user/.ethereum/geth.ipc -o ${OUTPUT1_STAGING_DIR}"
    ))

    t.add_resource(Pipeline(
        "EthereumETLPipeline",
        Name="EthereumETLPipeline",
        Description="Ethereum ETL Export Pipeline",
        PipelineTags=[PipelineTag(Key='Name', Value='ethereum-etl-pipeline')],
        ParameterObjects=[
            ParameterObject(Id='myS3Bucket', Attributes=[
                ParameterObjectAttribute(Key='type', StringValue='String'),
                ParameterObjectAttribute(Key='description', StringValue='S3 bucket'),
                ParameterObjectAttribute(Key='default', StringValue=Ref(S3Bucket)),
            ]),
            ParameterObject(Id='myShellCmd', Attributes=[
                ParameterObjectAttribute(Key='type', StringValue='String'),
                ParameterObjectAttribute(Key='description', StringValue='S3 bucket'),
                ParameterObjectAttribute(Key='default', StringValue=Ref(Command)),
            ])
        ],
        PipelineObjects=
        [PipelineObject(
            Id='Default',
            Name='Default',
            Fields=[
                ObjectField(Key='type', StringValue='Default'),
                ObjectField(Key='failureAndRerunMode', StringValue='cascade'),
                ObjectField(Key='scheduleType', StringValue='ondemand'),
                ObjectField(Key='role', StringValue='DataPipelineDefaultRole'),
                ObjectField(Key='pipelineLogUri', StringValue='s3://#{myS3Bucket}/'),

            ]
        )] +
        [PipelineObject(
            Id='ExportActivity_{}_{}_{}'.format(start, end, batch),
            Name='ExportActivity_{}_{}_{}'.format(start, end, batch),
            Fields=[
                ObjectField(Key='type', StringValue='ShellCommandActivity'),
                ObjectField(Key='command', StringValue='#{myShellCmd}'),
                ObjectField(Key='scriptArgument', StringValue=str(start)),
                ObjectField(Key='scriptArgument', StringValue=str(end)),
                ObjectField(Key='scriptArgument', StringValue=str(batch)),
                ObjectField(Key='workerGroup', StringValue='ethereum-etl'),
                ObjectField(Key='output', RefValue='S3OutputLocation'),
                ObjectField(Key='stage', StringValue='true')

            ]
        ) for start, end, batch in EXPORT_JOBS] +
        [PipelineObject(
            Id='S3OutputLocation',
            Name='S3OutputLocation',
            Fields=[
                ObjectField(Key='type', StringValue='S3DataNode'),
                ObjectField(Key='directoryPath', StringValue='s3://#{myS3Bucket}/ethereum-etl/export-pipeline')

            ]
        )]
    ))

    # Write json template to file

    with open(output, 'w+') as output_file:
        output_file.write(t.to_json())
