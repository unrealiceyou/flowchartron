import requests, re, json

class DuckChat:
    def __init__(self):
        self.url = 'https://duckduckgo.com/duckchat/v1/chat'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Accept": "text/event-stream",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://duckduckgo.com/",
            "Content-Type": "application/json",
            "x-vqd-4": "",
            "Content-Length": "73",
            "Origin": "https://duckduckgo.com",
            "Connection": "keep-alive",
            "Cookie": "5=1; 7=282828; 8=fbf1c7; 9=fe8019; 21=3b3735; j=282828; aa=f9bc2e; x=b7ba25; ah=ru-ru; l=wt-wt; aq=-1; ay=b; dcm=3; ap=-1; ax=-1; ak=-1; psb=-1; aj=m; ao=-1; au=-1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }
        self.refresh_token()

    def refresh_token(self):
        url = 'https://duckduckgo.com/duckchat/v1/status'

        tokenHeaders = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://duckduckgo.com/',
            'Connection': 'keep-alive',
            'Cookie': '5=1; 7=282828; 8=fbf1c7; 9=fe8019; 21=3b3735; j=282828; aa=f9bc2e; x=b7ba25; ah=ru-ru; l=wt-wt; aq=-1; ay=b; dcm=3; ap=-1; ax=-1; ak=-1; psb=-1; aj=m; ao=-1; au=-1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
            'Cache-Control': 'no-store, no-cache',
            'x-vqd-accept': '1',
            'Pragma': 'no-cache'
        }
        response = requests.get(url, headers=tokenHeaders)
        self.headers["x-vqd-4"] = str(response.headers.get("x-vqd-4"))

    def send_message(self, message):
        data = {
            'model': 'gpt-3.5-turbo-0125',
            'messages': [
                {
                    'role': 'user',
                    'content': message
                }
            ]
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        print(response.reason)
        self.refresh_token()

        response_text = response.content.decode("utf-8")
        pattern = """data: (.*)"""
        matches = re.finditer(pattern, response_text)

        msg = []
        for match in matches:
            jsonData = str(match.group(1))
            try:
                parsedData = json.loads(jsonData)
                msg.append(parsedData['message'])
            except:
                continue

        return "".join(msg)
    

if __name__ == '__main__':
    duck_chat = DuckChat()

    while True:
        user_input = input("=> ")
        if user_input.lower() == 'exit':
            break

        response_message = duck_chat.send_message(user_input)
        print(response_message)

