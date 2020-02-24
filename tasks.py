import os, sys
from io import StringIO
from bs4 import BeautifulSoup as bsp
from bs4 import Comment, Tag

tree = None
with open('tasks.xml', 'r', encoding='utf-16') as f:
    tree = bsp(f, 'xml')

for task in tree.find_all():
    for c in task.children:
        if (isinstance(c, Tag)):
            print('-{}-'.format(c.name))
    print('\n\n\n\n')
