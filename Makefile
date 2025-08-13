# ==== Config (можешь переопределять через env/CLI) ===========================
NETWORK               ?= mentalmentor_default
API_BASE              ?= http://api:8000
MINIO_SERVICE         ?= minio:9000
MINIO_BUCKET          ?= mentalmentor
MINIO_USER            ?= minioadmin
MINIO_PASS            ?= minioadmin

# ==== Helpers ================================================================
.PHONY: help
help:
	@echo "Targets:"
	@echo "  upload-presigned FILE=./intro.pdf URL='https://...signed'   - загрузить файл по presigned PUT"
	@echo "  download-presigned URL='https://...signed' OUT=./out.pdf    - скачать presigned GET"
	@echo "  upload-mc FILE=./intro.pdf DEST=courses/intro_v1.pdf        - загрузить через minio/mc по ключам"
	@echo "  api-presigned-upload KEY=courses/intro_v1.pdf TOKEN=...     - получить presigned PUT от API"
	@echo "  api-create-course TOKEN=... SLUG=... TITLE=... SUMMARY=... KEY=... PAGES=... VERSION=1 PUBLIC=true"
	@echo "  api-create-with-file TOKEN=... FILE=./intro.pdf SLUG=... TITLE=... SUMMARY=... VERSION=1 PUBLIC=true"
	@echo ""
	@echo "Параметры по умолчанию можно менять вверху файла (NETWORK, API_BASE, MINIO_*)"

# ==== Presigned: upload через curl внутри контейнера =========================
# Пример: make upload-presigned FILE=./intro.pdf URL="https://minio...signature..."
.PHONY: upload-presigned
upload-presigned:
	@[ -n "$(FILE)" ] || (echo "ERROR: set FILE=./file.pdf" && exit 1)
	@[ -n "$(URL)" ]  || (echo "ERROR: set URL='https://...presigned'" && exit 1)
	docker run --rm -v "$$(pwd):/work" curlimages/curl:latest \
	  -X PUT -H "Content-Type: application/pdf" \
	  --fail --show-error --silent \
	  --upload-file /work/$(FILE) "$(URL)" && echo "OK: uploaded $(FILE)"

# ==== Presigned: download через curl ========================================
# Пример: make download-presigned URL="https://...signed" OUT=./intro-dl.pdf
OUT ?= ./download.pdf
.PHONY: download-presigned
download-presigned:
	@[ -n "$(URL)" ] || (echo "ERROR: set URL='https://...presigned'" && exit 1)
	docker run --rm -v "$$(pwd):/work" curlimages/curl:latest \
	  -L --fail --show-error --silent \
	  -o /work/$(OUT) "$(URL)" && echo "OK: saved to $(OUT)"

# ==== Прямая загрузка через minio/mc (без presigned) ========================
# Пример: make upload-mc FILE=./intro.pdf DEST=courses/intro_v1.pdf
.PHONY: upload-mc
upload-mc:
	@[ -n "$(FILE)" ] || (echo "ERROR: set FILE=./file.pdf" && exit 1)
	@[ -n "$(DEST)" ] || (echo "ERROR: set DEST=courses/your.pdf" && exit 1)
	docker run --rm --network=$(NETWORK) \
	  -e MC_HOST_local="http://$(MINIO_USER):$(MINIO_PASS)@$(MINIO_SERVICE)" \
	  -v "$$(pwd):/work" minio/mc:latest \
	  sh -lc "mc mb -p local/$(MINIO_BUCKET) || true && mc cp /work/$(FILE) local/$(MINIO_BUCKET)/$(DEST)" \
	  && echo "OK: uploaded to s3://$(MINIO_BUCKET)/$(DEST)"

# ==== Получить presigned PUT от нашего API (JSON) ============================
# Пример: make api-presigned-upload KEY=courses/intro_v1.pdf TOKEN=eyJ...
.PHONY: api-presigned-upload
api-presigned-upload:
	@[ -n "$(KEY)" ]   || (echo "ERROR: set KEY=courses/intro_v1.pdf" && exit 1)
	@[ -n "$(TOKEN)" ] || (echo "ERROR: set TOKEN=<access_token>" && exit 1)
	docker run --rm --network=$(NETWORK) curlimages/curl:latest \
	  -H "Authorization: Bearer $(TOKEN)" \
	  "$(API_BASE)/api/v1/courses/upload_url?key=$(KEY)"

# ==== Создать курс (метаданные) через API ===================================
# Пример:
# make api-create-course TOKEN=eyJ... SLUG=intro-mental TITLE="Введение" SUMMARY="..." KEY=courses/intro_v1.pdf PAGES=42 VERSION=1 PUBLIC=true
.PHONY: api-create-course
api-create-course:
	@[ -n "$(TOKEN)" ]  || (echo "ERROR: set TOKEN=<access_token>" && exit 1)
	@[ -n "$(SLUG)" ]   || (echo "ERROR: set SLUG=intro-mental" && exit 1)
	@[ -n "$(TITLE)" ]  || (echo "ERROR: set TITLE='...'" && exit 1)
	@[ -n "$(SUMMARY)" ]|| (echo "ERROR: set SUMMARY='...'" && exit 1)
	@[ -n "$(KEY)" ]    || (echo "ERROR: set KEY=courses/intro_v1.pdf" && exit 1)
	@[ -n "$(VERSION)" ]|| (echo "ERROR: set VERSION=1" && exit 1)
	@[ -n "$(PUBLIC)" ] || (echo "ERROR: set PUBLIC=true|false" && exit 1)
	docker run --rm --network=$(NETWORK) curlimages/curl:latest \
	  -H "Authorization: Bearer $(TOKEN)" \
	  -H "Content-Type: application/json" \
	  -d "{\"slug\":\"$(SLUG)\",\"title\":\"$(TITLE)\",\"summary\":\"$(SUMMARY)\",\"storage_key\":\"$(KEY)\",\"pdf_pages\":$(PAGES),\"version\":$(VERSION),\"is_public\":$(PUBLIC)}" \
	  "$(API_BASE)/api/v1/courses"

# ==== Загрузить файл и сразу создать курс (multipart) через API =============
# Удобно для dev/Swagger-подобного сценария, без presigned и mc
# Пример:
# make api-create-with-file TOKEN=eyJ... FILE=./intro.pdf SLUG=intro-mental TITLE="Введение" SUMMARY="..." VERSION=1 PUBLIC=true
.PHONY: api-create-with-file
api-create-with-file:
	@[ -n "$(TOKEN)" ]  || (echo "ERROR: set TOKEN=<access_token>" && exit 1)
	@[ -n "$(FILE)" ]   || (echo "ERROR: set FILE=./intro.pdf" && exit 1)
	@[ -n "$(SLUG)" ]   || (echo "ERROR: set SLUG=intro-mental" && exit 1)
	@[ -n "$(TITLE)" ]  || (echo "ERROR: set TITLE='...'" && exit 1)
	@[ -n "$(SUMMARY)" ]|| (echo "ERROR: set SUMMARY='...'" && exit 1)
	@[ -n "$(VERSION)" ]|| (echo "ERROR: set VERSION=1" && exit 1)
	@[ -n "$(PUBLIC)" ] || (echo "ERROR: set PUBLIC=true|false" && exit 1)
	docker run --rm --network=$(NETWORK) -v "$$(pwd):/work" curlimages/curl:latest \
	  -H "Authorization: Bearer $(TOKEN)" \
	  -F "slug=$(SLUG)" \
	  -F "title=$(TITLE)" \
	  -F "summary=$(SUMMARY)" \
	  -F "version=$(VERSION)" \
	  -F "is_public=$(PUBLIC)" \
	  -F "file=@/work/$(FILE);type=application/pdf" \
	  "$(API_BASE)/api/v1/courses/create_with_file"
