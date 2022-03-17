# pylint: disable=no-name-in-module
from io import BytesIO
import itertools
# import matplotlib.pyplot as plt
import logging

from typing import Union

from PIL import Image
import aiofiles
import numpy as np
from sklearn.metrics import confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import imagenet_utils
from tensorflow.keras.applications.imagenet_utils import decode_predictions
from tensorflow.keras.layers import Activation, Dense
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing import image, image as keras_image
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from upscale_cli.dbx_logger import (  # noqa: E402
    generate_tree,
    get_lm_from_tree,
    get_logger,
    intercept_all_loggers,
)

LOGGER = get_logger(__name__, provider="Serve Model", level=logging.DEBUG)
model = None


def load_model():
    model = tf.keras.applications.MobileNetV2(weights="imagenet")
    print("Model loaded")
    return model


# SOURCE: https://deeplizard.com/learn/video/OO4HD-1wRN8
def prepare_image(file: str):
    img: Image.Image
    img = keras_image.load_img(file, target_size=(224, 224))
    img_array = keras_image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)

    # Lastly, we're calling preprocess_input() from tf.keras.applications.mobilenet, which preprocesses the given image data to be in the same format as the images that MobileNet was originally trained on. Specifically, it's scaling the pixel values in the image between - 1 and 1, and this function will return the preprocessed image data as a numpy array.
    return tf.keras.applications.mobilenet.preprocess_input(img_array_expanded_dims)


# SOURCE: https://github.com/keras-team/keras/issues/11684
def load_image_from_bytes(img, target_size=(224, 224)):
    # img_bytes is a PIL.PngImagePlugin.PngImageFile image mode=RGB size=350x233 at 0x1923AF700
    # img = Image.open(io.BytesIO(img_bytes))
    img = img.convert("RGB")
    img = img.resize(target_size, Image.NEAREST)
    img = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img, axis=0)
    return tf.keras.applications.mobilenet.preprocess_input(img_array_expanded_dims)


# # SOURCE: https://github.com/keras-team/keras/issues/11684
# def load_image_from_path(img_path, target_size=(224, 224)):
#     img = image.load_img(img_path, target_size=target_size)
#     img = image.img_to_array(img)


def predict(image: Union[Image.Image, str]):
    global model
    if model is None:
        model = load_model()

    preprocessed_image = load_image_from_bytes(image)
    LOGGER.info(f" preprocessed_image -> {type(preprocessed_image)}")

    predictions = model.predict(preprocessed_image)
    LOGGER.info(f" predictions -> {type(predictions)}")
    results = imagenet_utils.decode_predictions(predictions)
    LOGGER.info(f" type results -> {type(results)}")
    LOGGER.info(f" results -> {results}")

    response = []
    for i, res in enumerate(results[0]):
        resp = {}
        resp["class"] = res[1]
        resp["confidence"] = "{}".format(res[2] * 100)

        LOGGER.info(f" res -> {res}")
        LOGGER.info(f" type(res) -> {type(res)}")

        response.append(resp)

    return response


def read_imagefile(file) -> Image.Image:
    image = Image.open(BytesIO(file))
    return image
