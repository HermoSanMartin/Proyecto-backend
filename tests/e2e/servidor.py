"""Proceso Uvicorn de prueba. El cierre de stdin solicita una parada ordenada."""

import sys
from pathlib import Path
from threading import Thread

import uvicorn


def main():
    config = uvicorn.Config("app.main:app", host="127.0.0.1", port=0, log_level="warning")
    servidor = uvicorn.Server(config)

    def esperar_cierre():
        sys.stdin.buffer.read()
        servidor.should_exit = True

    with config.bind_socket() as sock:
        Thread(target=esperar_cierre, daemon=True).start()
        Path(sys.argv[1]).write_text(str(sock.getsockname()[1]))
        servidor.run(sockets=[sock])


if __name__ == "__main__":
    main()
