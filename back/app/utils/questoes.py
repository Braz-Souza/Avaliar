from pydantic import BaseModel
import sqlite3
import os
import json

class Questao(BaseModel):
    questaoID: int
    enunciado: str
    alternativas: dict 

script_dir = os.path.dirname(os.path.abspath(__file__))
back_dir = os.path.dirname(os.path.dirname(script_dir))
db_dir = os.path.join(back_dir, 'db')
questoesDB = os.path.join(db_dir, 'questoes.db')

os.makedirs(db_dir, exist_ok=True)

def clear_questoes_db():
    with sqlite3.connect(questoesDB) as connection:
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS questoes;')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questoes (
            questaoID INTEGER PRIMARY KEY,
            enunciado TEXT NOT NULL,
            alternativas TEXT NOT NULL
        );''')
        connection.commit()
    
def show_questoes_db():
    with sqlite3.connect(questoesDB) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM questoes;')
        questoes = cursor.fetchall()
    q = []
    for questao in questoes:
        q.append(Questao(
            questaoID=questao[0],
            enunciado=questao[1],
            alternativas=json.loads(questao[2])
        ))
    return q

def show_questao_db(questaoID=None, enunciado=None, alternativa=None):
    with sqlite3.connect(questoesDB) as connection:
        cursor = connection.cursor()
        if questaoID:
            cursor.execute('''SELECT * FROM questoes 
            WHERE questaoID IS ?;''', (questaoID,))
        if enunciado:
            search_term = f'%{enunciado}%'
            cursor.execute('''SELECT * FROM questoes 
            WHERE enunciado LIKE ?;''', (search_term,))
        if alternativa:
            search_term = f'%{alternativa}%'
            cursor.execute('''SELECT * FROM questoes 
            WHERE alternativas LIKE ?;''', (search_term,))
        questoes = cursor.fetchall()
        q = []
        for questao in questoes:
            q.append(Questao(
                questaoID=questao[0],
                enunciado=questao[1],
                alternativas=json.loads(questao[2])
            ))
        return q
    
def add_questoes_db(questaoID, enunciado, alternativas):
    with sqlite3.connect(questoesDB) as connection:
        cursor = connection.cursor()
        statement = '''
        INSERT INTO questoes (questaoID, enunciado, alternativas)
        VALUES (?, ?, ?);
        '''
        values = (questaoID, enunciado, alternativas)
        cursor.execute(statement, values)
        connection.commit()
