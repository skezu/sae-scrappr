from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scrappr import TwitterScraper  # Assurez-vous que c'est la fonction correcte à appeler dans scrappr.py

app = FastAPI()

class UserInfo(BaseModel):
    email: str
    username: str
    password: str

@app.post("/scrappr")
async def scrape(user_info: UserInfo):
    try:
        # Appeler la fonction de scraping avec les paramètres fournis
        result = TwitterScraper(user_info.email, user_info.username, user_info.password).initialisation()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
