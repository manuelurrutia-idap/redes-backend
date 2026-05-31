from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, models, schemas, crud, algorithms

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Project Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Projects ---

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    return crud.create_project(db=db, project=project)

@app.get("/projects/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_projects(db, skip=skip, limit=limit)

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(database.get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    crud.delete_project(db, project_id)
    return {"message": "Project deleted"}

# --- Activities ---

@app.post("/projects/{project_id}/activities/", response_model=schemas.Activity)
def create_activity(project_id: int, activity: schemas.ActivityCreate, db: Session = Depends(database.get_db)):
    return crud.create_activity(db=db, activity=activity, project_id=project_id)

@app.get("/projects/{project_id}/activities/", response_model=list[schemas.Activity])
def read_activities(project_id: int, db: Session = Depends(database.get_db)):
    return crud.get_activities(db, project_id=project_id)

@app.put("/activities/{activity_id}", response_model=schemas.Activity)
def update_activity(activity_id: int, activity: schemas.ActivityUpdate, db: Session = Depends(database.get_db)):
    db_act = crud.update_activity(db, activity_id=activity_id, activity_update=activity)
    if not db_act:
        raise HTTPException(status_code=404, detail="Activity not found")
    return db_act

@app.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(database.get_db)):
    crud.delete_activity(db, activity_id)
    return {"message": "Activity deleted"}

# --- Dependencies ---

@app.post("/projects/{project_id}/dependencies/", response_model=schemas.Dependency)
def create_dependency(project_id: int, dependency: schemas.DependencyCreate, db: Session = Depends(database.get_db)):
    # Verify both activities exist and belong to the project
    from_act = crud.get_activity(db, dependency.from_activity_id)
    to_act = crud.get_activity(db, dependency.to_activity_id)
    if not from_act or from_act.project_id != project_id:
        raise HTTPException(status_code=400, detail="From Activity not found in this project")
    if not to_act or to_act.project_id != project_id:
        raise HTTPException(status_code=400, detail="To Activity not found in this project")
        
    # Cycle detection
    nodes = crud.get_activities(db, project_id)
    edges = crud.get_dependencies(db, project_id)
    if algorithms.has_cycle(nodes, edges, dependency.from_activity_id, dependency.to_activity_id):
        raise HTTPException(status_code=400, detail="Error: Crear esta dependencia generaría un ciclo en el grafo.")
        
    return crud.create_dependency(db=db, dependency=dependency, project_id=project_id)

@app.get("/projects/{project_id}/dependencies/", response_model=list[schemas.Dependency])
def read_dependencies(project_id: int, db: Session = Depends(database.get_db)):
    return crud.get_dependencies(db, project_id=project_id)

@app.put("/dependencies/{dependency_id}", response_model=schemas.Dependency)
def update_dependency(dependency_id: int, dependency: schemas.DependencyUpdate, db: Session = Depends(database.get_db)):
    db_dep = crud.update_dependency(db, dependency_id=dependency_id, dependency_update=dependency)
    if not db_dep:
        raise HTTPException(status_code=404, detail="Dependency not found")
    return db_dep

@app.delete("/dependencies/{dependency_id}")
def delete_dependency(dependency_id: int, db: Session = Depends(database.get_db)):
    crud.delete_dependency(db, dependency_id)
    return {"message": "Dependency deleted"}

# --- Algorithms ---

@app.get("/projects/{project_id}/algorithms/shortest-path")
def shortest_path(project_id: int, algo: str, source: int, target: int = None, db: Session = Depends(database.get_db)):
    nodes = crud.get_activities(db, project_id)
    edges = crud.get_dependencies(db, project_id)
    
    if algo == 'dijkstra':
        return algorithms.dijkstra(nodes, edges, source, target)
    elif algo == 'bellman-ford':
        return algorithms.bellman_ford(nodes, edges, source, target)
    elif algo == 'floyd-warshall':
        return algorithms.floyd_warshall(nodes, edges)
    elif algo == 'a*':
        if not target: raise HTTPException(status_code=400, detail="Target required for A*")
        return algorithms.a_star(nodes, edges, source, target)
    else:
        raise HTTPException(status_code=400, detail="Unknown algorithm")

@app.get("/projects/{project_id}/algorithms/mst")
def mst(project_id: int, algo: str, db: Session = Depends(database.get_db)):
    nodes = crud.get_activities(db, project_id)
    edges = crud.get_dependencies(db, project_id)
    
    if algo == 'prim':
        return algorithms.prim(nodes, edges)
    elif algo == 'kruskal':
        return algorithms.kruskal(nodes, edges)
    else:
        raise HTTPException(status_code=400, detail="Unknown algorithm")

@app.get("/projects/{project_id}/algorithms/max-flow")
def max_flow(project_id: int, source: int, target: int, db: Session = Depends(database.get_db)):
    nodes = crud.get_activities(db, project_id)
    edges = crud.get_dependencies(db, project_id)
    return algorithms.ford_fulkerson(nodes, edges, source, target)

@app.get("/projects/{project_id}/algorithms/cpm")
def project_cpm(project_id: int, db: Session = Depends(database.get_db)):
    nodes = crud.get_activities(db, project_id)
    edges = crud.get_dependencies(db, project_id)
    return algorithms.cpm(nodes, edges)

@app.get("/projects/{project_id}/algorithms/pert")
def project_pert(project_id: int, db: Session = Depends(database.get_db)):
    nodes = crud.get_activities(db, project_id)
    edges = crud.get_dependencies(db, project_id)
    return algorithms.pert(nodes, edges)
