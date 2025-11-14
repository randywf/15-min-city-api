Installation of UV for Windows
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Synchronizing your local environment with this one. 
```
uv sync
```

Serving of the server, enter this in command line. 
```
uvicorn app:app --reload
``` 

This is normal text. 