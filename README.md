# label-studio-doctr-ocr-backend
The aim of this repository is to create and make available an image text annotation tool based on Doctr OCR.


1. Build and start Machine Learning backend on `http://localhost:9090`

```bash
docker-compose up
```

2. Validate that backend is running

```bash
$ curl http://localhost:9090/health
{"status":"UP"}
```

3. Connect to the backend from Label Studio: go to your OCR project `Settings -> Machine Learning -> Add Model` and specify `http://localhost:9090` as a URL.


# TODO: If everything else id done create a well documented README.md file
# TODO: Code formatting style, etc.