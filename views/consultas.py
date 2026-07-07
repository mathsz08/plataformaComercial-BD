import pandas as pd
from datetime import date, timedelta
import streamlit as st

from db import DB, get_db


def consultas():
    st.title("🔎 Consultas")
    st.markdown("Perguntas prontas para acompanhar a operação comercial.")

    db = DB(get_db())

    consulta = st.selectbox(
        "O que você deseja consultar?",
        [
            "Pedidos por situação",
            "Vendas por cliente e período",
            "Produtos por categoria e faixa de preço",
            "Produtos com pouco estoque",
            "Clientes por cidade e tipo",
            "Clientes com pedidos por situação",
            "Vendas por vendedor e período",
            "Vendedores por situação dos pedidos",
        ],
    )

    st.divider()

    if consulta == "Pedidos por situação":
        st.subheader("Pedidos por situação")
        status = st.selectbox(
            "Escolha a situação do pedido",
            ["PENDENTE", "PROCESSANDO", "ENVIADO", "CONCLUIDO", "CANCELADO"],
            index=1,
        )

        rows = db.q("""
            SELECT p.id_pedido AS pedido, p.data, pc.nome AS cliente,
                   COALESCE(pv.nome, 'Sem vendedor') AS vendedor,
                   COUNT(ip.id_item) AS quantidade_de_itens,
                   COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) AS valor_total
            FROM Pedido p
            JOIN Cliente c ON c.id = p.id_cliente
            JOIN Pessoa pc ON pc.id = c.id
            LEFT JOIN Vendedor v ON v.id = p.id_vendedor
            LEFT JOIN Pessoa pv ON pv.id = v.id
            LEFT JOIN Item_Pedido ip ON ip.id_pedido = p.id_pedido
            WHERE p.status = %s
            GROUP BY p.id_pedido, p.data, pc.nome, pv.nome
            ORDER BY p.data DESC, p.id_pedido DESC
        """, (status,))

        if rows:
            df = pd.DataFrame(rows)
            df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Pedidos encontrados", len(rows))
        else:
            st.info("Nenhum pedido encontrado nessa situação.")

    elif consulta == "Vendas por cliente e período":
        st.subheader("Vendas por cliente e período")
        clientes = db.q("""
            SELECT c.id, p.nome
            FROM Cliente c
            JOIN Pessoa p ON p.id = c.id
            ORDER BY p.nome
        """)
        cli_map = {"Todos os clientes": None}
        cli_map.update({c["nome"]: c["id"] for c in clientes})

        col1, col2, col3 = st.columns(3)
        with col1:
            cliente = st.selectbox("Cliente", list(cli_map.keys()))
        with col2:
            inicio = st.date_input("De", date.today() - timedelta(days=30))
        with col3:
            fim = st.date_input("Até", date.today())

        rows = db.q("""
            SELECT p.id_pedido AS pedido, p.data, pc.nome AS cliente, p.status,
                   COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) AS valor_total
            FROM Pedido p
            JOIN Cliente c ON c.id = p.id_cliente
            JOIN Pessoa pc ON pc.id = c.id
            LEFT JOIN Item_Pedido ip ON ip.id_pedido = p.id_pedido
            WHERE p.data BETWEEN %s AND %s
              AND (%s IS NULL OR c.id = %s)
            GROUP BY p.id_pedido, p.data, pc.nome, p.status
            ORDER BY p.data DESC, p.id_pedido DESC
        """, (inicio, fim, cli_map[cliente], cli_map[cliente]))

        if rows:
            total = sum([r["valor_total"] for r in rows])
            df = pd.DataFrame(rows)
            df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            col1, col2 = st.columns(2)
            col1.metric("Pedidos no período", len(rows))
            col2.metric("Valor total", f"R$ {total:,.2f}")
        else:
            st.info("Nenhuma venda encontrada para os filtros escolhidos.")

    elif consulta == "Clientes por cidade e tipo":
        st.subheader("Clientes por cidade e tipo")
        cidades = db.q("SELECT DISTINCT cidade FROM Endereco ORDER BY cidade")
        cidade_opcoes = ["Todas as cidades"] + [c["cidade"] for c in cidades if c["cidade"]]

        col1, col2 = st.columns(2)
        with col1:
            cidade = st.selectbox("Cidade", cidade_opcoes)
        with col2:
            tipo = st.selectbox("Tipo de cliente", ["Todos", "PESSOA_FISICA", "PESSOA_JURIDICA"])

        cidade_param = None if cidade == "Todas as cidades" else cidade
        tipo_param = None if tipo == "Todos" else tipo

        rows = db.q("""
            SELECT p.nome AS cliente, c.tipo, c.cpf_cnpj, p.telefone, p.email,
                   e.cidade, e.bairro, e.rua
            FROM Cliente c
            JOIN Pessoa p ON p.id = c.id
            LEFT JOIN Endereco e ON e.id_cliente = c.id
            WHERE (%s IS NULL OR e.cidade = %s)
              AND (%s IS NULL OR c.tipo = %s)
            ORDER BY e.cidade, p.nome
        """, (cidade_param, cidade_param, tipo_param, tipo_param))

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.metric("Clientes encontrados", len(rows))
        else:
            st.info("Nenhum cliente encontrado para os filtros escolhidos.")

    elif consulta == "Clientes com pedidos por situação":
        st.subheader("Clientes com pedidos por situação")
        status = st.selectbox(
            "Situação do pedido",
            ["Todos", "PENDENTE", "PROCESSANDO", "ENVIADO", "CONCLUIDO", "CANCELADO"],
        )
        status_param = None if status == "Todos" else status

        rows = db.q("""
            SELECT pc.nome AS cliente, COUNT(p.id_pedido) AS pedidos,
                   COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) AS valor_total,
                   MAX(p.data) AS ultimo_pedido
            FROM Cliente c
            JOIN Pessoa pc ON pc.id = c.id
            JOIN Pedido p ON p.id_cliente = c.id
            LEFT JOIN Item_Pedido ip ON ip.id_pedido = p.id_pedido
            WHERE (%s IS NULL OR p.status = %s)
            GROUP BY c.id, pc.nome
            ORDER BY pedidos DESC, valor_total DESC, pc.nome
        """, (status_param, status_param))

        if rows:
            df = pd.DataFrame(rows)
            df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Clientes encontrados", len(rows))
        else:
            st.info("Nenhum cliente possui pedidos nessa situação.")

    elif consulta == "Vendas por vendedor e período":
        st.subheader("Vendas por vendedor e período")
        vendedores = db.q("""
            SELECT v.id, p.nome
            FROM Vendedor v
            JOIN Pessoa p ON p.id = v.id
            ORDER BY p.nome
        """)
        vend_map = {"Todos os vendedores": None}
        vend_map.update({v["nome"]: v["id"] for v in vendedores})

        col1, col2, col3 = st.columns(3)
        with col1:
            vendedor = st.selectbox("Vendedor", list(vend_map.keys()))
        with col2:
            inicio = st.date_input("Início", date.today() - timedelta(days=45))
        with col3:
            fim = st.date_input("Fim", date.today())

        rows = db.q("""
            SELECT pv.nome AS vendedor, COUNT(DISTINCT p.id_pedido) AS pedidos,
                   COUNT(ip.id_item) AS itens_vendidos,
                   COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) AS valor_total
            FROM Vendedor v
            JOIN Pessoa pv ON pv.id = v.id
            LEFT JOIN Pedido p ON p.id_vendedor = v.id AND p.data BETWEEN %s AND %s
            LEFT JOIN Item_Pedido ip ON ip.id_pedido = p.id_pedido
            WHERE (%s IS NULL OR v.id = %s)
            GROUP BY v.id, pv.nome
            ORDER BY valor_total DESC, pedidos DESC, pv.nome
        """, (inicio, fim, vend_map[vendedor], vend_map[vendedor]))

        if rows:
            total = sum([r["valor_total"] for r in rows])
            df = pd.DataFrame(rows)
            df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Total vendido no período", f"R$ {total:,.2f}")
        else:
            st.info("Nenhuma venda encontrada para os filtros escolhidos.")

    elif consulta == "Vendedores por situação dos pedidos":
        st.subheader("Vendedores por situação dos pedidos")
        status = st.selectbox(
            "Situação do pedido",
            ["PENDENTE", "PROCESSANDO", "ENVIADO", "CONCLUIDO", "CANCELADO"],
            index=1,
        )

        rows = db.q("""
            SELECT pv.nome AS vendedor, v.matricula, COUNT(p.id_pedido) AS pedidos,
                   COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) AS valor_total
            FROM Vendedor v
            JOIN Pessoa pv ON pv.id = v.id
            LEFT JOIN Pedido p ON p.id_vendedor = v.id AND p.status = %s
            LEFT JOIN Item_Pedido ip ON ip.id_pedido = p.id_pedido
            GROUP BY v.id, pv.nome, v.matricula
            HAVING COUNT(p.id_pedido) > 0
            ORDER BY pedidos DESC, valor_total DESC, pv.nome
        """, (status,))

        if rows:
            df = pd.DataFrame(rows)
            df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Vendedores encontrados", len(rows))
        else:
            st.info("Nenhum vendedor possui pedidos nessa situação.")

    elif consulta == "Produtos por categoria e faixa de preço":
        st.subheader("Produtos por categoria e faixa de preço")
        categorias = db.q("SELECT id_categoria, nome FROM Categoria_Produto ORDER BY nome")
        cat_map = {"Todas as categorias": None}
        cat_map.update({c["nome"]: c["id_categoria"] for c in categorias})

        col1, col2, col3 = st.columns(3)
        with col1:
            categoria = st.selectbox("Categoria", list(cat_map.keys()))
        with col2:
            preco_min = st.number_input("Preço mínimo", min_value=0.0, value=0.0, step=10.0)
        with col3:
            preco_max = st.number_input("Preço máximo", min_value=0.0, value=5000.0, step=10.0)

        rows = db.q("""
            SELECT p.nome AS produto, cp.nome AS categoria, p.preco,
                   COALESCE(SUM(ep.quantidade), 0) AS quantidade_em_estoque
            FROM Produto p
            JOIN Categoria_Produto cp ON cp.id_categoria = p.id_categoria
            LEFT JOIN Estoque_Produto ep ON ep.id_produto = p.id_produto
            WHERE p.preco BETWEEN %s AND %s
              AND (%s IS NULL OR cp.id_categoria = %s)
            GROUP BY p.id_produto, p.nome, cp.nome, p.preco
            ORDER BY p.preco, p.nome
        """, (preco_min, preco_max, cat_map[categoria], cat_map[categoria]))

        if rows:
            df = pd.DataFrame(rows)
            df["preco"] = df["preco"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Produtos encontrados", len(rows))
        else:
            st.info("Nenhum produto encontrado nessa faixa.")

    elif consulta == "Produtos com pouco estoque":
        st.subheader("Produtos com pouco estoque")
        limite = st.number_input("Mostrar produtos com quantidade até", min_value=1, value=20, step=1)
        estoques = db.q("SELECT id_estoque, descricao FROM Estoque ORDER BY descricao")
        est_map = {"Todos os estoques": None}
        est_map.update({e["descricao"]: e["id_estoque"] for e in estoques})
        estoque_sel = st.selectbox("Estoque", list(est_map.keys()))

        rows = db.q("""
            SELECT e.descricao AS estoque, p.nome AS produto, cp.nome AS categoria,
                   ep.quantidade, p.preco,
                   (ep.quantidade * p.preco) AS valor_em_estoque
            FROM Estoque_Produto ep
            JOIN Estoque e ON e.id_estoque = ep.id_estoque
            JOIN Produto p ON p.id_produto = ep.id_produto
            JOIN Categoria_Produto cp ON cp.id_categoria = p.id_categoria
            WHERE ep.quantidade <= %s
              AND (%s IS NULL OR e.id_estoque = %s)
            ORDER BY ep.quantidade, p.nome
        """, (limite, est_map[estoque_sel], est_map[estoque_sel]))

        if rows:
            df = pd.DataFrame(rows)
            df["preco"] = df["preco"].apply(lambda x: f"R$ {x:,.2f}")
            df["valor_em_estoque"] = df["valor_em_estoque"].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.metric("Itens com pouco estoque", len(rows))
        else:
            st.info("Nenhum produto abaixo do limite escolhido.")

