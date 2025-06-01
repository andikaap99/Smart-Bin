from fastapi import FastAPI, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid
import io
import os
import time


app = FastAPI()
bg = BackgroundTasks()
templates = Jinja2Templates(directory="templates")
servo_feed = -1
servo_status = 0
servo_read = False  # baru dibaca ESP atau belum


app.mount("/static", StaticFiles(directory="static"), name="static")

def reset_servo():
    global servo_feed, servo_read
    time.sleep(2)
    print(2)
    servo_feed = -1
    servo_read = False
    print(servo_feed)

def servo(input):
    global servo_status
    servo_status = int(input)
    return {"message": "Status updated", "status":servo_status} 


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.get("/feed")
def get_servo_status(background_tasks: BackgroundTasks): 
    global servo_read
    if not servo_read:
        servo_read = True
        background_tasks.add_task(reset_servo)  # Gunakan parameter ini, bukan variabel global `bg`
        return {
            "servo_feed": 1
        }
    else:
        return {
            "servo_feed": -1
        }
    
@app.get("/status")
async def get_status():
    global servo_status
    return {"servo_status": servo_status}
