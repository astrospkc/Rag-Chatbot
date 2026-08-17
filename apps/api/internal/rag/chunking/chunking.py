from google.genai._api_client import CHUNK_SIZE
from langchain_text_splitters import RecursiveCharacterTextSplitter 

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

documents = """
Berlin, the capital and largest city of Germany, is a global center for culture, politics, media, and science.

With a rich and complex history, Berlin has reinvented itself multiple times, most notably after the fall of the Berlin Wall in 1989, which reunified the city and symbolized the end of the Cold War.

The city is known for its vibrant arts scene, historic landmarks such as the Brandenburg Gate and the Reichstag building, and its thriving startup ecosystem.

"""

chunks = splitter.split_documents(documents)