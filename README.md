# GraphWord Project

Welcome to **GraphWord-MJ**! This is a demonstration project that shows how to build and serve a graph-based API, both **locally** and on **AWS** using Terraform. 

## Purpose

- **Main Objective**: Create an APP that reads words (from Project Gutenberg books or local dictionaries), stores them in a structured manner, builds a graph of words of different sizes, and provides an API with endpoints to explore that graph.
- **AWS Deployment**: This project is set up to be easily deployed onto an EC2 instance via Terraform, so you can test the API live on AWS.
- **Local Testing**: You can also run the API locally (for development or debugging) using Python.

## How It Works

1. **Word Collection**  
   - The `main.py` script retrieves new words from:
     - A local dictionary file.
     - A Project Gutenberg URL (downloading a book and extracting words).
   - These new words are stored in the `datamart/` folder under `words_{length}.txt`, ensuring no duplicates.

2. **Building the Graph**  
   - The `initialize_graph.py` script constructs a graph from all the words found in the `datamart/` directory.
   - Each word becomes a node, and there is an edge between two words if they differ by exactly one letter.

3. **API**  
   - Locally, you can run the API using `api/api.py`.
   - Endpoints allow you to query the graph (shortest path, clusters, high-connectivity nodes, etc.).

## Local Usage

1. **Setup Credentials (optional)**  
   If you plan to download Project Gutenberg books and use certain AWS features, you might need valid AWS credentials set in `~/.aws/credentials`.  
   For purely local usage, you can often skip this.

2. **Install Dependencies**  
   pip3 install -r app/requirements.txt

3. **Download or Update Words**

   - **Run** `python3 app/main.py`.
   - **Select** whether to use a local dictionary or a Gutenberg URL.
   - This populates `datamart/` with new words.

4. **Initialize the Graph**

   - **Run** `python3 app/initialize_graph.py`
   - This reads all words_*.txt files from datamart/ and builds a pickle file (graph.pkl) containing your new graph.

5. **Run the API Locally**

   - **Run** `python3 app/api/api.py`
   - By default, it may run on port 5000 locally. Go to http://127.0.0.1:5000 to see the available endpoints.

## AWS Deployment (Terraform)

If you want to deploy your API to AWS:

1. **AWS Credentials**

   - Make sure your `~/.aws/credentials` file contains your AWS Access Key, Secret Key, and (if needed) Session Token.
   - Terraform will use these credentials to create resources (EC2, Security Groups, API Gateway, etc.).

2. **Navigate to the Terraform Directory**

   - In this project, there is a `terraform/` folder with `.tf` files.

3. **Initialize, Plan, and Apply**

   `cd terraform`
   `terraform init`
   `terraform plan`
   `terraform apply`

   - This will create an EC2 instance (and other resources such as VPC, Security Group, etc.).

4. **Obtain the EC2 Public DNS**

   - After terraform apply completes, it will output something like:
   `ec2_public_dns = "ec2-54-197-213-25.compute-1.amazonaws.com"`
   - Copy that DNS name.

5. **Test the Running API**

   - Once the instance is fully up, you can make requests, for example:
   `curl http://ec2-54-197-213-25.compute-1.amazonaws.com`
   - If your user-data installed Nginx & Gunicorn properly, you should see the API endpoints responding on port 80 (**NOTE**: It is necessary to wait between 1 and 2 minutes after the ec2 instance has been created for it to work correctly.).
   - Adjust routes like `/shortest-path`, `/clusters`, etc.

## Questions or Issues

Feel free to open an Issue or Pull Request if you have suggestions, or if you encounter problems running or deploying this project.

Enjoy exploring GraphWord-MJ and happy graphing!
