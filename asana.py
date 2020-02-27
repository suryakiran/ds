import os, sys
import requests, json
from concurrent.futures import ThreadPoolExecutor as tpe
import concurrent.futures
import numpy as np
import pandas as pd
import tempfile

from jinja2 import FileSystemLoader, Environment

lambda_env = os.environ.get('LAMBDA_ENV')
token = os.environ['ASANA_ACCESS_TOKEN']
url = 'https://app.asana.com/api/1.0'
request_header = {
    'Authorization': 'Bearer {}'.format(token),
    'Accept': 'application/json'
}
csv_file = os.path.join(tempfile.gettempdir(), 'records.csv')

project_id = None
loader = FileSystemLoader('.')
jenv = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
template = jenv.get_template('table.html')
tag_name = 'AJG Punchlist'
net_tasks = []


def get_json_response(session, route):
    resp = session.get('{}/{}'.format(url, route))
    if resp.ok:
        return resp.json()['data']
    return None


def get_id_by_route(session, route, name):
    resp = get_json_response(session, route)
    if resp is None:
        return None
    for d in resp:
        if (d['name'] == name):
            return d['gid']

def get_tasks_by_tag_name(session, name):
    tag = get_id_by_route(session, 'tags', name)
    if tag is not None:
        return get_json_response(session, 'tags/{}/tasks'.format(tag))
    return None


def get_project_id(name):
    return get_id_by_route('projects', name)


def task_as_record(task):
    td = {}
    membership = task.get('memberships')
    td['Status'] = np.nan
    td['Id'] = task['gid']
    pid = None

    if membership is not None and len(membership) > 0:
        section = membership[0].get('section')
        if section is not None:
            td['Status'] = section['name']
        project = membership[0].get('project')
        if project is not None:
            pid = project['gid']

    assignee = task.get('assignee')
    if assignee is not None:
        td['Assigned To'] = assignee['name']
    else:
        td['Assigned To'] = np.nan

    if pid is not None:
        url = 'https://app.asana.com/0/{}/{}'.format(pid, task['gid'])
        td['Name'] = '<a href="{}" target="_blank">{}</a>'.format(
            url, task['name'])
    else:
        td['Name'] = task['name']

    td['Due Date'] = task['due_on']

    for f in task['custom_fields']:
        key = f.get('name')
        if key == 'Priority' or key == 'Module':
            value = np.nan
            enum = f.get('enum_value')
            if enum is not None:
                value = enum.get('name')
            td[key] = value

    return td

def do_it_lambda(event, context):
    net_tasks = []
    session = requests.Session()
    session.headers.update(request_header)

    with tpe(max_workers=None) as executor:
        tasks_with_tag = get_tasks_by_tag_name(session, tag_name)
        tasks = [t['gid'] for t in tasks_with_tag]

        tasks_details = {
            executor.submit(get_json_response, session, 'tasks/{}'.format(t)): t
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
    df.to_csv(csv_file, index=False)

    return df

def do_it_local(event, context):
    return pd.read_csv(csv_file)
    

def do_it(event, context):
    df = None
    if lambda_env:
        df = do_it_lambda(event, context)
    else:
        df = do_it_local(event, context)

    df['Due Date'] = pd.to_datetime(df['Due Date']).dt.strftime('%d-%b-%Y')
    df = df.dropna(subset=['Status']) \
    .sort_values(['Priority', 'Status']) \
    .replace(np.nan, '') \
    .reindex(columns = ['Name', 'Assigned To', 'Status', 'Module', 'Due Date', 'Priority'])

    out_html = template.render(data = {'data': df, 'tag': tag_name})
    return out_html


if __name__ == '__main__':
    lambda_env = True
    out_html = do_it(None, None)
    with open('out.html', 'w') as f:
        f.write(out_html)

