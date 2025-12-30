from fastapi import FastAPI
import json
app=FastAPI()

@app.get("/")
def root():
    return "Url Shortner Says hi"