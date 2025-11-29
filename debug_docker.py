try:
    from app.services.docker_service import DockerService
    print("Import successful")
    svc = DockerService()
    print("DockerService initialized")
    print(svc.list_running_models())
except Exception as e:
    print(f"Error: {e}")
