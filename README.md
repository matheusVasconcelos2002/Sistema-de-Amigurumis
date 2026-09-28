# Sistema de Amigurumis

O Sistema de Amigurumis é uma aplicação web desenvolvida com o objetivo de auxiliar na organização e no gerenciamento de encomendas de amigurumis.

O sistema foi desenvolvido pensando nas necessidades de um pequeno negócio de produção artesanal, permitindo centralizar informações sobre clientes, encomendas, produtos, pagamentos e demais informações relacionadas ao processo de atendimento.

# Objetivo

O principal objetivo do sistema é ajudar a organizar melhor as encomendas de amigurumis, reduzindo a necessidade de controlar informações manualmente e facilitando o acompanhamento dos pedidos.

A aplicação busca tornar o processo de gerenciamento mais simples, organizado e seguro.

# Funcionalidades

Entre as principais funcionalidades disponíveis estão:

- Cadastro e gerenciamento de clientes;
- Cadastro de amigurumis;
- Criação de encomendas;
- Adição de diferentes amigurumis em uma mesma encomenda;
- Definição de quantidade, tamanho, tipo e preço;
- Definição de data prevista para entrega;
- Acompanhamento do status das encomendas;
- Gerenciamento de pagamentos;
- Registro de recebimentos;
- Histórico de pagamentos;
- Registro de devoluções;
- Relatórios;
- Anotações;
- Área de suporte;
- Gerenciamento de conta;
- Recuperação de senha;
- Autenticação de usuários;
- Organização dos dados por usuário.

# Tecnologias utilizadas

O sistema foi desenvolvido utilizando principalmente:

- Python
- Flask
- SQLAlchemy
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2
- python-dotenv
- XlsxWriter

#Estrutura do projeto

A estrutura geral do projeto está organizada de forma semelhante a:

Sistema de Amigurumis/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   ├── static/
│   ├── utils/
│   └── extensions.py
│
├── instance/
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.py