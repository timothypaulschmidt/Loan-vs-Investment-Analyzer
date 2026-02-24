# Loan-vs-Investment-Analyzer

This is my Python project with proper structure.

## Quick Start
Get started quickly! See the [Initial Deployment Guide](docs/INITIAL_DEPLOYMENT.md).

## Documentation
- 📋 [Initial Deployment Checklist](docs/INITIAL_DEPLOYMENT.md) - Complete setup guide
- 🔄 [Update Cycle](docs/UPDATE_CYCLE.md) - How to update and redeploy

## Setup (Traditional)
1. Activate virtual environment: `venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/main.py`

## Setup (Docker)
1. Build the image: `docker build -t loan-vs-investment-analyzer .`
2. Run the container: `docker run -it loan-vs-investment-analyzer`

## Push to Docker Hub
1. Tag: `docker tag loan-vs-investment-analyzer timothypaulschmidt/loan-vs-investment-analyzer`
2. Push: `docker push timothypaulschmidt/loan-vs-investment-analyzer`
