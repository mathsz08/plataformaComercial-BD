#!/usr/bin/env python3

import random
from datetime import date, timedelta
import psycopg2
from db_config import DB_CONFIG

# ============================================
# Configuração
# ============================================

N = 10  # quantidade de instâncias por entidade

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# ============================================
# Dados aleatórios
# ============================================

# 20 nomes: os 10 primeiros viram Clientes, os 10 seguintes viram Vendedores
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
    "Bruno Lima",
    "Camila Ferreira",
    "Diego Barbosa",
    "Larissa Gomes",
    "Thiago Carvalho",
    "Patrícia Ribeiro",
    "Eduardo Nascimento",
    "Beatriz Araújo",
    "Gustavo Pereira",
    "Isabela Correia",
    "Rodrigo Teixeira",
]

ruas = [
    "Rua das Flores",
    "Av. Brasil",
    "Rua Tiradentes",
    "Rua XV de Novembro",
    "Rua da Bahia",
    "Av. Getúlio Vargas",
]

bairros = [
    "Centro",
    "São José",
    "Industrial",
    "Nova Esperança",
]

cidades = [
    "Ouro Preto",
    "Belo Horizonte",
    "Mariana",
    "Itabirito",
]

categorias = [
    "Eletrônicos",
    "Informática",
    "Livros",
    "Escritório",
    "Casa e Decoração",
    "Papelaria",
    "Áudio e Vídeo",
    "Games",
    "Ferramentas",
    "Móveis",
]

produtos = [
    ("Notebook", "Notebook Dell"),
    ("Mouse", "Mouse Gamer"),
    ("Teclado", "Teclado Mecânico"),
    ("Livro Python", "Programação Python"),
    ("Monitor", "Monitor LED 24 polegadas"),
    ("Cadeira de Escritório", "Cadeira ergonômica"),
    ("Impressora", "Impressora multifuncional"),
    ("Webcam", "Webcam Full HD"),
    ("Headset", "Headset com microfone"),
    ("Roteador Wi-Fi", "Roteador Wi-Fi 6"),
]

fornecedores = [
    "Tech Distribuidora",
    "Mega Supply",
    "Info Center",
    "Brasil Componentes",
    "Alpha Distribuição",
    "Comercial Nordeste",
    "Prime Suprimentos",
    "Vale Tech",
    "Sul Distribuidora",
    "Central de Equipamentos",
]

estoques = [
    "Estoque Principal",
    "Estoque Secundário",
    "Estoque Filial Centro",
    "Estoque Filial Norte",
    "Estoque Filial Sul",
    "Estoque Filial Leste",
    "Estoque Filial Oeste",
    "Estoque de Devoluções",
    "Estoque Reserva",
    "Estoque Regional",
]

status_pedido_opcoes = ["PENDENTE", "PROCESSANDO", "ENVIADO", "CONCLUIDO", "CANCELADO"]
status_entrega_opcoes = ["AGUARDANDO", "EM_TRANSITO", "ENTREGUE", "DEVOLVIDO"]

assert len(nomes) == 2 * N, "É preciso 2*N nomes (N clientes + N vendedores)"
assert len(categorias) == N
assert len(produtos) == N
assert len(fornecedores) == N
assert len(estoques) == N

# ============================================
# Pessoa (2*N: N para Cliente + N para Vendedor)
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
        nome.lower().replace(" ", ".") + "@email.com"
    ))

    pessoas.append(cur.fetchone()[0])

# ============================================
# Cliente (N)
# ============================================

clientes = []

for i, pid in enumerate(pessoas[:N]):
    # ~1/3 dos clientes como PESSOA_JURIDICA, o resto PESSOA_FISICA
    tipo_cliente = 'PESSOA_JURIDICA' if i % 3 == 0 else 'PESSOA_FISICA'
    documento = (
        str(random.randint(10000000000000, 99999999999999))
        if tipo_cliente == 'PESSOA_JURIDICA'
        else str(random.randint(10000000000, 99999999999))
    )

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
# Vendedor (N)
# ============================================

vendedores = []

for i, pid in enumerate(pessoas[N:2 * N]):
    cur.execute("""
        INSERT INTO Vendedor(id,matricula)
        VALUES(%s,%s)
    """, (
        pid,
        f"MAT{1000 + i}"
    ))

    vendedores.append(pid)

# ============================================
# Endereço (N — um por cliente)
# ============================================

enderecos = []
endereco_por_cliente = {}

for cliente in clientes:
    cur.execute("""
        INSERT INTO Endereco
        (rua,bairro,cidade,complemento,id_cliente)
        VALUES(%s,%s,%s,%s,%s)
        RETURNING id_endereco
    """, (
        random.choice(ruas),
        random.choice(bairros),
        random.choice(cidades),
        "Casa",
        cliente
    ))

    id_endereco = cur.fetchone()[0]
    enderecos.append(id_endereco)
    endereco_por_cliente[cliente] = id_endereco

# ============================================
# Categoria (N)
# ============================================

ids_categoria = []

for cat in categorias:
    cur.execute("""
        INSERT INTO Categoria_Produto(nome)
        VALUES(%s)
        RETURNING id_categoria
    """, (cat,))

    ids_categoria.append(cur.fetchone()[0])

# ============================================
# Produto (N)
# ============================================

ids_produtos = []

for nome, desc in produtos:

    cur.execute("""
        INSERT INTO Produto
        (nome,descricao,preco,id_categoria)
        VALUES(%s,%s,%s,%s)
        RETURNING id_produto
    """, (
        nome,
        desc,
        round(random.uniform(50, 5000), 2),
        random.choice(ids_categoria)
    ))

    ids_produtos.append(cur.fetchone()[0])

# ============================================
# Fornecedor (N)
# ============================================

ids_fornecedor = []

for nome in fornecedores:

    cur.execute("""
        INSERT INTO Fornecedor(nome,contato)
        VALUES(%s,%s)
        RETURNING id_fornecedor
    """, (
        nome,
        "contato@empresa.com"
    ))

    ids_fornecedor.append(cur.fetchone()[0])

# ============================================
# Fornece (todos os fornecedores fornecem todos os produtos)
# ============================================

for f in ids_fornecedor:
    for p in ids_produtos:
        cur.execute("""
            INSERT INTO Fornece
            (id_fornecedor,id_produto)
            VALUES(%s,%s)
        """, (f, p))

# ============================================
# Endereços dos estoques (N)
# ------------------------------------------------
# CORREÇÃO: Estoque.id_endereco é NOT NULL/UNIQUE e referencia
# Endereco, cujo id_cliente também é NOT NULL. O script original
# tentava inserir Estoque sem id_endereco, o que violava a
# constraint NOT NULL e quebrava a execução. Aqui criamos um
# endereço próprio para cada estoque (vinculado a um cliente
# existente só para satisfazer a FK obrigatória de Endereco).
# ============================================

enderecos_estoque = []

for _ in range(N):
    cliente_base = random.choice(clientes)

    cur.execute("""
        INSERT INTO Endereco
        (rua,bairro,cidade,complemento,id_cliente)
        VALUES(%s,%s,%s,%s,%s)
        RETURNING id_endereco
    """, (
        random.choice(ruas),
        "Distrito Industrial",
        random.choice(cidades),
        "Depósito",
        cliente_base
    ))

    enderecos_estoque.append(cur.fetchone()[0])

# ============================================
# Estoque (N)
# ============================================

ids_estoque = []

for descricao, id_endereco in zip(estoques, enderecos_estoque):

    cur.execute("""
        INSERT INTO Estoque(descricao,id_endereco)
        VALUES(%s,%s)
        RETURNING id_estoque
    """, (
        descricao,
        id_endereco
    ))

    ids_estoque.append(cur.fetchone()[0])

# ============================================
# Estoque_Produto (todo produto em todo estoque)
# ============================================

for e in ids_estoque:
    for p in ids_produtos:

        cur.execute("""
            INSERT INTO Estoque_Produto
            (id_estoque,id_produto,quantidade)
            VALUES(%s,%s,%s)
        """, (
            e,
            p,
            random.choice([5, 8, 12, 18, 25, 40, 75, 100])
        ))

# ============================================
# Pedido (N)
# ============================================

ids_pedido = []
pedidos_info = []  # (id_pedido, id_cliente, data) — usado depois pela Entrega

for i in range(N):
    cliente = random.choice(clientes)
    # ~20% dos pedidos ficam sem vendedor (id_vendedor é opcional no schema)
    vendedor = random.choice(vendedores) if random.random() > 0.2 else None
    status = random.choice(status_pedido_opcoes)
    data_pedido = date.today() - timedelta(days=i * 4)

    cur.execute("""
        INSERT INTO Pedido
        (data,status,id_cliente,id_vendedor)
        VALUES(%s,%s,%s,%s)
        RETURNING id_pedido
    """, (
        data_pedido,
        status,
        cliente,
        vendedor
    ))

    id_pedido = cur.fetchone()[0]
    ids_pedido.append(id_pedido)
    pedidos_info.append((id_pedido, cliente, data_pedido))

# ============================================
# Entrega (N — uma por pedido, no endereço do respectivo cliente)
# ============================================

for id_pedido, id_cliente, data_pedido in pedidos_info:

    cur.execute("""
        INSERT INTO Entrega
        (status,data,id_pedido,id_endereco)
        VALUES(%s,%s,%s,%s)
    """, (
        random.choice(status_entrega_opcoes),
        data_pedido + timedelta(days=random.randint(1, 10)),
        id_pedido,
        endereco_por_cliente[id_cliente]
    ))

# ============================================
# Item Pedido (1 a 4 itens por pedido)
# ============================================

for pedido in ids_pedido:

    n_itens = random.randint(1, 4)

    for item in range(1, n_itens + 1):

        cur.execute("""
            INSERT INTO Item_Pedido
            (id_pedido,id_item,quantidade,preco_unitario,id_produto)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            pedido,
            item,
            random.randint(1, 5),
            round(random.uniform(50, 5000), 2),
            random.choice(ids_produtos)
        ))

# ============================================
# Compra (N)
# ============================================

ids_compra = []

for i in range(N):

    estoque = random.choice(ids_estoque)
    produto = random.choice(ids_produtos)

    cur.execute("""
        INSERT INTO Compra
        (data,id_estoque,id_produto)
        VALUES(%s,%s,%s)
        RETURNING id_compra
    """, (
        date.today() - timedelta(days=random.randint(0, 60)),
        estoque,
        produto
    ))

    ids_compra.append(cur.fetchone()[0])

# ============================================
# Item Compra (1 a 3 itens por compra)
# ============================================

for compra in ids_compra:

    n_itens = random.randint(1, 3)

    for item in range(1, n_itens + 1):

        cur.execute("""
            INSERT INTO Item_Compra
            (id_compra,id_item,quantidade,preco_unitario,id_produto)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            compra,
            item,
            random.randint(1, 20),
            round(random.uniform(30, 2000), 2),
            random.choice(ids_produtos)
        ))

conn.commit()

cur.close()
conn.close()

print("===================================")
print("Banco populado com sucesso!")
print(f"Pessoas: {len(pessoas)} | Clientes: {len(clientes)} | Vendedores: {len(vendedores)}")
print(f"Categorias: {len(ids_categoria)} | Produtos: {len(ids_produtos)} | Fornecedores: {len(ids_fornecedor)}")
print(f"Estoques: {len(ids_estoque)} | Pedidos: {len(ids_pedido)} | Compras: {len(ids_compra)}")
print("===================================")
