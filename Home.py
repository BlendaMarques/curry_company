import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="",
    layout='wide'
)

#image_path = '/home/blenda/repos/ftc_cds/ftc_ciclo5/'
image= Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown(' ### Curry Company')
st.sidebar.markdown(' ### Fastest Delivery in Town ')
st.sidebar.markdown( """---""" )

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard:
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de cresciemnto.
        - Visão Geografica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de Data Science no Discord
        - @blendamarques
""")