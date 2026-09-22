"""
Entrenamiento del modelo de clasificación de deficiencias nutricionales en hojas de café.
 
Usa transfer learning sobre MobileNetV2 (ideal cuando el dataset todavía es pequeño,
como suele pasar en la primera fase de un proyecto como este).
 
ESTRUCTURA DE CARPETAS ESPERADA (ajústala cuando llegue el dataset real):
 
    dataset/
        train/
            nitrogeno/   -> fotos de hojas con deficiencia de nitrógeno
            potasio/     -> fotos de hojas con deficiencia de potasio
            magnesio/    -> fotos de hojas con deficiencia de magnesio
            sana/        -> fotos de hojas sanas (importante: sin esta clase el
                             modelo "inventa" deficiencias en hojas normales)
        val/
            nitrogeno/
            potasio/
            magnesio/
            sana/
 
Cuando el grupo de investigación te envíe las imágenes, solo necesitas organizarlas
en esta estructura (o ajustar CLASS_NAMES abajo) y correr este script.
 
Uso:
    python train.py
"""
 
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils.class_weight import compute_class_weight
 
# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
IMG_SIZE = (224, 224)
BATCH_SIZE = 16          # baja esto si tienes pocas imágenes por clase (ej. 8)
EPOCHS_HEAD = 15         # entrenamiento inicial solo del clasificador nuevo
EPOCHS_FINE_TUNE = 10    # ajuste fino descongelando parte de MobileNetV2
LEARNING_RATE = 1e-3
FINE_TUNE_LR = 1e-5
 
TRAIN_DIR = "dataset/train"
VAL_DIR = "dataset/val"
MODEL_OUT = "modelo_deficiencias_cafe.keras"
 
CLASS_NAMES = ["magnesio", "nitrogeno", "potasio"]  # orden alfabético = orden de Keras
# Nota: la clase "sana" se quitó temporalmente por no tener fotos de hojas
# sanas todavía. Cuando el grupo de investigación las consiga, agrégala de
# nuevo aquí y crea las carpetas dataset/train/sana y dataset/val/sana.
 
 
def cargar_datasets():
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=CLASS_NAMES,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=CLASS_NAMES,
    )
 
    # Aumento de datos: útil porque al inicio probablemente tendrán pocas imágenes
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.1),
    ])
 
    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))
    train_ds = train_ds.map(lambda x, y: (preprocess_input(x), y)).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (preprocess_input(x), y)).prefetch(tf.data.AUTOTUNE)
 
    return train_ds, val_ds
 
 
def calcular_class_weights():
    """
    Si el dataset real llega desbalanceado (ej. 400 fotos de potasio pero
    solo 50 de magnesio), el modelo tiende a "favorecer" la clase con más
    ejemplos. Esto calcula un peso por clase para compensarlo durante el
    entrenamiento, sin necesidad de tener el mismo número de fotos en cada
    carpeta.
    """
    etiquetas = []
    for i, clase in enumerate(CLASS_NAMES):
        carpeta = os.path.join(TRAIN_DIR, clase)
        cantidad = len([f for f in os.listdir(carpeta) if not f.startswith(".")])
        etiquetas.extend([i] * cantidad)
        print(f"  {clase}: {cantidad} imágenes de entrenamiento")
 
    pesos = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(len(CLASS_NAMES)),
        y=np.array(etiquetas),
    )
    return {i: peso for i, peso in enumerate(pesos)}
 
 
def construir_modelo(num_clases):
    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # congelado en la primera etapa
 
    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_clases, activation="softmax")(x)
 
    model = models.Model(inputs, outputs)
    return model, base_model
 
 
def evaluar_con_matriz_confusion(model, val_ds):
    """
    Calcula la matriz de confusión y un reporte de precisión/recall por
    clase. Esto es lo que responde la pregunta clave del proyecto: ¿el
    modelo confunde potasio con hierro/magnesio, o los distingue bien?
    """
    y_verdadero = []
    y_predicho = []
 
    for lote_x, lote_y in val_ds:
        predicciones = model.predict(lote_x, verbose=0)
        y_predicho.extend(np.argmax(predicciones, axis=1))
        y_verdadero.extend(np.argmax(lote_y.numpy(), axis=1))
 
    print("\n=== Matriz de confusión ===")
    print("Filas = clase real, columnas = clase predicha")
    print("Orden de clases:", CLASS_NAMES)
    matriz = confusion_matrix(y_verdadero, y_predicho)
    print(matriz)
 
    print("\n=== Reporte por clase (precisión, recall, f1-score) ===")
    print(classification_report(y_verdadero, y_predicho, target_names=CLASS_NAMES))
 
 
def main():
    train_ds, val_ds = cargar_datasets()
    model, base_model = construir_modelo(len(CLASS_NAMES))
 
    print("Calculando pesos por clase (para compensar dataset desbalanceado)...")
    pesos_clase = calcular_class_weights()
    print(f"Pesos calculados: {pesos_clase}")
 
    # Si el modelo deja de mejorar en el set de validación, para antes de
    # tiempo en vez de seguir entrenando y sobreajustarse.
    parada_temprana = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=4,
        restore_best_weights=True,
    )
 
    # --- Etapa 1: entrenar solo el clasificador nuevo ---
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    print("=== Etapa 1: entrenando el clasificador (base congelada) ===")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_HEAD,
        class_weight=pesos_clase,
        callbacks=[parada_temprana],
    )
 
    # --- Etapa 2: fine-tuning descongelando las últimas capas de MobileNetV2 ---
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
 
    model.compile(
        optimizer=tf.keras.optimizers.Adam(FINE_TUNE_LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    print("=== Etapa 2: fine-tuning ===")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_FINE_TUNE,
        class_weight=pesos_clase,
        callbacks=[parada_temprana],
    )
 
    model.save(MODEL_OUT)
    print(f"Modelo guardado en {MODEL_OUT}")
 
    # Reporte final: accuracy general + matriz de confusión + métricas por clase
    print("\nEvaluación final sobre el set de validación:")
    loss, acc = model.evaluate(val_ds)
    print(f"Accuracy validación: {acc:.4f}")
 
    evaluar_con_matriz_confusion(model, val_ds)
 
 
if __name__ == "__main__":
    main()