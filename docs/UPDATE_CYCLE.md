# Update Cycle Checklist

## Quick Summary
Every update cycle:
1. Code → Test → Commit → Push to GitHub
2. Build Docker image → Tag → Push to Docker Hub
3. On other computer: Pull → Run

---

## Complete Update Workflow

### On Your Source Computer (Development Machine)

#### 1. Make Changes to Your Python Code
Edit your files in your IDE (VS Code, Spyder, etc.)

#### 2. Test Locally (Optional)
```bash
venv\Scripts\activate
python src/main.py
```

#### 3. Update Requirements (If You Added Packages)
```bash
pip freeze > requirements.txt
```

#### 4. Commit and Push to GitHub
```bash
git add .
git commit -m "Bugfix: description of what you fixed"
git push origin main
```

#### 5. Rebuild Your Docker Image
```bash
docker build -t loan-vs-investment-analyzer .
```

#### 6. Tag It for Docker Hub
```bash
docker tag loan-vs-investment-analyzer timothypaulschmidt/loan-vs-investment-analyzer
```

#### 7. Push to Docker Hub
```bash
docker push timothypaulschmidt/loan-vs-investment-analyzer
```

---

### On Your Destination Computer

#### Option A: Using Python/GitHub Only

1. Navigate to project:
   ```bash
   cd C:\Users\YourUsername\Documents\Projects\Loan-vs-Investment-Analyzer
   ```

2. Pull latest changes:
   ```bash
   git pull origin main
   ```

3. Activate venv:
   ```bash
   venv\Scripts\activate
   ```

4. Update dependencies (if requirements.txt changed):
   ```bash
   pip install -r requirements.txt
   ```

5. Run the updated code:
   ```bash
   python src/main.py
   ```

#### Option B: Using Docker Only

1. Pull the updated image:
   ```bash
   docker pull timothypaulschmidt/loan-vs-investment-analyzer
   ```

2. Run the new version:
   ```bash
   docker run -it timothypaulschmidt/loan-vs-investment-analyzer
   ```

---

## Pro Tips

### Version Tagging
Instead of always using `latest`, you can version your Docker images:

```bash
# On source computer
docker build -t loan-vs-investment-analyzer .
docker tag loan-vs-investment-analyzer timothypaulschmidt/loan-vs-investment-analyzer:v1.0
docker tag loan-vs-investment-analyzer timothypaulschmidt/loan-vs-investment-analyzer:latest
docker push timothypaulschmidt/loan-vs-investment-analyzer:v1.0
docker push timothypaulschmidt/loan-vs-investment-analyzer:latest
```

Then on destination:
```bash
# Pull specific version
docker pull timothypaulschmidt/loan-vs-investment-analyzer:v1.0
docker run -it timothypaulschmidt/loan-vs-investment-analyzer:v1.0

# Or always get latest
docker pull timothypaulschmidt/loan-vs-investment-analyzer:latest
docker run -it timothypaulschmidt/loan-vs-investment-analyzer:latest
```

### Git Best Practices
- Use descriptive commit messages
- Commit often (small, logical changes)
- Test before committing
- Always pull before pushing if working on multiple computers

### Docker Best Practices
- Rebuild image after any code changes
- Always test locally before pushing to Docker Hub
- Use version tags for important releases
- Keep your Dockerfile and .dockerignore up to date
