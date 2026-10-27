from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
import os 
import time 

load_dotenv() 
# Load Pdfs
DATA_PATH = "Data"
def load_pdfs(data_path):
    loader = PyPDFDirectoryLoader(data_path)
    documents = loader.load()
    return documents

documents = load_pdfs(DATA_PATH)
print(f"Total Number of Documents are:- {len(documents)}")

# Create chunks from documents
def create_chunks(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 600, chunk_overlap = 130)
    all_splites = text_splitter.split_documents(extracted_data)
    return all_splites

chunks = create_chunks(extracted_data=documents)

# Vector embeddings 
MODEL = "llama-text-embed-v2" 
def vector_embeddings():
    embeddings = PineconeEmbeddings(model = MODEL)
    return embeddings

embedding = vector_embeddings()

# Vector database(Pinecone)
INDEX_NAME = 'genai'
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name = INDEX_NAME,
        dimension=1024,
        metric='cosine', 
        spec=ServerlessSpec(cloud="aws", region='us-east-1') 
    )
    time.sleep(10) 

vector_store = PineconeVectorStore(index=pc.Index(INDEX_NAME), embedding=embedding)

# Upload in small batches with a puase after each one because it throw rate limit error 
BATCH_SIZE = 100 # chunks uploaded at a time. 
WAIT_SECONDS = 10 # pause between batches to avoids the rate limit.
for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i: i + BATCH_SIZE]
    ids = [f"chunks-{i + j}" for j in range(len(batch))]
    vector_store.add_documents(batch ,ids=ids)
    print(f"Uploaded {min(i + BATCH_SIZE, len(chunks))} / {len(chunks)}")
    time.sleep(WAIT_SECONDS)

print("Done!")
print(pc.Index(INDEX_NAME).describe_index_stats())






    



