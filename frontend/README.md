## Getting started 

### Docker 

```
# билд образа
docker build -t vite-image .
```

```
# запуск контейнера
docker run -it --name vite-container -p 5173:5173 vite-image
```

Веб-интерфейс доступен по ```http://localhost:5173/research```

```
# остановка контейнера
docker stop vite-container
```

```
# удаление контейнера и образа
docker rm vite-container
docker rmi vite-image
```

### Make (alternative)

```
# simple run
make run_app
```

Веб-интерфейс доступен по ```http://localhost:5173/research```

```
# simple stop
make stop_app
```
