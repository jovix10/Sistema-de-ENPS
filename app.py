import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import io
import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gestão de Engajamento FIEAC", layout="wide")

# 2. BANCO DE DADOS
def conectar():
    conn = sqlite3.connect('gestao_enps.db')
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def configurar_banco_inicial():
    conn = conectar()
    cursor = conn.cursor()
    # Tabela de Usuários com a nova coluna Unidade
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        nome TEXT, 
        usuario TEXT UNIQUE, 
        senha TEXT, 
        perfil TEXT,
        unidade TEXT)''')
    
    # Tabela de Respostas
    cursor.execute('''CREATE TABLE IF NOT EXISTS respostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        id_usuario INTEGER, 
        unidade TEXT, 
        nota_enps INTEGER,
        feedback_aberto TEXT, 
        data_envio DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insere você como ADM
    cursor.execute("""
        INSERT OR REPLACE INTO usuarios (id, nome, usuario, senha, perfil, unidade) 
        VALUES (1, 'João Victor', 'joao.adm', 'fieac123', 'ADM', 'FIEAC')
    """)
    conn.commit()
    conn.close()

configurar_banco_inicial()

# 3. PDF ESTRATÉGICO
def gerar_pdf_estrategico(df, score, p, n, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "RELATORIO DE ENGAJAMENTO - UNIPES/RH", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, f"Este relatorio apresenta o eNPS ({int(score)}). Notas 9-10 sao Promotores, 7-8 Neutros e 0-6 Detratores.")
    pdf.ln(5)
    pdf.cell(190, 8, f"Total de Respostas: {len(df)} | Promotores: {p} | Neutros: {n} | Detratores: {d}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# 4. GERENCIAMENTO DE ACESSO
if 'logado' not in st.session_state: st.session_state.logado = False
if 'respondido' not in st.session_state: st.session_state.respondido = False

if not st.session_state.logado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("📊 Portal eNPS FIEAC")
        u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
        if st.button("Acessar", use_container_width=True):
            conn = conectar(); cursor = conn.cursor()
            cursor.execute('SELECT perfil, nome, id FROM usuarios WHERE usuario = ? AND senha = ?', (u.strip(), p.strip()))
            d = cursor.fetchone(); conn.close()
            if d:
                st.session_state.update({"logado": True, "perfil": d[0], "nome": d[1], "user_id": d[2]})
                st.rerun()
            else: st.error("Acesso negado.")

else:
    st.sidebar.title(f"👤 {st.session_state.nome}")
    if st.sidebar.button("Sair"): st.session_state.clear(); st.rerun()

    if st.session_state.perfil == 'ADM':
        st.title("🛡️ Painel Administrativo")
        t1, t2, t3 = st.tabs(["📊 Dashboard", "🏢 Por Unidade", "👥 Gestão de Usuários"])

        conn = conectar()
        df_res = pd.read_sql_query("SELECT * FROM respostas", conn)
        df_users = pd.read_sql_query("SELECT id, nome, usuario, perfil, unidade FROM usuarios", conn)
        conn.close()

        with t1:
            if df_res.empty: st.info("Sem dados.")
            else:
                p_n = len(df_res[df_res['nota_enps'] >= 9])
                d_n = len(df_res[df_res['nota_enps'] <= 6])
                n_n = len(df_res) - (p_n + d_n)
                score = ((p_n - d_n) / len(df_res)) * 100
                fig = go.Figure(go.Pie(labels=['Promotores', 'Passivos', 'Detratores'], values=[p_n, n_n, d_n], hole=.6, marker_colors=['#79b3e1', '#f3d96e', '#d96c4d']))
                fig.update_layout(annotations=[dict(text=f"eNPS<br>{int(score)}", x=0.5, y=0.5, font_size=30, showarrow=False)], showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                pdf_bytes = gerar_pdf_estrategico(df_res, score, p_n, n_n, d_n)
                st.download_button("📥 Baixar PDF Estratégico", pdf_bytes, "Relatorio_FIEAC.pdf")

        with t2:
            if not df_res.empty:
                df_u = df_res.groupby('unidade').apply(lambda x: ((len(x[x['nota_enps']>=9]) - len(x[x['nota_enps']<=6])) / len(x)) * 100).reset_index(name='eNPS')
                st.plotly_chart(px.bar(df_u, x='unidade', y='eNPS', color='eNPS', color_continuous_scale='RdYlGn'), use_container_width=True)

        with t3:
            st.subheader("📥 Importação e Controle de Dados")
            c1, c2 = st.columns(2)
            with c1:
                # Modelo com exemplo incluindo Unidade
                buffer = io.BytesIO()
                pd.DataFrame({
                    "nome": ["Exemplo Silva"], 
                    "usuario": ["exemplo.1"], 
                    "senha": ["123"], 
                    "perfil": ["USER"], 
                    "unidade": ["SESI"]
                }).to_excel(buffer, index=False)
                st.download_button("📥 Baixar Modelo de Planilha", buffer.getvalue(), "modelo_usuarios_fieac.xlsx")
                
                up = st.file_uploader("Subir planilha preenchida", type=["xlsx"])
                if up:
                    df_up = pd.read_excel(up)
                    if st.button("Confirmar Importação"):
                        conn = conectar(); cursor = conn.cursor()
                        for _, r in df_up.iterrows():
                            try:
                                cursor.execute("""
                                    INSERT INTO usuarios (nome, usuario, senha, perfil, unidade) 
                                    VALUES (?,?,?,?,?)
                                """, (r['nome'], r['usuario'], str(r['senha']), r['perfil'], r['unidade']))
                            except: continue
                        conn.commit(); conn.close(); st.success("Importação concluída!"); st.rerun()
            
            with c2:
                # RESET TOTAL
                if st.button("⚠️ RESET TOTAL (Apagar Tudo)"):
                    conn = conectar(); cursor = conn.cursor()
                    cursor.execute("DELETE FROM respostas")
                    cursor.execute("DELETE FROM usuarios WHERE usuario != 'joao.adm'")
                    conn.commit(); conn.close()
                    st.warning("Banco de dados resetado com sucesso!")
                    st.rerun()

            st.divider()
            st.subheader("👥 Usuários Cadastrados (Excluir Individual)")
            if df_users.empty:
                st.write("Nenhum usuário cadastrado além do administrador.")
            else:
                for i, row in df_users.iterrows():
                    if row['usuario'] != 'joao.adm':
                        cols = st.columns([3, 2, 2, 1])
                        cols[0].write(f"**{row['nome']}**")
                        cols[1].write(f"Login: {row['usuario']}")
                        cols[2].write(f"Unidade: {row['unidade']}")
                        if cols[3].button("Excluir", key=f"del_{row['id']}"):
                            conn = conectar(); cursor = conn.cursor()
                            cursor.execute("DELETE FROM usuarios WHERE id = ?", (row['id'],))
                            conn.commit(); conn.close()
                            st.rerun()

    else:
        # TELA DO COLABORADOR (USER)
        if not st.session_state.respondido:
            st.title("📝 Qualidade de Vida e Engajamento")
            with st.form("pesquisa"):
                unidade = st.selectbox("Sua Unidade", ["FIEAC", "SESI", "SENAI", "IEL"])
                n = st.select_slider("O quanto você recomendaria a FIEAC? (0-10)", options=list(range(11)), value=5)
                f = st.text_area("O que podemos fazer para melhorar seu bem-estar?")
                if st.form_submit_button("Enviar Resposta"):
                    conn = conectar(); cursor = conn.cursor()
                    cursor.execute("INSERT INTO respostas (id_usuario, unidade, nota_enps, feedback_aberto) VALUES (?,?,?,?)", (st.session_state.user_id, unidade, n, f))
                    conn.commit(); conn.close()
                    st.session_state.respondido = True
                    st.rerun()
        else:
            st.balloons()
            st.success("🎉 Sua resposta foi registrada com sucesso!")
            st.info("💡 **Dica de Bem-Estar:** Pausas curtas para alongamento ajudam a manter a produtividade.")
            if st.button("Sair"): st.session_state.clear(); st.rerun()