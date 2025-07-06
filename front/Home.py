import streamlit as st

st.set_page_config(
    page_title="Avaliar",
    page_icon="✅",
)

st.title("Changelog")
st.markdown("""
## 0.1.0
- Authenticacao com JWT para um único usuario padrão definido
- Banco de dados de questões criado
- Definição de endpoints de:
    - Obter token de authenticação : ***/token***
    - Ver usuario atual logado : ***/users/me***
    - Visualizar questões : ***/questoes/***
    - Visualizar questão por ID, enunciado e alternativa 
        - ***/questoes/id/{questaoID}***
        - ***/questoes/enunciado/{enunciado}***
        - ***/questoes/alternativa/{alternativa}***
    - Adicionar questão : ***/questoes/***
    - Limpar questões do banco de dados : ***/questoes/clear***

## 0.0.0
- Definição do ambiente com Streamlit, FastAPI, Docker
- CI/CD com todos os PRs para a main atualizando automaticamente o site hospedado
""")

st.title('Sobre o Avaliar')
st.markdown("""
Avaliar é uma aplicação web desenvolvida com o objetivo de facilitar a criação e avaliação de provas. Com Avaliar, você pode criar questões, organizar provas e avaliar o desempenho dos alunos de forma simples e eficiente.

## Tecnologias
- Python
- FastAPI
- Streamlit
- SQLite


## Funcionalidades
- [INSERT HERE]

## Como usar
1. [INSERT HERE]

## Contribuindo
Se você deseja contribuir para o Avaliar, sinta-se à vontade para abrir uma issue ou
enviar um pull request no repositório do GitHub. Sua contribuição é muito apreciada!
""")
