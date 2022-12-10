"""AWS Step Function (State Machine) that deploys or destroys the Minecraft server."""
from pathlib import Path
from typing import Literal

from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from constructs import Construct

THIS_DIR = Path(__file__).parent


class ProvisionMinecraftServerStateMachine(Construct):
    """
    Class for the State Machine to deploy our Minecraft server.

    The State Machine will be responsible for starting and stopping the server.

    Parameters
    ----------
    scope : Construct
        The parent construct.
    construct_id : str
        The name of the construct.
    job_queue_arn : str
        The ARN of the AWS Batch Job Queue.
    deploy_or_destroy_mc_server_job_definition_arn : str
        The ARN of the AWS Batch Job Definition for the CDK Deploy or Destroy Job.

    Attributes
    ----------
    state_machine : sfn.StateMachine
        The AWS Step Function State Machine.
    namer : Callable[[str], str]
        A function that prefixes the name of the construct with the name of the construct.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        job_queue_arn: str,
        deploy_or_destroy_mc_server_job_definition_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.namer = lambda name: f"{construct_id}-{name}"

        submit_cdk_deploy_batch_job: sfn_tasks.BatchSubmitJob = (
            create__deploy_or_destroy__submit_batch_job_state(
                scope=self,
                command="deploy",
                id_prefix=construct_id,
                job_queue_arn=job_queue_arn,
                deploy_or_destroy_mc_server_job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
            )
        )

        submit_cdk_destroy_batch_job: sfn_tasks.BatchSubmitJob = (
            create__deploy_or_destroy__submit_batch_job_state(
                scope=self,
                command="destroy",
                id_prefix=construct_id,
                job_queue_arn=job_queue_arn,
                deploy_or_destroy_mc_server_job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
            )
        )

        state_machine = (
            sfn.Choice(
                self,
                id=self.namer("ChooseCdkDeployOrDestroy"),
            )
            .when(
                condition=sfn.Condition.string_equals("$.command", "deploy"), next=submit_cdk_deploy_batch_job
            )
            .when(
                condition=sfn.Condition.string_equals("$.command", "destroy"),
                next=submit_cdk_destroy_batch_job,
            )
        )

        self.state_machine = sfn.StateMachine(
            scope=self,
            id=self.namer("StateMachine"),
            definition=state_machine,
            # logs=sfn.LogOptions(),
            role=None,
        )


def create__deploy_or_destroy__submit_batch_job_state(
    scope: Construct,
    id_prefix: str,
    command: Literal["deploy", "destroy"],
    job_queue_arn: str,
    deploy_or_destroy_mc_server_job_definition_arn: str,
) -> sfn_tasks.BatchSubmitJob:
    """Create the AWS Step Function State that submits the AWS Batch Job to deploy or destroy the Minecraft server.

    Parameters
    ----------
    scope : Construct
        The parent construct.
    id_prefix : str
        The prefix for the ID of the AWS Step Function State.
    command : Literal["deploy", "destroy"]
        The command to run. Must be one of "deploy" or "destroy".
    job_queue_arn : str
        The ARN of the AWS Batch Job Queue.
    deploy_or_destroy_mc_server_job_definition_arn : str
        The ARN of the AWS Batch Job Definition for the CDK Deploy or Destroy Job.

    Returns
    -------
    sfn_tasks.BatchSubmitJob
        The AWS Step Function State that submits the AWS Batch Job to deploy or destroy the Minecraft server.
    """
    if command == "deploy":
        return sfn_tasks.BatchSubmitJob(
            scope=scope,
            id=f"{id_prefix}CdkDeployMcServerBatchJob",
            job_name=f"{id_prefix}DeployMinecraftServer",
            container_overrides=sfn_tasks.BatchContainerOverrides(
                environment=None,
                command=["cdk", "deploy", "--app", "'python3 /app/app.py'", "--require-approval=never"],
            ),
            job_queue_arn=job_queue_arn,
            job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
        )

    if command == "destroy":
        return sfn_tasks.BatchSubmitJob(
            scope=scope,
            id=f"{id_prefix}CdkDestroyMcServerBatchJob",
            job_name=f"{id_prefix}DestroyMinecraftServer",
            container_overrides=sfn_tasks.BatchContainerOverrides(
                environment=None,
                command=["cdk", "destroy", "--app", "'python3 /app/app.py'", "--force"],
            ),
            job_queue_arn=job_queue_arn,
            job_definition_arn=deploy_or_destroy_mc_server_job_definition_arn,
        )

    raise ValueError("Invalid command. ``command`` must be one of 'destroy' or 'deploy'")

    # def make_state_machine(
    #     self,
    #     customer_org_name: str,
    #     datalake_bucket_name: str,
    #     etl_function: lambda_.Function,
    #     s3_folder_deleter_function: lambda_.Function,
    # ) -> sfn.StateMachine:
    #     """Create the state machine (DAG) that does the ETL."""
    #     state_machine = sfn.StateMachine(
    #         self,
    #         self.namer("etl-state-machine"),
    #         definition=self.make__state_machine_definition(
    #             customer_org_name=customer_org_name,
    #             datalake_bucket_name=datalake_bucket_name,
    #             etl_function=etl_function,
    #             s3_folder_deleter_function=s3_folder_deleter_function,
    #         ),
    #     )

    #     self.grant_permissions_to_state_machine(
    #         state_machine_role=state_machine.role,
    #         datalake_bucket_name=datalake_bucket_name,
    #     )

    #     return state_machine

    # def make__state_machine_definition(
    #     self,
    #     customer_org_name: str,
    #     datalake_bucket_name: str,
    #     etl_function: lambda_.Function,
    #     s3_folder_deleter_function: lambda_.Function,
    # ) -> sfn.IChainable:
    #     """Define the entire DAG of states/tasks that will ELT data for a customer."""
    #     etl_chain = self.make_customer_etl_chain(
    #         customer_org_name=customer_org_name,
    #         datalake_bucket_name=datalake_bucket_name,
    #         etl_lambda=etl_function,
    #         s3_folder_deleter_lambda=s3_folder_deleter_function,
    #     )

    #     pillar_one_chain = self.make__pillar_one_query__state(
    #         customer_org_name=customer_org_name,
    #         datalake_bucket_name=datalake_bucket_name,
    #         s3_folder_deleter_lambda=s3_folder_deleter_function,
    #     )

    #     opportunity_field_history_chain = self.make__opportunity_field_history__state(
    #         customer_org_name=customer_org_name,
    #         datalake_bucket_name=datalake_bucket_name,
    #         s3_folder_deleter_lambda=s3_folder_deleter_function,
    #     )

    #     post_clean_queries_parallel = sfn.Parallel(
    #         self,
    #         self.namer("post-clean-queries"),
    #     )

    #     post_clean_queries_parallel.branch(pillar_one_chain)
    #     post_clean_queries_parallel.branch(opportunity_field_history_chain)

    #     return etl_chain.next(post_clean_queries_parallel)

    # def make_customer_etl_chain(
    #     self,
    #     customer_org_name: str,
    #     datalake_bucket_name: str,
    #     s3_folder_deleter_lambda: lambda_.Function,
    #     etl_lambda: lambda_.Function,
    # ):
    #     customer_object_etl_chains: List[sfn.Chain] = [
    #         self.make_customer_object_etl_chain(
    #             customer_org_name=customer_org_name,
    #             sf_object_name=sf_object_name,
    #             datalake_bucket_name=datalake_bucket_name,
    #             s3_folder_deleter_lambda=s3_folder_deleter_lambda,
    #             etl_lambda=etl_lambda,
    #         )
    #         for sf_object_name in get_sf_object_names()
    #     ]

    #     parallel = sfn.Parallel(
    #         self,
    #         self.namer("etl-for-all-customer-objects"),
    #     )

    #     for customer_object_etl_chain in customer_object_etl_chains:
    #         parallel.branch(customer_object_etl_chain)

    #     return parallel

    # def make_customer_object_etl_chain(
    #     self,
    #     customer_org_name: str,
    #     sf_object_name: str,
    #     s3_folder_deleter_lambda: lambda_.Function,
    #     etl_lambda: lambda_.Function,
    #     datalake_bucket_name: str,
    # ) -> sfn.Chain:
    #     customer__raw_obj__s3_folder = f"{customer_org_name}/{sf_object_name}_raw/"
    #     # delete the old raw data
    #     delete_raw_object_data_from_s3 = sfn_tasks.LambdaInvoke(
    #         self,
    #         self.name_by_sf_obj(sf_object_name, "delete-raw-obj-s3-folder"),
    #         lambda_function=s3_folder_deleter_lambda,
    #         comment=f"Delete folder {customer__raw_obj__s3_folder}",
    #         payload=sfn.TaskInput.from_object(
    #             {
    #                 "s3_bucket_name": datalake_bucket_name,
    #                 "prefix_to_delete": customer__raw_obj__s3_folder,
    #             },
    #         ),
    #     )

    #     # etl new raw data
    #     etl_raw_customer_obj_data = sfn_tasks.LambdaInvoke(
    #         self,
    #         self.name_by_sf_obj(sf_object_name, "etl-raw-data"),
    #         lambda_function=etl_lambda,
    #         comment=f"ETL {customer_org_name}'s {sf_object_name} data into s3://{datalake_bucket_name}/{customer__raw_obj__s3_folder}",
    #         payload=sfn.TaskInput.from_object(
    #             {
    #                 "customer_org_name": customer_org_name,
    #                 "salesforce_object_name": sf_object_name,
    #             }
    #         ),
    #     )

    #     clean_data__select_stmt: str = make__clean_sf_obj_table__query(
    #         customer_org_name=customer_org_name, sf_object=sf_object_name
    #     )
    #     create_or_replace__clean_sf_obj__table = create_or_replace_physical_table(
    #         scope=self,
    #         select_stmt=clean_data__select_stmt,
    #         table_name=sf_object_name,
    #         customer_org_name=customer_org_name,
    #         datalake_bucket_name=datalake_bucket_name,
    #         s3_folder_deleter_lambda=s3_folder_deleter_lambda,
    #     )

    #     return (
    #         # 1
    #         delete_raw_object_data_from_s3
    #         # 2
    #         .next(etl_raw_customer_obj_data)
    #         # 3
    #         .next(create_or_replace__clean_sf_obj__table)
    #     )

    # def make__pillar_one_query__state(
    #     self,
    #     customer_org_name: str,
    #     datalake_bucket_name: str,
    #     s3_folder_deleter_lambda: lambda_.Function,
    # ) -> sfn.Parallel:

    #     select__pillar_one_data__stmt: str = make__pillar_one__select_stmt(customer_org_name=customer_org_name)
    #     create_or_replace_pillar_one_table: sfn.Parallel = create_or_replace_physical_table(
    #         scope=self,
    #         customer_org_name=customer_org_name,
    #         datalake_bucket_name=datalake_bucket_name,
    #         s3_folder_deleter_lambda=s3_folder_deleter_lambda,
    #         select_stmt=select__pillar_one_data__stmt,
    #         table_name=PILLAR_ONE_QUERY_INFO.athena_table_name,
    #     )

    #     return create_or_replace_pillar_one_table

    # def make__opportunity_field_history__state(
    #     self,
    #     customer_org_name: str,
    #     datalake_bucket_name: str,
    #     s3_folder_deleter_lambda: lambda_.Function,
    # ) -> sfn.Parallel:

    #     select__opportunity_field_history__stmt: str = make__opp_field_history__select_stmt(
    #         customer_org_name=customer_org_name
    #     )
    #     create_or_replace_opportunity_field_history_table: sfn.Parallel = create_or_replace_physical_table(
    #         scope=self,
    #         customer_org_name=customer_org_name,
    #         datalake_bucket_name=datalake_bucket_name,
    #         s3_folder_deleter_lambda=s3_folder_deleter_lambda,
    #         select_stmt=select__opportunity_field_history__stmt,
    #         table_name=OPP_HISTORY_QUERY_INFO.athena_table_name,
    #     )

    #     return create_or_replace_opportunity_field_history_table

    # def grant_permissions_to_state_machine(self, state_machine_role: iam.Role, datalake_bucket_name: str):
    #     state_machine_role.attach_inline_policy(
    #         policy=iam.Policy(
    #             self,
    #             "allow-customer-athena-db-read-write",
    #             document=iam.PolicyDocument(
    #                 statements=[
    #                     iam.PolicyStatement(
    #                         actions=["glue:*"],
    #                         resources=[
    #                             f"arn:aws:glue:{self.region}:{self.account}:database/*",
    #                             f"arn:aws:glue:{self.region}:{self.account}:table/*",
    #                             # f"arn:aws:glue:{self.region}:{self.account}:database/{customer_org_name}",
    #                             # f"arn:aws:glue:{self.region}:{self.account}:table/{customer_org_name}/*",
    #                         ],
    #                         effect=iam.Effect.ALLOW,
    #                     )
    #                 ]
    #             ),
    #         )
    #     )

    #     grant_read_write_access_to_bucket(self, role=state_machine_role, bucket_name=datalake_bucket_name)
