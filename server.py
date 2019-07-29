import tensorflow as tf
from keras.models import load_model
from flask import Flask, render_template, request
import numpy as np
import base64
import json
import logging
from scipy.misc import imresize
import imageio
import warnings

tf.get_logger().setLevel(logging.ERROR)
warnings.filterwarnings("ignore")


app = Flask(__name__)

NUMBER = {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
          7: "Seven", 8: "Eight", 9: "Nine"}


@app.route("/", methods=["GET", "POST"])
def ready():
    if request.method == "GET":
        return render_template("index1.html")
    if request.method == "POST":
        data = request.form["payload"].split(",")[1]
        net = request.form["net"]

        graph = tf.get_default_graph()
        img = base64.b64decode(data)

        with open('temp.png', 'wb') as output:
            output.write(img)

        x = imageio.imread('temp.png', pilmode='L')

        x = imresize(x, (28, 28))

        '''
        failed to remove imresize warning
        tried np.array(Image.fromarray(x).resize((28, 28)))
        tried np.array(Image.fromarray(x, mode="Lc").resize((28, 28)))
        tried matplotlib, rgb2gray
        '''

        x = np.expand_dims(x, axis=0)
        x = x.reshape(28, 28, 1)
        x = np.invert(x)
        # brighten the image by 60%
        for i in range(len(x)):
            for j in range(len(x)):
                if x[i][j] > 50:
                    x[i][j] = min(255, x[i][j] + x[i][j] * 0.60)

        # normalize the values between 0 and 1
        x = np.interp(x, [0, 255], [0, 1])

        model = load_model("./models/augmented_data_best_model.h5")

        with graph.as_default():
            val = model.predict([[x]])

        pred = NUMBER[np.argmax(val)]
        classes = ["Zero", "One", "Two", "Three", "Four", "Five", "Six",
                   "Seven", "Eight", "Nine"]
        print(pred)
        print(list(val[0]))
        return render_template("index1.html", preds=list(val[0]), classes=json.dumps(classes), chart=True, putback=request.form["payload"], net=net, num=pred)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True, threaded=False)
