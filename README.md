To initialize the whole server use init.sh! \
Be sure to have Java 11+ running on this server.
This is needed, because we always want a reasonable version of the road-network and we should not store files this big in Git.



---
 
Makefile-Alternative
-


Local-Installation:


Installation of UV
```sh
pip install uv
```

Synchronizing your local environment with this one. 
```sh
uv sync
```

Serving of the server, enter this in command line. 
```sh
uvicorn app:app --reload
``` 

Container:

For docker compose setup, completely separate from prior steps.
````sh
docker compose up --build app
```` 
