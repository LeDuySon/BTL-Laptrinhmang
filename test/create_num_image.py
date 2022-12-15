import pandas as pd
import numpy as np
import os 
import cv2

path = "data/mnist_test.csv"

df = pd.read_csv(path)
label = df.iloc[:, 0]
df_img = df.iloc[:, 1:]

print(df_img.head())
w, h = 28, 28

file = open("output.txt", "wt")

for idx, elem in df.iterrows():
    print("Label: ", label[idx])
    file.write(f"Number: {label[idx]}\n")
    for s in range(0, w):
        row = elem[s*28:(s+1)*28]
        row[row < 50] = 0
        row[row >= 50] = 1
        
        result = " ".join(list(map(str, row.values.tolist())))
        file.write(f"{result}\n")
    
    file.write("\n")
    
    if(idx == 10):
        break