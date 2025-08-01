import argparse
import asyncio

from temporalio import workflow
from temporalio.client import (
    WorkflowQueryRejectedError,
    WorkflowUpdateFailedError,
)
from temporalio.common import QueryRejectCondition, WorkflowIDReusePolicy
from temporalio.service import RPCError, RPCStatusCode

from common.client_helper import ClientHelper
from common.data_converter_helper import DataConverterHelper

with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter

    from supervisor_workflow import (
        WealthManagementWorkflow,
    )
    from common.user_message import ProcessUserMessageInput


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conversation-id", type=str, required=True)
    args = parser.parse_args()

    clientHelper = ClientHelper()
    data_converter = DataConverterHelper().get_data_converter()
    client = await clientHelper.get_client(data_converter)

    handle = client.get_workflow_handle(args.conversation_id)

    # Query the workflow to get the chat history
    # If the workflow is not open, start a new one
    start = False
    try:
        print("Checking to see if the workflow is already running...")
        history = await handle.query(
            WealthManagementWorkflow.get_chat_history,
            reject_condition=QueryRejectCondition.NOT_OPEN,
        )
    except WorkflowQueryRejectedError as e:
        print("Workflow is not currently running. Will start it.")
        start = True
    except RPCError as e:
        if e.status == RPCStatusCode.NOT_FOUND:
            print("Got NOT FOUND. Will start it")
            start = True
        else:
            raise e

    if start:
        print(f"Starting workflow using {args.conversation_id}")
        handle = await client.start_workflow(
            WealthManagementWorkflow.run,
            id=args.conversation_id,
            task_queue=clientHelper.taskQueue,
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE
        )
        history = []

    print(*history, sep="\n")

    print("Welcome to ABC Wealth Management. How can I help you?")
    while True:
        user_input = input("Enter your message: ")
        lower_input = user_input.lower() if user_input is not None else ""
        if lower_input == "exit" or lower_input == "end" or lower_input == "quit":
            # assume that we're done with this workflow
            # So end the workflow
            await handle.signal(
                WealthManagementWorkflow.end_workflow
            )
            break

        message_input = ProcessUserMessageInput(
            user_input=user_input,
            chat_length=len(history),
        )
        try:
            # Returns a list of chat interactions
            new_history = await handle.execute_update(
                WealthManagementWorkflow.process_user_message, message_input
            )
            history.extend(new_history)
            # only want to print out the text response
            index = len(new_history)-1 if len(new_history) == 0 else 0
            last_item = new_history[index]
            print(last_item.text_response)
        except WorkflowUpdateFailedError:
            print("** Stale conversation. Reloading..")
            length = len(history)
            history = await handle.query(
                WealthManagementWorkflow.get_chat_history,
                reject_condition=QueryRejectCondition.NOT_OPEN,
            )
            # only want to print out the text response
            index = len(history)-1 if len(history) == 0 else 0
            last_item = history[index]
            print(last_item.text_response)

if __name__ == "__main__":
    asyncio.run(main())


