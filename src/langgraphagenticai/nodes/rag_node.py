import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import AIMessage
from pinecone import Pinecone
import tempfile
from dotenv import load_dotenv
load_dotenv()
import os


class RAGNode:
    def __init__(self, llm):
        self.llm = llm
        api_key = st.session_state.get("OPENAI_API_KEY")
        # Init embeddings
        self.embeddings = OpenAIEmbeddings(api_key=api_key)

        # Init Pinecone
        self.pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self.index_name = "ai-research-assistant"

    def load_document(self, uploaded_file):
        """Load PDF or Text file"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            file_path = tmp_file.name

        if uploaded_file.name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)

        documents = loader.load()
        return documents

    def split_documents(self, documents):
        """Split into chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return splitter.split_documents(documents)

    def store_in_pinecone(self, docs):
        """Store embeddings in Pinecone"""
        vectorstore = PineconeVectorStore.from_documents(
            docs,
            embedding=self.embeddings,
            index_name=self.index_name
        )
        return vectorstore

    def retrieve(self, query):
        """Retrieve relevant docs"""
        vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        return retriever.invoke(query)

    def generate_answer(self, query, docs):
        """Generate final answer using LLM"""
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
        You are an AI research assistant.

        - Answer clearly and concisely
        - Use bullet points if needed
        - Avoid unnecessary technical jargon
        - Format output nicely

        Context:
        {context}

        Question:
        {query}
        """

        response = self.llm.invoke(prompt)
        return response

    def __call__(self, state: dict):

        user_query = state["messages"][-1].content

        uploaded_file = st.session_state.get("uploaded_file", None)

        if uploaded_file and not st.session_state.get("rag_initialized", False):
            documents = self.load_document(uploaded_file)
            chunks = self.split_documents(documents)
            self.store_in_pinecone(chunks)
            st.session_state["rag_initialized"] = True
            st.success("✅ Document processed successfully!")

        docs = self.retrieve(user_query)

        answer = self.generate_answer(user_query, docs)

        return {"messages": [AIMessage(content=str(answer.content))]}