import requests

def search_images_bing(api_key, query, count=10):
    url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": count}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        return [img["contentUrl"] for img in results.get("value", [])]
    else:
        print(f"Error: {response.status_code}")
        return []

# 替换为你的 API 密钥
api_key = "YOUR_BING_API_KEY"
query = "sunset"
images = search_images_bing(api_key, query)
for img_url in images:
    print(img_url)
