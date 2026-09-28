# Documentação do Sistema de Amigurumis

# 1. Identificação

Nome do sistema: Sistema de Amigurumis

Tipo: Aplicação Web

Finalidade: Gerenciamento e organização de encomendas de amigurumis.


# 2. Descrição

O Sistema de Amigurumis foi desenvolvido com o intuito de auxiliar na organização das encomendas de amigurumis.

A aplicação permite centralizar informações relacionadas aos clientes, produtos, encomendas e pagamentos, facilitando o acompanhamento dos pedidos e a organização das atividades.

O sistema foi desenvolvido utilizando Python e Flask no backend, SQLAlchemy para comunicação com o banco de dados e tecnologias web como HTML, CSS e JavaScript no frontend.


# 3. Objetivo geral

Desenvolver uma aplicação web capaz de auxiliar no gerenciamento e na organização das encomendas de amigurumis.


# 4. Objetivos específicos

- Organizar os dados dos clientes;
- Cadastrar amigurumis;
- Registrar encomendas;
- Permitir o acompanhamento dos pedidos;
- Registrar informações de pagamento;
- Manter histórico de pagamentos;
- Gerar relatórios;
- Centralizar informações importantes do negócio;
- Facilitar o gerenciamento das encomendas.


# 5. Tecnologias

# Backend

- Python
- Flask
- SQLAlchemy

# Banco de dados

- SQLite

# Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2

# Bibliotecas auxiliares

- python-dotenv
- Werkzeug
- XlsxWriter



# 6. Principais módulos

# Clientes

Responsável pelo cadastro e gerenciamento das informações dos clientes.

# Amigurumis

Responsável pelo cadastro e gerenciamento dos produtos disponíveis.

# Encomendas

Responsável pelo registro e acompanhamento das encomendas.

Uma encomenda pode possuir um ou mais itens de amigurumi.

# Pagamentos

Responsável pelo gerenciamento dos pagamentos relacionados às encomendas.

O sistema permite registrar recebimentos, devoluções e consultar o histórico de movimentações.

# Relatórios

Permite consultar informações relacionadas às encomendas e aos pagamentos.

# Anotações

Permite registrar informações auxiliares relacionadas ao gerenciamento do negócio.

# Suporte

Área destinada às informações e recursos relacionados ao suporte do sistema.

# Configurações

Área destinada ao gerenciamento da conta e configurações disponíveis para o usuário.

# 7. Controle de acesso

O sistema possui autenticação de usuários.

Cada usuário possui seus próprios dados e informações relacionadas às suas encomendas.

O sistema utiliza uma chave secreta para proteção das sessões e variáveis de ambiente para informações sensíveis.


# 8. Banco de dados

O sistema utiliza banco de dados SQLite.

Entre as principais entidades utilizadas estão:

- Usuário;
- Cliente;
- Amigurumi;
- Pedido;
- Item do pedido;
- Pagamento;
- Recuperação de senha;
- Preferências do usuário.

As entidades possuem relacionamentos utilizados para organizar os dados do sistema.


# 9. Segurança

Foram utilizadas algumas práticas de segurança durante o desenvolvimento, incluindo:

- Senhas armazenadas utilizando recursos de hash;
- Controle de sessão;
- Autenticação de usuários;
- Utilização de variáveis de ambiente;
- Separação das informações sensíveis do código;
- Validação de dados recebidos pelos formulários;
- Utilização de `.gitignore` para evitar o envio de arquivos sensíveis.



# 10. Recuperação de senha

O sistema possui um mecanismo de recuperação de senha utilizando e-mail.

O usuário pode solicitar a recuperação de acesso e receber as informações necessárias para redefinir sua senha.

As configurações relacionadas ao envio de e-mails são armazenadas por meio de variáveis de ambiente.



# 11. Organização do projeto

O projeto utiliza uma organização baseada na separação de responsabilidades.

As principais partes são:


app/
├── models/
├── routes/
├── services/
├── templates/
├── static/
└── utils/