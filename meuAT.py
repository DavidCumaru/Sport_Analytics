import streamlit as st
from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def sb_competicoes():
    return sb.competitions()

@st.cache_data
def sb_temporadas(competicao_id):
    competicoes = sb.competitions()
    return competicoes[competicoes['competition_id'] == competicao_id][['season_id', 'season_name']]

@st.cache_data
def sb_partidas(competicao_id, temporada_id):
    return sb.matches(competition_id=competicao_id, season_id=temporada_id)

@st.cache_data
def sb_eventos_partida(partida_id):
    eventos = sb.events(match_id=partida_id)
    if 'location' in eventos.columns:
        eventos_validos = eventos[eventos['location'].apply(lambda x: isinstance(x, list) and len(x) == 2)]
        if not eventos_validos.empty:
            eventos_validos[['localizacao_x', 'localizacao_y']] = pd.DataFrame(eventos_validos['location'].tolist(), index=eventos_validos.index)
            eventos = eventos_validos
    return eventos

def sb_mapa_passes(eventos_df, time, jogador):
    passes = eventos_df[(eventos_df['type'] == 'Pass') & (eventos_df['team'] == time) & (eventos_df['player'] == jogador)]
    campo = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = campo.draw(figsize=(10, 7))
    if not passes.empty:
        campo.scatter(passes['localizacao_x'], passes['localizacao_y'], ax=ax, color='blue', label='Passes')
    else:
        st.write("Nenhum passe encontrado para o jogador selecionado.")
    return fig

def sb_mapa_chutes(eventos_df, time, jogador):
    chutes = eventos_df[(eventos_df['type'] == 'Shot') & (eventos_df['team'] == time) & (eventos_df['player'] == jogador)]
    campo = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = campo.draw(figsize=(10, 7))
    if not chutes.empty:
        campo.scatter(chutes['localizacao_x'], chutes['localizacao_y'], ax=ax, color='red', label='Chutes')
    else:
        st.write('Nenhum chute encontrado para o jogador selecionado.')
    return fig

def sb_mapa_passes_chutes_time(eventos_df, time):
    passes_time = eventos_df[(eventos_df['type'] == 'Pass') & (eventos_df['team'] == time)]
    chutes_time = eventos_df[(eventos_df['type'] == 'Shot') & (eventos_df['team'] == time)]
    campo = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = campo.draw(figsize=(10, 7))
    if not passes_time.empty:
        campo.scatter(passes_time['localizacao_x'], passes_time['localizacao_y'], ax=ax, color='blue', label='Passes', alpha=0.6)
    if not chutes_time.empty:
        campo.scatter(chutes_time['localizacao_x'], chutes_time['localizacao_y'], ax=ax, color='red', label='Chutes', alpha=0.6)
    plt.legend(loc='upper left')
    return fig
st.title('Sport Analytics')
st.sidebar.header('Selecione...')

competicoes = sb_competicoes()
nome_competicao = st.sidebar.selectbox('Competição', competicoes['competition_name'].unique())
competicao_id = competicoes[competicoes['competition_name'] == nome_competicao]['competition_id'].values[0]

temporadas = sb_temporadas(competicao_id)
nome_temporada = st.sidebar.selectbox('Temporada', temporadas['season_name'].unique())
temporada_id = temporadas[temporadas['season_name'] == nome_temporada]['season_id'].values[0]

partidas = sb_partidas(competicao_id, temporada_id)
nome_partida = st.sidebar.selectbox("Partida", partidas['home_team'] + " vs " + partidas['away_team'])
partida_id = partidas[partidas['home_team'] + " vs " + partidas['away_team'] == nome_partida]['match_id'].values[0]

with st.spinner('Carregando eventos da partida...'):
    eventos = sb_eventos_partida(partida_id)

st.write(f'**Competição:** {nome_competicao}')
st.write(f'**Temporada:** {nome_temporada}')
st.write(f'**Partida:** {nome_partida}')

times = eventos['team'].unique()
time = st.selectbox("Selecione o Time", times)
jogadores = eventos[eventos['team'] == time]['player'].unique()
jogador = st.selectbox("Selecione o Jogador", jogadores)

gols_time = len(eventos[(eventos['team'] == time) & (eventos['type'] == 'Shot') & (eventos['shot_outcome'] == 'Goal')])
passes_time = len(eventos[(eventos['team'] == time) & (eventos['type'] == 'Pass')])
chutes_time = len(eventos[(eventos['team'] == time) & (eventos['type'] == 'Shot')])
desarmes_time = len(eventos[(eventos['team'] == time) & (eventos['type'] == 'Tackle')])
passes_bem_sucedidos_time = len(eventos[(eventos['team'] == time) & (eventos['type'] == 'Pass') & (eventos['pass_outcome'].isna())])

gols_jogador = len(eventos[(eventos['team'] == time) & (eventos['player'] == jogador) & (eventos['type'] == 'Shot') & (eventos['shot_outcome'] == 'Goal')])
passes_jogador = len(eventos[(eventos['team'] == time) & (eventos['player'] == jogador) & (eventos['type'] == 'Pass')])
chutes_jogador = len(eventos[(eventos['team'] == time) & (eventos['player'] == jogador) & (eventos['type'] == 'Shot')])
desarmes_jogador = len(eventos[(eventos['team'] == time) & (eventos['player'] == jogador) & (eventos['type'] == 'Tackle')])
passes_bem_sucedidos_jogador = len(eventos[(eventos['team'] == time) & (eventos['player'] == jogador) & (eventos['type'] == 'Pass') & (eventos['pass_outcome'].isna())])

st.subheader(f'Estatísticas do Time: {time}')
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric('Gols', gols_time)
col2.metric('Passes', passes_time)
col3.metric('Chutes', chutes_time)
col4.metric('Passes Bem-sucedidos)', passes_bem_sucedidos_time)
col5.metric('Desarmes', desarmes_time)

st.subheader(f'Estatísticas do Jogador: {jogador}')
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric('Gols', gols_jogador)
col2.metric('Passes', passes_jogador)
col3.metric('Chutes', chutes_jogador)
col4.metric('Passes Bem-sucedidos', passes_bem_sucedidos_jogador)
col5.metric('Desarmes', desarmes_jogador)

st.subheader(f'Mapa de Passes: {jogador}')
mapa_de_passes = sb_mapa_passes(eventos, time, jogador)
st.pyplot(mapa_de_passes)

st.subheader(f'Mapa de Chutes: {jogador}')
mapa_de_chutes = sb_mapa_chutes(eventos, time, jogador)
st.pyplot(mapa_de_chutes)

st.subheader(f'Mapa de Passes e Chutes do Time: {time}')
mapa_passes_chutes_time = sb_mapa_passes_chutes_time(eventos, time)
st.pyplot(mapa_passes_chutes_time)

st.subheader('Comparação entre Jogadores')

with st.form('formulario_comparacao'):
    time_1 = st.selectbox('Selecione o Time 1', times, key='time_1')
    jogador_1 = st.selectbox("Selecione o Jogador do Time 1", eventos[eventos['team'] == time_1]['player'].unique(), key='jogador_1')
    time_2 = st.selectbox('Selecione o Time 2', times, key='time_2')
    jogador_2 = st.selectbox('Selecione o Jogador do Time 2', eventos[eventos['team'] == time_2]['player'].unique(), key='jogador_2')
    opcao_comparacao = st.radio('Comparar', ('Gols', 'Passes', 'Chutes', 'Desarmes'))
    enviado = st.form_submit_button('Comparar Jogadores')
    
    if enviado:
        st.write(f'**Estatísticas de {jogador_1} do {time_1}:**')
        eventos_jogador_1 = eventos[(eventos['team'] == time_1) & (eventos['player'] == jogador_1)]
        if opcao_comparacao == 'Gols':
            estatistica_jogador_1 = len(eventos_jogador_1[(eventos_jogador_1['type'] == 'Shot') & (eventos_jogador_1['shot_outcome'] == 'Goal')])
        elif opcao_comparacao == 'Passes':
            estatistica_jogador_1 = len(eventos_jogador_1[eventos_jogador_1['type'] == 'Pass'])
        elif opcao_comparacao == 'Chutes':
            estatistica_jogador_1 = len(eventos_jogador_1[eventos_jogador_1['type'] == 'Shot'])
        else:
            estatistica_jogador_1 = len(eventos_jogador_1[eventos_jogador_1['type'] == 'Tackle'])
        st.write(f"{opcao_comparacao} de {jogador_1}: {estatistica_jogador_1}")
        st.write(f'**Estatísticas de {jogador_2} do {time_2}:**')
        eventos_jogador_2 = eventos[(eventos['team'] == time_2) & (eventos['player'] == jogador_2)]
        if opcao_comparacao == 'Gols':
            estatistica_jogador_2 = len(eventos_jogador_2[(eventos_jogador_2['type'] == 'Shot') & (eventos_jogador_2['shot_outcome'] == 'Goal')])
        elif opcao_comparacao == 'Passes':
            estatistica_jogador_2 = len(eventos_jogador_2[eventos_jogador_2['type'] == 'Pass'])
        elif opcao_comparacao == 'Chutes':
            estatistica_jogador_2 = len(eventos_jogador_2[eventos_jogador_2['type'] == 'Shot'])
        else:
            estatistica_jogador_2 = len(eventos_jogador_2[eventos_jogador_2['type'] == 'Tackle'])
        st.write(f"{opcao_comparacao} de {jogador_2}: {estatistica_jogador_2}")

st.subheader('Eventos')
tipos_de_eventos = eventos['type'].unique()
tipo_evento = st.selectbox('Tipo de Evento', tipos_de_eventos)
num_eventos = st.number_input('Quantidade de eventos a serem exibidos:', min_value=1, value=5, step=1)
intervalo_tempo = st.slider('Intervalo de Tempo (minutos):', 0, 90, (0, 90))

eventos_filtrados = eventos[(eventos['team'] == time) & (eventos['player'] == jogador) & 
                            (eventos['type'] == tipo_evento) & 
                            (eventos['minute'] >= intervalo_tempo[0]) & 
                            (eventos['minute'] <= intervalo_tempo[1])]

eventos_limitados = eventos_filtrados.head(num_eventos)
st.dataframe(eventos_limitados[['minute', 'team', 'player', 'location', 'type']])
st.sidebar.download_button(label='Baixar dados em CSV', data=eventos_filtrados.to_csv(), file_name='eventos.csv', mime='text/csv')