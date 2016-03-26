# -*- coding: utf-8 -*-
import glob
import os.path
from flask import Flask, render_template, make_response, request, redirect, url_for
app = Flask(__name__)

userlist = dict()
datalist = []

def save_user(user):
    with open(os.path.join('users', user), 'w') as f:
        f.write(str(userlist[user]))

def load_datalist(datafile):
    with open(datafile, 'r') as f:
        return [x.strip().split() for x in f.readlines()]

def load_users():
    users = dict()
    for userfile in sorted(glob.glob('./users/*')):
        name = os.path.split(userfile)[-1]
        print name
        with open(userfile, 'r') as f:
            users[name] = int(f.read()) 
    return users

def new_user(user):
    global userlist
    userlist[user] = 0
    save_user(user)

def get_pair(user):
    return datalist[userlist[user]]

@app.route('/')
def index():
    if 'name' not in request.cookies or request.cookies['name'] not in userlist:
        return render_template('login.html')
    name = request.cookies['name']
    if userlist[name] == len(datalist):
        return render_template('end.html')
    pair = get_pair(name)
    return render_template('index.html', left_id=pair[0], right_id=pair[1])

def log_choice(name, a, b):
    print name, a, b
    #with open(os.path.join('./logs', name+'.txt'), 'a') as f:
        #print >>f, a, b
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
    if len(name) < 4 or len(name) > 20:
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
    datalist = load_datalist('data.txt')
    userlist = load_users()
    print userlist, datalist
    app.run(host='0.0.0.0',port=8888,debug=True)
