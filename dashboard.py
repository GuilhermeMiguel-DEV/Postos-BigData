import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from postos_app.utils import normalizar_texto
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa o app Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard de Postos - Salvador"

# Layout do dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Dashboard de Postos - Salvador", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Dropdown(
                id='bairro-dropdown',
                placeholder="Selecione um bairro...",
                style={'width': '100%', 'marginBottom': '20px'}
            ),
        ], style={'width': '60%', 'margin': '0 auto', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
        
        dcc.Loading(
            id="loading",
            type="circle",
            children=[
                html.Div(id='info-bairro', 
                        style={'margin': '20px 0', 'padding': '15px', 
                              'backgroundColor': '#e9ecef', 'borderRadius': '5px'}),
                
                html.Div([
                    dcc.Graph(id='grafico-preco-medio', 
                             style={'width': '48%', 'display': 'inline-block'}),
                    dcc.Graph(id='grafico-boxplot', 
                             style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                ], style={'marginBottom': '30px'}),
                
                html.H3("Detalhes dos Postos", 
                       style={'marginTop': '30px', 'borderBottom': '2px solid #2c3e50', 'paddingBottom': '5px'}),
                html.Div(id='tabela-postos', 
                        style={'marginTop': '15px'})
            ]
        ),
    ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})
])

# Callback para carregar os bairros no dropdown
@app.callback(
    Output('bairro-dropdown', 'options'),
    Input('bairro-dropdown', 'search_value')
)
def carregar_bairros(search_value):
    try:
        url = 'http://127.0.0.1:8000/postos/?municipio=Salvador'
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        # Normalização dos nomes de bairros
        df['bairro'] = df['bairro'].str.strip().str.title()
        df = df.dropna(subset=['bairro'])
        
        # Remove duplicados mantendo a grafia original
        bairros_unicos = sorted(df['bairro'].unique(), key=lambda x: normalizar_texto(x))
        
        options = [{'label': 'Todos os bairros', 'value': ''}]
        options += [{'label': b, 'value': b} for b in bairros_unicos]
        
        return options
    
    except Exception as e:
        print(f"Erro ao carregar bairros: {str(e)}")
        return [{'label': 'Erro ao carregar dados', 'value': ''}]

# Callback principal para atualizar os gráficos e tabela
@app.callback(
    [Output('grafico-preco-medio', 'figure'),
     Output('grafico-boxplot', 'figure'),
     Output('tabela-postos', 'children'),
     Output('info-bairro', 'children')],
    [Input('bairro-dropdown', 'value')]
)
def atualizar_dashboard(bairro):
    if bairro is None:
        raise PreventUpdate
    
    try:
        # URL corrigida com parâmetros codificados
        params = {
            'municipio': 'Salvador',
            'bairro': bairro if bairro else ''
        }
        url = 'http://127.0.0.1:8000/postos/'
        response = requests.get(url, params=params, timeout=10)
        logger.info(f"Requisição para: {url}?{params}")
        logger.info(f"Resposta: {response.status_code}, Dados: {data[:2] if data else 'vazio'}")

        # Verificação mais robusta da resposta
        if response.status_code != 200:
            raise Exception(f"Erro na API: Status {response.status_code}")
            
        data = response.json()
        if not data:
            return (
                go.Figure(layout={'title': 'Nenhum dado disponível'}),
                go.Figure(layout={'title': 'Nenhum dado disponível'}),
                html.Div("Nenhum posto encontrado para os filtros selecionados", 
                        style={'color': 'gray', 'textAlign': 'center'}),
                html.Div(f"Filtro: {bairro if bairro else 'Todos os bairros'}")
            )
        
        df = pd.DataFrame(data)
        
        # Verificação das colunas necessárias
        required_columns = ['bairro', 'produto', 'preco_revenda', 'bandeira', 'endereco']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise Exception(f"Colunas faltando: {missing}")

        # Processamento seguro dos dados
        df = df.dropna(subset=['preco_revenda', 'produto'])
        df['preco_revenda'] = pd.to_numeric(df['preco_revenda'], errors='coerce')
        df = df[df['preco_revenda'].notna()]
        
        # Informações do bairro selecionado
        num_postos = len(df['razao'].unique())
        produtos = ', '.join(df['produto'].unique())
        
        info = html.Div([
            html.H4(f"Bairro selecionado: {bairro if bairro else 'Todos'}"),
            html.P(f"Total de postos: {num_postos}"),
            html.P(f"Produtos analisados: {produtos}")
        ])
        
        # Gráfico 1: Preço médio por produto
        preco_medio = df.groupby('produto')['preco_revenda'].mean().reset_index()
        fig1 = px.bar(
            preco_medio, 
            x='produto', 
            y='preco_revenda',
            title='Preço Médio por Produto',
            color='produto',
            labels={'preco_revenda': 'Preço (R$)', 'produto': 'Produto'},
            height=400
        )
        fig1.update_layout(showlegend=False)
        
        # Gráfico 2: Boxplot de preços
        fig2 = px.box(
            df, 
            x='produto', 
            y='preco_revenda',
            title='Distribuição de Preços por Produto',
            color='produto',
            labels={'preco_revenda': 'Preço (R$)', 'produto': 'Produto'},
            height=400
        )
        fig2.update_layout(showlegend=False)
        
        # Tabela de postos
        cols_to_show = ['bairro', 'produto', 'preco_revenda', 'bandeira', 'endereco']
        tabela = dash_table.DataTable(
            id='tabela-postos-det',
            columns=[{"name": col.capitalize(), "id": col} for col in cols_to_show],
            data=df[cols_to_show].to_dict('records'),
            page_size=10,
            style_table={
                'overflowX': 'auto',
                'marginTop': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'border': '1px solid #dee2e6'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'column_id': 'preco_revenda'},
                    'type': 'numeric',
                    'format': {'specifier': '$.2f'}
                }
            ],
            filter_action='native',
            sort_action='native',
            sort_mode='multi'
        )
        
        return fig1, fig2, tabela, info
        
    except requests.exceptions.RequestException as e:
        error = html.Div([
            html.H5("Erro de conexão", style={'color': 'red'}),
            html.P(str(e)),
            html.P("Verifique se o servidor Django está rodando.")
        ])
        return go.Figure(), go.Figure(), error, html.Div()
        
    except Exception as e:
        error = html.Div([
            html.H5("Erro ao processar dados", style={'color': 'red'}),
            html.P(str(e)),
            html.P("Verifique os dados retornados pela API.")
        ])
        return go.Figure(), go.Figure(), error, html.Div()

if __name__ == '__main__':
    app.run(debug=True, port=8050)