import websockets
import asyncio
import sqlite3
import json

con = sqlite3.connect("db.db", autocommit=True)
cur = con.cursor()

users = {}
connections = set()

async def handler(websocket):
    try:
        uname = ""
        loggedin = False
        connections.add(websocket)
        print(f"{websocket.remote_address} connected")

        async for msg in websocket:
            msg = json.loads(msg)
            match msg["type"]:
                case 0:
                    #send msg
                    if(loggedin):
                        cur.execute("INSERT INTO msgs VALUES ( ? , ? , ? , ? )", (msg["server"], uname, msg["time"], msg["content"]))
                        members = cur.execute("SELECT uname FROM servermemlist WHERE server = ?", (msg["server"],)).fetchall()
                        for user in users:
                            if (user,) in members:
                                await users[user].send(json.dumps({"type" : 0, "server" : msg["server"], "uname" : uname, "time" : msg["time"], "content" : msg["content"]}))
                        print(f"{uname} sending '{msg["content"]}'")
                case 1:
                    #get last 50 msgs and server members
                    if(loggedin):
                        if((msg["server"],) in cur.execute("SELECT server FROM servermemlist WHERE uname = ?", (uname,)).fetchall()):
                            for sender, time, content in cur.execute("SELECT uname, time, content FROM msgs WHERE server = ? ORDER BY time ASC LIMIT 50", (msg["server"],)):
                                await websocket.send(json.dumps({"type" : 0, "server" : msg["server"], "uname" : sender, "time" : time, "content" : content}))                            
                            await websocket.send(json.dumps({"type" : 1, "members" : cur.execute("SELECT uname FROM servermemlist WHERE server = ?", (msg["server"],)).fetchall()}))
                        print(f"{uname} fetching {msg["server"]} data")
                case 3:
                    #join server
                    if(loggedin):
                        if(not msg["new?"]):
                            if(cur.execute("SELECT * FROM servermemlist WHERE server = ?", (msg["server"],)).fetchall()):
                                cur.execute("INSERT INTO servermemlist VALUES ( ? , ? )", (msg["server"], uname))
                        else:
                            cur.execute("INSERT INTO servermemlist VALUES ( ? , ? )", (msg["server"], uname))
                        await websocket.send("success")
                        print(f"{uname} joined {msg["server"]}")
                case 4:
                    #logon/signup
                    check = cur.execute("SELECT pass FROM users WHERE uname = ?", (msg["uname"],)).fetchone()
                    if(check):
                        print(f"{check[0]} == {hash(msg["pass"])}")
                        if(check[0] == hash(msg["pass"])):
                            uname = msg["uname"]
                            users[uname] = websocket
                            servers = cur.execute("SELECT server FROM servermemlist WHERE uname = ?", (uname,)).fetchall()
                            await websocket.send(json.dumps({"type":4, "servers" : servers}))
                            print(f"{uname} logged on")
                            loggedin = True
                    else:
                        uname = msg["uname"]
                        cur.execute("INSERT INTO users VALUES ( ? , ? )", (uname, hash(msg["pass"])))
                        users[uname] = websocket
                        servers = cur.execute("SELECT server FROM servermemlist WHERE uname = ?", (uname,)).fetchall()
                        await websocket.send(json.dumps({"type":4, "servers" : servers}))
                        print(f"{uname} signed up")
                        loggedin = True
            con.commit()
    finally:
        del users[uname]
        print(f"{uname} logging off")
        
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8002):
        print("server@ws://0.0.0.0:8002")
        await asyncio.Future()

asyncio.run(main())