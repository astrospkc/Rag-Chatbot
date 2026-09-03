Commands

1- Generate first migration:
    alembic revision --autogenerate -m "Create uploaded_documents table"

2- Apply migration:
    alembic upgrade head

3- 
if mvenv is not active :-
mvenv/bin/alembic revision --autogenerate -m "Create uploaded_documents table"  

<!-- to find in celery -->
mvenv/bin/celery -A internal.services.celery_app worker --loglevel=info -Q rag