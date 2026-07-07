import pandas as pd
from datetime import date
import streamlit as st

from db import DB, get_db


def pedidos():
    st.title("🛒 Pedidos")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        st.subheader("Novo Pedido")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    clientes = db.q("SELECT c.id, p.nome FROM Cliente c JOIN Pessoa p ON p.id=c.id ORDER BY p.nome")
    cli_map = {c["nome"]: c["id"] for c in clientes}
    
    vendedores = db.q("SELECT v.id, p.nome FROM Vendedor v JOIN Pessoa p ON p.id=v.id ORDER BY p.nome")
    vend_map = {v["nome"]: v["id"] for v in vendedores}
    
    with st.form("novo_pedido"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cliente = st.selectbox("Cliente *", list(cli_map.keys()) if cli_map else [""])
        with col2:
            vendedor = st.selectbox("Vendedor (opcional)", ["—"] + list(vend_map.keys()))
        with col3:
            data_pedido = st.date_input("Data", date.today())
        
        status = st.selectbox("Status", ["PENDENTE", "PROCESSANDO", "ENVIADO", "CONCLUIDO", "CANCELADO"])
        
        submitted = st.form_submit_button("➕ Criar Pedido", use_container_width=True)
        
        if submitted:
            if not cliente:
                st.error("Cliente é obrigatório!")
            else:
                try:
                    vend_id = vend_map.get(vendedor) if vendedor != "—" else None
                    db.run("INSERT INTO Pedido(data,status,id_cliente,id_vendedor) VALUES(%s,%s,%s,%s)",
                          (data_pedido, status, cli_map[cliente], vend_id))
                    st.success(f"✅ Pedido criado para {cliente}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Pedidos Registrados")
    rows = db.q("""
        SELECT p.id_pedido, p.data, p.status, pc.nome AS cliente, COALESCE(pv.nome,'—') AS vendedor,
               COUNT(ip.id_item) as itens, COALESCE(SUM(ip.quantidade*ip.preco_unitario),0) as total
        FROM Pedido p
        JOIN Cliente c ON c.id=p.id_cliente
        JOIN Pessoa pc ON pc.id=c.id
        LEFT JOIN Vendedor v ON v.id=p.id_vendedor
        LEFT JOIN Pessoa pv ON pv.id=v.id
        LEFT JOIN Item_Pedido ip ON ip.id_pedido=p.id_pedido
        GROUP BY p.id_pedido, p.data, p.status, pc.nome, pv.nome
        ORDER BY p.id_pedido DESC
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        
        # Colorir status
        status_colors = {
            "PENDENTE": "🟡",
            "PROCESSANDO": "🔵",
            "ENVIADO": "🟣",
            "CONCLUIDO": "🟢",
            "CANCELADO": "🔴"
        }
        df["status"] = df["status"].map(lambda x: f"{status_colors.get(x, '')} {x}")
        
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Atualizar Pedido")
        pedidos_map = {f"Pedido {r['id_pedido']} - {r['cliente']} ({r['status']})": r for r in rows}

        with st.form("alterar_status_pedido"):
            col1, col2 = st.columns(2)
            with col1:
                pedido_label = st.selectbox("Pedido", list(pedidos_map.keys()))
            with col2:
                novo_status = st.selectbox(
                    "Novo status",
                    ["PENDENTE", "PROCESSANDO", "ENVIADO", "CONCLUIDO", "CANCELADO"],
                )

            if st.form_submit_button("💾 Salvar status do pedido", use_container_width=True):
                pedido_id = pedidos_map[pedido_label]["id_pedido"]
                try:
                    db.run("UPDATE Pedido SET status=%s WHERE id_pedido=%s", (novo_status, pedido_id))
                    st.success(f"✅ Pedido {pedido_id} atualizado para {novo_status}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar pedido: {e}")

        st.subheader("Cancelar ou Excluir Pedido")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            acao_label = st.selectbox("Pedido para ação", list(pedidos_map.keys()), key="pedido_acao")
        pedido_acao_id = pedidos_map[acao_label]["id_pedido"]
        with col2:
            if st.button("🚫 Cancelar", use_container_width=True):
                try:
                    db.run("UPDATE Pedido SET status='CANCELADO' WHERE id_pedido=%s", (pedido_acao_id,))
                    st.success(f"✅ Pedido {pedido_acao_id} cancelado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cancelar pedido: {e}")
        with col3:
            if st.button("🗑️ Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Pedido WHERE id_pedido=%s", (pedido_acao_id,))
                    st.success(f"✅ Pedido {pedido_acao_id} excluído.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir pedido: {e}")
    else:
        st.info("Nenhum pedido registrado")

