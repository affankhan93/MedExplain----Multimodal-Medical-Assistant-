from Retrieval import qa_chain

user_query = input("Enter you query here...")

response =qa_chain().invoke({'query': user_query})
print("Answer:- ", response['result'])
print("Source Documents:- ", response['source_documents'])