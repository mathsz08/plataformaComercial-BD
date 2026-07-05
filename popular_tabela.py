#!/usr/bin/env python3

import random
from datetime import date, timedelta
import psycopg2
from db_config import DB_CONFIG
# ============================================
# Configuração do banco
# ============================================

conn = psycopg2.connect(**DB_CONFIG)

cur = conn.cursor()

# ============================================
# Dados aleatórios
# ============================================

nomes = [
    "João Silva",
    "Maria Oliveira",
    "Pedro Santos",
    "Ana Costa",
    "Lucas Souza",
    "Julia Martins",
    "Carla Mendes",
    "Rafael Almeida",
    "Fernanda Rocha",
    "Bruno Lima"
]

ruas = [
    "Rua das Flores",
    "Av. Brasil",
    "Rua Tiradentes",
    "Rua XV de Novembro"
]

bairros = [
    "Centro",
    "São José",
    "Industrial",
    "Nova Esperança"
]

cidades = [
    "Ouro Preto",
    "Belo Horizonte",
    "Mariana",
    "Itabirito"
]

categorias = [
    "Eletrônicos",
    "Informática",
    "Livros",
    "Escritório"
]

produtos = [
    ("Notebook", "Notebook Dell"),
    ("Mouse", "Mouse Gamer"),
    ("Teclado", "Teclado Mecânico"),
    ("Livro Python", "Programação Python"),
    ("Monitor", "Monitor LED 24 polegadas"),
    ("Cadeira de Escritório", "Cadeira ergonômica"),
    ("Impressora", "Impressora multifuncional"),
    ("Webcam", "Webcam Full HD")
]

fornecedores = [
    "Tech Distribuidora",
    "Mega Supply",
    "Info Center"
]

estoques = [
    "Estoque Principal",
    "Estoque Secundário"
]

status_pedido = [
    "PENDENTE",
    "PROCESSANDO",
    "PROCESSANDO",
    "ENVIADO",
    "CONCLUIDO",
    "CANCELADO",
    "PENDENTE",
    "PROCESSANDO",
    "ENVIADO",
    "CONCLUIDO"
]

status_entrega = [
    "AGUARDANDO",
    "EM_TRANSITO",
    "ENTREGUE"
]

# ============================================
# Pessoa
# ============================================

pessoas = []

for nome in nomes:
    cur.execute("""
        INSERT INTO Pessoa(nome,telefone,email)
        VALUES(%s,%s,%s)
        RETURNING id
    """, (
        nome,
        f"31{random.randint(900000000,999999999)}",
        nome.lower().replace(" ",".") + "@email.com"
    ))

    pessoas.append(cur.fetchone()[0])

# ============================================
# Cliente
# ============================================

clientes = []

for i, pid in enumerate(pessoas[:6]):
    tipo_cliente = 'PESSOA_JURIDICA' if i in (1, 4) else 'PESSOA_FISICA'
    documento = str(random.randint(10000000000000,99999999999999)) if tipo_cliente == 'PESSOA_JURIDICA' else str(random.randint(10000000000,99999999999))

    cur.execute("""
        INSERT INTO Cliente(id,cpf_cnpj,tipo)
        VALUES(%s,%s,%s)
    """, (
        pid,
        documento,
        tipo_cliente
    ))

    clientes.append(pid)

# ============================================
# Vendedor
# ============================================

vendedores = []

for pid in pessoas[6:10]:
    cur.execute("""
        INSERT INTO Vendedor(id,matricula)
        VALUES(%s,%s)
    """, (
        pid,
        f"MAT{random.randint(1000,9999)}"
    ))

    vendedores.append(pid)

# ============================================
# Endereço
# ============================================

enderecos = []

for cliente in clientes:
    cur.execute("""
        INSERT INTO Endereco
        (rua,bairro,cidade,complemento,id_cliente)
        VALUES(%s,%s,%s,%s,%s)
        RETURNING id_endereco
    """,(
        random.choice(ruas),
        random.choice(bairros),
        random.choice(cidades),
        "Casa",
        cliente
    ))

    enderecos.append(cur.fetchone()[0])

# ============================================
# Categoria
# ============================================

ids_categoria = []

for cat in categorias:
    cur.execute("""
        INSERT INTO Categoria_Produto(nome)
        VALUES(%s)
        RETURNING id_categoria
    """,(cat,))

    ids_categoria.append(cur.fetchone()[0])

# ============================================
# Produto
# ============================================

ids_produtos = []

for nome,desc in produtos:

    cur.execute("""
        INSERT INTO Produto
        (nome,descricao,preco,id_categoria)
        VALUES(%s,%s,%s,%s)
        RETURNING id_produto
    """,(
        nome,
        desc,
        round(random.uniform(50,5000),2),
        random.choice(ids_categoria)
    ))

    ids_produtos.append(cur.fetchone()[0])

# ============================================
# Fornecedor
# ============================================

ids_fornecedor = []

for nome in fornecedores:

    cur.execute("""
        INSERT INTO Fornecedor(nome,contato)
        VALUES(%s,%s)
        RETURNING id_fornecedor
    """,(
        nome,
        "contato@empresa.com"
    ))

    ids_fornecedor.append(cur.fetchone()[0])

# ============================================
# Fornece
# ============================================

for f in ids_fornecedor:
    for p in ids_produtos:
        cur.execute("""
            INSERT INTO Fornece
            VALUES(%s,%s)
        """,(f,p))

# ============================================
# Estoque
# ============================================

ids_estoque=[]

for nome in estoques:

    cur.execute("""
        INSERT INTO Estoque(descricao)
        VALUES(%s)
        RETURNING id_estoque
    """,(nome,))

    ids_estoque.append(cur.fetchone()[0])

# ============================================
# Estoque Produto
# ============================================

for e in ids_estoque:
    for p in ids_produtos:

        cur.execute("""
            INSERT INTO Estoque_Produto
            VALUES(%s,%s,%s)
        """,(
            e,
            p,
            random.choice([5, 8, 12, 18, 25, 40, 75, 100])
        ))

# ============================================
# Pedido
# ============================================

ids_pedido=[]

for i, status in enumerate(status_pedido):

    cur.execute("""
        INSERT INTO Pedido
        (data,status,id_cliente,id_vendedor)
        VALUES(%s,%s,%s,%s)
        RETURNING id_pedido
    """,(
        date.today()-timedelta(days=i * 4),
        status,
        clientes[i % len(clientes)],
        vendedores[i % len(vendedores)]
    ))

    ids_pedido.append(cur.fetchone()[0])

# ============================================
# Entrega
# ============================================

for i,pedido in enumerate(ids_pedido[:len(enderecos)]):

    cur.execute("""
        INSERT INTO Entrega
        (status,data,id_pedido,id_endereco)
        VALUES(%s,%s,%s,%s)
    """,(
        random.choice(status_entrega),
        date.today(),
        pedido,
        enderecos[i]
    ))

# ============================================
# Item Pedido
# ============================================

for pedido in ids_pedido:

    for item in range(1,3):

        cur.execute("""
            INSERT INTO Item_Pedido
            VALUES(%s,%s,%s,%s,%s)
        """,(
            pedido,
            item,
            random.randint(1,5),
            round(random.uniform(50,5000),2),
            random.choice(ids_produtos)
        ))

# ============================================
# Compra
# ============================================

ids_compra=[]

for i in range(2):

    estoque=random.choice(ids_estoque)
    produto=random.choice(ids_produtos)

    cur.execute("""
        INSERT INTO Compra
        (data,id_estoque,id_produto)
        VALUES(%s,%s,%s)
        RETURNING id_compra
    """,(
        date.today()-timedelta(days=random.randint(0,20)),
        estoque,
        produto
    ))

    ids_compra.append(cur.fetchone()[0])

# ============================================
# Item Compra
# ============================================

for compra in ids_compra:

    for item in range(1,3):

        cur.execute("""
            INSERT INTO Item_Compra
            VALUES(%s,%s,%s,%s,%s)
        """,(
            compra,
            item,
            random.randint(1,20),
            round(random.uniform(30,2000),2),
            random.choice(ids_produtos)
        ))

conn.commit()

cur.close()
conn.close()

print("===================================")
print("Banco populado com sucesso!")
print("===================================")
