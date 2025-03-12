from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from prompts.SBtoEOPrompt import prompt_template, fields_to_extract
import asyncio
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "llama3"
EMBEDDING_MODEL = "nomic-embed-text"

llm = ChatOllama(model=MODEL_NAME, temperature=0.1)

def load_md(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        logger.info("Markdown file loaded.")
        return content

def chunk_md(md_content: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=500, separators=["\n\n", "\n", " "])
    chunks = text_splitter.split_text(md_content)
    documents = text_splitter.create_documents(chunks)
    logger.info("Markdown file chunked.")
    return documents

async def create_vector_db(chunks):
    try:
        vector_db = await asyncio.to_thread(
            FAISS.from_documents,
            documents=chunks,
            embedding=OllamaEmbeddings(model=EMBEDDING_MODEL),
        )
        logger.info("Vector database created.")
        return vector_db
    except Exception as e:
        logger.error(f"Error creating vector database: {e}")

async def run_preprocessing(file_path):
    try:
        md = load_md(file_path=file_path)
        chunks = chunk_md(md_content=md)
        vector_db = await create_vector_db(chunks)
        return vector_db
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")

async def extract_field(field, vector_db, llm):
    try:
        relevant_chunks = await asyncio.to_thread(
            vector_db.similarity_search, query=field, k=5
        )
        relevant_text = ""
        for chunk in relevant_chunks:
            relevant_text += chunk.page_content + "\n\n"
        prompt = prompt_template.format(text=relevant_text, fields=field)
        response = await llm.ainvoke(prompt)
        content = response.content
        print(content)
        dict_pattern = re.compile(r"\{.*\}", re.DOTALL)
        match = dict_pattern.search(content)
        if match:
            extracted_dict = match.group(0)
            logger.info(f"Extracted field: {field} -> {extracted_dict}")
            return field, extracted_dict
        else:
            logger.warning(f"No dictionary found in response for field: {field}")
            return field, None
    except Exception as e:
        logger.error(f"Error extracting field {field}: {e}")

async def extract_information(vector_db, fields_to_extract, llm):
    tasks = [extract_field(field, vector_db, llm) for field in fields_to_extract]
    results = await asyncio.gather(*tasks)
    extracted_info = {field: response for field, response in results}
    return extracted_info

async def main():
    try:
        vector_db = await run_preprocessing(file_path="filee.md")
        logger.info("Vector database preprocessing completed.")
        extracted_info = await extract_information(vector_db=vector_db, fields_to_extract=fields_to_extract, llm=llm)
        logger.info("Information extraction completed.")
        print(extracted_info)
    except Exception as e:
        logger.error(f"Error in main function: {e}")

asyncio.run(main())


