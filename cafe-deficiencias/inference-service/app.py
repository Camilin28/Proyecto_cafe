"""
Microservicio de inferencia (FastAPI).

Este servicio SOLO se encarga de cargar el modelo entrenado y devolver
la predicción para una imagen. El backend Spring Boot le habla a este
servicio internamente.

Ejecutar:
    uvicorn app:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import numpy as np
import io
import tensorflow as tf

app = FastAPI(title="Servicio de inferencia - Deficiencias en café")

MODEL_PATH = "modelo_deficiencias_cafe.keras"
CLASS_NAMES = ["magnesio", "nitrogeno", "potasio"]
IMG_SIZE = (224, 224)

model = None


@app.on_event("startup")
def cargar_modelo():
    global model
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"Modelo cargado desde {MODEL_PATH}")
    except Exception as e:
        # No tumbamos el servicio: útil mientras aún no hay modelo entrenado
        # (por ejemplo, mientras llega el dataset). El endpoint /predict
        # devolverá error hasta que exista modelo_deficiencias_cafe.keras
        print(f"Aviso: no se pudo cargar el modelo todavía ({e})")


def preprocesar_imagen(bytes_imagen: bytes) -> np.ndarray:
    imagen = Image.open(io.BytesIO(bytes_imagen)).convert("RGB")
    imagen = imagen.resize(IMG_SIZE)
    arreglo = np.array(imagen, dtype=np.float32)
    arreglo = tf.keras.applications.mobilenet_v2.preprocess_input(arreglo)
    return np.expand_dims(arreglo, axis=0)


@app.get("/health")
def health():
    return {"status": "ok", "modelo_cargado": model is not None}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="El modelo aún no está entrenado/cargado. Corre train.py y export_tflite.py primero.",
        )

    contenido = await file.read()
    entrada = preprocesar_imagen(contenido)

    probabilidades = model.predict(entrada)[0]
    indice_max = int(np.argmax(probabilidades))

    return {
        "deficiencia": CLASS_NAMES[indice_max],
        "confianza": float(probabilidades[indice_max]),
        "probabilidades": {
            clase: float(prob) for clase, prob in zip(CLASS_NAMES, probabilidades)
        },
    }