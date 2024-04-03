#import
import plotly.express as px
import pandas as pd
import folium
from haversine import haversine
import streamlit as st
import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', layout='wide')


#-------------
# Funcoes
#-------------

def clean_code( df1 ):
    """ 
    Esta funcao tem a responsabilidade de limpar o dataframe 
    Tipos de limpeza:
    1.Remocao dos dados NAN
    2. Mudanca do tipo da coluna de dados
    3. Remocao dos espacos das variaveis de texto
    4. Formatacao da coluna de datas
    5. Limpeza da coluna de tempo ( renovacao do texto da variavel numerica )

    Input: Dataframe
    Output: Dataframe
    """
    
    #convertendo coluna Age para int
    linhas_selecionadas = (df1.loc[:, 'Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, : ]
    
    linhas_selecionadas = (df1.loc[:, 'City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, : ]
    
    linhas_selecionadas = (df1.loc[:, 'Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, : ]
    
    linhas_selecionadas = (df1.loc[:, 'Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, : ]
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype ( int )
    
    #convertendo coluna rating para float
    
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    #convertendo coluna order-date para data    
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')
    
    #convertendo coluna multiple=deliverys para int    
    linhas_selecionadas = (df1.loc[:, 'multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, : ]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    #limpando a coluna tike taken    
    df1.loc[:, 'Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min)' )[1])
    df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].astype(int)
    
    # Removendo espacos strings    
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    return df1
#
def top_delivers(df1, top_asc):
    
    aux = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
             .groupby(['City', 'Delivery_person_ID'])
             .mean()
             .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
             .reset_index())
    
    df_aux01 = aux.loc[aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = aux.loc[aux['City'] == 'Urban', :].head(10)
    df_aux03 = aux.loc[aux['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index( drop=True)
    return df3

#upload arquivos
df = pd.read_csv('dataset/train.csv')

df1 = clean_code(df)

# ===================
# Barra Lateral
# ===================
st.header('Market place - Visão Entregadores')
#image_path='/home/blenda/repos/ftc_cds/ftc_ciclo5/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=250)

st.sidebar.markdown(' ### Curry Company')
st.sidebar.markdown(' ### Fastest Delivery in Town ')
st.sidebar.markdown( """---""" )

st.sidebar.markdown(' ## Selecione uma data limite ')

data_slider = st.sidebar.slider('Até qual valor?', value = datetime.datetime(2022, 4, 13), min_value=datetime.datetime(2022, 2, 11), max_value = datetime.datetime(2022, 6, 4), format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condicoes do transito ?', 
    ['Low', 'Medium', 'High', 'Jam'], default= ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Porwed by Comunidade DS')

# Filtro de data
linhas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas, :]

# Filtro de transito
linhas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas, :]

# =======
# Layout
# =======

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #A maior idade dos entregadores
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
            
        with col2:
            #A menor idade dos entregadores
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            #A melhor condicao de veiculos
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor_condicao)
            
        with col4:
            #A pior condicao de veiculos
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior condicao', pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacoes medias por entregador')
            avaliacoes = df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().reset_index()
            st.dataframe(avaliacoes)

        with col2:
            st.markdown('##### Avaliacoes medias por transito')
            aux = (df1.loc[:,[ 'Delivery_person_Ratings', 'Road_traffic_density']]
                      .groupby(['Road_traffic_density'])
                      .agg({'Delivery_person_Ratings':['mean', 'std']}))
            
            aux.columns = ['delivery_mean', 'delivery_std']
            aux = aux.reset_index()
            st.dataframe(aux)
            
            st.markdown('#####  Avaliacoes medias por clima')
            aux = (df1.loc[:,[ 'Delivery_person_Ratings', 'Weatherconditions']]
                      .groupby(['Weatherconditions'])
                      .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            aux.columns = ['delivery_mean', 'delivery_std']
            aux = aux.reset_index()
            st.dataframe(aux)

            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1,col2= st.columns(2)
        
        with col1:
            
            st.markdown('##### Top entregadores mais rapidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
            
























