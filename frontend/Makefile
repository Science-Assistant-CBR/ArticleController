.PHONY: *  # Ensures all targets are treated as phony


IMAGE_NAME=vite-image
CONTAINER_NAME=vite-container

# ================== RUN WEB INTERFACE ==================
run_app:
	@echo "=== Running container ==="
	docker build -t $(IMAGE_NAME) .
	docker run -it --name $(CONTAINER_NAME) -p 5173:5173 $(IMAGE_NAME)
	@echo "=== Web is up ==="

# ================== STOP AND DELETE CONTAINER ==================
stop_app:
	@echo "=== Stopping and removing the container ==="
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME) || true
	@echo "=== Container has been stopped and removed ==="
