import os, sys
import requests, json
from concurrent.futures import ThreadPoolExecutor as tpe
import concurrent.futures
import numpy as np
import pandas as pd

token = os.environ['ASANA_ACCESS_TOKEN']
url = 'https://app.asana.com/api/1.0'
request_header = {
    'Authorization': 'Bearer {}'.format(token),
    'Accept': 'application/json'
}


def get_json_response(route):
    resp = requests.get('{}/{}'.format(url, route), headers=request_header)
    if resp.ok:
        return resp.json()['data']
    return None


def get_id_by_route(route, name):
    resp = get_json_response(route)
    if resp is None:
        return None
    for d in resp:
        if (d['name'] == name):
            return d['gid']


def get_project_id(name):
    return get_id_by_route('projects', name)


project_id = get_project_id('EigenPrism Release Mgmt')


def task_as_record(task):
    td = {}
    assignee = task.get('assignee')
    if assignee is not None:
        td['Assigned To'] = assignee['name']
    else:
        td['Assigned To'] = np.NaN
    td['Url'] = 'https://app.asana.com/0/{}/{}'.format(project_id, task['gid'])
    td['Name'] = task['name']
    td['Due Date'] = task['due_on']
    td['Status'] = np.NaN

    membership = task.get('memberships')
    if membership is not None and len(membership) > 0:
        section = membership[0].get('section')
        if section is not None:
            td['Status'] = section['name']

    for f in task['custom_fields']:
        key = f.get('name')
        if key == 'Priority' or key == 'Module':
            value = np.NaN
            enum = f.get('enum_value')
            if enum is not None:
                value = enum.get('name')
            td[key] = value

    return td


tag_name = 'AJG Punchlist'
net_tasks = []

with tpe(max_workers=50) as executor:
    tag_id = executor.submit(get_id_by_route, 'tags', tag_name)

    tasks_with_tag = executor.submit(get_json_response,
                                     'tags/{}/tasks'.format(tag_id.result()))

    tasks = pd.Series([t['gid'] for t in tasks_with_tag.result()],
                      name='task.id')

    tasks_details = {
        executor.submit(get_json_response, 'tasks/{}'.format(t)): t
        for t in tasks
    }

    for f in concurrent.futures.as_completed(tasks_details):
        fut = tasks_details[f]
        try:
            t = f.result()
            net_tasks.append(t)
        except Exception as exc:
            print('Error: {}'.format(exc))

records = [task_as_record(t) for t in net_tasks]
df = pd.DataFrame(records)
df.to_csv('records.csv', index=False)

print(df.dropna(subset=['Status']).sort_values(['Status', 'Priority']))
