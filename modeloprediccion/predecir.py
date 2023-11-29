import numpy as np
from keras.models import load_model

def analizar(entrada):
    model = load_model('C:/Users/modeloprueba.h5')

    prediction = model.predict(np.array([entrada]))
    porcentaje = prediction * 100
    return {'resultado':round(float(porcentaje[0][0]),2)}
