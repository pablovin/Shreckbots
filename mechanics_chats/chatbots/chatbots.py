from llama_index.core import (Settings, PromptTemplate)
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from mechanics_chats.update_database.update_db_utils import get_storage_context
from llama_index.core import load_index_from_storage
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from dotenv import load_dotenv,dotenv_values
import os




CONFIG_DIR = "config_files"
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
load_dotenv(API_CONFIG_FILE)


STORE_DIRECTORY = os.getenv("STORE_DIRECTORY")


def initialize_llm(logger):

    llm_type = os.getenv("LLM")
    embedding_model = os.getenv("HUGGING_FACE_EMBEDDING")
    
    logger.info('Initialize LLM')
    logger.info(f' -- LLM Type: {llm_type}')
    
    if llm_type == "GPT":        
        gpt_model_name = os.getenv('GPT_MODEL_NAME')
        logger.info(f' -- GPT Model : {gpt_model_name}')
        llm = OpenAI(temperature=0, model=gpt_model_name)
    else:
        llm = Ollama(model=llm_type, request_timeout=int(os.getenv('LLM_REQUEST_TIME_OUT')))

    logger.info(f' -- Embedding Model : {embedding_model}')
    embed_model = HuggingFaceEmbedding(model_name=embedding_model)

    Settings.llm = llm
    Settings.embed_model = embed_model        
    logger.info(f' -- LLM Loaded : {embedding_model}')


def get_index(bot, logger):
    
    print (f"STORE_DIRECTORY:{STORE_DIRECTORY} - bot: {bot}")
    save_dir = os.path.join(STORE_DIRECTORY,bot)
    logger.info(f'Getting stored emmbedings for {bot}')
    logger.info(f' -- Loading from: {save_dir}')
    #Get the storage context    
    storage_context = get_storage_context(save_dir, bot, logger, persist=True, )
        
    #Read the index from the storage context
    logger.info(f' -- Settings embed model: {Settings.embed_model} ')    
    index = load_index_from_storage(storage_context=storage_context, embed_model=Settings.embed_model)

    return index    

def get_chat_engine(bot, index, memory):


    before_context = os.getenv(f"PROMPT_INSTRUCTION_BEFORE_CONTEXT_{bot}") +"\n"
    context = "Here is some context related to the query:\n {context_str} \n"
    after_context = os.getenv(f"PROMPT_INSTRUCTION_AFTER_CONTEXT_{bot}") +"\n"
    question = "Question: {query_str}\n"
    
    template_text = before_context+context+after_context+question

    # template = os.getenv(f"CHAT_TEMPLATE_{bot}")
    
    qa_template = PromptTemplate(template_text)

    original_question = "The original question is as follows: {query_str}\n"
    existing_answer = "We have provided this answer: {existing_answer}\n"
    context_message = "This was the context: {context_msg}\n"
    refine_request = "Using both the new context and your own knowledge, update or repeat the existing answer.\n"
    personality = "Responde concisely as you were " + os.getenv(f"PROMPT_PERSONALITY_{bot}") +"\n"
    
    refine_text = original_question + existing_answer + context_message + refine_request + personality

    refine_template = PromptTemplate(refine_text) 

    response_synthesizer = get_response_synthesizer(
    response_mode=ResponseMode.COMPACT  ,
    text_qa_template=qa_template,
        refine_template=refine_template
    )

    chat_engine = index.as_chat_engine(memory=memory, verbose=False, chat_mode="condense_plus_context", response_synthesizer=response_synthesizer, similarity_top_k=int(os.getenv("TOP_K_RETRIEVAL")), node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.3)])

    return chat_engine


def get_chat_memory(user, bot, logger):

    chat_storage_folder = os.path.join(os.getenv(f"CHAT_STORAGE"), bot)
    if not os.path.exists(chat_storage_folder):
        os.makedirs(chat_storage_folder)

    this_chat_store = os.path.join(chat_storage_folder, f"{user}.json")
    
    if os.path.exists(this_chat_store):    
        chat_store = SimpleChatStore.from_persist_path(
            persist_path=this_chat_store
        )
        logger.info(f' -- Chat History exists: {this_chat_store}')
    else:
        chat_store = SimpleChatStore()
        logger.info(f' -- New Chat History: {this_chat_store}')

    return chat_store, this_chat_store

def chat(input_question, index, user, bot, logger):
    
    logger.info(f'Message to: {bot}')
    logger.info(f' -- [{user}]: {input_question}')

    chat_store, this_chat_store = get_chat_memory(user, bot, logger)

    memory = ChatMemoryBuffer.from_defaults(chat_store_key=user,chat_store=chat_store, token_limit=int(os.getenv("CHAT_BUFFER_LIMIT")))

    query_engine = get_chat_engine(bot, index, memory)

    response = query_engine.chat(input_question)   
        
    chat_store.persist(persist_path=this_chat_store)

    return response.response

def chat_cmd(index, user, bot, logger):
    
    chat_store, this_chat_store = get_chat_memory(user, bot, logger)

    memory = ChatMemoryBuffer.from_defaults(chat_store_key=user,chat_store=chat_store, token_limit=int(os.getenv("CHAT_BUFFER_LIMIT")))

    query_engine = get_chat_engine(bot, index, memory)

    while True:
        input_question = input("Enter your question (or 'exit' to quit): ")
        if input_question.lower() == 'exit':
            break

        response = query_engine.chat(input_question)
        print(f"{bot} - {response}")
        chat_store.persist(persist_path=this_chat_store)


