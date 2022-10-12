# fastapi-postgre
Exercise on Fastapi and Postgre for CS127

# Prerequisite
1. Create your own database. (guide is include under documents folder)
2. review `SQL Basics - PostgreSQL.ipynb` which is included in this repo.
3. Test it with your own database credentials `DONT USE THE ONES IN THIS REPO. LOL`






# Running FastAPI with Postgre
Using pipenv

```bash
pipenv shell
pipenv install -r ./requirements.txt
```

to run the application
```bash
uvicorn main:app --reload
```



# Testing the API in a webpage
1. run the server
2. run `index.html`
3. check console for result.
