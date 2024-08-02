from mechanics_chats.update_database.update_db_utils import get_documents, get_storage_context, save_embedded_index, read_wiki
from dotenv import load_dotenv
import os
import argparse

CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
load_dotenv(API_CONFIG_FILE)
STORE_DIRECTORY = os.getenv("STORE_DIRECTORY")


def read_wiki_pages(bot, logger):
        load_dotenv(API_CONFIG_FILE)
        config_file_bot = os.path.join(CONFIG_DIR, f"{bot}.env")
        load_dotenv(config_file_bot)        
        try:
            logger.info(f"Extracting WIKI pages for {bot}")        
            wiki_url = os.getenv(f"WIKI_API_URL_{bot}")                
            save_dir = os.path.join(os.getenv(f"SOURCE_{bot}"), "wiki")
            
            logger.info(f" --- Wiki URL: {wiki_url}")
            logger.info(f" --- Saving Directory: {save_dir}")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            read_wiki(wiki_url, save_dir, logger)
            logger.info(f" --- Update Done!")
        except Exception as e:
            logger.error(e.with_traceback())


def update_embeddings(bot, folder,logger):
    load_dotenv(API_CONFIG_FILE)   
    config_file_bot = os.path.join(CONFIG_DIR, f"{bot}.env")
    load_dotenv(config_file_bot)           
    
    logger.info(f"Embedding Documents for {bot}")
    source_dir = os.path.join(os.getenv(f"SOURCE_{bot}"), folder)
    logger.info(f" --- Reading from: {source_dir}")

    try:
        if len(os.listdir(source_dir)) == 0:
            logger.info(f" --- directory is empty!")
        else:
            #Read and Save Documents
            embedding_model = os.getenv("HUGGING_FACE_EMBEDDING")
            logger.info(f' --- Embedding Model : {embedding_model}')

            save_dir = os.path.join(STORE_DIRECTORY,bot)
            documents = get_documents(source_dir, logger)
            storage_context = get_storage_context(save_dir, bot, logger)
            save_embedded_index(documents, storage_context, embedding_model, save_dir, bot, logger)
            logger.info(f" --- Update Done!")

    except Exception as e:
         logger.error(e.with_traceback())
        




# def update_database_books(input_dir, save_dir, embeddings, index_id):

#     if not os.path.exists(save_dir):
#         os.makedirs(save_dir)

#     #Read and Save Documents
#     documents = get_documents(input_dir)
#     storage_context = get_storage_context(save_dir, index_id)
#     save_embedded_index(documents, storage_context, embeddings, save_dir, index_id)


# if __name__ == "__main__":
#     parser=argparse.ArgumentParser(description="sample argument parser")
#     parser.add_argument("chat")
#     parser.add_argument("source")

#     args=parser.parse_args()

#     if args.chat == "st":
#         suffix = "ELDER"
#     elif args.chat == "dm":
#         suffix = "SAGE"
#     else:
#         print (f"Chat Not recognized! Try st or dm")
#         exit()
    
#     if not args.source in ["book", "wiki", "both"]:
#          print (f"Source Not recognized! Try book, wiki or both")
#          exit()

#     source = args.source
#     if source =="both":
#         source = ["wiki", "book"]
#     else:
#         source = [source]

    # embeddings = os.getenv("HUGGING_FACE_EMBEDDING")
    # index_id = os.getenv(f"INDEX_ID_{suffix}")
    # save_dir = os.getenv(f"STORAGE_DATA_{suffix}")
    # source_dir = os.getenv(f"SOURCE_{suffix}")

    # if "wiki" in source:    
    #      print (f"READING WIKI")          

    #      wiki_url = os.getenv(f"WIKI_API_URL_{suffix}")
    #      save_pages_dir = os.getenv(f"WIKI_API_URL_{suffix}")
    #      read_wiki(wiki_url, os.path.join(source_dir, "wiki"))

    #      update_database_books(os.path.join(source_dir, "wiki"), save_dir, embeddings, index_id)
    # if "book" in source:
    #     print (f"READING BOOKS")          
    #     update_database_books(os.path.join(source_dir, "books"), save_dir, embeddings, index_id)

   

