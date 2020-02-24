import os, sys
import requests, json
from concurrent.futures import ThreadPoolExecutor as tpe
import concurrent.futures
import threading
import pandas as pd
import time

token = os.environ['ASANA_ACCESS_TOKEN']
url = 'https://app.asana.com/api/1.0'
request_header = {
    'Authorization': 'Bearer {}'.format(token),
    'Accept': 'application/json'
}

section_tasks = {}
custom_field_map = {}
custom_field_names_map = {}
section_name = {}
section_name_to_id = {}
section_id_to_name = {}
task_to_section_map = {}


def get_json_response(route):
    resp = requests.get('{}/{}'.format(url, route), headers=request_header)
    if resp.ok:
        print('done for {} ({})'.format(route, threading.current_thread().ident))
        return resp.json()['data']
    return None


def get_id_by_route(route, name):
    resp = get_json_response(route)
    if resp is None:
        return None
    for d in resp:
        if (d['name'] == name):
            return d['gid']


def get_tag_id(name):
    return get_id_by_route('tags', name)


def get_project_id(name):
    return get_id_by_route('projects', name)


def get_sections_of_project(gid):
    return get_json_response('projects/{}/sections'.format(gid))


def get_custom_fields_of_project(gid):
    return get_json_response('projects/{}/custom_field_settings'.format(gid))


def get_tasks_of_tag(name):
    tag_id = get_tag_id(name)
    tasks = get_json_response('tags/{}/tasks'.format(tag_id))
    return tasks

tasks = ['1157562707024814', '1161854664864243', '1156460975802774', '1162837460852153', '1161298893105353', '1159907257029281', '1155933470055352', '1162183369370567', '1162183369370563']

# project_id = get_project_id('EigenPrism Release Mgmt')
# cfmap = get_custom_fields_of_project(project_id)

# cf_ser = pd.Series(dtype=object)
# for cf in cfmap:
    # field = cf['custom_field']
    # enums = field.get('enum_options')
    # if enums is not None:
        # for e in enums:
            # custom_field_names_map[e['gid']] = e['name']
    # id = field['gid']
    # name = field['name']
    # custom_field_map[id] = name
    # cf_ser[id] = name

# section_frame = pd.DataFrame()
# sections = get_sections_of_project(project_id)
# for s in sections:
    # id = s['gid']
    # section_name_to_id[s['name']] = s['gid']
    # section_id_to_name[id] = s['name']
    # tasks_from_section = get_json_response('sections/{}/tasks'.format(id))
    # for t in tasks_from_section:
        # task_to_section_map[t['gid']] = s['gid']

# tag_name = 'AJG Punchlist'
# tasks_with_tag = get_tasks_of_tag(tag_name)
# tasks = pd.Series([t['gid'] for t in tasks_with_tag], name='task.id')
# task_sections = pd.Series(
    # [task_to_section_map.get(t['gid']) for t in tasks_with_tag],
    # name='section.id')

# section_ids = []
# section_names = []
# for k, v in section_id_to_name.items():
    # section_ids.append(k)
    # section_names.append(v)

# sec_df = pd.DataFrame({
    # 'section.id': section_ids,
    # 'section.name': section_names
# }).dropna()

# df = pd.concat([tasks, task_sections], axis=1)
# merged = pd.merge(df, sec_df, on='section.id', how='inner')
# merged.to_csv('merged.csv', index=False)

# task_dict = {
    # 'task.id': [],
    # 'task.name': [],
    # 'task.assigned.to': [],
    # 'task.due.date': [],
    # 'task.priority': [],
    # 'task.module': [],
    # 'task.url': []
# }

# for t in merged['task.id']:
#     task_dict['task.id'].append(t)
#     task_dict['task.url'].append('https://app.asana.com/0/{}/{}'.format(
#         project_id, t))
#     task = get_json_response('tasks/{}'.format(t))
#     fields = task['custom_fields']
#     task_dict['task.name'].append(task['name'])
#     task_dict['task.due.date'].append(task['due_on'])
#     assignee = task.get('assignee')
#     if assignee is not None:
#         task_dict['task.assigned.to'].append(assignee['name'])
#     else:
#         task_dict['task.assigned.to'].append(pd.NA)

#     for f in fields:
#         key = f.get('name')
#         if key == 'Priority' or key == 'Module':
#             value = pd.NA
#             enum = f.get('enum_value')
#             if enum is not None:
#                 value = enum.get('name')
#             task_dict['task.{}'.format(key.lower())].append(value)

# task_df = pd.DataFrame(task_dict)
# task_df.to_csv('tasks.csv', index=False)

# merged.merge(task_df, on='task.id',
#              how='inner').drop(labels=['task.id', 'section.id'],
#                                axis=1).to_csv('net.csv',
#                                               header=[
#                                                   'Status', 'Name',
#                                                   'Assigned To', 'Due Date',
#                                                   'Priority', 'Module', 'Url'
#                                               ],
#                                               index=False)


with tpe(max_workers=50) as executor:
    future_jsons = [executor.submit(get_json_response, 'tasks/{}'.format(t)) for t in tasks]
    time1 = time.time()
    for future in concurrent.futures.as_completed(future_jsons):
        try:
            data = future.result()
            print(data['gid'])
        except Exception as exc:
            print('exception')
        finally:
            print('done')
