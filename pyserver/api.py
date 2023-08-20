from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from util.gradio import queryGLMResult
from util.handleEmbeding import queryFaiss, getEmbeding, saveFaiss
from util.pdf2txt import change_pdf_to_txt
from util.qaTemplate import getQuestionWithContext
from pydantic import BaseModel
import uvicorn
import json
import shutil
from typing import Optional

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class QueryObj(BaseModel):
    url: str
    name: str
    passwd: str
    content: str
    knowledge: Optional[str]
    
@app.post("/api/v1/glm")
async def getGLM(query: QueryObj):
    print(query)
    if(query.content):
        try:
            content_json = json.loads(query.content)
            content_text = ''
            for v in content_json:
                if v['type'] == "system":
                    content_text = content_text + '\n' + v['data']['content']
                if v['type'] == "human":
                    content_text = content_text + '\n' + v['data']['content']
                if v['type'] == "ai":
                    action = json.loads(v['data']['content'])
                    content_text = content_text + '\nuse ' + action['action'] + ' tool, the intermediate answer is as follows:' # + action['action_input']
            print('content_text:')
            print(content_text)
        except ValueError:
            content_text = query.content
            print('content_text', content_text)
        if(query.knowledge):
            fileName = query.knowledge  #'test.txt'
            corpus_embeddings, corpus_sentences = getEmbeding(fileName)
            saveFaiss(fileName, corpus_embeddings)
            similar = queryFaiss(fileName, content_text, corpus_embeddings, corpus_sentences)
            context = '\n'.join(similar)
            prompt = getQuestionWithContext(context, content_text)
            print('---prompt----')
            print(prompt)
            return  queryGLMResult(prompt)
        else:
            return  queryGLMResult(content_text)
    else:
        return 'error'

# pip install python-multipart
@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"upload/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # 转换pdf文件
    if file.filename.split('.')[1] == 'pdf':
        change_pdf_to_txt(file_path, "embededFile")
    elif file.filename.split('.')[1] == 'txt':
        destination_file = f"embededFile/{file.filename}"
        # Copy the file
        shutil.copyfile(file_path, destination_file)
    
    return {"filename": file.filename}

uvicorn.run(app, host="127.0.0.1", port=3006)