import requests

def test_catbox():
    url = "https://catbox.moe/user/api.php"
    files = {
        'reqtype': (None, 'fileupload'),
        'fileToUpload': ('test.txt', b'hello world', 'text/plain')
    }
    res = requests.post(url, files=files)
    print(res.status_code, res.text)

test_catbox()
