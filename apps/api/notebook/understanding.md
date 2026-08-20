# RAG & LangChain Text Chunking: Q&A Summary

This document summarizes the questions and answers from today's session regarding LangChain text splitters, attribute errors, embedding requirements, and internal chunking logic.

---

## Question 1: Fixing `AttributeError` in Chunking Notebook

### **Question**
> What is wrong with this code? Getting `AttributeError`.
> ```python
> from google.genai._api_client import CHUNK_SIZE
> from langchain_text_splitters import RecursiveCharacterTextSplitter 
> 
> splitter = RecursiveCharacterTextSplitter(
>     chunk_size=500,
>     chunk_overlap=50
> )
> 
> documents = """
> Berlin, the capital and largest city of Germany, is a global center for culture, politics, media, and science...
> """
> 
> chunks = splitter.split_documents(documents)
> print(chunks)
> ```

### **Answer**
The `AttributeError` occurs because `split_documents()` expects a list of LangChain `Document` objects, not a plain `str`.

#### **Solution 1: Use `split_text()` for raw strings**
```python
chunks = splitter.split_text(documents)
print(chunks)
```

#### **Solution 2: Convert text to `Document` objects**
```python
docs = splitter.create_documents([documents])
chunks = splitter.split_documents(docs)
print(chunks)
```

---

## Question 2: Is `splitter.split_text()` the exact point where splitting happens?

### **Question**
> Does `chunks = splitter.split_text(documents)` mean split at this point?

### **Answer**
**Yes.** Calling `splitter.split_text(documents)` (or `splitter.split_documents(...)`) is the execution line where the actual chunking operation takes place based on the rules configured in `RecursiveCharacterTextSplitter`.

---

## Question 3: Are AI models required for chunking vs embeddings?

### **Question**
> So that means for chunking we don't need any model if we are using LangChain, but we have to use an embedding model, right?

### **Answer**
**Yes, exactly.**

1. **Text Chunking (Rule-Based — No Model Needed)**: Splitters like `RecursiveCharacterTextSplitter` use pure algorithmic rules (character counts, token counts, separator boundaries like `\n\n` or spaces) without making any LLM or AI model API calls.
2. **Embeddings & Vector Storage (Requires AI Model)**: An **Embedding Model** (e.g., Google `text-embedding-004`, OpenAI, Jina) is required to convert each generated text chunk into numerical vector embeddings before storing them in a vector database (e.g., Chroma, PGVector).

---

## Question 4: PDF Chunking & `RecursiveCharacterTextSplitter` Under the Hood

### **Question**
> So when I upload a PDF, does that mean at that point it will not use any model to chunk it? And in LangChain, under the hood, how is `TextSplitter` actually working?

### **Answer**

### 1. PDF Uploading Process
When a PDF is uploaded:
- **Document Loading**: PyPDF/pdfplumber parses the PDF bytes to extract raw string text. **(No AI model used)**
- **Text Chunking**: The splitter breaks the extracted text string into smaller pieces. **(No AI model used)**

### 2. Under the Hood: `RecursiveCharacterTextSplitter` Logic
It uses a prioritized hierarchy of separators to preserve semantic context (paragraphs > sentences > words):

```python
separators = ["\n\n", "\n", " ", ""]
```

#### **Step-by-Step Algorithm:**
1. **Try 1st Separator (`\n\n`)**: Tries to split on paragraph breaks. Groups paragraphs up to `chunk_size`.
2. **Check Chunk Size**: If any paragraph exceeds `chunk_size`, it falls back to the next separator (`\n`) specifically for that chunk.
3. **Fallback Hierarchy**: Falls back down through lines (`\n`), spaces (`" "`), and finally individual characters (`""`) if necessary.
4. **`chunk_overlap`**: Includes trailing characters from the prior chunk to prevent context loss across boundaries.
