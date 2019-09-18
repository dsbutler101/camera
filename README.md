# Motion Detecting Security Camera

This is a sample project to demonstrate a motion/face detecting security camera running on a Raspberry Pi using GCP Cloud Functions, Vision API, integrated with Cloud Storage and BigQuery.

## How it works?

1. Motion software runs on Raspberry Pi, detecting  movement and triggering a script to upload images to Google Cloud storage bucket (Raspberry Pi config details coming shortly)
2. The object key (or image path) for image uses a naming convention that captures the user's email address, camera name and whether the user's mobile phone is 'home' or 'away' (eg. connected to the local WiFi network or not).
3. Once the upload is completed, a Google Cloud Function script is triggered and calls the Google Vision API to perform facial recognition on the image. The Raspberry Pi uses a rather hacky method to determine whether you are at home (pings mobile phone device on LAN via configurable DNS entry) and only triggers the Cloud Funtion script if you are away to save on unnecessary Vision API calls.
4. If a face is detected an email is sent to the user via the Send Grid SMTP service with the image attached and a short note containing additional information such as the name of the camera that captured the image

## Overview of Repo

The repository is essentially divided in to two parts. The `deployment-manager` folder is used to deploy the 'backend' services hosted in GCP. This provides a Cloud Storage Bucket to host files, some Cloud Functions to perform facial recognition and email notification, and a BigQuery table to store all of the event data and allow you to do some analytics.

The `ansible` folder is used to deploy motion sensing software to the Raspberry Pi and configure it to upload images to Google Cloud Storage for facial recognition purposes.

## Backend Prequisites

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

## Backend Installation

* Change to the deployment-manager directory and run the following command (use 'update' instead of 'create' for subsequent updates):
`gcloud deployment-manager deployments create backend --config config.yml`

## Frontend Prerequisites Steps

This is ideally suited the Raspberry Pi Zero W with a camera mounted in the ZeroView window mount. You will need the following hardware:

* Raspberry Pi Zero W
* SD card (at least 4GB)
* Raspberry Pi Camera (https://thepihut.com/products/raspberry-pi-camera-module)
* Raspberry Pi Camera cable (https://thepihut.com/products/raspberry-pi-zero-camera-adapter)
* ZeroView window mount (https://thepihut.com/products/zeroview)

For an optional blinking security light so that people are aware the camera is active, you will also need the following. Note that unless you purchase a Pi Zero with the header preinstalled this will require soldering:

* A Blinkt LED strip (https://thepihut.com/products/blinkt)
* Header Strip (https://thepihut.com/collections/raspberry-pi-hats/products/40-pin-2x20-hat-dual-male-headers)

Before you start the (headless) installation you will need to initialise your SD card. This is not necessary if you Pi is already initialised and on your network. I use the handy `rpi-init` Ansible script to do this direct from a Mac as it configures both SSH and wifi without needing to write to ext4 filesystems: 

* Clone the following repo `git clone https://github.com/dsbutler101/rpi-init` and follow the instructions in the `README.md`

## Frontend Installation Steps

Once your Pi is initialised you are ready to install the motion software and associated scripts for interacting with GCP. Change to a suitable directory and run the following commands to clone the repo and install the software on your Pi:

`git clone https://github.com/dsbutler101/rpi-servers.git`

`cd rpi-servers`

`vi hosts`

Update `site.yml` with the IP address of your Raspberry pi on the network:

`vi camera.yml`

Replace each of the `vars` with suitable values for your GCP project:

`project_id: <project-id-of-your-gcp-project>`

`bucket_name: <bucket-name-must-be-globally-unique>`

`service_name: <hostname-to-set-for-pi>`

`username: <your-email-address>`

`iphone_name: <host-name-of-your-iphone-as-it-appears-on-your-network>`

Finally the install step:

`ansible-playbook camera.yml`

The script should complete successfully. Note, there may be one 'error' that is ignored due to the logic implemented to install service-account keys. You can ignore this if the subsequent steps all complete successfully.

This script will use the current GCP credentials on your workstation to create a service-account, create service-account keys and install the keys on your Pi so that it can make the necessary API calls.bThe role associated with the service-account is carefully configured with the minimum permissions required to work. 

## To-Do

* Remove need to write IPHONE-AT-HOME file to disk - store state in memory
* create separate events when phone location changes
* upload tado data daily in batch
* Log additional Vision outut values in bigquery
* Speed up security flash
* Deal with edge case where multiple keys already exist for service account
* Update instructions for adding parameters to ansible-vault
* Fix issue where upload fails if object in Cloud Storage already exists
