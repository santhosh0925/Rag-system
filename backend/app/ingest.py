import os

from .config import DATA_DIR, CHROMA_DIR

DATA_PATH = str(DATA_DIR)
DB_PATH = str(CHROMA_DIR)


def ingest_documents():
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings

    documents = []

    for file in os.listdir(DATA_PATH):

        print("Found file:", file)

        if file.endswith(".txt"):

            file_path = os.path.join(DATA_PATH, file)

            print(f"Loading: {file}")

            loader = TextLoader(file_path)

            documents.extend(loader.load())

    print(f"Loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    if len(chunks) == 0:
        print("No chunks created!")
        return

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print("Documents ingested successfully!")


if __name__ == "__main__":
    ingest_documents()
