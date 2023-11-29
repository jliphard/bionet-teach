# bionet-teach

The goal of this repo is to instantiate a basic AI / synthetic biology workflow. The workflow assumes that a knowledgeable human scientist will participate in the design/build/test cycle, although the human can be replaced by an AI agent with some code changes. 

 ## Canonical workflow

 In the basic workflow, the human provides a needs statement to the AI. The AI then uses a variety of tools to check public databases (e.g. Pubmed), evaluate the cost/complexity of DNA synthesis, check for potentially harmful sequences, and translate the required designs into a universal format understood by DNA synthesizers.

 ## Usage

 Make sure you have python 3 up and running on your command line. Install various packages with `pip` as needed, for example, `pip install openai`. Define API keys as needed:


 ```shell
export SERPAPI_API_KEY="..." 
export OPENAI_API_KEY="..."
 ```    

## Training and basic usage

Create a knowledge base for the Bionet grammar

```shell
python3 create_index.py --path ./training_data/bionet
Loaded 58 docs. Please be patient...
Generating new index
All done - you can now query a fine-tuned ChatGPT

Your key words are: Weekly Feedback, BioNet Tabletop, Systems Integrator, Foundries

Your example prompts are: 
1. What is the purpose of the "Cotton Tattoo" project mentioned in the workflow example?
2. How does the Systems Integrator on the BioNet handle customer requests for protein design and testing?
3. What are the requirements of the customer in terms of the protein, DNA, and cell strains used in the testing process?
```

Now, try it out...

```shell
python3 query.py --path ./training_data/bionet
```

## Generic setup

```python
llm = ChatOpenAI(
	model_name="gpt-4", # alternative is gpt-3.5-turbo
	temperature=0.7,
	max_tokens=4096,
	streaming=True,
	model_kwargs={
	  'top_p':0.2,
	}
)

history = ChatMessageHistory()

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, chat_memory=history, k=10)

agent_kwargs = {
  "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
}
```

## Forced tool invocation

```python
query_engine = index.as_query_engine()
response = query_engine.query("What's the best way to synthesize DNA?")
print(response)
```

```txt
Response: The best way to synthesize DNA is through artificial DNA synthesis. This process involves the base-by-base synthesis of oligonucleotides (oligos), which are then assembled into double-stranded DNA (dsDNA) fragments. This method allows scientists to create DNA molecules of virtually any sequence without a template. The synthesis of oligos is a highly automated process that involves cycles of chemical reactions using phosphoramidites as precursors. However, it's important to note that there is a tradeoff between using longer oligos, which simplifies assembly, and the sequence fidelity of the final product
```

## Example thought process

1. Check Bionet Tool status

The best way to synthesize DNA is through artificial DNA synthesis. This process involves the base-by-base synthesis of oligonucleotides, followed by assembly into double-stranded DNA fragments. These custom DNA fragments can be used directly, cloned into vectors, or assembled into larger constructs. Gene synthesis technology offers a combination of speed, precision, and flexibility that is unmatched by classical molecular biology techniques. It is important to define project goals, design the sequence, synthesize oligos, assemble the fragments, and verify the sequence of the gene fragment or cloned product. Additionally, it is recommended to consider factors such as communication with collaborators, project timeline planning, literature knowledge, codon optimization, access to instrumentation, and sequence verification. While these steps can be performed in-house, using a service provider for gene synthesis can save time and effort.

> Entering new AgentExecutor chain...
```json
{
    "action": "Final Answer",
    "action_input": "As BIOGEN, I'm here to assist you with synthesizing enzymes. Please provide more details about the specific enzyme you're interested in, such as its name or the sequence of amino acids it's composed of. This will help me provide more accurate and helpful information."
}
```
> Finished chain.

> Entering new AgentExecutor chain...
```json
{
    "action": "Final Answer",
    "action_input": "I am BIOGEN, an AI assistant designed to help with tasks related to bioengineering, synthetic biology, protein design, and DNA synthesis. I can provide information, assist with calculations, and help you use tools like BIONET, custom_search, Calculator, and NBlast to answer more complex questions."
}
```
> Finished chain.

2. Check correct tool invocation

> Entering new AgentExecutor chain...
```json
{
    "action": "BIONET",
    "action_input": "What's the best way to synthesize DNA?"
}
```
Observation: The best way to synthesize DNA is through artificial DNA synthesis. This process involves the base-by-base synthesis of oligonucleotides, followed by assembly into double-stranded DNA fragments. These custom DNA fragments can be used directly, cloned into vectors, or assembled into larger constructs. Gene synthesis technology offers a combination of speed, precision, and flexibility that is unmatched by classical molecular biology techniques. It is important to define project goals, design the sequence, synthesize oligos, assemble the fragments, and verify the sequence of the gene fragment or cloned product. Additionally, it is recommended to consider factors such as communication with collaborators, project timeline planning, literature knowledge, sequence and codon optimization, access to instrumentation, and the rigor of quality control. While these steps can be performed in-house, using a service provider for gene synthesis can save time and effort.
> Finished chain.

3. Check math and search tools
> Entering new AgentExecutor chain...
```json
{
    "action": "custom_search",
    "action_input": "number of genes in the human genome"
}
```
tool query: number of genes in the human genome

Observation: [{'link': 'https://homework.study.com/explanation/approximately-how-many-genes-does-the-human-genome-include.html', 'source': 'Study.com', 'question': 'Approximately how many genes does the human genome include?', 'answer': 'The human genome contains approximately 19,000-20,000 protein-coding genes. Advances in sequencing technologies and our understanding of human genetics has allowed scientists to narrow down this estimate. Further progress in this field will likely create an even better estimate in the future.', 'votes': 0}, {'link': 'https://www.pearson.com/channels/biology/asset/b2c9ca03/the-human-genome-is-thought-to-contain-about-how-many-genes', 'source': 'Pearson', 'question': 'The human genome is thought to contain about how many genes?', 'answer': '20,000–25,000', 'votes': 0}, {'link': 'https://www.toppr.com/ask/question/number-of-genes-present-in-human-genome-is-about/', 'source': 'Toppr', 'question': 'Number of genes present in human genome is about', 'answer': 'A gene is a distinct sequence of nucleotides forming part of a chromosome-Most of the genes do not code for proteins- In humans- genes vary in size from a few hundred DNA bases to more than 2 million bases- The Human Genome Project estimated that humans have around 21-000 genes-So- the correct option is -apos-21-000-apos-', 'votes': 0}, {'link': 'https://www.biostars.org/p/272336/', 'source': 'BioStars', 'question': 'number of genes in human genome', 'answer': 'a quick check: $ curl -s "ftp://ftp.ensembl.org/pub/release-90/gtf/homo_sapiens/Homo_sapiens.GRCh38.90.gtf.gz" | gunzip -c | awk \'($3=="gene")\' | cut -f 9 | tr ";" " " | grep gene_biotype | sed \'s/gene_biotype//\' | sort | uniq -c | sort -rn 19847 "protein_coding" 10235 "processed_pseudogene" 7493 "lincRNA" 5517 "antisense_RNA" 2637 "unprocessed_pseudogene" 2221 "misc_RNA" 1909 "snRNA" 1879 "miRNA" 1066 "TEC" 943 "snoRNA" 904 "sense_intronic" 828 "transcribed_unprocessed_pseudogene" 549 "rRNA" 543 "processed_transcript" 462 "transcribed_processed_pseudogene" 189 "sense_overlapping" 188 "IG_V_pseudogene" 144 "IG_V_gene" 111 "transcribed_unitary_pseudogene" 108 "TR_V_gene" 95 "unitary_pseudogene" 79 "TR_J_gene" 63 "polymorphic_pseudogene" 49 "scaRNA" 37 "IG_D_gene" 31 "3prime_overlapping_ncRNA" 30 "TR_V_pseudogene" 22 "pseudogene" 22 "Mt_tRNA" 19 "bidirectional_promoter_lncRNA" 18 "IG_J_gene" 14 "IG_C_gene" 9 "IG_C_pseudogene" 8 "ribozyme" 6 "TR_C_gene" 5 "sRNA" 4 "TR_J_pseudogene" 4 "TR…', 'votes': 4}, {'link': 'https://typeset.io/questions/how-many-genes-are-in-human-genome-2att30kxr0', 'source': 'SciSpace by Typeset', 'question': 'how many genes are in human genome?', 'answer': 'The human genome contains an estimated range of 30,000-100,000 genes. Early estimates suggested a range of 60,000-100,000 genes. However, recent analyses of available data from EST sequencing projects have estimated as few as 45,000 or as many as 140,000 distinct genes. The Chromosome 22 Sequencing Consortium estimated a minimum of 45,000 genes based on their annotation of the complete chromosome. The first draft sequence of the human genome indicated about 30,000-40,000 different genes. The final count is likely to be closer to 30,000 genes. The size of the human genome, about 3 x 10^9 base pairs, suggests an upper limit of about 3 million genes, but evidence from various approaches indicates a much lower figure.', 'votes': 0}, {'link': 'https://www.quora.com/How-many-genes-are-in-the-human-genome', 'source': 'Quora', 'question': 'How many genes are in the human genome?', 'answer': '20,000-25,000. Source: Finishing the euchromatic sequence of the human genome (2004 Nature article, http://www.ncbi.nlm.nih.gov/pubmed/15496913?dopt=Abstract) "...The current genome sequence (Build 35) contains 2.85 billion nucleotides interrupted by only 341 gaps. It covers approximately 99% of the euchromatic genome and is accurate to an error rate of approximately 1 event per 100,000 bases. Many of the remaining euchromatic gaps are associated with segmental duplications and will require focused work with new methods...Notably, the human genome seems to encode only 20,000-25,000 protein-coding genes. The genome sequence reported here should serve as a firm foundation for biomedical research in the decades ahead."', 'votes': 7}, {'link': 'https://biology.stackexchange.com/questions/101031/how-many-genes-per-23-chromosomes-in-human-genome', 'source': 'Stack Exchange', 'question': 'How many genes per 23 chromosomes in human genome? [closed]', 'answer': "Answer A is correct! The human genome has around 20,000 genes. In both, diploid and haploid chromosome-count, the gene-count stays the same; grown humans have 2 alleles per gene in most of their cells, which is considered 'diploid'. Gametes are haploid. Willyard, C., Expanded human gene tally reignites debate. Nature, 2018. 558(7710): p. 354-355."}, {'link': 'https://byjus.com/question-answer/how-many-genes-are-in-the-human-body/', 'source': "BYJU'S", 'question': 'How Many Genes Are In The Human Body- - NEET', 'answer': 'Gene:A gene is the basic physical and functional unit of heredity, made up of nucleotides called DNA.The Human Genome Project, which was an international resear ...', 'votes': 8}, {'link': 'https://www.researchgate.net/post/How_many_genes_in_human_genome_have_known_identified_function', 'source': 'ResearchGate', 'question': 'How many genes in human genome have known identified function?', 'answer': 'Shubham Bhardwaj Please read this 2018 Nature paper. They might include some info you are looking for. https://www.nature.com/articles/d41586-018-05462-w', 'votes': 0}, {'link': 'https://www.reddit.com/r/evolution/comments/u8o5eo/how_true_surprising_is_this_the_human_genome/', 'source': 'Reddit', 'question': 'How true & surprising is this: "The human genome comprises about 3.5 billion base pairs. It contains a surprisingly low number of fewer than 24,000 functional genes"', 'answer': "It was surprising to my (90s) generation, we were taught there were about 100,000 genes, based on the average observed gene size was about 30kbp and the human genome was 3.2Gbp, we didn't have EST, genomic sequencing or know about alternate splicing and 'junk' DNA.", 'votes': 7}]

Thought:
```json
{
    "action": "Calculator",
    "action_input": "20000^0.43"
}
```

> Entering new LLMMathChain chain...
20000^0.43
```text
20000**0.43
```
...numexpr.evaluate("20000**0.43")...

Answer: 70.70382318380996
> Finished chain.

Observation: Answer: 70.70382318380996
Thought:
```json
{
    "action": "Final Answer",
    "action_input": "The number of genes in the human genome is estimated to be around 20,000. When this number is raised to the power of 0.43, the result is approximately 70.7."
}
```
> Finished chain.

5. Forcing invocation by direct instruction
> Entering new AgentExecutor chain...
```json
{
    "action": "BIONET",
    "action_input": "Explain DNA synthesis"
}
```
Observation: DNA synthesis is the process of creating DNA molecules from scratch without the need for a template. It is a fundamental tool in synthetic biology that allows scientists to generate DNA sequences of virtually any desired sequence. The process involves several steps, including defining project goals, designing the DNA sequence, synthesizing short DNA fragments called oligonucleotides, assembling these fragments into longer DNA fragments, and verifying the accuracy of the final synthetic DNA product. DNA synthesis offers advantages in terms of speed, precision, and flexibility compared to traditional molecular biology techniques. It can be used to create custom DNA fragments for various research purposes, such as cloning into vectors or assembling into larger constructs.
> Finished chain.

6. Enzyme Design Help
> Entering new AgentExecutor chain...
```json
{
    "action": "BIONET",
    "action_input": "Design an enzyme for tooth whitening"
}
```
Observation: To design an enzyme for tooth whitening, you can fuse an enamel-binding peptide with a perhydrolase. The resulting fusion protein will hopefully be retained on the teeth longer than a perhydrolase enzyme only. The enamel-binding peptide will bind the tooth enamel, and the perhydrolase will whiten the teeth. It is important to note that using hydrogen peroxide in a rinse or paste may help whiten teeth, but a high concentration may cause side effects, including damaging the teeth.
> Finished chain.

> Entering new AgentExecutor chain...
```json
{
    "action": "BIONET",
    "action_input": "What are the steps for synthesizing a fusion protein of an enamel-binding peptide and a perhydrolase for tooth whitening?"
}
```
Observation: To synthesize a fusion protein of an enamel-binding peptide and a perhydrolase for tooth whitening, the following steps can be followed:

1. Fuse the enamel-binding peptide with the perhydrolase.
2. Ensure that the resulting fusion protein is retained on the teeth for a longer period compared to a perhydrolase enzyme alone.
3. The enamel-binding peptide will bind to the tooth enamel.
4. The perhydrolase will whiten the teeth.
5. Test the enzyme activity retention after toothbrushing through contract lab testing.
6. Optionally, avoid adding affinity purification tags to the fusion protein in some use cases.
> Finished chain.