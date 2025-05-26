
# 🚗 Postos-BigData

Este projeto é uma aplicação desenvolvida com **Django** que realiza a **análise de dados de postos de combustíveis**, com o objetivo de indicar o **melhor local para abastecimento**, com base em critérios como localização, preços e outros fatores analisados.

---

## 📌 Funcionalidades

- Armazenamento dos dados em banco SQLite;
- Identificação do melhor posto com base em métricas definidas;
- Análise de dados gerada por Gemini modelo Flash 2.0
- Interface web para visualização dos dados.

---

## 🛠️ Tecnologias Utilizadas

- Python
- Django
- SQLite
- Pandas
- Matplotlib / Seaborn (para visualização)
- OpenPyXL (leitura de Excel)

---

## 📁 Estrutura de Arquivos

- `manage.py`: Gerenciador do projeto Django.
- `db.sqlite3`: Banco de dados com os dados dos postos.
- `importexcel.py`: Script para importar dados da planilha.
- `.git/`: Repositório Git.
- `requeriments.txt`: Dependências do projeto.

---

## ▶️ Como Executar o Projeto

1. Clone o repositório:
    ```bash
    git clone <repo-url>
    cd Postos-BigData
    ```

2. Crie um ambiente virtual e ative:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate   # Windows
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Execute o servidor:
    ```bash
    python manage.py runserver
    ```

---

## 📊 Importação e Visualização

- Execute `importexcel.py` para importar os dados da planilha.

---

## 👨‍💻 Autor

Projeto acadêmico desenvolvido por:
Guilherme Miguel Neto Santa Rosa
João Víctor Miranda Carvalho
Luiz Fernando Ferreira Barbosa



