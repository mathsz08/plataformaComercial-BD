#!/bin/bash

echo "======================================"
echo "Instalando Plataforma Comercial"
echo "======================================"
echo ""

echo "[1/4] Atualizando pip..."
python3 -m pip install --upgrade pip

echo ""
echo "[2/4] Instalando dependencias..."
pip3 install -r requirements.txt

echo ""
echo "[3/4] Criando banco de dados..."

# SQL para criar o banco e as tabelas
SQL_SCRIPT=$(
  cat <<'EOF'
-- Criar banco de dados
CREATE DATABASE plataforma_comercial;

-- Conectar ao banco novo
\c plataforma_comercial

-- Tabelas
CREATE TABLE Pessoa (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE Cliente (
    id INT PRIMARY KEY,
    cpf_cnpj VARCHAR(18) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('PESSOA_FISICA','PESSOA_JURIDICA')),
    FOREIGN KEY (id) REFERENCES Pessoa(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Vendedor (
    id INT PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL,
    FOREIGN KEY (id) REFERENCES Pessoa(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Endereco (
    id_endereco SERIAL PRIMARY KEY,
    rua VARCHAR(150),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    complemento VARCHAR(100),
    id_cliente INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Categoria_Produto (
    id_categoria SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE Produto (
    id_produto SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    preco NUMERIC(10,2) NOT NULL CHECK (preco>=0),
    id_categoria INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categoria_Produto(id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Fornecedor (
    id_fornecedor SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    contato VARCHAR(150)
);

CREATE TABLE Fornece (
    id_fornecedor INT NOT NULL,
    id_produto INT NOT NULL,
    PRIMARY KEY(id_fornecedor,id_produto),
    FOREIGN KEY(id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(id_produto) REFERENCES Produto(id_produto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Estoque (
    id_estoque SERIAL PRIMARY KEY,
    descricao VARCHAR(200)
);

CREATE TABLE Estoque_Produto (
    id_estoque INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade>=1),
    PRIMARY KEY(id_estoque,id_produto),
    FOREIGN KEY(id_estoque) REFERENCES Estoque(id_estoque)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(id_produto) REFERENCES Produto(id_produto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Pedido (
    id_pedido SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (
      status IN ('PENDENTE','PROCESSANDO','ENVIADO','CONCLUIDO','CANCELADO')
    ),
    id_cliente INT NOT NULL,
    id_vendedor INT,
    FOREIGN KEY(id_cliente) REFERENCES Cliente(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY(id_vendedor) REFERENCES Vendedor(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE Entrega (
    id_entrega SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (
      status IN ('AGUARDANDO','EM_TRANSITO','ENTREGUE','DEVOLVIDO')
    ),
    data DATE,
    id_pedido INT NOT NULL UNIQUE,
    id_endereco INT NOT NULL,
    FOREIGN KEY(id_pedido) REFERENCES Pedido(id_pedido)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(id_endereco) REFERENCES Endereco(id_endereco)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Item_Pedido (
    id_pedido INT NOT NULL,
    id_item INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade>=1),
    preco_unitario NUMERIC(10,2) NOT NULL,
    id_produto INT NOT NULL,
    PRIMARY KEY(id_pedido,id_item),
    FOREIGN KEY(id_pedido) REFERENCES Pedido(id_pedido)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(id_produto) REFERENCES Produto(id_produto)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Compra (
    id_compra SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    id_estoque INT NOT NULL,
    id_produto INT NOT NULL,
    FOREIGN KEY(id_estoque,id_produto)
      REFERENCES Estoque_Produto(id_estoque,id_produto)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Item_Compra (
    id_compra INT NOT NULL,
    id_item INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade>=1),
    preco_unitario NUMERIC(10,2) NOT NULL,
    id_produto INT NOT NULL,
    PRIMARY KEY(id_compra,id_item),
    FOREIGN KEY(id_compra) REFERENCES Compra(id_compra)
      ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(id_produto) REFERENCES Produto(id_produto)
      ON DELETE RESTRICT ON UPDATE CASCADE
);
EOF
)

# Tenta criar o banco (ignora se já existe)
echo "$SQL_SCRIPT" | psql -U postgres 2>/dev/null || {
  echo "⚠️  Banco pode já existir. Continuando..."
}

echo ""
echo "[4/4] Instalacao concluida!"
echo ""
echo "======================================"
echo "Para Popular a tabela rode"
echo ""
echo " python popular_tabela.py"
echo ""
echo "Para rodar o sistema:"
echo ""
echo "  streamlit run plataforma_streamlit.py"
echo ""
echo "======================================"
