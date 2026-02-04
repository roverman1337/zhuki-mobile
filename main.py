from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from pydantic import BaseModel
import random
import database as db

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Зависимость для получения сессии БД
def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Модель данных, приходящих от клиента
class ActionRequest(BaseModel):
    tg_id: int
    username: str = "Unknown"

# --- Вспомогательная функция для отправки состояния ---
def get_state(p):
    return {
        "name": p.beetle_name,
        "money": p.money,
        "hunger": int(p.hunger),
        "strength": round(p.strength, 1),
        "level": p.level
    }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Отдает страницу HTML"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/init")
async def init_player(data: ActionRequest, session: Session = Depends(get_db)):
    """Вход в игру или регистрация"""
    player = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    
    if not player:
        player = db.Player(tg_id=data.tg_id, username=data.username)
        session.add(player)
        session.commit()
        session.refresh(player)
    
    return get_state(player)

@app.post("/api/feed")
async def feed_beetle(data: ActionRequest, session: Session = Depends(get_db)):
    """Кормление"""
    player = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    if not player: raise HTTPException(404, "Player not found")

    cost = 15
    if player.money < cost:
        return {"status": "error", "message": "Не хватает багсов! Иди работать!"}
    
    if player.hunger <= 0:
        return {"status": "error", "message": "Жук сыт по горло!"}

    player.money -= cost
    player.hunger = max(0, player.hunger - 25)
    player.exp += 2
    session.commit()
    
    return {"status": "success", "message": "Ням-ням! Жук поел.", "state": get_state(player)}

@app.post("/api/work")
async def work_beetle(data: ActionRequest, session: Session = Depends(get_db)):
    """Работа"""
    player = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    if not player: raise HTTPException(404, "Player not found")
    
    if player.hunger >= 90:
        return {"status": "error", "message": "Жук слишком голоден для работы..."}

    salary = 20
    player.money += salary
    player.hunger = min(100, player.hunger + 15)
    player.strength += 0.1 
    session.commit()
    
    return {"status": "success", "message": f"Тяжелый труд. +{salary} багсов.", "state": get_state(player)}

@app.post("/api/fight")
async def fight_beetle(data: ActionRequest, session: Session = Depends(get_db)):
    """Арена (Боевая система)"""
    hero = session.query(db.Player).filter(db.Player.tg_id == data.tg_id).first()
    if not hero: raise HTTPException(404, "Player not found")
    
    # Проверки
    if hero.hunger >= 90:
        return {"status": "error", "message": "Жук шатается от голода! Покорми его.", "state": get_state(hero)}
    
    if hero.money < 5:
        return {"status": "error", "message": "Взнос за арену: 5 багсов.", "state": get_state(hero)}

    # Списываем взнос
    hero.money -= 5
    hero.hunger = min(100, hero.hunger + 10)

    # Ищем врага (случайного, не себя)
    enemy = session.query(db.Player).filter(db.Player.tg_id != hero.tg_id).order_by(func.random()).first()
    
    if not enemy:
        # Если игроков нет, создаем бота
        enemy_name = "Дикий Муравей"
        enemy_str = 1.0
    else:
        enemy_name = enemy.beetle_name
        enemy_str = enemy.strength

    # Логика боя
    hero_roll = hero.strength * random.uniform(0.8, 1.2)
    enemy_roll = enemy_str * random.uniform(0.8, 1.2)
    
    battle_log = []
    status = ""
    msg = ""

    if hero_roll > enemy_roll:
        # Победа
        reward = 15
        hero.money += reward
        hero.exp += 10
        
        # Level Up?
        if hero.exp >= 100 * hero.level:
            hero.level += 1
            hero.strength += 0.5
            battle_log.append(f"🌟 УРОВЕНЬ ПОВЫШЕН! Теперь {hero.level}!")
        
        status = "win"
        msg = f"Победа! +{reward}$"
        battle_log.append(f"Ваш жук провел серию ударов.")
        battle_log.append(f"{enemy_name} повержен и убегает.")
    else:
        # Поражение
        hero.exp += 2
        status = "lose"
        msg = "Поражение..."
        battle_log.append(f"{enemy_name} оказался хитрее.")
        battle_log.append(f"Вы получили легкие ушибы.")

    session.commit()
    
    return {
        "status": "success", 
        "message": msg, 
        "log": battle_log, 
        "state": get_state(hero)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
