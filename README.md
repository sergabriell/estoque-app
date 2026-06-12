# 📦 Solução de Controle de Estoque - Armazém 4 Irmãos

Uma aplicação desktop moderna, ágil e segura desenvolvida em Python para gerenciar o fluxo de mercadorias, relacionamento com fornecedores e exibir métricas financeiras e de estoque do Armazém 4 irmãos. O sistema centraliza as informações, automatiza os cálculos de valor de estoque, facilita a reposição de mercadorias e fornece um dashboard visual com a saúde do comércio.

---

## 🚀 Descrição do Projeto

O projeto foi concebido para resolver os problemas de falta de controle preciso sobre a entrada e saída de estoque no comércio varejista/atacadista, mitigando a perda de validade de produtos, compras desnecessárias (encalhe) ou falta de itens importantes na prateleira. Ele substitui a gestão feita de forma desorganizada (em papel ou planilhas soltas) por uma arquitetura Single Page Application (SPA) para desktop, dividida em dois perfis de acesso:

* **Gerente/Dono:** Possui acesso total a todas as telas, principalmente ao Dashboard, relatórios e gestão financeira.
* **Operador de Estoque/Caixa:** Possui acesso restrito focado apenas em registrar as entradas e saídas de produtos.

## 🛠️ Tecnologias Utilizadas

O sistema foi desenvolvido alinhado com a metodologia RAD (Rapid Application Development), utilizando as seguintes ferramentas:

* **Linguagem:** Python
* **Interface Gráfica (UI):** Custom Tkinter ou PyQt (fornecendo na navegação por menu lateral esquerdo fixo)
* **Banco de Dados Relacional:** SQLite (mapeado via SQLAlchemy ORM)
* **Manipulação e Análise de Dados:** Pandas
* **Gráficos do Dashboard:** Matplotlib
* **Segurança:** `bcrypt` (para criptografia e hashing de senhas)

## 📁 Estrutura do Banco de Dados (Schema)

O esquema do banco de dados relacional é composto por 4 tabelas principais:

* **`suppliers` (Fornecedores):** Armazena as informações de identificação dos parceiros comerciais.
* **`products` (Produtos):** Catálogo de itens com limite de quantidade mínima e relacionamento N:1 com fornecedores.
* **`stock_movements` (Movimentações):** Histórico completo de entradas e saídas para auditoria.
* **`users` (Usuários):** Credenciais e níveis de acesso (Gerente ou Operador).

## ⚙️ Requisitos para Execução

Antes de começar, certifique-se de ter instalado em sua máquina:
* Python 3.10 ou superior.
* Gerenciador de pacotes **pip** (geralmente embutido na instalação do Python).

## 🛠️ Passo a Passo para Instalação

Siga as etapas abaixo no terminal do seu sistema operacional para configurar o ambiente local do projeto:

### 1. Clonar o Repositório
```bash
git clone [https://github.com/sergabriell/estoque-app.git](https://github.com/sergabriell/estoque-app.git)
cd estoque-app
```
***
### 2. Criar e Ativar o Ambiente Virtual (Recomendado)

**No Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**No Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
***


### 3. Instalar as Dependências do Projeto
```bash
pip install -r requirements.txt
```
***

## ⚡ Passo a Passo para Execução

### 1. Povoar o Banco de Dados (Gerar Usuário Admin Padrão)
O projeto conta com um script de semente (`seed.py`) para estruturar as tabelas locais no banco SQLite e criar o primeiro usuário Administrador (Gerente):
```bash
python seed.py
```

⚠️ Nota Importante: Isso gerará o arquivo de banco em data/app.db com os seguintes dados de acesso padrão:

Usuário: admin

Senha: 123456

***

### 2. Executar a Aplicação
Com o ambiente configurado e o banco inicializado, execute o ponto de entrada principal do software:
```bash
python main.py
```

O sistema abrirá a tela de Login e, após a autenticação com sucesso, direcionará o usuário para o menu principal em formato SPA.

***

## 👥 Integrantes do Grupo (Equipe Little Python)

* **CARLOS ANDRÉ DOS SANTOS JÚNIOR** – Matrícula: 202504153471
* **JOSÉ MÁRIO DE OLIVEIRA NETO DOS SANTOS** – Matrícula: 202503368406
* **RODRIGO BEZERRA DE LIRA** – Matrícula: 202504118853
* **SÉRGIO GABRIEL PAZ DOS SANTOS SILVA** – Matrícula: 202504118713

---
Desenvolvido com 💙 pela equipe **Little Python** para a disciplina de *Desenvolvimento Rápido de Aplicações em Python* – **UNIFAVIP Wyden**.