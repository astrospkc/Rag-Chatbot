# # pipeline.py

# from internal.rag.loaders.documentLoader import DocumentLoader
# class IngestionPipeline:

#     def __init__(self, loader, chunker, embedder, vector_store):
#         self.loader = loader
#         self.chunker = chunker
#         self.embedder = embedder
#         self.vector_store = vector_store

#     def run(self, file_path):

#         # 1. Load
#         documents = self.loader.load_pdf(file_path)

#         # 2. Chunk
#         chunks = self.chunker.split(documents)

#         # 3. Embeddings
#         vectors = self.embedder.embed(chunks)

#         # 4. Store
#         self.vector_store.add(chunks, vectors)

#         return {
#             "status": "completed",
#             "chunks": len(chunks)
#         }
    
# ingestion_pipeline = IngestionPipeline(
#     loader=DocumentLoader(),
#     # chunker=TextChunker(),
#     # embedder=OpenAIEmbedder(),
#     # vector_store=ChromaStore(persist_directory="./data/chroma_db")
# )
    