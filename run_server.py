from __future__ import annotations

import os
import socket

import uvicorn


def _is_port_available(host: str, port: int) -> bool:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			sock.bind((host, port))
		except OSError:
			return False
	return True


def _pick_port(host: str, preferred_port: int, search_window: int = 20) -> int:
	for offset in range(search_window + 1):
		candidate = preferred_port + offset
		if _is_port_available(host, candidate):
			return candidate

	raise RuntimeError(
		f"No free port found in range {preferred_port}-{preferred_port + search_window}."
	)


def main() -> None:
	host = os.getenv("HOST", "0.0.0.0")
	port_env = os.getenv("PORT")
	preferred_port = int(port_env or "8000")
	port = preferred_port
	reload_enabled = os.getenv("RELOAD", "0") == "1"

	# If PORT is explicitly set, keep strict behavior for predictable deployments.
	if not port_env:
		port = _pick_port(host=host, preferred_port=preferred_port)
		if port != preferred_port:
			print(
				f"Port {preferred_port} is in use. Starting server on available port {port}."
			)

	uvicorn.run(
		"app.main:app",
		host=host,
		port=port,
		reload=reload_enabled,
	)


if __name__ == "__main__":
	main()
