import requests

title = "A cat"
url = 'http://localhost:5000/generate' # ここにPOSTリクエストを送りたいURLを設定します
data = {'title': title} # ここにPOSTしたいデータを辞書形式で設定します

response = requests.post(url, data=data)

print(response.text) # サーバーからのレスポンスを出力します
