# -*- coding: utf-8 -*-
import glob
import random
import os.path
import argparse
from flask import Flask, render_template, make_response, request, redirect, url_for
app = Flask(__name__)

userlist = dict() #keep record of current progress of all users
datalist = dict()
groupdata = [] 
group = []
max_people = 6
max_group  = 4

# 24 people * 600 = (3 * 800) * 6
# 4 stages, each 600 pics

def save_user(user):
    with open(os.path.join('users', user), 'w') as f:
        f.write(str(userlist[user]))
    with open(os.path.join('userdata', user+'.txt'), 'w') as f:
        for x, y in datalist[user]:
            print >>f, x, y

def load_data(datafile):
    with open(datafile, 'r') as f:
        return [x.strip().split() for x in f.readlines()]

def load_datalist():
    res = dict()
    for user in userlist:
        res[user] = load_data(os.path.join('userdata', user+'.txt'))
    return res

def load_groupdata():
    return [load_data('data{}.txt'.format(i + 1)) for i in range(max_group)]

def load_users():
    users = dict()
    for userfile in sorted(glob.glob('./users/*')):
        name = os.path.split(userfile)[-1]
        #print name
        with open(userfile, 'r') as f:
            users[name] = int(f.read()) 
    return users

def save_group():
    with open('group.txt', 'w') as f:
        for g in group:
            print >>f, ' '.join(g)

def load_group(groupfile):
    res = []
    with open(groupfile, 'r') as f:
        for line in f.readlines():
            res.append(line.strip().split())
    return res

def new_user(user):
    global userlist
    x = 0
    while x < len(group):
        if user in group[x]:
            break
        if len(group[x]) < max_people:
            group[x].append(user)
            break
        x += 1
    if x == len(group):
        group.append([user])
    data = [[x, y] for x, y in groupdata[x]]
    random.seed(user)
    random.shuffle(data)
    datalist[user] = data
    userlist[user] = 0
    with open(os.path.join('userdata', user+'.txt'), 'w') as f:
        for x, y in datalist[user]:
            print >>f, x, y
    save_group()
    save_user(user)
    

def get_datalist(user):
    return datalist[user]

def get_pair(user):
    return get_datalist(user)[userlist[user]]


@app.route('/')
def index():
    if 'name' not in request.cookies or request.cookies['name'] not in userlist:
        return render_template('login.html')
    name = request.cookies['name']
    if userlist[name] == len(get_datalist(name)):
        return render_template('end.html')
    pair = get_pair(name)
    random.shuffle(pair)
    return render_template('index.html', left_id=pair[0], right_id=pair[1], 
            progress= (userlist[name] * 100 + len(get_datalist(name)) - 1) / len(get_datalist(name)))

def log_choice(name, a, b): #choice a over b
    print name, a, b
    if not app.debug:
        with open(os.path.join('./logs', name+'.txt'), 'a') as f:
            print >>f, a, b
    userlist[name] = userlist[name] + 1
    save_user(name)

@app.route('/choose', methods=['POST'])
def choose():
    left = request.form['left']
    right = request.form['right']
    choice = request.form['choice']
    name = request.cookies.get('name')
    if sorted(get_pair(name)) == sorted((left, right)):
        if left == choice:
            log_choice(name, left, right)
        elif right == choice:
            log_choice(name, right, left)
    return ('', 200)

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    if len(name) < 4 or len(name) > 20 or (not name.isalnum()):
        return render_template('login.html')
    if name not in userlist:
        new_user(name)
    response = make_response(render_template('intro.html'))
    response.set_cookie('name', name)
    return response

@app.route('/clear')
def clear():
    response = make_response(redirect(url_for('index')))
    response.set_cookie('name', '', expires=0)
    return response

if __name__ == '__main__':
    groupdata = load_groupdata()
    print len(groupdata)
    userlist = load_users()
    print userlist
    datalist = load_datalist()
    group    = load_group('group.txt')
    print group
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    app.run(host='0.0.0.0',port=8888, debug=args.debug)
