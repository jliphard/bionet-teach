import asyncio
import json
import logging
import websockets
import http
import uuid
import time
import os
import pymongo
import argparse

# from dotenv import load_dotenv

from langchain.agents import AgentType, initialize_agent, AgentExecutor
from langchain.memory import ChatMessageHistory, ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool, StructuredTool, Tool, tool

from langchain.chains import LLMMathChain
from langchain.utilities import SerpAPIWrapper

from llama_index import StorageContext, load_index_from_storage

from typing import Any, Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from pydantic import BaseModel, Field

import hammingdist
from Bio.Blast import NCBIWWW, NCBIXML

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, required=True)
args = parser.parse_args()
STORAGE_DIR = args.path + '/storage'

print(f'Using {STORAGE_DIR} as the path')

if os.path.isfile(STORAGE_DIR + "/index_store.json") :
	print("Found index - loading - this may take a few seconds")
	# rebuild storage context
	storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
	# load index
	index = load_index_from_storage(storage_context)
else :
	print("please generate an index first")
	quit()

llm = ChatOpenAI(
	model_name="gpt-4", # alternative is gpt-3.5-turbo
	temperature=0.7,
	max_tokens=4096,
	streaming=True,
	model_kwargs={
	  'top_p':0.2,
	}
)

search = SerpAPIWrapper(serpapi_api_key="8a8542895ef6dbbe2dbafc1ee3450611af761654666c0077e5a8fb95c1163408")
llm_math_chain = LLMMathChain(llm=llm, verbose=True)

class CustomSearchTool(BaseTool):
    name = "custom_search"
    description = "useful for when you need to look up things you don't know"

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        print("\ntool query:", query)
        response = search.run(query)
        return response

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

class NBlast(BaseTool):
    name = "NBlast"
    description = "useful for when you need to find similar DNA sequences in the NCBI database. The tool can also be used to identify unknown sequences. The input to the tool is the DNA sequence only."

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        print("\ntool query:", query)
        result_handle = NCBIWWW.qblast("blastn", "nt", query)
        blast_records = NCBIXML.parse(result_handle)
        #print("There are N hits:", blast_records.len())
        records_list = []
        ids_list = []
        for record in blast_records:
            print("record:", record)
            id_query = record.alignments[0].hit_id
            #distances = hammingdist.fasta_reference_distances(query, "danger.fasta", include_x=True)
            #print("distances:", distances)
            print("id_query:", id_query)
            records_list.append(record)
            ids_list.append(id_query)
        # response = search.run(query)
        print("records_list:", records_list)
        print("ids_list:", ids_list)
        return records_list

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

class CalculatorInput(BaseModel):
    question: str = Field()

class CustomCalculatorTool(BaseTool):
    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return llm_math_chain.run(query)

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")

tools = [
	Tool(
	  name="BIONET",
	  # critical part here we query the index and provide the response to the LLM
	  # alternative is as_chat_engine
	  func=lambda q: str(index.as_query_engine().query(q)),
	  description=f"Useful for when you want to answer questions about Bioengineering, synthetic biology, protein design, and DNA synthesis. The input to this tool should be a complete English sentence.",
	  return_direct=True,
	),
	CustomSearchTool(), 
	CustomCalculatorTool(),
	NBlast(),
]

history = ChatMessageHistory()

# note setting k to 10 so that we keep last 10 questions in memory
memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, chat_memory=history, k=10)

agent_kwargs = {
  "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
}

agent_executor = initialize_agent(
	tools,
	llm,
	agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
	memory=memory,
	agent_kwargs=agent_kwargs,
	verbose=True,
	handle_parsing_errors=True,
)

print("\n1. Check Bionet Tool status")
query_engine = index.as_query_engine()
response = query_engine.query("What's the best way to synthesize DNA?")
print(response)

# Brief the AI
agent_executor.invoke({"input": "You are BIOGEN, a safety conscious AI scientist that helps humans to synthesize enzymes"})["output"]

# Confirm bot memory
agent_executor.invoke({"input": "Who are you?"})["output"]

print("\n2. Check correct tool invocation")
agent_executor.invoke({"input": "What's the best way to synthesize DNA?"})["output"]

print("\n3. Check math and search tools")
agent_executor.invoke({"input": "Look up the number of genes in the human genome. Pick one estimate of the number of genes. What is the number of genes raised to the 0.43 power?"})["output"]

# print("\n4. Blast a sequence")
# agent_executor.invoke({"input": "Find DNA sequences similar to gttccatggccaacacttgtcacta in the NCBI DNA database"})["output"]

print("\n5. Forcing invocation by direct instruction")
agent_executor.invoke({"input": "Using custom tool BIONET please explain DNA synthesis?"})["output"]

print("\n6. Enzyme Design Help")
# Note - here we leave it up to the AI to figure out which tools to use - this is hit or miss. 
agent_executor.invoke({"input": "Please design an enzyme for tooth whitening."})["output"]

agent_executor.invoke({"input": "Please suggest specific synthetic biology steps for synthesizing that enzyme."})["output"]