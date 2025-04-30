from fastapi import FastAPI, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import tensorflow as tf
import uuid
import numpy as np
from PIL import Image
import io
import os
import time


app = FastAPI()
bg = BackgroundTasks()
templates = Jinja2Templates(directory="templates")
servo_predict = -1
servo_status = 0
servo_read = False  # baru dibaca ESP atau belum


app.mount("/static", StaticFiles(directory="static"), name="static")

model = tf.keras.models.load_model("model/model_2.keras")
class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
def reset_predict():
    global servo_predict
    time.sleep(2)
    print(2)
    servo_predict = -1
    print(servo_predict)
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img = np.array(img).astype(np.float32)
    return np.expand_dims(img, axis=0)

async def predict_image(file: UploadFile = File(...)):
    global servo_predict, servo_read
    servo_read = False 
    image = await file.read()

    filename = f"{uuid.uuid4().hex}.jpg"
    save_path = f"static/uploads/{filename}"
    with open(save_path, "wb") as f:
        f.write(image)

    input_tensor = preprocess_image(image)
    prediction = model.predict(input_tensor)
    predicted_class_index = np.argmax(prediction[0])
    pred_class = int(class_names[predicted_class_index])  

    # Logika servo_predict
    if 0 <= pred_class <= 6:
        servo_predict = 0
    elif 7 <= pred_class <= 12:
        servo_predict = 1
    else:
        servo_predict = -1 

    return{
        "servo_predict": servo_predict,
        "filename": filename
    }

def servo(input):
    global servo_status
    servo_status = int(input)
    return {"message": "Status updated", "status":servo_status} 

def show_predict(request: Request, servo, filename):
    return templates.TemplateResponse("predict.html", {
        "request": request,
        "result": servo,
        "uploaded_image": f"/static/uploads/{filename}",
    })


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.get("/predict")
def get_servo_status(): 
    # bg.add_task(reset_predict)   
    # return {
    #     "servo_predict": servo_predict
    # }
    global servo_read
    if not servo_read:
        servo_read = True  # ditandai sudah dibaca
        bg.add_task(reset_predict)
        return {
            "servo_predict": servo_predict
        }
    else:
        return {
            "servo_predict": -1
        }


@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    image = await predict_image(file)
    
    
    servo(image["servo_predict"])
    # print(f"servo_predik ", image["servo_predict"])
    return show_predict(request, str(image["servo_predict"]), image["filename"])


    # image = await file.read()

    # filename = f"{uuid.uuid4().hex}.jpg"
    # save_path = f"static/uploads/{filename}"
    # with open(save_path, "wb") as f:
    #     f.write(image)

    # input_tensor = preprocess_image(image)
    # prediction = model.predict(input_tensor)
    # predicted_class_index = np.argmax(prediction[0])
    # pred_class = int(class_names[predicted_class_index])  

    # # Logika servo_predict
    # if 0 <= pred_class <= 6:
    #     servo_predict = 0
    # elif 7 <= pred_class <= 12:
    #     servo_predict = 1
    # else:
    #     servo_predict = 0 

    # servo_predict = str(servo_predict)


    # return templates.TemplateResponse("predict.html", {
    #     "request": request,
    #     "result": servo_predict,
    #     "uploaded_image": f"/static/uploads/{filename}",
    # })
