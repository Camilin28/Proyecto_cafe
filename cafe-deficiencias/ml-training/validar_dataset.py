"""
Valida todas las imágenes del dataset ANTES de entrenar, para detectar
fotos corruptas, incompletas o en un formato que TensorFlow no puede leer
(esto evita que el entrenamiento se caiga a la mitad, como pasó con
"NewRandomAccessFile failed").
 
Uso:
    python validar_dataset.py
"""
 
import os
from PIL import Image
 
CARPETAS = ["dataset/train", "dataset/val"]
EXTENSIONES_VALIDAS = (".jpg", ".jpeg", ".png", ".bmp")
 
 
def validar():
    total = 0
    dañadas = []
 
    for carpeta_base in CARPETAS:
        if not os.path.isdir(carpeta_base):
            continue
        for clase in os.listdir(carpeta_base):
            ruta_clase = os.path.join(carpeta_base, clase)
            if not os.path.isdir(ruta_clase):
                continue
            for archivo in os.listdir(ruta_clase):
                ruta_completa = os.path.join(ruta_clase, archivo)
 
                if not archivo.lower().endswith(EXTENSIONES_VALIDAS):
                    print(f"[EXTENSIÓN RARA] {ruta_completa}")
                    continue
 
                total += 1
                try:
                    with Image.open(ruta_completa) as img:
                        img.verify()  # revisa que el archivo no esté corrupto
                    # Se vuelve a abrir porque verify() deja el archivo inutilizable después
                    with Image.open(ruta_completa) as img:
                        img.convert("RGB")
                except Exception as e:
                    dañadas.append(ruta_completa)
                    print(f"[DAÑADA] {ruta_completa} -> {e}")
 
    print(f"\nTotal revisadas: {total}")
    print(f"Dañadas encontradas: {len(dañadas)}")
 
    if dañadas:
        print("\nSe recomienda borrar o reemplazar estas fotos antes de entrenar:")
        for ruta in dañadas:
            print(f"  - {ruta}")
    else:
        print("Todas las imágenes se pudieron leer correctamente. Ya puedes correr train.py")
 
 
if __name__ == "__main__":
    validar()
 