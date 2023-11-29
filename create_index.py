from llama_index import VectorStoreIndex, SimpleDirectoryReader
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, required=True)
args = parser.parse_args()
PROJECT_DIR = args.path + '/data'

print("Generating new index")

required_exts = [".md", ".pdf", ".txt"]

reader = SimpleDirectoryReader(
	input_dir=PROJECT_DIR,
	required_exts=required_exts, 
	recursive=True
)

documents = reader.load_data()
print(f"Loaded {len(documents)} docs. Please be patient...")

index = VectorStoreIndex.from_documents(documents)

print(f"Indexing completed. Writing index to file...")
STORAGE_DIR=args.path + '/storage'
index.storage_context.persist(persist_dir=STORAGE_DIR)

print("All done - you can now query a fine-tuned ChatGPT")

query_engine = index.as_query_engine()

key_words = query_engine.query("Summarize the material using no more than five words. The response should consist only of keywords. These keywords are used to help the AI decide when to use your data to augment its responses. Examples are: 'cars and trains" or "CS104 Introduction to Essential Software Systems and Tools'")
print(f"Your key words are: {key_words}")

prompts = query_engine.query("Generate three example questions that can be answered with the material.")
print(f"Your example prompts are: {prompts}")