import time
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()


class Post(BaseModel):
    name: str
    address: str
    city: str
    state: str
    postal: str
    country: str
    phone: str
    url: str


try:
    conn = psycopg2.connect(
        host="localhost",
        database="samplepostgres",
        user="testuser",
        password="password123",
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()
    print("Database connection is successful")
except Exception as e:
    print("Connection failed", e)
    time.sleep(2)


@app.get("/")
def getDetails():
    cursor.execute("""SELECT * FROM museum ORDER BY museum_id ASC """)
    details = cursor.fetchall()
    # conn.commit()
    return {"details": details}

@app.get("/posts/latest")
def getLatestEntry():
    cursor.execute("""SELECT * FROM museum WHERE museum_id = (SELECT MAX(museum_id) FROM museum )""")
    latest_post = cursor.fetchone()
    return latest_post


@app.post("/posts/{id}", status_code=status.HTTP_201_CREATED)
def createPost(id: int, post: Post):
    cursor.execute(
        """INSERT INTO museum (museum_id,name,address,city,state,postal,country,phone,url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING * """,(str(id),post.name,post.address,post.city,post.state,post.postal,post.country,post.phone,post.url) )
    
    insert_post = cursor.fetchall()
    conn.commit()

    if insert_post == None:
        raise HTTPException(status_code=404, detail=f"Item with id {id} not found")

    return Response(status_code=status.HTTP_201_CREATED)

@app.post("/posts/{id}")
def getPosts(id: int):
    item_id = str(id)
    # cursor.execute(f"""SELECT * FROM museum WHERE museum_id = {id} """)
    cursor.execute("""SELECT * FROM museum WHERE museum_id= {0} """.format(item_id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
    return post

@app.put("/posts/{id}")
def updatePost(id: int, post: Post):
    cursor.execute(
        """UPDATE museum SET name = {0},address={1},city={2},state={3},postal={4},country={5},phone={6},url={7},museum_id={8} WHERE museum_id= {9} """.format(
            post.name,
            post.address,
            post.city,
            post.state,
            post.postal,
            post.country,
            post.phone,
            post.url,
            post.museum_id,
            str(id),
        )
    )

    update_post = cursor.fetchone()
    conn.commit()

    if update_post == None:
        raise HTTPException(
            status_code=404,
            detail=f"Post you are trying to update with id {id} doesn't exists.",
        )


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(id: int):
    cursor.execute(
        """DELETE FROM museum WHERE museum_id= {0} returning * """.format(str(id)),
    )
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(
            status_code=404,
            detail=f"Post you want to delete with id {id} does not exists.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
