#import
import plotly.express as px
import pandas as pd
import folium
from haversine import haversine
import streamlit as st
import datetime
from PIL import Image
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go

st.set_page_config( page_title='Visão Restaurante', layout='wide')

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
def distance( df1, fig ):
    
    if fig == False:
        cols=['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:,cols].apply( lambda x: 
                                                haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                          (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)  
        avg_distance = np.round(df1['distance'].mean())
        return avg_distance
    
    else:
        cols=['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = (df1.loc[:,cols].apply( lambda x: 
                                              haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig= go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
        return fig
#
    

def avg_std_time_delivery(df1, festival, op):
    """ 
    Esta funcao calcula o tempo medio e o desvio padrao do tempo de entrega
    Parametros:
    Input: df: Dataframe com os dados necessarios para o calculo
    op:Tipo de operacao que precisa ser calculado:
    'avg_time': Calcula o tempo medio
    'std_time': Calcula o desvio padrao do tempo
    Output: 
    df:Dataframe com 2 colunas e uma linha            
    """
    df_aux = (df1.loc[:, ['Festival','Time_taken(min)']]
                 .groupby(['Festival'])
                 .agg({'Time_taken(min)': ['mean', 'std']}))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)      
    return df_aux

#
def avg_std_time_graf(df1):

    df_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

#
def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig
#========================================================
#upload arquivos
df = pd.read_csv('dataset/train.csv')

df1 = clean_code(df)

# ===================
# Barra Lateral
# ===================
st.header('Market place - Visão Restaurantes')
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
        col1, col2,col3, col4, col5,col6 = st.columns(6) 
        
        with col1:
            aux = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores unicos',aux)
            
        with col2:
            avg_distance = distance(df1, fig = False)
            col2.metric('Distancia media', avg_distance)
                   
        with col3:  
            df_aux =   avg_std_time_delivery(df1, 'Yes', op='avg_time') 
            col3.metric('Tempo médio', df_aux )
       
        with col4:            
             df_aux =   avg_std_time_delivery(df1, 'Yes', op='std_time') 
             col4.metric(' STD de entrega c/ Festival', df_aux) 
        
        with col5:            
             df_aux =   avg_std_time_delivery(df1, 'No', op='avg_time') 
             col5.metric('Média entrega s/ Festival', df_aux)  
    
        with col6:            
             df_aux =   avg_std_time_delivery(df1, 'No', op='std_time') 
             col6.metric('STD de entrega s/ Festival', df_aux)  
            
    with st.container(): 
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:  
            st.title('Tempo medio de entrega por cidade ')
            fig = avg_std_time_graf(df1)
            st.plotly_chart(fig, use_container_width=True)
         
        with col2:            
            st.title('Distribuicao da distancia')
            df_aux = (df1.loc[:, ['City','Time_taken(min)', 'Road_traffic_density']]
                         .groupby(['City', 'Road_traffic_density'])
                         .agg({'Time_taken(min)': ['mean', 'std']}))
    
            df_aux.columns = ['avg_time', 'std_time']
            
            df_aux = df_aux.reset_index()
            st.dataframe( df_aux )
            
    with st.container(): 
        st.markdown("""---""")
        st.title(' Distribuicao do tempo')       
        col1, col2 = st.columns(2)
        
        with col1:            
            fig = distance(df1, fig=True)            
            st.plotly_chart(fig, use_container_width=True)
                
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
    
    
                    
        
    


