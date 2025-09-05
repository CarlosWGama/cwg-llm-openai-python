# pip install langchain langchain-community langchain-openai faiss-cpu python-dotenv
# pip install beautifulsoup4
# pip install pypdf

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader, WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.output_parsers import StrOutputParser


# ========= Configurações
load_dotenv()
llm = ChatOpenAI(model=os.environ["CWG_LLM_OPENAI_MODEL"], temperature=0, api_key=os.environ["CWG_LLM_OPENAI_KEY"])
embeddings = OpenAIEmbeddings(api_key=os.environ["CWG_LLM_OPENAI_KEY"], model=os.environ["CWG_LLM_OPENAI_EMBEDDING"] if os.environ["CWG_LLM_OPENAI_EMBEDDING"] else  "text-embedding-3-small")
RAG_DIR = os.path.abspath('./src/rag-dir')+'/';

# =================================================================
def ask(question):
    try:
        response = llm.invoke([HumanMessage(question)]);
        return response.content;
    except Exception as error:
        print("Ocorreu um erro:", error)
    

# --------------------------
def ask_from_prompt(question, context):
    try:
        prompt = ChatPromptTemplate.from_template("""Para responder, utilize o conhecimento disponivel no contexto abaixo. 
                Caso não saiba responder, responda com 'Não tenho essa informação'

                Contexto: 
                {context}
                
                Pergunta: 
                {question}
        """);
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({ "context":context, "question":question });
        return response

    except Exception as error:
        print("Ocorreu um erro:", error);
  
# --------------------------
def save_embedding(URL = None, PDF = None, rag = 'default'):
    # --- ETAPA 1: CARREGAR O CONTEÚDO DO LINK ---
    # CARREGA DADOS DA URL OU PDF
    docs = None
    if (URL): 
        loader = WebBaseLoader(URL);
        docs = loader.load();
    elif (PDF): 
        loader = PyPDFLoader(PDF);
        docs = loader.load_and_split();


    # --- ETAPA 2: DIVIDIR O CONTEÚDO EM PEDAÇOS (CHUNKS) ---
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200);
    split_docs = text_splitter.split_documents(docs);

    # --- ETAPA 3: INDEXAR O CONTEÚDO (CRIAR VECTOR STORE) ---
    vector_store = FAISS.from_documents(split_docs, embeddings);
    vector_store.save_local(RAG_DIR + rag)

# -----------------------
def ask_from_url(question, URL, saveDir = False):
    try:
        
        # --- ETAPA 1: CARREGAR O CONTEÚDO DO LINK ---
        # CARREGA DADOS DA URL
        loader = WebBaseLoader(URL);
        docs = loader.load();

        # --- ETAPA 2: DIVIDIR O CONTEÚDO EM PEDAÇOS (CHUNKS) ---
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200);
        split_docs = text_splitter.split_documents(docs);

        # --- ETAPA 3: INDEXAR O CONTEÚDO (CRIAR VECTOR STORE) ---
        vector_store = FAISS.from_documents(split_docs, embeddings);
        if (saveDir): 
            print(RAG_DIR+saveDir)
            vector_store.save_local(RAG_DIR+saveDir)
        
        retriever = vector_store.as_retriever();

        # --- ETAPA 4: CRIAR A CHAIN PARA FAZER PERGUNTAS ---
        prompt = ChatPromptTemplate.from_template("""
            Responda à pergunta do usuário baseando-se exclusivamente no seguinte contexto extraído de uma página web.
            Se a informação não estiver no contexto, diga: Não tenho essa informação

            Contexto:
            {context}

            Pergunta:
            {input}
        """);
        
        # --- ETAPA 5: RECUPERANDO A INFORMAÇÃO
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({
            "input": question
        });

        return response['answer']

    except Exception as error:
        print("Ocorreu um erro:", error)

# ------------
def ask_from_pdf(question, filePath, saveDir = False):
    try:
        
        # --- ETAPA 1: CARREGAR O CONTEÚDO DO LINK ---
        # CARREGA DADOS DO PDF
        loader = PyPDFLoader(filePath);
        docs = loader.load();

        # --- ETAPA 2: DIVIDIR O CONTEÚDO EM PEDAÇOS (CHUNKS) ---
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200);
        split_docs = text_splitter.split_documents(docs);

        # --- ETAPA 3: INDEXAR O CONTEÚDO (CRIAR VECTOR STORE) ---
        vector_store = FAISS.from_documents(split_docs, embeddings);
        if (saveDir): vector_store.save_local(RAG_DIR+saveDir)
        
        retriever = vector_store.as_retriever();

        # --- ETAPA 4: CRIAR A CHAIN PARA FAZER PERGUNTAS ---
        prompt = ChatPromptTemplate.from_template("""
            Responda à pergunta do usuário baseando-se exclusivamente no seguinte contexto extraído de uma página web.
            Se a informação não estiver no contexto, diga: Não tenho essa informação

            Contexto:
            {context}

            Pergunta:
            {input}
        """);
        
        # --- ETAPA 5: RECUPERANDO A INFORMAÇÃO
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({
            "input": question
        });

        return response['answer']

    except Exception as error:
        print("Ocorreu um erro:", error)

# -------------------------------------------
def ask_from_embedding(question, ragPath = 'default'):
    try:
        
        # --- ETAPA 1: CARREGAR O CONTEÚDO DO LINK ---
        vector_store = FAISS.load_local(RAG_DIR+ragPath, embeddings, allow_dangerous_deserialization=True);
        retriever = vector_store.as_retriever();

        # --- ETAPA 2: CRIAR A CHAIN PARA FAZER PERGUNTAS ---
        prompt = ChatPromptTemplate.from_template("""
            Responda à pergunta do usuário baseando-se exclusivamente no seguinte contexto extraído de uma página web.
            Se a informação não estiver no contexto, diga: Não tenho essa informação

            Contexto:
            {context}

            Pergunta:
            {input}
        """);
        
        # --- ETAPA 3: RECUPERANDO A INFORMAÇÃO
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({
            "input": question
        });

        return response['answer']

    except Exception as error:
        print("Ocorreu um erro:", error)