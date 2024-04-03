#import
import plotly.express as px
import pandas as pd
import folium
from haversine import haversine
import streamlit as st
import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', layout='wide')

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
def order_metric( df1 ):
    df_aux=(df1.loc[:,['ID','Order_Date']]
               .groupby(['Order_Date'])
               .count() 
               .reset_index())
    
    #grafico de barras
    fig =px.bar( df_aux, x= 'Order_Date', y= 'ID')
    
    return fig
#
def traffic_order_share ( df1 ):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    #grafico de pizza    
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig =px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    
    return fig

#
def traffic_order_city ( df1 ):
    df_aux = (df1.loc[:, ['ID', 'City','Road_traffic_density']]
                 .groupby(['City','Road_traffic_density'])
                 .count()
                 .reset_index())
    
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size = 'ID', color='City' )
    
    return fig

#
def order_by_week( df1 ):
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U ')            
    df_aux = (df1.loc[:,['ID','week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
        
    #grafico de linhas
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    
    return fig 
#
def order_share_by_week(df1):

    df_aux01 = (df1.loc[:, ['week_of_year', 'ID']]
                   .groupby('week_of_year')
                   .count()
                   .reset_index())
    
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .nunique()
                   .reset_index())
    
    df_aux = pd.merge( df_aux01, df_aux02, how='inner')
    
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig = px.line ( df_aux, x='week_of_year', y= 'order_by_deliver') 
    
    return fig 

#
def contry_maps( df1 ):
        
    data_plot = (df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                    .groupby( ['City', 'Road_traffic_density'] )
                    .median()
                    .reset_index())
    
    data_plot = data_plot.loc[data_plot['City'] != 'NaN', :]
    data_plot = data_plot.loc[data_plot['Road_traffic_density'] != 'NaN', :]
    
    # Desenhar o mapa    
    map_ = folium.Map( zoom_start=11 )
    
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    folium_static(map_, width=1024, height=600)


#--------------------------------------------------------Estrutura logica do codigo ----------------------------------------------------------------------
#upload arquivos
df = pd.read_csv('dataset/train.csv')

#limpando os dados

df1 = clean_code( df )

# ==================
# Barra Lateral
# ==================


st.header('Market place - Visão Cliente')
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geografica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric( df1 )
        st.markdown('# Orders by day')
        st.plotly_chart(fig, use_container_width=True)
     
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share ( df1 )
            st.markdown( '# Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = traffic_order_city( df1 )
            st.markdown( '# Traffic Order City')
            st.plotly_chart(fig, use_container_width=True )
            
with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.markdown('# Order By Week')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        fig = order_share_by_week( df1 )
        st.markdown('# Order Share By Week')
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:    
    st.markdown('# Country Maps') 
    contry_maps( df1)
    



















