from fastapi import FastAPI, Depends, HTTPException
from schemas import Todo as TodoSchema, TodoCreate
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import Todo 

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

# POST - Create TODO

@app.post("/todos", response_model=TodoSchema)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    #converting api obect to database object
    db_todo = Todo(**todo.dict())
    #adding the object to the database
    db.add(db_todo)
    #committing the changes
    db.commit()
    #refreshing the object to get the id
    db.refresh(db_todo)
    #returning the object to the api
    return db_todo


@app.get("/todos", response_model=list[TodoSchema])
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos

@app.get("/todos/{todo_id}", response_model=TodoSchema)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo(todo_id: int, updated_todo: TodoCreate, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key,value in updated_todo.dict().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"detail": "Todo deleted successfully"}