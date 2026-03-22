# Cloud Resource Manager 🚀

Cloud Resource Manager is a Python-based AWS infrastructure automation project built using boto3 and YAML configuration.

This project provisions a complete cloud environment programmatically, including networking, compute, and security components — and deploys a live web server accessible via a public IP.

---

## 🔥 What This Project Does

This system automates the creation and management of:

- VPC (Virtual Private Cloud)  
- Subnet  
- Internet Gateway  
- Route Table + Internet Routing  
- Security Group (SSH + HTTP access)  
- EC2 Instance  
- Public IP retrieval  
- Apache web server deployment (via SSH)  

The infrastructure is idempotent, meaning:

- Running the script multiple times will reuse existing resources  
- Prevents duplication and AWS limits issues  

---

## 🧠 Architecture

![Architecture Diagram](architecture.png)

config.yaml  
↓  
Python (main.py + utils.py)  
↓  
boto3 (AWS SDK)  
↓  
AWS Infrastructure (VPC → Subnet → IGW → EC2)  

---

## ⚙️ Tech Stack

- Python  
- boto3  
- PyYAML  
- AWS EC2 / VPC / IAM  

---

## 📁 Project Structure

cloud-resource-manager/  
├── config.yaml  
├── main.py  
├── utils.py  
├── requirements.txt  
├── README.md  
└── .gitignore  

---

## 🚀 How to Run

Clone repo  
git clone <your-repo-url>  
cd cloud-resource-manager  

Create virtual environment  
python3 -m venv .venv  
source .venv/bin/activate  

Install dependencies  
pip install -r requirements.txt  

Configure AWS  
aws configure  

Run automation  
python main.py  

---

## 🌐 Live Deployment

After provisioning, the EC2 instance hosts a live Apache web server.

Example output:  
EC2 public IP: 98.85.100.34  

Accessible via browser:  
http://<public-ip>  

Custom page deployed:

Hello Zonique 🚀  
This server was deployed using Python + AWS automation.  

---

## 🎥 Demo

This project provisions AWS infrastructure and deploys a live web server automatically.

Due to AWS account requirements, running this project requires valid AWS credentials and may incur usage costs.

Instead of running it locally, the functionality is demonstrated through the architecture, automation logic, and deployed output.

---

## 🧠 Key Learning Outcomes

- AWS networking (VPC, subnets, routing)  
- Infrastructure automation with boto3  
- Idempotent resource design  
- EC2 provisioning and lifecycle management  
- Security group configuration and debugging  
- SSH access and remote server management  
- Web server deployment on cloud infrastructure  

---

## 🔮 Future Improvements

- EC2 User Data automation (no manual SSH setup)  
- Elastic IP automation  
- IAM role attachment to EC2  
- Flask or full-stack app deployment  
- Terraform version of this project  

---

## 👨‍💻 Author

Zonique Foyle  
Future Solutions Architect 💪  