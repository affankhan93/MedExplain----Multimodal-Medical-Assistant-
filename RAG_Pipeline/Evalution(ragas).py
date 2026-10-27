from datasets import Dataset
from ragas_data import data_samples2
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate 
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeEmbeddings
from ragas.run_config import RunConfig
import os

load_dotenv() 

# Evalute with groq LLM 
groq_llm = ChatGroq(
        api_key=os.environ['GROQ_API_KEY'],
        model = "openai/gpt-oss-120b",
        temperature = 0.0
)

ragas_llm = LangchainLLMWrapper(groq_llm)

# Pinecone Embedding Model
EMBED_MODEL = 'llama-text-embed-v2'
pinecone_embeddings = LangchainEmbeddingsWrapper(PineconeEmbeddings(model = EMBED_MODEL))


# Convert the sample records into a dataset 
eval_dataset = Dataset.from_list(data_samples2)

run_config = RunConfig(
    timeout=300, 
    max_retries= 2, 
    max_workers= 1 
)

result = evaluate(
    dataset=eval_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ],
    llm= groq_llm,
    embeddings=pinecone_embeddings,
    run_config=run_config
)

print(result)

df = result.to_pandas()
print(df)

df.to_csv("ragas_medical_result.csv", index = False)
# {'faithfulness': 1.0000, 'answer_relevancy': 0.5367, 'context_precision': 1.0000, 'context_recall': 1.0000}

# print("Total evalution questions", len(eval_dataset))
# print(eval_dataset[0])

