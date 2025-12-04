import docker
from typing import List, Optional, Dict
from app.schemas import ModelConfig, ContainerStatus

class DockerService:
    def __init__(self):
        self.client = docker.from_env()

    def get_container_by_model_id(self, model_id: str) -> Optional[docker.models.containers.Container]:
        containers = self.client.containers.list(all=True, filters={"label": f"orchestrator.model_id={model_id}"})
        if containers:
            return containers[0]
        return None

    def start_container(self, model_config: ModelConfig) -> ContainerStatus:
        container = self.get_container_by_model_id(model_config.id)
        print("model id", model_config.id)
        print("model source", model_config.source)
        
        if container:
            if container.status != "running":
                container.start()
            
            # Reload attributes to get port mapping if needed, though we know the config
            container.reload()
            return ContainerStatus(
                model_id=model_config.id,
                status=container.status,
                container_id=container.id,
                port=model_config.container_config.port
            )
        
        # Run new container
        try:
            # Ensure image exists (simple check, or pull)
            try:
                self.client.images.get(model_config.container_config.image)
            except docker.errors.ImageNotFound:
                # In a real scenario, we might pull or build. 
                # For now, we assume it's built locally as 'orchestrar-runner:latest'
                pass

            container = self.client.containers.run(
                model_config.container_config.image,
                detach=True,
                ports={'8000/tcp': model_config.container_config.port},
                environment={"MODEL_REPO_ID": model_config.repo_id},
                labels={"orchestrator.model_id": model_config.id},
                name=f"orchestrar-{model_config.id}"
            )
            return ContainerStatus(
                model_id=model_config.id,
                status="running", # It takes a moment to actually be 'running' but it's started
                container_id=container.id,
                port=model_config.container_config.port
            )
        except Exception as e:
            return ContainerStatus(model_id=model_config.id, status=f"error: {str(e)}")

    def stop_container(self, model_id: str) -> ContainerStatus:
        container = self.get_container_by_model_id(model_id)
        if container:
            container.stop()
            return ContainerStatus(model_id=model_id, status="stopped", container_id=container.id)
        return ContainerStatus(model_id=model_id, status="not_found")

    def remove_container(self, model_id: str) -> ContainerStatus:
        container = self.get_container_by_model_id(model_id)
        if container:
            try:
                container.stop()
            except:
                pass # Might be already stopped
            container.remove()
            return ContainerStatus(model_id=model_id, status="removed")
        return ContainerStatus(model_id=model_id, status="not_found")

    def list_running_models(self) -> List[ContainerStatus]:
        containers = self.client.containers.list(filters={"label": "orchestrator.model_id"})
        statuses = []
        for c in containers:
            model_id = c.labels.get("orchestrator.model_id")
            # Find mapped port
            # Ports format: {'8000/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '8001'}]}
            ports = c.attrs['NetworkSettings']['Ports']
            host_port = None
            if '8000/tcp' in ports and ports['8000/tcp']:
                host_port = int(ports['8000/tcp'][0]['HostPort'])

            statuses.append(ContainerStatus(
                model_id=model_id,
                status=c.status,
                container_id=c.id,
                port=host_port
            ))
        return statuses
