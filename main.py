from fastapi import FastAPI
from pydantic import BaseModel,AnyUrl,Field
from typing import Annotated
import hashlib
import json
import os
from pydantic import BaseModel, field_validator, HttpUrl
from urllib.parse import urlparse
app=FastAPI()

#middlewareSTARTS
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://the-url-shortner-frontend.onrender.com","*"],  # Update to your frontend URL after deploy, e.g., ["https://yourfrontend.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#middlewareENDS



#URL SHORTNER FUNCTION
def shorten(longUrl):
    # longUrl=str(longUrlModel.url)
    hash_digest = hashlib.md5(longUrl.encode()).hexdigest()
    seven_char = hash_digest[:7]
    return seven_char

#ShortURL maker
def urlMaker(hostname,shorturl):
    return f"{hostname}/{shorturl}"

#Store into DB
def store(longUrl: str, shortUrl: str) -> bool:
    """
    Store the provided shortUrl -> longUrl mapping.
    Args:
        longUrl: Full destination URL
        shortUrl: Generated short URL
    Returns:
        True if stored successfully
    """
    # Load existing data safely
    if not os.path.exists("urls.json"):
        data = {}
    else:
        try:
            with open("urls.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
    # Check duplicate longUrl → reuse existing short if found
    for existing_short, stored_long in data.items():
        if stored_long == longUrl:
            print(f"Duplicate long URL '{longUrl}' already mapped to '{existing_short}'")
            return existing_short  # Don't overwrite with new short
    
    # Store new unique mapping
    if shortUrl in data:
        print(f"Short code '{shortUrl}' already exists!")
        return False
    
    data[shortUrl] = longUrl
    with open("urls.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    print(f"Stored: {shortUrl} → {longUrl}")
    return True

#url Finder

def findUrl(shortUrl:str):
     # Load existing data safely
    if not os.path.exists("urls.json"):
        data = {}
    else:
        try:
            with open("urls.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
    # Check duplicate longUrl → reuse existing short if found
    for short, long in data.items():
        if short == shortUrl:
            print(f"long URL '{long}' found mapped to '{short}'")
            return long  # Don't overwrite with new short
    


#PYDANTIC MODEL FOR URL VALIDATION
class url_val(BaseModel):
    url: str = Field(..., description="Long URL to shorten")
    
    @field_validator('url')
    @classmethod
    def complete_url(cls, v: str) -> str:
        """Auto-complete URL before validation"""
        if v.startswith(('http://', 'https://')):
            return v
        if not v.startswith('www.'):
            v = 'www.' + v
        completed = 'https://' + v
        # Validate after completion
        parsed = urlparse(completed)
        if not parsed.netloc:
            raise ValueError("Invalid URL - needs domain like 'google.com'")
        return HttpUrl(completed)  # Validates + returns URL object
    
    def url_str(self) -> str:
        """Helper to get string"""
        return str(self.url)


@app.get("/")
def root():
    return "Url Shortner Says hi"

@app.get("/about")
def root():
    return "This Is An FastAPI project focussing in url shortening and redirection "


@app.post("/shorten")
def shortner(longUrl: url_val):
    long_str = longUrl.url_str()  # Now always valid full URL
    hostname = "https://the-url-shortner.onrender.com"
    short_code = shorten(long_str)
    full_short = f"{hostname}/{short_code}"
    if store(long_str, short_code):
        return {"short_url": full_short, "original": long_str}
    return JSONResponse(status_code=400, content={"error": "Duplicate/collision"})


# Fix /longen as GET /{code} redirect (path param, not POST)
@app.get("/{short_code}")
def redirect_to_long(short_code: str):
    long_url = findUrl(short_code)
    print(long_url)
    if long_url:
        return RedirectResponse(url=long_url)
    return JSONResponse(status_code=404, content={"error": "Not found"})




































# @app.post("/shorten")
# def shortner(longUrl:url_val):
#     longUrl=str(longUrl.url) #pydantic model to str conversion
#     hostname="https://www.rockycoc.com"#hostname for the url shortner
#     shortUrl = urlMaker(hostname,shorten(longUrl))
#     store(longUrl,shortUrl)

# @app.post("/longen")
# def longner(shortUrl:url_val):
#     shortUrl=str(shortUrl.url) #pydantic model to str conversion
#     longUrl=findUrl(shortUrl)
#     print(longUrl)