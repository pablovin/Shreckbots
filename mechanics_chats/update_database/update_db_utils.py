import chromadb
import logging
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import (VectorStoreIndex, SimpleDirectoryReader)
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

import logging
from datetime import datetime
import os
from mediawiki import MediaWiki

def read_wiki(wiki_url, save_page_dir, logger):

    mediawiki = MediaWiki(wiki_url)
    all_pages = mediawiki.allpages(results=5000)    
    
    logger.info(f" --- Total pages: {len(all_pages)}")
    
    now = datetime.now()
    for page in all_pages:
        this_page = mediawiki.page(page)
        test_html = this_page.wikitext        
        f = open(os.path.join(save_page_dir, f"{page}.txt"), "w")
        f.write(test_html)
        f.close()
        
    logger.info(f" --- ({(datetime.now()-now).total_seconds()} s) Done!")    


def get_documents(input_dir, logger):

    now = datetime.now()        
    reader = SimpleDirectoryReader(input_dir=input_dir, recursive=True)
    documents = reader.load_data()
    logger.info(f" --- ({(datetime.now()-now).total_seconds()} s) Done! Total documents: {len(documents)}")

    return documents
    

def get_storage_context(save_dir, index_id, logger, persist=False):

    now = datetime.now()    
    logger.info(f' -- Preparing Chroma DB: {save_dir}')    
    chroma_client = chromadb.PersistentClient(path=save_dir)
    chroma_collection = chroma_client.get_or_create_collection(index_id)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    if persist:
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=os.path.join(os.path.join(save_dir, index_id))) 
    else:
        storage_context = StorageContext.from_defaults(vector_store=vector_store) 
    
    logger.info(f' -- ({(datetime.now()-now).total_seconds()} s) Done!')        

    return storage_context

def save_embedded_index(documents, storage_context, embeddings, save_dir, index_id, logger):
    
    embed_model = HuggingFaceEmbedding(model_name=embeddings)

    now = datetime.now()
    logger.info(f" -- Embedding...")
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)
    logger.info(f" --- ({(datetime.now()-now).total_seconds()} s) Done!")

    now = datetime.now()
    logger.info(f" -- Saving in: {save_dir}")
    index.storage_context.persist(os.path.join(save_dir, index_id))
    logger.info(f" --- ({(datetime.now()-now).total_seconds()} s) Done!")

    logger.info(f"Saved documents:{save_dir}")