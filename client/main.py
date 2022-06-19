import requests
from urllib.parse import urljoin
from pprint import pprint


class Client:
    def __init__(self, username, password, url) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.token = ""
        self.header = {'x-access-token': ''}

    def get_token(self):
        myjson = requests.get(urljoin(self.url, 'login'), auth=(self.username, self.password)).json()
        self.token = (myjson['token'])
        self.header['x-access-token'] = self.token
        return pprint("token: " + self.token)

    def get_all_mems(self):
        return pprint(
            requests.get(urljoin(self.url, '/get_all_mems'), headers=self.header).json())

    def likes_or_skip(self, l_or_p):
        return pprint(
            requests.post(urljoin(self.url, '/likes_or_skip'), headers=self.header, data={'l_or_p': l_or_p}).json())

    def delete_all_mems(self):
        return pprint(
            requests.delete(urljoin(self.url, '/delete_all_mems'), headers=self.header).json())

    def load_mems(self, url):
        return pprint(
            requests.post(urljoin(self.url, '/load_mems'), headers=self.header, data={'url': url}).json())

    def generate_likes(self):
        return pprint(
            requests.get(urljoin(self.url, '/test_for_third'), headers=self.header).json())


def main():
    url = 'http://127.0.0.1:5000'
    username = 'Boba'
    password = '12345'
    client = Client(url=url, username=username, password=password)
    client.get_token()

    active = True
    while active:
        print('>>>', end=' ')
        req = input().strip().split()
        try:
            if req[0] == 'exit':
                print('Finishing program...')
                active = False
            elif req[0] == 'likes_or_skip':
                client.likes_or_skip(req[1])
            elif req[0] == 'get_all_mems':
                client.get_all_mems()
            elif req[0] == 'load_mems':
                client.load_mems(req[1])
            elif req[0] == 'delete_all_mems':
                client.delete_all_mems()
            elif req[0] == 'generate_likes':
                client.generate_likes()

            elif req[0] == 'help' or req[0] == 'list':
                print('help | list -- prints list of all commands')
                print('likes_or_skip -- likes mems or skip mems, example: likes_of_skip 0/1')
                print('get_all_mems -- get all mems')
                print('load_mems -- load mems, example: load_mems https://vk.com/album-197700721_281940823')
                print('delete_all_mems -- delete all my mems')
                print('generate_likes -- change status of todo list element')
                print('exit -- finishing the program')
            else:
                raise Exception()
        except:
            print('Incorrect command. Enter help or list for list of all commands')


if __name__ == '__main__':
    main()
