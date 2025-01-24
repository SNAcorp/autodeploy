from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import docker

app = FastAPI()
client = docker.from_env()


@app.get("/")
async def health_check():
    return {"status": "healthy"}


@app.post("/deploy")
async def deploy():
    try:
        # Создаем команду для выполнения на хосте через Docker API
        container = client.containers.get('host-runner')  # Контейнер с доступом к Docker socket

        # Git pull
        git_result = container.exec_run(
            cmd=['sh', '-c', 'cd nomerhub_front && git pull'],
            privileged=True
        )
        git_output = git_result.output.decode()

        # Docker compose up
        compose_result = container.exec_run(
            cmd=['sh', '-c', 'cd nomerhub_front && docker compose up --build -d'],
            privileged=True
        )
        compose_output = compose_result.output.decode()

        if git_result.exit_code != 0 or compose_result.exit_code != 0:
            raise subprocess.CalledProcessError(
                git_result.exit_code or compose_result.exit_code,
                'host commands',
                output=f"Git: {git_output}\nCompose: {compose_output}"
            )

        return JSONResponse(content={
            'status': 'success',
            'git_output': git_output,
            'compose_output': compose_output
        })

    except Exception as e:
        error_message = str(e)
        return JSONResponse(status_code=500, content={
            'status': 'error',
            'message': error_message
        })


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)


if __name__ == "__main__":
    main()