from mediawiki import MediaWiki
import openai
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat
import os
import json
from dotenv import load_dotenv
import os
import shutil
# from utils.config_utils import load_bot_config, load_shreckbot_config
import traceback

import logging
import re


CONFIG_DIR = "config_files"

def load_shreckbot_config():
    
    API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api.env")
    load_dotenv(API_CONFIG_FILE)
    
def load_bot_config(bot):    
    config_file_bot = os.path.join(CONFIG_DIR, f"{bot}.env")
    load_dotenv(config_file_bot)  


def get_fields(template_html):

    # Regular expression pattern to match {{{field_name}}}
    pattern = r'\{\{\{([^\|}]+)[\|}]*\}\}\}'

    # Find all matches in the content
    fields = re.findall(pattern, template_html)

    # Remove duplicates by converting the list to a set, then back to a list (if needed)
    unique_fields = sorted(set(fields))

    return list(unique_fields)


def get_entity_templates_dic(entities):
    # Initialize the dictionary
    parsed_dict = {}

    # Regex to match key-value pairs
    pattern = re.compile(r'(\w+)\[(.*?)\]')

    # Find all matches of the pattern
    matches = pattern.findall(entities)

    # Populate the dictionary with matched key-value pairs
    for match in matches:
        key = match[0]
        values = match[1].split(", ")
        parsed_dict[key] = values

    # Find remaining keys without brackets
    remaining_keys_str = re.sub(pattern, '', entities).strip()
    remaining_keys = [key.strip() for key in remaining_keys_str.split(',') if key.strip()]

    for key in remaining_keys:
        parsed_dict[key] = []

    return parsed_dict



def get_template(mediawiki, found_entities , all_entities_templates):

    this_entity_fields = {}
    for entity in found_entities:

        if entity in all_entities_templates:
            # logger.warning(f" ---- Entity: {entity}")
            templates = all_entities_templates[entity]
            # print (f"Templates: {all_entities_templates[entity]}")

            for template in templates:
                print(f" ------ Template: {template}")
                params = {
                    'action': 'query',
                    'prop': 'revisions',
                    'titles': template,
                    'rvslots': '*',  # Required for newer MediaWiki versions with multi-content revisions (MCR)
                    'rvprop': 'content',
                    'format': 'json'
                }

                request = mediawiki.wiki_request(params=params)["query"]["pages"]
                
                page_key = list(request.keys())
                
                template_html = request[page_key[0]]["revisions"][0]["slots"]["main"]["*"]
                page_key = template_html
                tempalte_fields = get_fields(template_html)

                # if len(tempalte_fields) > 0:
                if not entity in this_entity_fields:                        
                    this_entity_fields[entity] = []

                this_entity_fields[entity].append([template, tempalte_fields])
                # logger.warning(f" -------- Fields: {tempalte_fields}")


    return this_entity_fields    

    

def get_all_categories(mediawiki, logger):
     # Parameters for the API request
    params = {
        'action': 'query',
        'list': 'allcategories',
        'aclimit': 'max',  # Maximum number of categories per request
        'format': 'json'
    }
    request = mediawiki.wiki_request(params=params)["query"]["allcategories"]
    all_categories = []
    for category in request:
        for key in category:
            all_categories.append(category[key])
    # logger.warning(f" ---- All Categories: {all_categories}")
    return all_categories

def get_pages_from_categories(mediawiki, entity,categories, logger):
    pages = set()
    for category in categories:
        try:
            category_pages = mediawiki.categorymembers(category, results=5000)            
            pages.update(category_pages[0])
        except Exception as e:
            logger.error(f"ERROR: {traceback.format_exc()}")   

    pages = list(pages)   
    # logger.warning(f" ---- Pages for entity {entity}: {pages}")          
    return pages

def get_all_existing_pages(mediawiki, entities_list, logger):
    all_categories = get_all_categories(mediawiki, logger)    
    
    entities = {}
    for entity in list(entities_list.keys()):        
        entity_categories = [category for category in all_categories if entity in category] 
        entities[entity] =  get_pages_from_categories(mediawiki, entity, entity_categories, logger)
    
    return entities


def extract_entities(text, entities, model):

    prompt = f"""    
    You are my assistant to mantain a wiki page. You will help me to identify new pages that I can create in my wiki page, based on a summary of 
    descriptive information that I will give you.
    You will also receive a list of important entities to be extracted from the text.
    
    For that, you will:
    
    1) Extract the list of entities from the given text.    
    3) For all the extracted entities, List the pages that need to be created.
    
    """    
        
    prompt+=f"These are the entities that you need to extract from the text: {list(entities.keys())}\n."
    
    
    prompt +=f"""
        
    This is the text:
    {text}\n"""

    prompt+="""       
    Provide the output in the following JSON format:
    {{
    """
    for count, entity in enumerate(entities.keys()):    
       prompt+= f""" "{entity}":          
            ["new_{entity}1", "new_{entity}2", ...]
        """       
       if count < len(entities) -1:
           prompt+=",\n"
       
    prompt +="""}}"""

    
    client = OpenAI()
    
    messages=[
    {"role": "system", "content": prompt},
    {"role": "user", "content": text}]
    
    response = client.chat.completions.create(
        model=model,        
        messages=messages,        
        temperature=0,
        response_format=ResponseFormat(type="json_object")
    )
    
    entities = response.choices[0].message.content.replace("json", "").replace("```","").replace("```","")
    
    return parse_entities(entities)



def fill_template_fields(text, fields, model):

    prompt = f"""    
    You are my assistant to mantain a wiki page. You will help me to fill the fields of a wiki template.
    You must use only the information I am giving you to fill these fields. No other source.              
    """    
        
    prompt+=f"These are the fields you need to fill: {fields}. If you do not know the information, then add unknown. If the entity is a character, it will always be an NPC.\n"
    
    
    prompt +=f"""
        
    This is the text:
    {text}\n"""

    prompt+="""       
    Provide the output in the following JSON format:
    {{
    """
    for count, field in enumerate(fields):    
       prompt+= f""" "{field}": field value
        """      
       if count < len(fields) -1:
           prompt+=",\n"
       
    prompt +="""}}"""

    
    client = OpenAI()
    
    messages=[
    {"role": "system", "content": prompt}]
    
    response = client.chat.completions.create(
        model=model,        
        messages=messages,        
        temperature=0,
        response_format=ResponseFormat(type="json_object")
    )
    
    entities = response.choices[0].message.content.replace("json", "").replace("```","").replace("```","")
    
    return parse_entities(entities)



def get_template_text(text, template_name, fields, model):
    
    title = template_name.split(":")[1]            

    if len(fields) == 0:
            
            return f"{{{{{title}}}}}\n"
    else:
        fields_values = fill_template_fields (text, fields, model) 
        key_value_pairs = '|'.join([f"{key}={value}\n" for key, value in fields_values.items()]) 
        result_string=""" {{"""
        result_string += f"{title}|{key_value_pairs}"
        result_string+="""}}\n"""
        return result_string




def add_template_to_text(pages_text, pages_template, model):

    for entity in pages_text:

        # logger.warning(f" ---- Entity: {entity}")  
        if entity in pages_template:
                templates_this_entity = pages_template[entity]

                for page in pages_text[entity]:
                    # logger.warning(f" ------ Page: {page}")                      
                    for template in templates_this_entity:
                        template_name = template[0]
                        fields = template[1]                                                
                        # logger.warning(f" -------- Template Name: {template_name}")                         
                        # logger.warning(f" -------- Template Fields: {fields}")                                                 
                        page_text = pages_text[entity][page]["text"]                                                                                        
                        template_text = get_template_text(page_text, template_name, fields, model)
                        # logger.warning(f" -------- Template {template_name}: {template_text}")                        
                        pages_text[entity][page]["text"]=template_text + pages_text[entity][page]["text"]


    return pages_text

    # prompt = f"""    
    # You are my assistant to mantain a wiki page. You will help me to create a new page for my wiki.
    # The page must contain a lenghty and detailed description of a certain entity, written in a proper and entertainment style.  
    # You must take all the information to create the pages only from the text I am giving you. No other source.              
    # """    
    
    # # prompt+=f"These are the entities that you need to extract from the text: {list(entities.keys())}\n These pages already existing on my wiki:\n"
    # # prompt+=f"These are the pages we need to create:\n"
    # # for entity in entities:
    # #     if len(entities[entity])>0:
    # #         prompt+=f"{entity}: {entities[entity]}\n"

            
    # prompt +=f"""
        
    # This is the text:
    # {text}\n"""

    # prompt+="""       
    # Provide the output in the following JSON format, for the template fields that do not exist in the text write "unknown":
    # {
    # """
    # for count, entity in enumerate(entities):         
    #     if len(entities[entity])>0:
    #         prompt+= f""" "{entity}": """
    #         prompt+= """{"""
    #         for count_page, page in enumerate(entities[entity]):
    #             prompt+= f""" "{page}":  """
    #             prompt+= """{"""
    #             prompt+= """ "text":"[text for this wiki page]"""                                     
    #             prompt+= """}"""
    #             if count_page < len(entities[entity]) -1:
    #                 prompt+=","
    #         prompt+= """}"""
    #         if count < len(entities) -1:
    #             prompt+=",\n"
    
   
    # prompt+= """}"""
    
    # client = OpenAI()
    
    # messages=[
    # {"role": "system", "content": prompt},
    # {"role": "user", "content": text}]
    
    # response = client.chat.completions.create(
    #     model=model,        
    #     messages=messages,        
    #     temperature=0,
    #     response_format=ResponseFormat(type="json_object")
    # )
    
    # entities = response.choices[0].message.content.replace("json", "").replace("```","").replace("```","")

    # return parse_entities(entities)


def create_summary_from_entity(text, entities, page_type, model):

    prompt = f"""    
    You are my assistant to mantain a wiki page. You will help me to create a new page for my wiki.
    The page must contain a lenghty and detailed description of a certain entity, written in a proper and entertainment style.  
    You must take all the information to create the pages only from the text I am giving you. No other source.              
    """    
    
    # prompt+=f"These are the entities that you need to extract from the text: {list(entities.keys())}\n These pages already existing on my wiki:\n"
    # prompt+=f"These are the pages we need to create:\n"
    # for entity in entities:
    #     if len(entities[entity])>0:
    #         prompt+=f"{entity}: {entities[entity]}\n"

            
    prompt +=f"""
        
    This is the text:
    {text}\n"""

    prompt+="""       
    Provide the output in the following JSON format, for the template fields that do not exist in the text write "unknown":
    {
    """
    for count, entity in enumerate(entities):         
        if len(entities[entity])>0:
            prompt+= f""" "{entity}": """
            prompt+= """{"""
            for count_page, page in enumerate(entities[entity]):
                prompt+= f""" "{page}":  """
                prompt+= """{"""
                prompt+= """ "text":"[text for this wiki page],"""
                prompt+= f""" "type":"{page_type}"""                                         
                prompt+= """}"""
                if count_page < len(entities[entity]) -1:
                    prompt+=","
            prompt+= """}"""
            if count < len(entities) -1:
                prompt+=",\n"
    
   
    prompt+= """}"""
    
    client = OpenAI()
    
    messages=[
    {"role": "system", "content": prompt}]
    
    response = client.chat.completions.create(
        model=model,        
        messages=messages,        
        temperature=0,
        response_format=ResponseFormat(type="json_object")
    )
    
    entities = response.choices[0].message.content.replace("json", "").replace("```","").replace("```","")

    return parse_entities(entities)

def create_session_existing_page(mediawiki, page, summary, model):
    try:
        page_text = mediawiki.page(title=page).wikitext

        prompt = f"""    
        You are my assistant to mantain a wiki page. You will help me to update existing pages for my wiki.
        I will give you the text of the original page and the summary information that is a candidate for the page update.
        You have to tell me if the summary is redundant based on the original page text.

        If the summary contains new information, write a new wiki session describing only the new information, in away that complements the original page text.        
        
        """    
        
        # prompt+=f"These are the entities that you need to extract from the text: {list(entities.keys())}\n These pages already existing on my wiki:\n"
        # prompt+=f"These are the pages we need to create:\n"
        # for entity in entities:
        #     if len(entities[entity])>0:
        #         prompt+=f"{entity}: {entities[entity]}\n"

                
        prompt +=f"""
            
        This is the original page text:
        {page_text}\n

        This is the summary candidate:
        {summary}\n"""

        prompt+="""       
        Provide the output in the following JSON format:
        {
        new_information: [ True or False],
        session_title: "Title of the new session",
        session_text: "Text of the new session"
        }
        """    
        
        client = OpenAI()
        
        messages=[
        {"role": "system", "content": prompt}   
        ]
        
        response = client.chat.completions.create(
            model=model,        
            messages=messages,        
            temperature=0,
            response_format=ResponseFormat(type="json_object")
        )
        
        entities = response.choices[0].message.content.replace("json", "").replace("```","").replace("```","")
    except:
        result = {}
        result["new_information"] = False
        return result
    
    return parse_entities(entities)


def categorize_entities(parsed_data, Entities):
    new_items = {}
    existing_items = {}

    for category in parsed_data.keys():
        new_items[category] = []
        existing_items[category] = []
        
        json_entities = set(parsed_data[category])
        existing_entities = set(Entities.get(category, []))
                
        for new in list(json_entities):
            new_entity = True
            original = ""
            for existing in list(existing_entities):
                # print (f"{new.title()} in {existing.title()} = {new.title() in existing.title()}")
                if new.title() in existing.title():
                    new_entity = False
                    original = existing.title()
                    break

            if new_entity:
                new_items[category].append(new)
            else:
                existing_items[category].append(original)                    

    return new_items, existing_items


def parse_entities(entities_text):
    entities = json.loads(entities_text)
    return entities

def clear_old_files_wiki_pages(bot):
    save_folder = os.path.join(os.getenv("WIKI_PAGES_FOLDER"),bot)
    if os.path.exists(save_folder):
        shutil.rmtree(save_folder)

    os.makedirs(os.path.join(save_folder,"NewPage"))
    os.makedirs(os.path.join(save_folder,"UpdatePage"))


def create_text_files(entities_with_content, bot, logger):

    save_folder = os.path.join(os.getenv("WIKI_PAGES_FOLDER"),bot)
    # Create a directory to save the text files             

    # clear_old_files_wiki_pages(bot)
    already_cleaned = False
    # Iterate over each key-value pair in the dictionary
    for entity, pages_list in entities_with_content.items():
        # Create the filename using the key
        # logger.warning(f" ---- Entity: {entity}")  
        for page, page_text in pages_list.items():
            page_type = page_text['type']  
            save_directory = os.path.join(save_folder, page_type)   

            if not already_cleaned:
                if os.path.exists(save_directory):
                    shutil.rmtree(save_directory)
                os.makedirs(save_directory)
                already_cleaned = True

            filename = os.path.join(save_directory,f'{page}.txt')
            # # Write the content to the file
            with open(filename, 'w') as txt_file:
                 txt_file.write(page_text['text'])

    logger.warning(f" ------ All pages created at {save_folder}/")         

   
def create_new_sessions(mediawiki, updatable_pages_sumaries, model, logger):

    updatable_entities = {}
    for entity in updatable_pages_sumaries:
        if entity not in updatable_entities:
            updatable_entities[entity] = {}

        
        for page in updatable_pages_sumaries[entity]:
            page_summary = updatable_pages_sumaries[entity][page]["text"]    

            result_page_session = create_session_existing_page(mediawiki, page, page_summary, model)                         
            
            

            if result_page_session["new_information"]:                
                
                summary = f"""=== {result_page_session["session_title"]} === \n\n {result_page_session["session_text"]}"""
                logger.warning(f" ------ New Session Proposed for {page}")
    
                updatable_entities[entity][page] = {}
                updatable_entities[entity][page]["text"] = summary     
                updatable_entities[entity][page]["type"] = "UpdatePage"     
                

        # updatable_entities[entity][page] = updatable_page                
    
    return updatable_entities
                                                                                                                 
    

def get_entities(bot, text, logger):

    load_shreckbot_config()
    load_bot_config(bot)

    openai.api_key =  os.getenv("OPENAI_API_KEY")

    model = os.getenv("GPT_MODEL_NAME")
    wiki_url = os.getenv(f"WIKI_API_URL_{bot}")
    
    this_bot_entities = get_entity_templates_dic(os.getenv(f"WIKI_UPDATE_ELEMENTS_{bot}"))    
    mediawiki = MediaWiki(url=wiki_url)
   
    logger.warning(f"Parsing given text for {bot} wiki")        
    logger.warning(f" -- Wiki: {wiki_url}")        
    logger.warning(f" -- Looking for these entities (and templates) in the text:") 
    for entity in  this_bot_entities:
        logger.warning(f" ---- Entity: {entity}  Templates: {this_bot_entities[entity]}") 

    logger.warning(f" -- Reading all wiki pages...")            

    entities = get_all_existing_pages(mediawiki, this_bot_entities, logger)

    logger.warning(f" -- Extracting entities from given text...")
    llm_response = extract_entities(text, entities, model)
    logger.warning(f" -- Deciding which pages are new and which will be updated...")
    new_entities, updatable_entities = categorize_entities(llm_response, entities)  

    all_pages = []
    all_updatable_pages = {}
    # logger.warning(f" -- I will create pages for these entities")
    for entity in updatable_entities.keys():
        #  logger.warning(f"  ---- {entity}: {new_entities[entity]}")
         for page in updatable_entities[entity]:
            if not entity in all_updatable_pages:                
                all_updatable_pages[entity] = []              

            if not page in all_pages:
                all_updatable_pages[entity].append(page)

            all_pages.append(page)

    print (all_updatable_pages)
    logger.warning(f" -- I will update these existing pages:")
    for entity in all_updatable_pages:
         logger.warning(f"  ---- {entity}: {all_updatable_pages[entity]}")

    logger.warning(f" --- Creating new sessions to update the pages...")  
    updatable_pages_sumaries = create_summary_from_entity(text, all_updatable_pages, "UpdatePage", model)       

    logger.warning(f" --- Deciding if the updates are worth it...")  
    updatable_pages = create_new_sessions(mediawiki, updatable_pages_sumaries, model, logger)  
    
    logger.warning(f" --- Creating .txt files for the update pages...")  
    create_text_files(updatable_pages, bot, logger)        
    

     
    all_new_pages = {}
    # logger.warning(f" -- I will create pages for these entities")
    for entity in new_entities.keys():
        #  logger.warning(f"  ---- {entity}: {new_entities[entity]}")
         for page in new_entities[entity]:
            if not entity in all_new_pages:
                all_new_pages[entity] = []

            if not page in all_pages:
                all_new_pages[entity].append(page)
                
            all_pages.append(page)
                                            
    logger.warning(f" -- I will create these new pages:")
    for entity in all_new_pages:
         logger.warning(f"  ---- {entity}: {all_new_pages[entity]}")

    logger.warning(f" --- Creating content for the new pages...")  
    new_pages = create_summary_from_entity(text, all_new_pages, "NewPage", model)        

    logger.warning(f" --- Adding templates to new pages...")  
    template_fields = get_template(mediawiki, all_new_pages , this_bot_entities)    
    new_pages_with_template = add_template_to_text(new_pages,template_fields,model)    

    logger.warning(f" --- Creating new pages .txt files...")
    create_text_files(new_pages_with_template, bot, logger)    


    logger.info(f" --- Update Done!")
    

def main():

    bot = "Elder"    
    file_path = r"example.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        text_input = file.read()    

    # print (f"text_input: {text_input}")
    get_entities(bot, text_input, logging)

if __name__ == "__main__":
    main() 