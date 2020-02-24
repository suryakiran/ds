import os, sys, time
import tempfile, zipfile
import requests
from mandrill import Mandrill

apikey = os.environ.get('MANDRILL_API_KEY')
client = Mandrill(apikey)

out = client.exports.list()
for o in out:
    if o['state'] == 'complete':
        print(o)

url = 'https://mandrillapp.com/api/1.0'

activity = {
    'key': apikey,
    'date_from': '2020-02-01 00:00:00',
    'date_to': '2020-02-02 00:00:00'
}

# export_info_list = {'key': apikey}

# res = requests.post('{}/exports/list.json'.format(url), json=export_info_list)
# if res.ok:
# print(res.content)


def doit():
    if apikey is None:
        return

    id = None
    res = requests.post('{}/exports/activity.json'.format(url), json=activity)
    if (res.ok):
        id = res.json()['id']

    if id is None:
        return

    export_info = {'key': apikey, 'id': id}
    res_url = None
    while True:
        res = requests.post('{}/exports/info.json'.format(url),
                            json=export_info)
        if res.ok:
            j = res.json()
            if (j['state'] == 'complete'):
                res_url = j['result_url']
                break
            time.sleep(10)
        else:
            break

    if res_url is None:
        return

    temp = tempfile.NamedTemporaryFile()
    res = requests.get(res_url)
    if res.ok:
        with open(temp.name, 'wb') as f:
            f.write(res.content)

        with zipfile.ZipFile(temp.name, 'r') as f:
            f.extractall(os.getcwd())


if __name__ == '__main__':
    pass
