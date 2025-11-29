# Orchestrar SLM Server

A local Orchestrator Server to manage and deploy Small Language Models (SLMs) in isolated Docker containers.

## Features

- **Model Registry**: Manage models via `config/models.yaml`.
- **Docker Isolation**: Each model runs in its own container.
- **REST API**: List, start, stop, and query models.
- **On-demand Loading**: Models are started only when requested.

## Prerequisites

- Docker Engine installed and running.
- Python 3.9+

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Build Runner Image**:
    The server uses a generic runner image. Build it first:

    ```bash
    docker build -t orchestrar-runner:latest runner/
    ```

3.  **Configure Models**:
    Edit `config/models.yaml` to add your HuggingFace models.

## Usage

1.  **Start the Server**:

    ```bash
    uvicorn app.main:app --reload
    ```

2.  **API Endpoints**:
    - `GET /models`: List available models.
    - `POST /run`: Start a model container.
      ```json
      { "model_id": "tiny-llama" }
      ```
    - `GET /status`: Check running models.
    - `POST /inference`: Run inference.
      ```json
      { "model_id": "tiny-llama", "prompt": "Hello" }
      ```
    - `POST /stop`: Stop a model container.

## Architecture

```mermaid
graph TD
    subgraph Client_Layer [Client Layer]
        User[User / Client]
        Postman[Postman / Scripts]
    end

    subgraph Orchestrator_Server [Orchestrator Server (Host: 8000)]
        direction TB
        FastAPI_App[FastAPI App]

        subgraph Endpoints
            E_Models[GET /models]
            E_Run[POST /run]
            E_Status[GET /status]
            E_Stop[POST /stop]
            E_Inference[POST /inference]
            E_Health[GET /health]
        end

        subgraph Services
            Reg[Model Registry]
            DockerSvc[Docker Service]
        end

        FastAPI_App --> E_Models & E_Run & E_Status & E_Stop & E_Inference & E_Health
        E_Models -->|Read Config| Reg
        E_Run -->|Start Container| DockerSvc
        E_Status -->|List Containers| DockerSvc
        E_Stop -->|Stop Container| DockerSvc
        E_Inference -->|Proxy Request| DockerSvc
    end

    subgraph Docker_Infrastructure [Docker Infrastructure]
        DockerDaemon[Docker Daemon]

        subgraph Model_Container [Model Container (Host: 8001+)]
            direction TB
            RunnerApp[Runner FastAPI (Port: 8000)]

            subgraph Runner_Endpoints
                R_Inference[POST /inference]
                R_Health[GET /health]
            end

            HF_Model[HuggingFace Model]

            RunnerApp --> R_Inference & R_Health
            R_Inference -->|Generate| HF_Model
        end
    end

    %% Flows
    User -->|HTTP Requests| FastAPI_App
    Postman -->|HTTP Requests| FastAPI_App

    DockerSvc -->|Docker API (Socket)| DockerDaemon
    DockerDaemon -->|Spin up| Model_Container

    E_Inference -.->|Proxy HTTP (127.0.0.1:8001)| R_Inference
```

- **Orchestrator**: FastAPI app managing the lifecycle.
- **Runner**: A separate Docker image (`orchestrar-runner`) that loads the model using `transformers` and exposes an internal API.
