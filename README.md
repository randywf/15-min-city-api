<a id="readme-top"></a>

<div align="center">
 <h1>Welcome to the backend repository for the 15-Minute City application</h1>

<br />
<div align="center">
  <p align="center">
    <img src="image/logo_15min.png" alt="15-min-city" width="300"/>
  </p>
</div>

  

  <p align="center">
    An application to explore the city of Münster and find your ideal location!
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    &middot;
    <a href="https://github.com/othneildrew/Best-README-Template/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/othneildrew/Best-README-Template/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

## Contributors

<p align="center">
  <a href="https://github.com/Hex-commits">
    <img src="https://avatars.githubusercontent.com/Hex-commits?s=120" width="80" alt="Jan-Philipp Wegmeyer"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/randywf">
    <img src="https://avatars.githubusercontent.com/randywf?s=120" width="80" alt="Randy Flores"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/pmunding">
    <img src="https://avatars.githubusercontent.com/pmunding?s=120" width="80" alt="Philipp Mundinger"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/nimesh7814">
    <img src="https://avatars.githubusercontent.com/nimesh7814?s=120" width="80" alt="Nimesh Akalanka"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/laurenfissel11-ux">
    <img src="https://avatars.githubusercontent.com/laurenfissel11-ux?s=120" width="80" alt="Lauren"/>
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/Aadilwaris">
     <img src="https://avatars.githubusercontent.com/Aadilwaris?s=120" width="80" alt="Adil Waris"/>
  </a>
</p>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

### Built With

![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Isochrone](https://img.shields.io/badge/Isochrone-Routing-green)
![Stack Overflow](https://img.shields.io/badge/StackOverflow-Used-orange)

-

## Description of the application


## How to Install and Run the Application

### Initialization (Recommended)

To initialize the complete backend environment, run the provided `init.sh` script.

> **Requirements**
- Java **11+** must be installed  
- Required to download and process the road network data  
- Large network files are intentionally **not stored in Git**

```sh
./init.sh compose up --build app
````

## Local Installation (Without Docker)

Follow these steps if you want to run the backend **without Docker**.

### 1. Install `uv`

`uv` is used to manage and synchronize the Python environment.

```sh
pip install uv
```

### 2. Synchronize the Local Environment

This step installs all required dependencies defined in the project configuration and ensures your local Python environment matches the expected setup.

```sh
uv sync
```
### 3. Start the backend server

Run the FastAPI application in development mode with auto-reload enabled.  
The server will automatically restart when code changes are detected.

```sh
uvicorn app:app --reload
```

Once started, the API will be available at:

| Service                         | URL                           |
|---------------------------------|-------------------------------|
| API Root                        | http://localhost:8000         |
| Interactive API Docs (Swagger)  | http://localhost:8000/docs    |
| Alternative API Docs (ReDoc)    | http://localhost:8000/redoc   |


<hr>

<hr>

<div align="center" style="font-size: 0.85em; color: #666; line-height: 1.6;">

© 2026 <strong>15-min-city</strong><br>
<strong>Course:</strong> Geoinformation in Society<br>
<strong>Responsible:</strong> Contact contributors<br>
<strong>Date:</strong> 02.02.2026<br>
<strong>University of Münster</strong>

</div>
