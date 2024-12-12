

from io import BytesIO
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import numpy as np
import faiss
import torch
import os

from scripts.init import app


index:faiss.IndexIDMap = faiss.IndexIDMap(faiss.IndexFlatL2(384))

device = 'cuda'

processor = AutoImageProcessor.from_pretrained('facebook/dinov2-small')
model = AutoModel.from_pretrained('facebook/dinov2-small').to(device)

index_path = app.config['INDEX_PATH']

def img2vec(image):
    if type(image) == str :
        img = Image.open(image).convert('RGB')
    else:
        img = Image.open(BytesIO(image.read()))
    
    with torch.no_grad():
        inputs = processor(images=img, return_tensors="pt").to(device)
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)
    vector = embedding.detach().cpu().numpy()
    #Convert to float32 numpy
    vector = np.float32(vector)
    #Normalize vector: important to avoid wrong results when searching
    
    faiss.normalize_L2(vector)

    return vector

def add_img_to_index(image_path, image_id):
    #convert embedding to numpy
    vector = img2vec(image_path)
    #Add to index
    # index.add(vector)
    # breakpoint()
    index.add_with_ids(vector, np.array([image_id], dtype=np.int64))
    # indices = index.search(vector+0.02, 3)
    print(image_id)
    # image_map[len(image_map)] = image_id
    dump_index()


    
def remove_image(remove_id):
    global index
    index.remove_ids(np.array([remove_id], dtype=np.int64))
    dump_index()

def dump_index():
    faiss.write_index(index, index_path)

def search_similar_img(image, k:int):
    global index
    vector = img2vec(image)

    # index = faiss.read_index(index_path)
    d,indices = index.search(vector, k)
    print(d)
    indices = indices.squeeze()
    indices = indices[np.logical_and(indices >= 0, d.squeeze() < 1.2)]
    # print(indices)
    
    return indices

def init_faiss():
    global index
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
    else:
        dump_index()
