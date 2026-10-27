import asyncio 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RAG_Pipeline.Retrieval import qa_chain
from MCP_Pipeline.mcp_client import generate_image 


app = FastAPI() 

class Query(BaseModel):
    question : str 

chain = qa_chain()
def rag_answer(question: str) -> str: 
    response = chain.invoke({'query' : question})
    return response['result']


@app.post("/question")
async def ask_question(query: Query):
    text_task = asyncio.to_thread(rag_answer, query.question)
    image_task = generate_image(query.question)

    answer, image_b64 = await asyncio.gather(text_task, image_task, return_exceptions=True)

    if isinstance(answer, Exception):
        print("RAG error:- ", repr(answer))
        raise HTTPException(status_code=500, detail="RAG pipeline faild.")
    if isinstance(image_b64, Exception):
        print("Image error:-", repr(image_b64))
        image_b64 = None 

    return {'answer': answer, 'image_base64': image_b64}

    
