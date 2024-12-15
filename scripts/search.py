import sqlite3
import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np

# 初始化数据库
def initialize_feature_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT,
            features BLOB
        )
    ''')
    conn.commit()
    conn.close()

# 提取图片特征向量
def extract_features(image_path, model, preprocess):
    image = Image.open(image_path).convert("RGB")
    input_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        features = model(input_tensor).squeeze(0).numpy()
    return features

# 添加图片及特征到数据库
def add_image_with_features(db_path, image_name, image_path, features):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO image_features (name, path, features)
        VALUES (?, ?, ?)
    ''', (image_name, image_path, features.tobytes()))
    conn.commit()
    conn.close()

# 检索相似图片
def search_similar_images(db_path, query_features, top_k=5):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name, path, features FROM image_features')
    results = []
    for name, path, features_blob in cursor.fetchall():
        features = np.frombuffer(features_blob, dtype=np.float32)
        similarity = np.dot(query_features, features) / (np.linalg.norm(query_features) * np.linalg.norm(features))
        results.append((name, path, similarity))
    conn.close()
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]

# 初始化模型
model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*(list(model.children())[:-1]))
model.eval()

# 图像预处理
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 示例用法
db_path = "image_feature_database.db"
initialize_feature_db(db_path)

# 提取图片特征并存储
image_path = "sunset.jpg"
features = extract_features(image_path, model, preprocess)
add_image_with_features(db_path, "sunset.jpg", image_path, features)

# 查询相似图片
query_image_path = "query.jpg"
query_features = extract_features(query_image_path, model, preprocess)
results = search_similar_images(db_path, query_features)
print("Similar Images:")
for name, path, similarity in results:
    print(f"Name: {name}, Path: {path}, Similarity: {similarity}")
