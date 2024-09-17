# Quotes service

## Description

It's a service that shows random quotes, allows to like them and show quote that is pretty similar to a specified one

## Additional programs

1. [Taskfile](https://taskfile.dev/installation/) (Optional)
2. docker-compose or podman-compose
3. [Postman](https://www.postman.com/downloads/) or [Yaak](https://yaak.app/download)
4. [uv](https://docs.astral.sh/uv/getting-started/installation/)

## How to run

1. Create new virtual environment and install deps

   ```shell
   uv sync
   ```

   Or you can initialize everything with the following taskfile command.
   In that case, you can skip point 2 and start from point 3:
   ```shell
   task init && nano .env
   ```

2. Copy the [.env.example](.env.example) file to `.env` and change variables to what you need

   ```shell
   cp .env.example .env && nano .env
   ```

3. Start the postgres database

   > **<span style="color:#79b6c9">ⓘ NOTE:</span>** If you're starting the program by running the taskfile command, you
   can skip this step because db will start up automatically

   ```shell
   export POSTGRES_PORT=5432 POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=quotes
   cd containers && docker-compose -f database.yml up -d && cd ..
   ```

   Or use next taskfile command:
   ```shell
   task db
   ```

4. Run the following command to start fastapi server:

    ```shell
    fastapi dev main.py --host "0.0.0.0" --port 1140
    ```

   Or you can run `Run uvicorn` configuration if you are using `PyCharm`

   Or you can run the following taskfile command:
   ```shell
   task run
   ```

5. Import [postman `Quotes` collection](./requests/Quotes.postman_collection.json) into `Postman` program
   or [yaak `Quotes` collection](./requests/yaak.quotes.json) into `Yaak` program

   > **<span style="color:#FCE205">⚠ WARNING:</span>** Postman `Quotes` collection contains only http requests, because
   of Postman limitations, so if you want to send graphql or grpc requests it's better to start with Yaak `Quotes`
   collection.

6. Send request throw `Postman` or `Yaak`
