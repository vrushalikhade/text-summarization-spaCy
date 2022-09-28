import os
from string import punctuation

import spacy
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from spacy.lang.en.stop_words import STOP_WORDS

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

INPUT_FILE = "input_file.txt"



@app.get("/", response_class=HTMLResponse)
async def root(request: Request,):
    return templates.TemplateResponse("item.html", {"request": request})

@app.get("/summary")
async def summary(request: Request,):
    try:
        with open(INPUT_FILE, "r", encoding="utf8") as file:
            text =file.read().splitlines()
            text = ' '.join(text)
    except:
        return {"message": "There was an error summarizing the file"}
    finally:
        if os.path.isfile(INPUT_FILE):
            os.remove(INPUT_FILE)
            file.close()
        
    
    stopwords = list(STOP_WORDS)
        
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.text for token in doc]
        
    word_frequencies = {}
        
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
                        
                        
    max_frequency = max(word_frequencies.values())
        
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency
        
    sentence_tokens = [sent for sent in doc.sents]
        
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
                        
    from heapq import nlargest
    select_length = int(len(sentence_tokens)*0.3)
        
    summary = nlargest(select_length, sentence_scores, key = sentence_scores.get)

    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
    return templates.TemplateResponse("summary.html", {"request":request, "summary": summary})

@app.post("/upload")
def upload(request:Request, file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(INPUT_FILE, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    return templates.TemplateResponse("success.html", {"request": request})


# with open("suresh raina.txt", "r") as file:
#     data = file.read().replace("\n", "")
