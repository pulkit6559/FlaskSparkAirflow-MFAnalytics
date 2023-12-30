# FlaskSparkAirflow-MFAnalytics

An application that facilitates monitoring Mutual Fund movement trends. API data is provided by [Indian Mutual Fund API](https://www.mfapi.in/). The focus of this repository is managing and scheduling Airflow DAG's which run ETL data pipelins through Spark jobs in a containerized environment. 
The processed data files are stored in Amazon S3 which are used by a Flask webserver to plot and monitor tends using Plotly.

The following core functionalities are implemeted:
1. Creating a Docker containerized enviroment which runs Airflow (webserver, worker, scheduler) and Spark cluster (master and worker nodes)
2. Built custom docker images for Airflow and Spark to facilitate interaction of the containers.
3. PySpark scripts to run ETL operations via spark jobs on requested mutual funds data.
4. Airflow DAG script to schedule and manage PySpark scripts.
5. Saving the processed data into an AWS S3 bucket as `.parquet` files for efficient access. 
6. Testing the ETL script with unittests.
7. Flask webserver which allows the user to **_thematically group Mutual funds_**, initiate data extraction, and plot the data on a dashboard.


![Alt text](tmp/images/Architecture.png?raw=true "Project Architecture")

## Project Overview

### 1. Thematically extract Mutual Funds
For example, Mutual Funds grouped to the theme `"technology"` are shown in the Figure

![Alt text](tmp/images/mf-dashboard.PNG?raw=true "Flask dashboard")

### 2. Submit job that starts the extraction of the selected mutual funds 
For each mutual fund in the group, a new DAG is initiated in Airflow. The DAG requires the `SchemeCode` as an input which is provided through the airflow-client API.
![Alt text](tmp/images/Flaskjobs.PNG?raw=true "Flask dashboard")

### 3. Plot the Mutual funds grouped by respective themes in a Plotly graph
![Alt text](tmp/images/MF-plot.PNG?raw=true "Flask dashboard")



### How to Run

0. ```mkdir -p ./dags ./logs ./plugins```
    ```
    # Before starting the containers, setup AWS credentials in docker-compose.yml
        AWS_ACCESS_KEY_ID: <>
        AWS_SECRET_ACCESS_KEY: <>
        AWS_DEFAULT_REGION: <>
    ```

1. Run `docker-compose up --build` in the project directory
2. Access the Airflow web UI at `http://localhost:8080`
3. Use the provided Airflow credentials to log in (`airflow:airflow`)
4. Explore and manage your DAGs (Directed Acyclic Graphs) in the Airflow web UI
5. Monitor Spark jobs using the Spark web UI at `http://localhost:8000`
6. Run Flask webserver
   ``` 
   pip install -r requirements.txt
   cd dashboard 
   python app.py
   ```


### Containers and Dependencies

This Docker Compose file orchestrates a multi-container environment for running Apache Airflow with Spark. The project involves several services, including Apache Airflow components, a PostgreSQL database, a Redis message broker, and Apache Spark components.

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
