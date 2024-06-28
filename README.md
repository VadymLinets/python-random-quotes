# Quotes service

## Description

It's a service that shows random quotes, allows to like them and show quote that is pretty similar to a specified one

## Additional programs

1. [Taskfile](https://taskfile.dev/installation/) (Optional)
2. docker-compose or podman-compose
3. [Postman](https://www.postman.com/downloads/)

## How to run

1. Copy the [.env.example](.env.example) file to `.env` and change variables to what you need

   ```shell
   cp .env.example .env && nano .env
   ```

2. Start the postgres database

   > **<span style="color:#79b6c9">ⓘ NOTE:</span>** If you're starting the program by running the taskfile command, you
   can skip this step because db will start up automatically

   ```shell
   export POSTGRES_PORT=5432 POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=quotes
   cd containers && docker-compose -f database.yml up -d && cd ..
   ```

   Or

   ```shell
   task db
   ```

3. Run the following command:

    ```shell
    fastapi dev main.py --host "0.0.0.0" --port 1140
    ```

4. Or you can run the following taskfile command:

    ```shell
    task run
    ```

5. Import [Quotes](./postman/Quotes.postman_collection.json) collection into `Postman` program
6. Send request throw `Postman`
