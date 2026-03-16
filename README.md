![Banner FIEAC](4casas.png)
# 📊 Sistema de Engajamento e eNPS - FIEAC

Este projeto é uma plataforma completa para coleta e análise de **eNPS (Employee Net Promoter Score)**, desenvolvida para modernizar a gestão de clima organizacional no **Sistema FIEAC (SESI, SENAI, IEL)**.

O sistema permite que colaboradores avaliem sua experiência anonimamente, enquanto o RH/UNIPES tem acesso a um dashboard estratégico com análise de dados em tempo real.

---

## 🚀 Funcionalidades Principais

### Para o Administrador (RH/UNIPES):
* **Dashboard "Estilo Qservus":** Gráfico Donut interativo com o Score eNPS centralizado.
* **Análise Comparativa:** Visualização do desempenho por unidade (SESI, SENAI, IEL, FIEAC).
* **Gestão de Usuários:** Cadastro manual, exclusão individual e **importação em massa via Excel**.
* **Relatórios Estratégicos:** Geração de PDF com explicações metodológicas e sugestões de melhoria.
* **Segurança:** Botão de "Reset Total" para limpeza segura da base de dados.

### Para o Colaborador:
* **Interface Simples:** Formulário de votação intuitivo baseado na escala de 0 a 10.
* **UX Interativa:** Feedback visual após o envio (balões e mensagens de impacto).
* **Dicas de Saúde:** Sugestões dinâmicas de bem-estar e ergonomia no trabalho.

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as melhores práticas de **Sistemas de Informação**:

* **Linguagem:** [Python](https://www.python.org/)
* **Interface Web:** [Streamlit](https://streamlit.io/)
* **Banco de Dados:** [SQLite3](https://www.sqlite.org/index.html) (com modo WAL para alta performance)
* **Gráficos:** [Plotly](https://plotly.com/python/) e [Seaborn](https://seaborn.pydata.org/)
* **Geração de Documentos:** [FPDF](https://pyfpdf.readthedocs.io/en/latest/) e [XlsxWriter](https://xlsxwriter.readthedocs.io/)

---

## 📦 Como Instalar e Rodar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/sistema-enps-fieac.git](https://github.com/SEU_USUARIO/sistema-enps-fieac.git)
