from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess

app = FastAPI()


@app.get("/")
async def health_check():
    return {"status": "healthy"}


@app.post("/deploy")
async def deploy():
    try:
        # Выполняем команды напрямую
        git_result = subprocess.run(
            'git pull',
            shell=True,
            cwd='../nomerhub_front',
            capture_output=True,
            text=True
        )

        compose_result = subprocess.run(
            'docker compose up --build -d',
            shell=True,
            cwd='../nomerhub_front',
            capture_output=True,
            text=True
        )

        return JSONResponse(content={
            'status': 'success',
            'git_output': git_result.stdout,
            'compose_output': compose_result.stdout
        })

    except subprocess.CalledProcessError as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': str(e),
                'output': e.stdout or e.stderr
            }
        )


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()