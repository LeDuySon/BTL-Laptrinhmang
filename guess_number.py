import math
import numpy as np
import cv2
import onnxruntime as ort


class NumberGuesser():
    """
    Refer: https://github.com/onnx/models/tree/main/vision/classification/mnist
    Download checkpoints: https://github.com/onnx/models/blob/main/vision/classification/mnist/model/mnist-12.onnx
    """
    def __init__(self, checkpoint_path):
        self.image_size = (28, 28)
        self.model = self.load_model(checkpoint_path)
        
        # threshold for determine guess or not
        self.threshold = 0.9
        
    def load_model(self, path):
        ort_sess = ort.InferenceSession(path)
        
        return ort_sess
    
    def preprocess_image(self, image):
        image[image == 2] = 0
        if(len(image.shape) == 1):
            img_size = int(math.sqrt(image.shape[0]))
            image = image.reshape((img_size, img_size))
            
        image = cv2.resize(image.astype(np.float32), self.image_size)
        return image[np.newaxis, np.newaxis, ...]
    
    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        return np.exp(x) / np.sum(np.exp(x), axis=0)

    def run(self, image):
        prep_img = self.preprocess_image(image)
        outputs = self.model.run(None, {'Input3': prep_img})[0]
        
        probs = self.softmax(outputs[0])
        idx = np.argmax(probs)
        
        if(probs[idx] >= self.threshold):
            return idx
        return 100

if __name__ == '__main__':
    guess = NumberGuesser("checkpoints/mnist-12.onnx")
    
    path = "data/mnist_test.csv"

    import pandas as pd
    df = pd.read_csv(path)
    
    label = df.iloc[:, 0]
    df_img = df.iloc[:, 1:]
    
    
    idx = 5
    image = df_img.iloc[idx].to_numpy()
    image[image < 50] = 0
    image[image >= 50] = 1
        
    print(guess.run(image))
    print(label.iloc[idx])
        
        
