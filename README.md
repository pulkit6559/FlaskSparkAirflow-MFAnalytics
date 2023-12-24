# spark-airflow-docker-etl

In this repository, I have designed an ETL process that 
1. Extract data from an API
2. Transforms the data using Spark 
3. Loading this data into an AWS S3 bucket. We running this batch processes using Airflow by Spark job submit Operator in Airflow. 

API data is provided by [Indian Mutual Fund API](https://www.mfapi.in/), you can read more about the API online to learn more about it. The focus of this repository is running and scheduling Airflow DAG's which runs Spark jobs in a containerized environment. 


## Things to do;

*  Set up Apache Spark locally. 
*  Set up Apache Airflow on locally.
*  Write the Spark Jobs to Extract, Transform and Load the data. 
*  Design the Airflow DAG to trigger and schedule the Spark jobs.

### How to Run

```mkdir -p ./dags ./logs ./plugins```

1. Run `docker-compose up --build` in the project directory

    ```
    # Before starting the containers, setup AWS credentials in docker-compose.yml
        AWS_ACCESS_KEY_ID: <>
        AWS_SECRET_ACCESS_KEY: <>
        AWS_DEFAULT_REGION: <>
    ```
2. Access the Airflow web UI at `http://localhost:8080`
3. Use the provided Airflow credentials to log in (`airflow:airflow`)
4. Explore and manage your DAGs (Directed Acyclic Graphs) in the Airflow web UI
5. Monitor Spark jobs using the Spark web UI at `http://localhost:8000`

#### Starting the DAG manually
Access the Airflow web UI at `http://localhost:8080`


## Project Overview

This Docker Compose file orchestrates a multi-container environment for running Apache Airflow with Spark. The project involves several services, including Apache Airflow components, a PostgreSQL database, a Redis message broker, and Apache Spark components.

### Containers and Dependencies

1. **PostgreSQL Container (`postgres`):**
   - Image: `postgres:13`
   - Responsible for hosting the PostgreSQL database used by Apache Airflow.
   - Credentials:
     - Username: `airflow`
     - Password: `airflow`
     - Database: `airflow`
   - Healthcheck: Verifies the availability of the PostgreSQL service.

2. **Redis Container (`redis`):**
   - Image: `redis:latest`
   - Acts as a message broker for Celery, which is used for distributed task execution in Apache Airflow.
   - Healthcheck: Pings the Redis server to ensure its availability.

3. **Spark Master Container (`spark-master`):**
   - Image: Built from a custom Dockerfile located in the `./spark_image` directory.
   - Serves as the master node for Apache Spark.
   - Exposes ports `8000` for the Spark web UI and `7077` for the Spark master service.
   - Healthcheck: Checks the availability of the Spark web UI.

4. **Spark Worker Container (`spark-worker`):**
   - Image: Built from the same custom Dockerfile as the Spark Master.
   - Acts as a worker node for Apache Spark, connected to the Spark Master.
   - Healthcheck: Verifies the availability of the Spark worker.

5. **Airflow Webserver Container (`airflow-webserver`):**
   - Image: Built from a custom Dockerfile located in the `./custom_airflow_image` directory.
   - Runs the Apache Airflow webserver.
   - Exposes port `8080` for accessing the Airflow web UI.
   - Healthcheck: Checks the availability of the Airflow web UI.

6. **Airflow Scheduler Container (`airflow-scheduler`):**
   - Image: Same as the Airflow Webserver.
   - Manages the scheduling of tasks in Apache Airflow.

7. **Airflow Worker Container (`airflow-worker`):**
   - Image: Same as the Airflow Webserver.
   - Executes tasks distributed by the Airflow scheduler using Celery.

8. **Airflow Triggerer Container (`airflow-triggerer`):**
   - Image: Same as the Airflow Webserver.
   - Handles triggering of tasks in Apache Airflow.

9. **Airflow Initialization Container (`airflow-init`):**
   - Image: Same as the Airflow Webserver.
   - Initializes the Apache Airflow environment, including database setup and user creation.
   - Executes the `airflow version` command.

10. **Airflow CLI Container (`airflow-cli`):**
    - Image: Same as the Airflow Webserver.
    - Provides a command-line interface for Apache Airflow tasks.

11. **Flower Container (`flower`):**
    - Image: Same as the Airflow Webserver.
    - Runs Flower, a real-time web-based monitoring tool for Celery clusters.
    - Exposes port `5555` for accessing the Flower web UI.
    - Healthcheck: Verifies the availability of the Flower web UI.

### Environment Variables

- **Common Environment Variables (`&airflow-common-env`):**
  - Sets up common environment variables shared across Airflow containers.
  - Defines executor, database connection, Celery broker, and other configurations.
  - Includes AWS access key, secret key, and default region.

### Volumes

- **PostgreSQL Database Volume (`postgres-db-volume`):**
  - Persists the PostgreSQL database data to ensure data durability.




<!-- ```
source ~/.bashrc \
start-master.sh 
```

```
start-slave.sh spark://XXXXXXXXXXXX:7077
```
## Set up Apache Airflow on locally
```bash
bash scripts/airflow_installer.sh
```
## Run the Spark job to see if everything works on the Spark side
```bash
spark-submit --master spark://XXXXXXXXXXXX:7077 spark_etl_script.py
```

* If everything works as expected on the Spark side, now create the Airflow dags folder in AIRFLOW_HOME
```bash
mkdir ~/airflow/dags
```

* Move the Spark job DAG file to the Airflow dags folder
```bash
mv dags/spark_jobs_dag.py ~/airflow/dags
```

* Go to http://localhost:8080/ to access the Airflow UI -->
