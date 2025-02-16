import boto3
import time
import argparse

def monitor_training_job(job_name):
    sm_client = boto3.client('sagemaker')
    
    print(f"Monitoring training job: {job_name}")
    while True:
        response = sm_client.describe_training_job(TrainingJobName=job_name)
        status = response["TrainingJobStatus"]
        print(f"Training job status: {status}")
        
        if status in ["Completed", "Failed", "Stopped"]:
            print(f"Training job ended with status: {status}")
            break
        
        time.sleep(30)

def main():
    parser = argparse.ArgumentParser(description="Monitor a SageMaker training job.")
    parser.add_argument("--job-name", required=True, help="Name of the SageMaker training job")

    args = parser.parse_args()
    monitor_training_job(args.job_name)

if __name__ == "__main__":
    main()
