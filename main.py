from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import subprocess

app = FastAPI()


@app.get("/")
async def lol():
    return {"msg": "lol"}


@app.post("/deploy")
async def deploy():
    try:
        result = subprocess.run(['git', 'pull'], cwd='nomerhub_front', check=True, capture_output=True, text=True)
        git_output = result.stdout

        result = subprocess.run(['docker compose', 'up', '--build', '-d'], cwd='nomerhub_front', check=True, capture_output=True,
                                text=True)
        up_output = result.stdout

        return JSONResponse(content={
            'status': 'success',
            'git_output': git_output,
            'up_output': up_output
        })

    except subprocess.CalledProcessError as e:
        error_message = f"Command '{e.cmd}' returned non-zero exit status {e.returncode}."
        return JSONResponse(status_code=500, content={
            'status': 'error',
            'message': error_message,
            'output': e.output.decode()
        })


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)


if __name__ == "__main__":
    main()
