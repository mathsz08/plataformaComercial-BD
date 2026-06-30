# 🏪 Plataforma Comercial

Sistema de gestão comercial integrado com PostgreSQL e interface web moderna em Streamlit.

## 📋 Requisitos

- **Python 3.8+** instalado
- **PostgreSQL** em execução (localhost:5432)

## 🚀 Instalação Rápida

### Linux / Mac

```bash
# 1. Dar permissão de execução
chmod +x instalar.sh

# 2. Instalar dependências e criar banco de dados
./instalar.sh

# 3. (Opcional) Popular banco com dados de teste
python3 popular_tabela.py

# 4. Rodar a aplicação
streamlit run plataforma_comercial.py
```

### Windows

```bash
# 1. Instalar dependências e criar banco de dados
python -m pip install -r requirements.txt

# 2. (Opcional) Popular banco com dados de teste
python popular_tabela.py

# 3. Rodar a aplicação
streamlit run plataforma_comercial.py
```

## 📦 O que será instalado

- **psycopg2-binary** — Driver PostgreSQL para Python
- **streamlit** — Framework web para interface visual
- **pandas** — Manipulação de dados
- **altair** — Visualizações de gráficos

## 🔧 Configuração do Banco de Dados

O script `instalar.sh` faz tudo automaticamente:
- ✅ Cria o banco `plataforma_comercial`
- ✅ Cria todas as tabelas

Credenciais usadas (altere se necessário):
```
Host: localhost
Port: 5432
Database: plataforma_comercial
User: postgres
Password: senha_do_usuario
```

## 📊 Populando o Banco com Dados de Teste (Opcional)

O arquivo `popular_tabela.py` cria dados aleatórios para teste:

```bash
python3 popular_tabela.py  # Linux/Mac
# ou
python popular_tabela.py   # Windows
```

**O que é adicionado:**
- 👥 4 pessoas registradas
- 🛍️ 2 clientes
- 💼 2 vendedores
- 📦 2 produtos com categorias
- 🏭 2 fornecedores
- 🗃️ 2 estoques com produtos
- 🛒 2 pedidos com itens
- 🚚 2 entregas registradas
- 📋 Dados de compras

**Não é obrigatório** — você pode usar a aplicação vazia e adicionar dados manualmente.

## ▶️ Rodando a Aplicação

```bash
streamlit run plataforma_streamlit.py
```

A aplicação abrirá em: **http://localhost:8501**

## 📂 Estrutura de Arquivos

```
plataforma_comercial/
├── plataforma_comercial.py    # Aplicação principal
├── requirements.txt            # Dependências Python
├── instalar.sh                # Script instalação (Linux/Mac)
└── README.md                  # Este arquivo
```

## 📖 Como Usar

### Dashboard
Veja um resumo das operações comerciais, número de clientes, produtos, pedidos ativos e vendedores.

### Clientes
- ➕ Cadastre pessoas física/jurídica
- 📋 Visualize clientes cadastrados
- CPF/CNPJ obrigatório

### Produtos
- ➕ Adicione produtos com categoria e preço
- 📝 Crie categorias na hora
- 📊 Visualize catálogo completo

### Vendedores
- ➕ Cadastre vendedores com matrícula
- 📋 Veja equipe de vendas
- 📞 Registre telefone de contato

### Pedidos
- ➕ Crie pedidos vinculados a clientes
- 🔄 Atualize status (Pendente → Processando → Enviado → Concluído)
- 🛑 Cancele pedidos quando necessário

### Estoque
- ➕ Adicione produtos ao estoque
- 📦 Veja quantidade e valor total
- 📊 Resumo de itens em estoque

## 🐛 Troubleshooting

### Erro: "can't connect to database"
```
✓ Verifique se PostgreSQL está rodando
✓ Confirme credenciais (user/password)
✓ Verifique se banco 'plataforma_comercial' existe
```

### Erro: "module not found"
```bash
pip install -r requirements.txt
```

### Streamlit não abre no navegador
```bash
# Tente manualmente:
start http://localhost:8501
streamlit run plataforma_comercial.py
```

## 💡 Dicas

- **Atualizar dados**: Clique no botão "🔄 Atualizar" na página
- **Exportar tabelas**: Clique nas três barras (⋮) da tabela Streamlit
- **Validações**: Campos marcados com * são obrigatórios


## Suporte

Se encontrar problemas:
1. Verifique conexão com PostgreSQL
2. Reinstale dependências: `pip install -r requirements.txt --force-reinstall`
3. Reinicie a aplicação

---

**v1.0 — Plataforma Comercial | PostgreSQL + Streamlit**
