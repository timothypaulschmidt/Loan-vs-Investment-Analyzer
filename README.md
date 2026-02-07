# Loan-vs-Investment-Analyzer

This is my Python project with proper structure.

## Setup (Traditional)
1. Activate virtual environment: `venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/main.py`

## Setup (Docker)
1. Build the image: `docker build -t loan-vs-investment-analyzer .`
2. Run the container: `docker run -it loan-vs-investment-analyzer`

## Push to Docker Hub
1. Tag: `docker tag Loan-vs-Investment-Analyzer yourusername/Loan-vs-Investment-Analyzer`
2. Push: `docker push yourusername/Loan-vs-Investment-Analyzer`
