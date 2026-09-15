from sqlalchemy.orm import Session
from internal.models import UploadedDocument
from internal.llm.factory import LLMFactory
from internal.models import DocumentVector
from internal.rag.embeddings import EmbeddingFactory
class RouterService:
    def __init__(self,llm:str|None=None):
        # self.llm =  LLMFactory.get_llm(provider=llm)
        self.llm = LLMFactory.get_llm()

    def route_query_to_document(self,user_query: str, db: Session) -> int | None:
    # 1. Fetch available documents
        docs = db.query(UploadedDocument.id, UploadedDocument.title).filter(
            UploadedDocument.status == "COMPLETED"
        ).all()

        if not docs:
            return None

        # Build a brief manifest of documents
        doc_catalog = "\n".join([f"- ID {d.id}: {d.title}" for d in docs])

        # 2. Prompt a fast LLM (e.g. gpt-4o-mini or gemini-flash)
        router_prompt = f"""
        You are an intelligent document routing engine.
        Given the list of uploaded documents and a user query, determine if the user is asking about a specific document.

        Available Documents:
        {doc_catalog}

        User Query: "{user_query}"

        Instructions:
        - If the query specifically targets or clearly belongs to one document, respond ONLY with its integer ID.
        - If the query is general, could apply to multiple documents, or you are unsure, respond ONLY with "ALL".
        """


        result = self.llm.invoke(router_prompt)
        final = int(result.content.strip()) if result.content.strip().isdigit() else None
        if final is not None:
            print(f"Routing query to document ID: {final}")
            return final
        return None

    def answer_query(self, doc_id:int, user_query:str, db:Session) ->dict|None:
        """
        Full Rag :
        route -> vector retrieve -> llm answer generation
        """
         # Fetch the document by ID
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == doc_id).first()
        if not doc:
            return None


        # route the query to a document 
        doc_id =self.route_query_to_document(user_query, db)
        print(f"Routed query to document ID: {doc_id}")
        embed_provider = EmbeddingFactory.get_provider(provider_name="openai")
        # retrieve chunks from pgvector 
        query_vector = embed_provider.embed_query(user_query)
        
        query = db.query(DocumentVector)
        if doc_id is not None:
            query = query.filter(DocumentVector.doc_metadata["document_id"].as_integer() == doc_id)

        # retrieve top 4 most similar chunks using pgvector cosine distance 
        chunks  = (
            query.order_by(DocumentVector.embedding.cosine_distance(query_vector)).limit(4).all()
        )
        if not chunks:
            return {
                "answer": "I could not find any relevant information in the uploaded documents to answer your question.",
                "sources": []
            }

        context_text = "\n\n---\n\n".join([f"[Title:{chunk.title}]\n{chunk.content}" for chunk in chunks])

        # generate final answer using llm 
        answer_prompt = f"""
         You are an AI assistant answering questions based strictly on the provided context.
        Use only the following context to answer the user's question clearly and accurately.
        If the answer cannot be found in the context, state that you don't have enough information.
        Context:
        {context_text}
        User Question:
        {user_query}
        Answer:
        """

        llm_response = self.llm.invoke(answer_prompt)
        final_answer  = str(llm_response.content).strip()
       
        return {
            "answer": final_answer,
            "matched_document_id": doc_id,
            "sources": [
                {
                    "title": chunk.title,
                    "metadata": chunk.doc_metadata
                }
                for chunk in chunks
            ]
        }