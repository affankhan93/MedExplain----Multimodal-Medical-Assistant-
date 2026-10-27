import os 
import warnings 
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain_classic.chains import RetrievalQA 
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq


load_dotenv()

INDEX_NAME = 'genai'
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

# Semantic search: Pinecone vector store
EMBED_MODEL = "llama-text-embed-v2"
embedding = PineconeEmbeddings(model=EMBED_MODEL)
vector_store = PineconeVectorStore(index=pc.Index(INDEX_NAME), embedding=embedding)

# Keyword search (BM25)
print("Loading PDFs for keyword search... (take a minute)")
DATA_PATH = 'Data'
documents = PyPDFDirectoryLoader(DATA_PATH).load()
chunks = RecursiveCharacterTextSplitter(chunk_size = 600, chunk_overlap = 130).split_documents(documents)
TOP_K_EACH = 10 # chunks fetched by each search (dense and keyword)
bm25  = BM25Retriever.from_documents(chunks, k = TOP_K_EACH)


# Hybrid Search :- It combines sematic search and keyword search to retrieve relevant documents.
TOP_K_CONDIDATES = 20 # chunks kept after merging, sent to the reranker 
def hybrid_search(query):
    """Run dense + keyword search, then merge with Reciprocal Rank Fusion (RRF)."""
    dense_docs = vector_store.similarity_search(query, k = TOP_K_EACH)
    keyword_docs = bm25.invoke(query)

    scores = {}       # chunk text -> combined score
    docs_by_text = {} # chunk text -> document object

    for results in (dense_docs, keyword_docs):
        for rank, doc in enumerate(results):
            text = doc.page_content
            docs_by_text[text] = doc 
            # chunks ranked higher in either list get a biggger score, and chunks found by both searches get the scores added together.
            scores[text] = scores.get(text, 0) + 1 / (60 + rank + 1)


    best_texts = sorted(scores, key = scores.get, reverse=True)[:TOP_K_CONDIDATES]
    return [docs_by_text[t] for t in best_texts]


# Re-ranking:- It can give the highest properity those have highest scores and rerank it according to score.
TOP_K_FINAL = 5 # Best 5 chunks after reranking, sent to the LLM.
def rerank(query, docs):
    """Let the rerank read query + chunk together and keep the best chunks."""
    result = pc.inference.rerank(
        model="bge-reranker-v2-m3", # pinecone hosted reranker model.
        query=query,
        documents=[d.page_content for d in docs],
        top_n=TOP_K_FINAL, 
    )
    return [docs[item.index] for item in result.data] # result.data is sorted best-first while item.index points to the original chunk


# Custom retrieval (hybrid search + rerank)
class HybridRerankRetriever(BaseRetriever): 
    """Lets RetrievalQA use our hybrid search + reranking like a normal retriever."""

    def _get_relevant_documents(self, query, *, run_manager = None):
        candidates = hybrid_search(query) # hybrid search
        return rerank(query, candidates) # reranking 

def create_retreiver():
    return HybridRerankRetriever() 


# Groq llm 
def load_llm():
    groq_llm = ChatGroq(
        api_key=os.environ['GROQ_API_KEY'],
        model = 'openai/gpt-oss-120b',
        temperature=0.4,
        max_tokens=1024
    )
    return groq_llm 

llm = load_llm() 

# custom prompt that guide llm to answer properly.
def create_custom_prompt():
    CUSTOM_PROMPT = """
        You are a helpful medical assitant. Youre job is to answer the question using only the context below.
        If the answer is not in the context, Just say: "I could not find this in the documents."

        Context:{context}
        Qeustion:{question}
        Answer: 
        """
    prompt = PromptTemplate(
        template=CUSTOM_PROMPT,
        input_variables=['context', 'question'],
    )
    return prompt 
 

# Question and answer chain
def qa_chain():
    llm = load_llm()
    retriever = create_retreiver() 

    qa_chain = RetrievalQA.from_chain_type(
        llm = llm,
        retriever = retriever,
        chain_type = 'stuff',
        return_source_documents = True,
        chain_type_kwargs = {'prompt': create_custom_prompt()}

    )
    return qa_chain

# print("Everything is working properly...")





