from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from airflow import DAG
import airflow_client.client
from airflow.utils.dates import days_ago
from flask_sqlalchemy import SQLAlchemy

import airflow_client.client
from airflow_client.client.api import config_api, dag_api, dag_run_api
from airflow_client.client.model.dag_run import DAGRun

import uuid
import requests
import json

configuration = airflow_client.client.Configuration(
    host="http://localhost:8080/api/v1",
    username='airflow',
    password='airflow',
)
api_client = airflow_client.client.ApiClient(configuration) 
dag_run_api_instance = dag_run_api.DAGRunApi(api_client)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
db = SQLAlchemy(app)



with open(f"mf.json", "r") as data_file:
    mf_scheme_data = json.load(data_file)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_str = db.Column(db.String(50), nullable=False)
    fund_name = db.Column(db.String(50), default="")
    dag_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

class MFIdMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_str = db.Column(db.String(50))
    mf_ids = db.Column(db.String, nullable=False)  

@app.route('/')
def landing_page():
    try:
        jobs = Job.query.all()
    except:
        jobs=[]
    return render_template('index.html', jobs=jobs)


@app.route('/search', methods=['GET'])
def search():
    search_text = request.args['search_text']
    matched_lines = []
    for mf_id_name in mf_scheme_data:
        if search_text in mf_id_name['schemeName'].lower():
            matched_lines.append([mf_id_name['schemeCode'], mf_id_name['schemeName']])
                
    print(matched_lines[:5])
    
    jobs = Job.query.all()
    # matched_lines = ["Line 1", "Line 2", "Line 3"]  # Replace with actual matched lines
    return render_template('index.html', matched_lines=matched_lines[:5], jobs=jobs)


@app.route('/start_dag', methods=['POST', "GET"])
def start_dag():
    
    if request.form["btn"]=="Search Funds":
        return redirect(url_for('search', search_text=request.form['search_text']))
    # query_str = request.form['search_text']
    
    query_str = request.form['search_text']
    print("QUERY STR: ", query_str)
    
    matched_lines = []
    for mf_id_name in mf_scheme_data:
        if query_str in mf_id_name['schemeName'].lower():
            matched_lines.append([mf_id_name['schemeCode'], mf_id_name['schemeName']])
    print("matched_lines", matched_lines[:5])
    
    DAG_ID = f"spark_api_data_to_s3"
    
    for line in matched_lines[:5]:
        
        mf_id, mf_name = line[0], line[1]
        job_id=f'{mf_id}_' + str(uuid.uuid4().hex)
        # new_job = Job(id=str(job_id), query_str=str(query_str), status='started', timestamp=datetime.utcnow())
        new_job = Job(query_str=query_str, fund_name=mf_name, dag_id=job_id, status='Started')
        # Add the job to the database session
        db.session.add(new_job)
        # Commit the changes to the database
        db.session.commit()
        
        dag_run = DAGRun(
            dag_run_id=job_id,
            conf={"mf_id":str(mf_id)}
        )
        api_response = dag_run_api_instance.post_dag_run(DAG_ID, dag_run)
        print(api_response)

    return redirect(url_for('search', search_text=request.form['search_text']))

@app.route('/check_job_status')
def check_job_status():
    # Check the status of all jobs with status "Running" using Airflow client
    from airflow.api.client.local_client import Client
    client = Client(api_base_url='http://localhost:8080/api/v1')
    running_jobs = Job.query.all()

    DAG_ID = "spark_api_data_to_s3"
    for job in running_jobs:
        run_id = job.dag_id
        response = dag_run_api_instance.get_dag_run(dag_id=DAG_ID, dag_run_id=run_id, async_req=False)
        print("Status: ", run_id, response.state)
        job.status = str(response.state)
        
        db.session.commit()
        
        if job.status == "success":
            print(job.dag_id.split("_")[0], job.dag_id)
            new_mapping = MFIdMapping(query_str=job.query_str, mf_ids=job.dag_id.split("_")[0])
            print(MFIdMapping.query.all())
            db.session.add(new_mapping)  
            db.session.commit()
        
    return redirect(url_for('landing_page'))

@app.route('/delete_jobs')
def delete_jobs():
    Job.query.delete()
    # Commit the changes to the database
    db.session.commit()
    return render_template('index.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
