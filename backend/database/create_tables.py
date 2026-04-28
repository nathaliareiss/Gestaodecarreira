from database.database import engine, Base
from database import models

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")