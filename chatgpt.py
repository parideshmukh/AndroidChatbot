from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, request, render_template, session 
from flask import jsonify
from werkzeug.utils import secure_filename
import PyPDF2
import re
import os
import base64
import speech_recognition as sr
import openai
#from gpt_index import SimpleDirectoryReader, GPTListIndex, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext,StorageContext, load_index_from_storage
from langchain.chat_models import ChatOpenAI
import sys
import speech_recognition as sr
import cv2
from flask_restful import Api, Resource
from shutil import copyfile
app = Flask(__name__)



app.secret_key = '\x96O\xae\x93\x829\x8f\xda\xfa>}ZV!\xba\x8f\xc4qV\xb2Xl\xda\x0f'
file_path = ""
#os.environ["OPENAI_API_KEY"] = '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'
#openai = "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" 
api_key = "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"
os.environ["OPENAI_API_KEY"] = api_key
ALLOWED_EXTENSIONS = {'pdf', 'txt'} 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('chatbot.html')
def construct_index(directory_path):
    print("Inside construct_index. Directory path:", directory_path)
    max_input_size = 40960
    num_outputs = 5120
    max_chunk_overlap = 200
    chunk_size_limit = 6000
    # prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
    # llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=num_outputs))
    # rebuild storage context
    # storage_context = StorageContext.from_defaults(persist_dir='./storage')
    # load index
    # index = load_index_from_storage(storage_context)
    documents = SimpleDirectoryReader(directory_path).load_data()
    index = GPTVectorStoreIndex.from_documents(documents)
    print(index)
    index.storage_context.persist()
    print("index file createdSSS")
    return index
def upload():
    global file_path
    try:
        uploaded_file_path = "C:/Users/hande/OneDrive/Documents/Major_Shell_Projects-LNG_Canada.pdf"

        if os.path.exists(uploaded_file_path) and allowed_file(uploaded_file_path):
            filename = secure_filename(os.path.basename(uploaded_file_path))
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            static_folder_path = os.path.join(current_script_dir, "vectorIndex")
            os.makedirs(static_folder_path, exist_ok=True)
            file_path = os.path.join(static_folder_path, filename)
            copyfile(uploaded_file_path, file_path)

            print("File copied to:", file_path)

            if filename.endswith('.pdf'):
                print("Processing PDF file...")
                with open(file_path, 'rb') as pdf_file:
                    pdf_data = base64.b64encode(pdf_file.read()).decode('utf-8')
                    folder_path = os.path.dirname(file_path)
                    index = construct_index(folder_path)
                    print("PDF file processed successfully.")

            elif filename.endswith('.txt'):
                print("Processing TXT file...")
                with open(file_path, 'r') as file:
                    all_text = file.read()
                folder_path = os.path.dirname(file_path)
                index = construct_index(folder_path)
                print("TXT file processed successfully.")
        else:
            return 'Invalid file type or file does not exist.'

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/local_chat', methods=['POST'])
def local_chat():
    if 'input_text' in request.json:
        input_text = request.json.get('input_text')
        #index = GPTSimpleVectorIndex.load_from_disk('index.json')
        storage_context = StorageContext.from_defaults(persist_dir='./storage')
        index = load_index_from_storage(storage_context)
        # index = GPTVectorStoreIndex.from_documents('index.json')
        query_engine = index.as_query_engine()
        input_text_with_role_and_context = f"{input_text}."
        print("input text, role, and context", input_text_with_role_and_context)
        # response = query_engine.query(input_text_with_role_and_context, response_mode="compact")
        response = query_engine.query(input_text_with_role_and_context)
        #response = {"response": "When refuelling at a self-service stand, it is important to take the necessary safety precautions, regardless of age, number of vehicles in the household, or household income. Make sure to turn off the engine and any other electrical equipment before refuelling. Do not smoke or use any open flames near the refuelling area. Wear protective clothing, such as gloves and safety glasses, to protect yourself from any potential spills. Make sure to keep any children away from the refuelling area. Additionally, be aware of any potential hazards, such as fuel spills, and take the necessary steps to clean them up. It is also important to consider the preferences of those who are likely to purchase a two-wheeler in the next 5 years, as indicated by the survey results. Factors such as style, environmental performance, safety, reliability, comfort, cargo-carrying capacity, and replacement part availability are all important considerations when refuelling at a self-service stand."}
    else:
        return jsonify({'error': 'Invalid request. Please provide either "input_text" or "speech_transcript".'})
    #if response and response["response"] is not None:
        #formatted_response = response["response"].replace('\n', '<br>')
        #print("final response", formatted_response)
        #return jsonify(formatted_response)
    if response and response.response is not None:
        formatted_response = response.response.replace('\n', '<br>')
        print("final response", formatted_response)
        return jsonify(formatted_response)
    #else:
        #return jsonify(response["response"])
    else:
        return jsonify(response.response)

if __name__ == '__main__':
    app.run(debug=True)

    
