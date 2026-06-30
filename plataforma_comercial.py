import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime, date
import subprocess, sys
from db_config import DB_CONFIG
def _pip(pkg):
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--break-system-packages"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    import psycopg2
except ImportError:
    _pip("psycopg2-binary")
    import psycopg2

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plataforma Comercial",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Sistema de Gestão Comercial v1.0"}
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary-color: #2563eb;
        --text-color: #1f2937;
        --background-color: #f9fafb;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .success-box {
        background-color: #dcfce7;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #22c55e;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fef3c7;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #f59e0b;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── DB CLASS ─────────────────────────────────────────
@st.cache_resource
def get_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Erro de conexão: {e}")
        st.stop()

class DB:
    def __init__(self, conn):
        self.conn = conn

    def q(self, sql, p=(), fetch=True):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as c:
            c.execute(sql, p)
            if fetch:
                return c.fetchall()
            self.conn.commit()
            return c.rowcount

    def run(self, sql, p=()):
        try:
            return self.q(sql, p, fetch=False)
        except Exception as e:
            self.conn.rollback()
            raise e

# ─────────────────────────── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/shop.png", width=80)
    st.title("🏪 Plataforma Comercial")
    st.divider()
    
    page = st.radio(
        "Navegação",
        ["📊 Dashboard", "👤 Clientes", "📦 Produtos", "🧑‍💼 Vendedores", 
         "🛒 Pedidos", "🗃️ Estoque"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.caption("v1.0 — PostgreSQL")

# ─────────────────────────── DASHBOARD ────────────────────────────────────────
def dashboard():
    st.title("📊 Visão Geral do Sistema")
    st.markdown("Resumo das operações comerciais")
    
    db = DB(get_db())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        n_clientes = db.q("SELECT COUNT(*) as n FROM Cliente")[0]["n"]
        st.metric("👥 Clientes", n_clientes, "registrados")
    
    with col2:
        n_produtos = db.q("SELECT COUNT(*) as n FROM Produto")[0]["n"]
        st.metric("📦 Produtos", n_produtos, "no catálogo")
    
    with col3:
        n_pedidos = db.q("""SELECT COUNT(*) as n FROM Pedido 
                            WHERE status NOT IN ('CANCELADO','CONCLUIDO')""")[0]["n"]
        st.metric("🛒 Pedidos Ativos", n_pedidos, "em processamento")
    
    with col4:
        n_vendedores = db.q("SELECT COUNT(*) as n FROM Vendedor")[0]["n"]
        st.metric("💼 Vendedores", n_vendedores, "ativos")
    
    st.divider()
    
    # Gráfico de pedidos recentes
    st.subheader("📈 Pedidos Recentes")
    rows = db.q("""
        SELECT p.id_pedido, p.data, p.status, pc.nome, COUNT(ip.id_item) as itens
        FROM Pedido p
        JOIN Cliente c ON c.id=p.id_cliente
        JOIN Pessoa pc ON pc.id=c.id
        LEFT JOIN Item_Pedido ip ON ip.id_pedido=p.id_pedido
        GROUP BY p.id_pedido, p.data, p.status, pc.nome
        ORDER BY p.id_pedido DESC LIMIT 10
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum pedido registrado ainda")
    
    # Produtos mais cadastrados
    st.subheader("🏆 Produtos em Catálogo")
    prods = db.q("""
        SELECT nome, preco, 
               (SELECT COUNT(*) FROM Estoque_Produto WHERE id_produto=Produto.id_produto) as em_estoque
        FROM Produto
        LIMIT 10
    """)
    
    if prods:
        df_prods = pd.DataFrame(prods)
        st.dataframe(df_prods, use_container_width=True, hide_index=True)

# ─────────────────────────── CLIENTES ─────────────────────────────────────────
def clientes():
    st.title("👤 Clientes")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Novo Cliente")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    # Form
    with st.form("novo_cliente"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome completo *")
        with col2:
            telefone = st.text_input("Telefone")
        with col3:
            email = st.text_input("Email")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpf_cnpj = st.text_input("CPF / CNPJ *")
        with col2:
            tipo = st.selectbox("Tipo *", ["PESSOA_FISICA", "PESSOA_JURIDICA"])
        
        submitted = st.form_submit_button("➕ Salvar Cliente", use_container_width=True)
        
        if submitted:
            if not nome or not cpf_cnpj:
                st.error("Nome e CPF/CNPJ são obrigatórios!")
            else:
                try:
                    rows = db.q("INSERT INTO Pessoa(nome,telefone,email) VALUES(%s,%s,%s) RETURNING id",
                               (nome, telefone, email))
                    db.run("INSERT INTO Cliente(id,cpf_cnpj,tipo) VALUES(%s,%s,%s)",
                          (rows[0]["id"], cpf_cnpj, tipo))
                    st.success(f"✅ Cliente '{nome}' cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    # Lista de clientes
    st.subheader("Clientes Cadastrados")
    rows = db.q("""
        SELECT p.id, p.nome, p.telefone, p.email, c.cpf_cnpj, c.tipo
        FROM Cliente c JOIN Pessoa p ON p.id=c.id
        ORDER BY p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado ainda")

# ─────────────────────────── PRODUTOS ─────────────────────────────────────────
def produtos():
    st.title("📦 Produtos")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Novo Produto")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    # Categorias
    cats = db.q("SELECT id_categoria, nome FROM Categoria_Produto ORDER BY nome")
    cat_map = {c["nome"]: c["id_categoria"] for c in cats}
    
    with st.form("novo_produto"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome do produto *")
        with col2:
            preco = st.number_input("Preço (R$) *", min_value=0.01, step=0.01)
        with col3:
            categoria = st.selectbox("Categoria *", list(cat_map.keys()) if cat_map else [""])
        
        descricao = st.text_area("Descrição", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            nova_cat = st.text_input("Criar nova categoria")
        with col2:
            if st.form_submit_button("➕ Adicionar Categoria"):
                if nova_cat:
                    try:
                        db.run("INSERT INTO Categoria_Produto(nome) VALUES(%s)", (nova_cat,))
                        st.success("Categoria criada!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        
        submitted = st.form_submit_button("➕ Salvar Produto", use_container_width=True)
        
        if submitted:
            if not nome or not categoria:
                st.error("Nome e categoria são obrigatórios!")
            else:
                try:
                    db.run("INSERT INTO Produto(nome,descricao,preco,id_categoria) VALUES(%s,%s,%s,%s)",
                          (nome, descricao, preco, cat_map[categoria]))
                    st.success(f"✅ Produto '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Produtos em Catálogo")
    rows = db.q("""
        SELECT p.id_produto, p.nome, p.preco, cp.nome AS categoria, p.descricao
        FROM Produto p JOIN Categoria_Produto cp ON cp.id_categoria=p.id_categoria
        ORDER BY p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum produto cadastrado")

# ─────────────────────────── VENDEDORES ──────────────────────────────────────
def vendedores():
    st.title("🧑‍💼 Vendedores")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Novo Vendedor")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    with st.form("novo_vendedor"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome completo *")
        with col2:
            telefone = st.text_input("Telefone")
        with col3:
            matricula = st.text_input("Matrícula *")
        
        submitted = st.form_submit_button("➕ Salvar Vendedor", use_container_width=True)
        
        if submitted:
            if not nome or not matricula:
                st.error("Nome e matrícula são obrigatórios!")
            else:
                try:
                    r = db.q("INSERT INTO Pessoa(nome,telefone) VALUES(%s,%s) RETURNING id",
                            (nome, telefone))
                    db.run("INSERT INTO Vendedor(id,matricula) VALUES(%s,%s)",
                          (r[0]["id"], matricula))
                    st.success(f"✅ Vendedor '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Vendedores Cadastrados")
    rows = db.q("""
        SELECT v.id, p.nome, p.telefone, v.matricula
        FROM Vendedor v JOIN Pessoa p ON p.id=v.id
        ORDER BY p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum vendedor cadastrado")

# ─────────────────────────── PEDIDOS ──────────────────────────────────────────
def pedidos():
    st.title("🛒 Pedidos")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1])
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
    else:
        st.info("Nenhum pedido registrado")

# ─────────────────────────── ESTOQUE ──────────────────────────────────────────
def estoque():
    st.title("🗃️ Estoque")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Gerenciar Estoque")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    estoques = db.q("SELECT id_estoque, descricao FROM Estoque ORDER BY id_estoque")
    est_map = {e["descricao"]: e["id_estoque"] for e in estoques}
    
    produtos = db.q("SELECT id_produto, nome FROM Produto ORDER BY nome")
    prod_map = {p["nome"]: p["id_produto"] for p in produtos}
    
    with st.form("adicionar_estoque"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estoque_sel = st.selectbox("Estoque *", list(est_map.keys()) if est_map else [""])
        with col2:
            produto_sel = st.selectbox("Produto *", list(prod_map.keys()) if prod_map else [""])
        with col3:
            quantidade = st.number_input("Quantidade *", min_value=1, step=1)
        
        submitted = st.form_submit_button("➕ Adicionar ao Estoque", use_container_width=True)
        
        if submitted:
            if not estoque_sel or not produto_sel:
                st.error("Selecione estoque e produto!")
            else:
                try:
                    db.run("""INSERT INTO Estoque_Produto(id_estoque,id_produto,quantidade)
                             VALUES(%s,%s,%s)
                             ON CONFLICT(id_estoque,id_produto)
                             DO UPDATE SET quantidade=Estoque_Produto.quantidade+EXCLUDED.quantidade""",
                          (est_map[estoque_sel], prod_map[produto_sel], quantidade))
                    st.success(f"✅ {quantidade} un. de {produto_sel} adicionadas!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Situação do Estoque")
    rows = db.q("""
        SELECT e.descricao AS estoque, p.nome AS produto, ep.quantidade, p.preco,
               (ep.quantidade * p.preco) as valor_total
        FROM Estoque_Produto ep
        JOIN Estoque e ON e.id_estoque=ep.id_estoque
        JOIN Produto p ON p.id_produto=ep.id_produto
        ORDER BY e.descricao, p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
        df["preco"] = df["preco"].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Resumo
        total_items = sum([r["quantidade"] for r in rows])
        st.metric("📦 Total de itens em estoque", total_items)
    else:
        st.info("Estoque vazio")

# ─────────────────────────── MAIN ────────────────────────────────────────────
if page == "📊 Dashboard":
    dashboard()
elif page == "👤 Clientes":
    clientes()
elif page == "📦 Produtos":
    produtos()
elif page == "🧑‍💼 Vendedores":
    vendedores()
elif page == "🛒 Pedidos":
    pedidos()
elif page == "🗃️ Estoque":
    estoque()
