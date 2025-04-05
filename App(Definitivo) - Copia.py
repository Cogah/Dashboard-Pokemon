import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Theme settings
url_theme_claro = dbc.themes.MINTY
url_theme_escuro = dbc.themes.DARKLY
template_claro = "minty"
template_escuro = "darkly"

df = pd.read_csv("C:\\Users\\gabri\\OneDrive\\Documentos\\Códigos\\Python\\DashBoard\\PokedexDefinitivo.csv")

tipos_options = [{'label': x, 'value': x} for x in sorted(df['Type'].unique())]
stats_columns = [col for col in df.columns if col not in ['Name', 'Type', 'Height', 'Weight']]
stats_options = [{'label': stat, 'value': stat} for stat in stats_columns]

# LAYOUT
app.layout = dbc.Container([
    # TÍTULO E SELETOR DE TEMAS
    dbc.Row([
        dbc.Col(html.H1("Dashboard de Pokémon :3", className="text-center mb-4"), width=10),
        dbc.Col(ThemeSwitchAIO(aio_id='theme', themes=[url_theme_claro, url_theme_escuro]), 
                width=2, className="d-flex align-items-center")
    ], className="mb-4"),
    
    # FILTROS PARA OS TIPOS MÚLTIPLOS
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Analise por tipos múltiplos", id="filtro_header"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='tipo_escolha',
                        value=[tipo['value'] for tipo in tipos_options[:3]],
                        multi=True,
                        options=tipos_options,
                        placeholder="Selecione tipos de Pokémon"
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id='stat_choice',
                        value='HP',
                        options=stats_options,
                        placeholder="Selecione uma estatística"
                    )
                ])
            ], id="filtro_card")
        ], width=12, className="mb-4")
    ]),
    
    # GRÁFICOS PARA OS TIPOS MÚLTIPLOS
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar_tipo'), width=6, className="mb-4"),
        dbc.Col(dcc.Graph(id='scatter_tipo'), width=6, className="mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar_isBasic'), width=6, className="mb-4")
    ]),
    
    # FILTROS PARA OS TIPOS INDIVIDUAIS
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Análise por tipo individual", id="analise_header"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='tipo_selecionado',
                        value=df['Type'].unique()[0],
                        options=tipos_options,
                        placeholder="Selecione um tipo de Pokémon"
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id='stat_selecionado',
                        value='HP',
                        options=stats_options,
                        placeholder="Selecione uma estatística"
                    )
                ])
            ], id="analise_card")
        ], width=12, className="mb-4")
    ]),
    
    # GRÁFICOS PARA OS TIPOS INDIVIDUAIS
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico_ataque_defesa"), width=6, className="mb-4"),
        dbc.Col(dcc.Graph(id="grafico_distribuicao"), width=6, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico_spatk_spdef"), width=6, className="mb-4"),#GRÁFICO AINDA NÃO IMPLEMENTADO
        dbc.Col(dcc.Graph(id="grafico_top10BST"), width=6, className="mb-4"),#GRÁFICO AINDA NÃO IMPLEMENTADO
    ]),
    
    # TABELA DOS POKÉMON
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Estatísticas dos Pokémon"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='status',
                        columns=[{'name': col, 'id': col} for col in ['Name', 'Type'] + stats_columns],
                        data=df.to_dict('records'),
                        page_size=10,
                        filter_action="native",
                        sort_action="native",
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'minWidth': '100px',
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ])
            ])
        ], width=12)
    ])
], fluid=True)

# FUNÇÕES
@app.callback(
    Output('bar_tipo', 'figure'),
    Output('bar_isBasic', 'figure'),
    Input('tipo_escolha', 'value'),
    Input('stat_choice', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_bar_chart(tipo_escolhido, stat_choice, theme):
    template = template_claro if theme else template_escuro
    df_filtrado = df[df['Type'].isin(tipo_escolhido)]
    
    fig = px.bar(
        df_filtrado.groupby('Type')[stat_choice].mean().reset_index(),
        x='Type', 
        y=stat_choice,
        title=f'Média de {stat_choice} por Tipo',
        template=template,
        color='Type',
        text_auto='.2f'
    )
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Tipo de Pokémon",
        yaxis_title=stat_choice
    )
    
    contagem_por_tipo = df_filtrado['Type'].value_counts().reset_index()
    contagem_por_tipo.columns = ['Type', 'Count']  # Renomear colunas

    fig2 = px.bar(
        contagem_por_tipo,
        x='Type',
        y='Count',
        title='Número de Pokémon Básicos por Tipo',
        template=template,
        color='Type',
        text_auto=True
    )
    
    fig2.update_layout(
        title_x=0.5,
        xaxis_title="Tipo de Pokémon",
        yaxis_title="Quantidade de Básicos",
    )
    
    return fig, fig2

@app.callback(
    Output('scatter_tipo', 'figure'),
    Input('tipo_escolha', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_scatter_plot(tipo_escolha, theme):
    template = template_claro if theme else template_escuro
    df_filtrado = df[df['Type'].isin(tipo_escolha)]
    
    fig = px.scatter(
        df_filtrado,
        x='Height',
        y='Weight',
        color='Type',
        hover_data=['Name', 'Type', 'HP', 'Attack', 'Defense'],
        title='Altura vs Peso dos Pokémon',
        template=template,
        labels={'Height': 'Altura (m)', 'Weight': 'Peso (kg)'}
    )
    fig.update_layout(
        title_x=0.5,
        hovermode='closest'
    )
    return fig

@app.callback(
    [Output("grafico_ataque_defesa", "figure"),
     Output("grafico_distribuicao", "figure"),
     Output("grafico_spatk_spdef", "figure"),
     Output("grafico_top10BST", "figure")],
    [Input("tipo_selecionado", "value"),
     Input("stat_selecionado", "value"),
     Input(ThemeSwitchAIO.ids.switch('theme'), 'value')]
)
def update_graphs(tipo_selecionado, stat_selecionado, theme):
    template = template_claro if theme else template_escuro
    df_filtrado = df[df["Type"] == tipo_selecionado]

    fig1 = px.scatter(
        df_filtrado, 
        x="Attack", 
        y="Defense", 
        text="Name",
        title=f"Ataque vs Defesa - Tipo {tipo_selecionado}",
        labels={"Attack": "Ataque", "Defense": "Defesa"},
        template=template,
        hover_data=['id', 'Name']
    )
    fig1.update_layout(title_x=0.5)
    
    fig2 = px.histogram(
        df_filtrado, 
        x=stat_selecionado, 
        title=f"Distribuição de {stat_selecionado} - Tipo {tipo_selecionado}",
        template=template,
        labels={"Speed": "Velocidade"}
    )
    fig2.update_layout(title_x=0.5)
    
    fig3 = px.scatter(
        df_filtrado,
        x="Sp.Attack",
        y="Sp.Defense",
        text="Name",
        title=f"Sp. Atk vs Sp. Def do tipo {tipo_selecionado}",
        labels={"Sp.Attack": "Ataque Especial", "Sp.Defense": "Defesa Especial"},
        template=template,
        hover_data=['id', 'Name']
    )
    fig3.update_layout(title_x=0.5)
    
    fig4 = px.bar(
        df_filtrado.sort_values(by='BST', ascending=True).head(10),
        x='BST', 
        y='Name',
        title=f'Maiores BST do tipo {tipo_selecionado}',
        template=template,
        color='Type',
        text_auto='.2f'
    )
    fig4.update_layout(
        title_x=0.5,
        xaxis_title="Nome",
        yaxis_title="BST",
        xaxis_tickangle=-45,
        yaxis=dict(tickmode='linear')
    )
    
    return fig1, fig2,fig3, fig4



#AJUSTE DA TABELA
@app.callback(
    Output('status', 'style_data_conditional'),
    Output('status', 'style_header'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_table_theme(theme):
    if theme:  # TEMA CLARO
        style_data_conditional = [
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
            {'if': {'row_index': 'even'}, 'backgroundColor': 'white'}
        ]
        style_header = {
            'backgroundColor': 'rgb(230, 230, 230)',
            'color': 'black',
            'fontWeight': 'bold'
        }
    else:  # TEMA ESCURO
        style_data_conditional = [
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(50, 50, 50)'},
            {'if': {'row_index': 'even'}, 'backgroundColor': 'rgb(40, 40, 40)'},
            {'if': {'column_id': 'Name'}, 'color': 'rgb(255, 165, 0)'}
        ]
        style_header = {
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'fontWeight': 'bold'
        }

    return style_data_conditional, style_header

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
