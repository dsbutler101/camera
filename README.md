# Motion Detecting Security Camera

Sample project to demonstrate a motion/face detecting security camera running on a Raspberry Pi using  GCP Cloud Functions, Vision API integrated with Cloud Storage

## How it works?

1. Motion software runs on Raspberry Pi, detecting  movement and triggering a script to upload images to Google Cloud storage bucket (Raspberry Pi config details coming shortly)
2. The object key (or image path) for image uses a naming convention that captures the user's email address, camera name and whether the user's mobile phone is 'home' or 'away' (eg. connected to the local WiFi network or not)
3. Once the upload is completed, a Google Cloud Function script is triggered and uses the Google Vision API to perform facial recognition on the image only if the user's phone is 'away' (prevents images being scanned unnecessarily if the user is home)
4. If a face is detected an email is sent to the user via the Send Grid SMTP service with the image attached and a short note containing additional information such as the name of the camera that captured the image

## Prequisites

The installation process uses Google Cloud Deployment Manager to configure GCP and Ansible to configure the Raspberry Pi. Details of the Raspberry Pi Ansible configuration will be added shortly. 

In the meantime, this guide assumes you have the following prerequisites in place for GCP:

* Downloaded the latest version of the Google Cloud Platform [gcloud CLI and SDK](https://cloud.google.com/sdk/)
* Created a new GCP project that the service will be deployed to
* Created a GCP user with sufficient permissions to deploy the GCP resources to your chosen project (eg. project editor)
* Authenticated the gcloud CLI using: `gcloud auth login <user_name>`
* Configured the gcloud CLI with your chosen project: `gcloud config set project <project_name>`
* Created a [free trial Send Grid SMTP account](https://signup.sendgrid.com) making a note of the API key details
* Edit the deployment-manager/config.yml and update the following information:

   `SEND_GRID_API_KEY:` - enter the long API key obtained from the previous step

   `SEND_GRID_DOMAIN:` - enter the domain suffix that will be used for sending notifications details

   `BUCKET_NAME:` - bucket name, must be [globally unique](https://cloud.google.com/storage/docs/naming)

## GCP Installation

* Change to the deployment-manager directory and run the following command (use 'update' instead of 'create' for subsequent updates):
`gcloud deployment-manager deployments create camera-resources --config config.yml`

## To-Do

* Add instructions to complete configuration of Raspberry Pi using Ansible
* Add instructions for allowing users to assume role that grants bucket upload access to specific locations only
