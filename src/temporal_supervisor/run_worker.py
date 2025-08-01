import asyncio
import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

from temporalio.contrib.openai_agents import OpenAIAgentsPlugin

from common.client_helper import ClientHelper
from temporal_supervisor.claim_check_plugin import ClaimCheckPlugin
from temporal_supervisor.activities.beneficiaries import Beneficiaries
from temporal_supervisor.activities.investments import Investments

with workflow.unsafe.imports_passed_through():
    from temporal_supervisor.supervisor_workflow import (
        WealthManagementWorkflow
    )

async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s")

    client_helper = ClientHelper()
    print(f"address is {client_helper.address}")
    client = await Client.connect(target_host=client_helper.address,
                                  namespace=client_helper.namespace,
                                  tls=client_helper.get_tls_config(),
                                  plugins=[
                                      OpenAIAgentsPlugin(),
                                      ClaimCheckPlugin()
                                  ])

    worker = Worker(
        client,
        task_queue=client_helper.taskQueue,
        workflows=[WealthManagementWorkflow],
        activities=[
            Beneficiaries.list_beneficiaries,
            Beneficiaries.add_beneficiary,
            Beneficiaries.delete_beneficiary,
            Investments.list_investments,
            Investments.open_investment,
            Investments.close_investment,
        ],
    )
    print(f"Running worker on {client_helper.address}")
    await worker.run()

if __name__ == '__main__':
    asyncio.run(main())