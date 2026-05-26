from app.rag_pipeline import query_rag

question = "What are the benefits of RAG?"

response = query_rag(question)

print("\n")
print(response)