from fastapi import FastAPI

# Import functions from sub-package
#from functions.func_a import run_func_a
#from functions.func_b import run_func_b
#from functions.func_c import run_func_c
#from functions.func_d import run_func_d

app = FastAPI()


@app.get("/reachability")
def endpoint_a():
    return #run_func_a()


@app.get("/poi")
def endpoint_b():
    return #run_func_b()

