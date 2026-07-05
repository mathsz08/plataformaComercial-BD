import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime, date, timedelta
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
         "🛒 Pedidos", "🗃️ Estoque", "🔎 Consultas"],
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

    if 'edit_cliente' not in st.session_state:
        st.session_state.edit_cliente = None
    if 'del_cliente' not in st.session_state:
        st.session_state.del_cliente = None
    
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

     # ================ SEÇÃO DE EDIÇÃO ================
    if st.session_state.edit_cliente:
        with st.expander("✏️ Editando Cliente", expanded=True):
            cliente_id = st.session_state.edit_cliente
            # Buscar dados atuais
            dados = db.q("""
                SELECT p.nome, p.telefone, p.email, c.cpf_cnpj, c.tipo 
                FROM Cliente c JOIN Pessoa p ON p.id=c.id 
                WHERE c.id=%s
            """, (cliente_id,))[0]
            
            with st.form("edit_cliente_form"):
                st.info(f"Editando cliente ID: {cliente_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome *", value=dados['nome'])
                with col2:
                    cpf_edit = st.text_input("CPF/CNPJ *", value=dados['cpf_cnpj'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    telefone_edit = st.text_input("Telefone", value=dados['telefone'] or '')
                with col2:
                    email_edit = st.text_input("Email", value=dados['email'] or '')
                with col3:
                    tipo_edit = st.selectbox(
                        "Tipo *", 
                        ["PESSOA_FISICA", "PESSOA_JURIDICA"],
                        index=0 if dados['tipo'] == 'PESSOA_FISICA' else 1
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit or not cpf_edit:
                            st.error("Nome e CPF/CNPJ são obrigatórios!")
                        else:
                            try:
                                db.run("UPDATE Pessoa SET nome=%s, telefone=%s, email=%s WHERE id=%s", 
                                      (nome_edit, telefone_edit, email_edit, cliente_id))
                                db.run("UPDATE Cliente SET cpf_cnpj=%s, tipo=%s WHERE id=%s", 
                                      (cpf_edit, tipo_edit, cliente_id))
                                st.success("✅ Cliente atualizado com sucesso!")
                                st.session_state.edit_cliente = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_cliente = None
                        st.rerun()
    
    # ================ SEÇÃO DE EXCLUSÃO ================
    if st.session_state.del_cliente:
        cliente_id = st.session_state.del_cliente
        nome_cliente = db.q("""
            SELECT p.nome FROM Cliente c JOIN Pessoa p ON p.id=c.id WHERE c.id=%s
        """, (cliente_id,))[0]['nome']
        
        st.warning(f"""
        ### ⚠️ Confirmar Exclusão
        
        Tem certeza que deseja excluir o cliente **{nome_cliente}**?
        
        **ATENÇÃO:** Esta ação pode ser bloqueada se o cliente tiver pedidos vinculados.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Cliente WHERE id=%s", (cliente_id,))
                    st.success(f"✅ Cliente '{nome_cliente}' excluído com sucesso!")
                    st.session_state.del_cliente = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_cliente = None
                st.rerun()
    
    # ================ TABELA DE CLIENTES COM BOTÕES ================
    # Converter para DataFrame
    df = pd.DataFrame(rows)
    
    # Exibir tabela com botões usando colunas
    st.write("### Lista de Clientes")
    
    for idx, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
        
        with col1:
            st.write(f"**{row['nome']}**")
        with col2:
            st.write(row['cpf_cnpj'])
        with col3:
            st.write(row['telefone'] or '—')
        with col4:
            st.write(row['email'] or '—')
        with col5:
            if st.button("✏️", key=f"edit_{row['id']}", help="Editar cliente"):
                st.session_state.edit_cliente = row['id']
                st.rerun()
        with col6:
            if st.button("🗑️", key=f"del_{row['id']}", help="Excluir cliente"):
                st.session_state.del_cliente = row['id']
                st.rerun()
        
        st.divider()

# ─────────────────────────── PRODUTOS ─────────────────────────────────────────
def produtos():
    st.title("📦 Produtos")
    
    db = DB(get_db())

    if 'edit_produto' not in st.session_state:
        st.session_state.edit_produto = None
    if 'del_produto' not in st.session_state:
        st.session_state.del_produto = None
    
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

    # ================ SEÇÃO DE EDIÇÃO ================
    if st.session_state.edit_produto:
        with st.expander("✏️ Editando Produto", expanded=True):
            produto_id = st.session_state.edit_produto
            # Buscar dados atuais
            dados = db.q("""
                SELECT p.id_produto, p.nome, p.descricao, p.preco, p.id_categoria, cp.nome AS categoria_nome
                FROM Produto p 
                JOIN Categoria_Produto cp ON cp.id_categoria = p.id_categoria
                WHERE p.id_produto=%s
            """, (produto_id,))[0]
            
            # Recarregar categorias para o selectbox
            cats_edit = db.q("SELECT id_categoria, nome FROM Categoria_Produto ORDER BY nome")
            cat_edit_map = {c["nome"]: c["id_categoria"] for c in cats_edit}
            
            with st.form("edit_produto_form"):
                st.info(f"Editando produto ID: {produto_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome *", value=dados['nome'])
                with col2:
                    preco_edit = st.number_input("Preço (R$) *", min_value=0.01, step=0.01, value=float(dados['preco']))
                
                col1, col2 = st.columns(2)
                with col1:
                    categoria_edit = st.selectbox(
                        "Categoria *", 
                        list(cat_edit_map.keys()),
                        index=list(cat_edit_map.keys()).index(dados['categoria_nome']) if dados['categoria_nome'] in cat_edit_map else 0
                    )
                with col2:
                    # Campo para criar nova categoria durante a edição
                    nova_cat_edit = st.text_input("Ou crie uma nova categoria")
                    if nova_cat_edit and st.form_submit_button("➕ Adicionar Categoria (edição)"):
                        try:
                            db.run("INSERT INTO Categoria_Produto(nome) VALUES(%s)", (nova_cat_edit,))
                            st.success("Categoria criada! Recarregue a página.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                
                descricao_edit = st.text_area("Descrição", value=dados['descricao'] or '', height=100)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit or not preco_edit:
                            st.error("Nome e preço são obrigatórios!")
                        else:
                            try:
                                # Atualizar dados do produto
                                db.run("""
                                    UPDATE Produto 
                                    SET nome=%s, descricao=%s, preco=%s, id_categoria=%s 
                                    WHERE id_produto=%s
                                """, (nome_edit, descricao_edit, preco_edit, cat_edit_map[categoria_edit], produto_id))
                                st.success("✅ Produto atualizado com sucesso!")
                                st.session_state.edit_produto = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_produto = None
                        st.rerun()
    
    # ================ SEÇÃO DE EXCLUSÃO ================
    if st.session_state.del_produto:
        produto_id = st.session_state.del_produto
        nome_produto = db.q("SELECT nome FROM Produto WHERE id_produto=%s", (produto_id,))[0]['nome']
        
        st.warning(f"""
        ### ⚠️ Confirmar Exclusão
        
        Tem certeza que deseja excluir o produto **{nome_produto}**?
        
        **ATENÇÃO:** Esta ação pode ser bloqueada se o produto estiver vinculado a:
        - Pedidos (itens de pedido)
        - Estoque
        - Fornecedores
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Produto WHERE id_produto=%s", (produto_id,))
                    st.success(f"✅ Produto '{nome_produto}' excluído com sucesso!")
                    st.session_state.del_produto = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_produto = None
                st.rerun()
    
    # ================ TABELA DE PRODUTOS COM BOTÕES ================
    if rows:
        df = pd.DataFrame(rows)
        df['preco'] = df['preco'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.write("### Lista de Produtos")
        
        for idx, row in df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
            
            with col1:
                st.write(f"**{row['nome']}**")
            with col2:
                st.write(row['categoria'])
            with col3:
                st.write(row['preco'])
            with col4:
                st.write(row['descricao'][:50] + '...' if len(str(row['descricao'])) > 50 else row['descricao'])
            with col5:
                if st.button("✏️", key=f"edit_prod_{row['id_produto']}", help="Editar produto"):
                    st.session_state.edit_produto = row['id_produto']
                    st.rerun()
            with col6:
                if st.button("🗑️", key=f"del_prod_{row['id_produto']}", help="Excluir produto"):
                    st.session_state.del_produto = row['id_produto']
                    st.rerun()
            
            st.divider()

# ─────────────────────────── VENDEDORES ──────────────────────────────────────
def vendedores():
    st.title("🧑‍💼 Vendedores")
    
    db = DB(get_db())

    if 'edit_vendedor' not in st.session_state:
        st.session_state.edit_vendedor = None
    if 'del_vendedor' not in st.session_state:
        st.session_state.del_vendedor = None
    
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

    # ================ SEÇÃO DE EDIÇÃO ================
    if st.session_state.edit_vendedor:
        with st.expander("✏️ Editando Vendedor", expanded=True):
            vendedor_id = st.session_state.edit_vendedor
            # Buscar dados atuais
            dados = db.q("""
                SELECT p.nome, p.telefone, v.matricula 
                FROM Vendedor v JOIN Pessoa p ON p.id=v.id 
                WHERE v.id=%s
            """, (vendedor_id,))[0]
            
            with st.form("edit_vendedor_form"):
                st.info(f"Editando vendedor ID: {vendedor_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome *", value=dados['nome'])
                with col2:
                    matricula_edit = st.text_input("Matrícula *", value=dados['matricula'])
                
                telefone_edit = st.text_input("Telefone", value=dados['telefone'] or '')
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit or not matricula_edit:
                            st.error("Nome e matrícula são obrigatórios!")
                        else:
                            try:
                                db.run("UPDATE Pessoa SET nome=%s, telefone=%s WHERE id=%s", 
                                      (nome_edit, telefone_edit, vendedor_id))
                                db.run("UPDATE Vendedor SET matricula=%s WHERE id=%s", 
                                      (matricula_edit, vendedor_id))
                                st.success("✅ Vendedor atualizado com sucesso!")
                                st.session_state.edit_vendedor = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_vendedor = None
                        st.rerun()
    
    # ================ SEÇÃO DE EXCLUSÃO ================
    if st.session_state.del_vendedor:
        vendedor_id = st.session_state.del_vendedor
        nome_vendedor = db.q("""
            SELECT p.nome FROM Vendedor v JOIN Pessoa p ON p.id=v.id WHERE v.id=%s
        """, (vendedor_id,))[0]['nome']
        
        st.warning(f"""
        ### ⚠️ Confirmar Exclusão
        
        Tem certeza que deseja excluir o vendedor **{nome_vendedor}**?
        
        **ATENÇÃO:** Esta ação pode ser bloqueada se o vendedor tiver pedidos vinculados.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Vendedor WHERE id=%s", (vendedor_id,))
                    st.success(f"✅ Vendedor '{nome_vendedor}' excluído com sucesso!")
                    st.session_state.del_vendedor = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_vendedor = None
                st.rerun()
    
    # ================ TABELA DE VENDEDORES COM BOTÕES ================
    df = pd.DataFrame(rows)
    
    st.write("### Lista de Vendedores")
    
    for idx, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        
        with col1:
            st.write(f"**{row['nome']}**")
        with col2:
            st.write(row['matricula'])
        with col3:
            st.write(row['telefone'] or '—')
        with col4:
            if st.button("✏️", key=f"edit_vend_{row['id']}", help="Editar vendedor"):
                st.session_state.edit_vendedor = row['id']
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"del_vend_{row['id']}", help="Excluir vendedor"):
                st.session_state.del_vendedor = row['id']
                st.rerun()
        
        st.divider()

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

# ─────────────────────────── CONSULTAS ────────────────────────────────────────
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
elif page == "🔎 Consultas":
    consultas()
