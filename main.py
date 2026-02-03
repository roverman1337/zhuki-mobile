from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database as db

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

class ActionRequest(BaseModel):
    tg_id: int
    username: str = "Unknown"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/init")
async def init_player(data: ActionRequest, session: Session = Depends(get_db)):
    player = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    if not player:
        player = db.Player(tg_id=data.tg_id, username=data.username)
        session.add(player)
        session.commit()
        session.refresh(player)
    return get_state(player)

@app.post("/api/feed")
async def feed_beetle(data: ActionRequest, session: Session = Depends(get_db)):
    player = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    if player.money < 15: return {"status": "error", "message": "Мало денег!"}
    player.money -= 15
    player.hunger = max(0, player.hunger - 25)
    session.commit()
    return {"status": "success", "message": "Ням!", "state": get_state(player)}

@app.post("/api/work")
async def work_beetle(data: ActionRequest, session: Session = Depends(get_db)):
    player = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    player.money += 20
    player.hunger = min(100, player.hunger + 15)
    session.commit()
    return {"status": "success", "message": "Работа сделана!", "state": get_state(player)}

def get_state(p):
    return {"name": p.beetle_name, "money": p.money, "hunger": int(p.hunger), "strength": round(p.strength, 1), "level": p.level}