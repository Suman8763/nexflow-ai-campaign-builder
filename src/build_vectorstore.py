import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


print("Loading documents...")

# Load all .txt files
loader = DirectoryLoader("../data", glob="*.txt")
documents = loader.load()

print(f"Loaded {len(documents)} documents")

# -------------------------------------------------
# 🔥 ADD CLEAN METADATA (IMPORTANT PART)
# -------------------------------------------------

cleaned_docs = []

for doc in documents:
    # Extract clean filename from path
    source_path = doc.metadata.get("source", "")
    filename = os.path.basename(source_path)

    new_doc = Document(
        page_content=doc.page_content,
        metadata={
            "source": filename,          # file name only
            "category": filename.replace(".txt", "")  # optional future filtering
        }
    )

    cleaned_docs.append(new_doc)

print("Metadata attached to documents.")

# -------------------------------------------------
# Split documents into chunks
# -------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

docs = text_splitter.split_documents(cleaned_docs)

print(f"Split into {len(docs)} chunks")

# -------------------------------------------------
# Create embeddings
# -------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

print("Creating vector store...")

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="../chroma_db"
)

vectorstore.persist()

print("Vector store successfully built.")

# -------------------------------------------------
# 🔎 TEST RETRIEVAL (WITH METADATA CHECK)
# -------------------------------------------------

print("\nTesting retrieval...\n")

test_query = "What CRM integrations are available in NexFlow?"

results = vectorstore.similarity_search(test_query, k=5)

for r in results:
    print("-----")
    print("Source:", r.metadata)
    print(r.page_content[:300])
