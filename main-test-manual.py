from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import tensorflow as tf
import uuid
import numpy as np
from PIL import Image
import io
import os


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

model = tf.keras.models.load_model("model/model_2.keras")
class_names = ['Metal', 'Plastik']

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img = np.array(img).astype(np.float32)
    return np.expand_dims(img, axis=0)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, input: str = Form(...)):

    # Kirim sinyal kalau prediksi adalah kelas 0
    if input == "1":
        # Masukkan kode untuk ESP32!!!
        pass

    return templates.TemplateResponse("predict.html", {
        "request": request,
        "result": input,
    })
