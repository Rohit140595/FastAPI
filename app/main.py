from cmd import IDENTCHARS
from random import randrange
from turtle import title
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres",
                                password="1495", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!!!")
        break
    except Exception as error:
        print("Connection to database failed!!")
        print("Error: ", error)
        time.sleep(3)
 

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """ ,
                  (post.title, post.content, post.published))
    # Retrieve post
    new_post = cursor.fetchone()
    # Push changes to database
    conn.commit()

    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} is not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    post = cursor.fetchone()
    conn.commit()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} is not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} is not found")
    return {'data': updated_post}