To initialize the whole server use init.sh! 
This is needed, because we always want a reasonable version of the road-network and we should not store files this big in Git.

Installation of UV
```
pip install uv
```

Synchronizing your local environment with this one. 
```
uv sync
```

Serving of the server, enter this in command line. 
```
uvicorn app:app --reload
``` 

