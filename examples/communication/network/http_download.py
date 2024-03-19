import requests

url = 'https://example.com'
response = requests.get(url)
print("Response:")
print("-- status code:", response.status_code)
print("")
print("-- headers:", response.headers)
print("")
print("-- content:", response.content)
print("")
print("-- text:", response.text)
print("")




