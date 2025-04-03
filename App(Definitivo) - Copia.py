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

# Load data
df = pd.read_csv("C:\\Users\\gabri\\OneDrive\\Documentos\\Códigos\\Python\\DashBoard\\PokedexDefinitivo.csv")

# Prepare dropdown options
tipos_options = [{'label': x, 'value': x} for x in sorted(df['Type'].unique())]
stats_columns = [col for col in df.columns if col not in ['Name', 'Type', 'Height', 'Weight']]
stats_options = [{'label': stat, 'value': stat} for stat in stats_columns]

# Layout
app.layout = dbc.Container([
    # Header row with title and theme switch
    dbc.Row([
        dbc.Col(html.H1("Dashboard de Pokémon :3", className="text-center mb-4"), width=10),
        dbc.Col(ThemeSwitchAIO(aio_id='theme', themes=[url_theme_claro, url_theme_escuro]), 
                width=2, className="d-flex align-items-center")
    ], className="mb-4"),
    
    # Controls row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filtros"),
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
            ])
        ], width=12, className="mb-4")
    ]),
    
    # First row of graphs
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar_tipo'), width=6, className="mb-4"),
        dbc.Col(dcc.Graph(id='scatter_tipo'), width=6, className="mb-4")
    ]),
    
    # Second row controls
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Análise por Tipo Individual"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='tipo_selecionado',
                        value=df['Type'].unique()[0],
                        options=tipos_options,
                        placeholder="Selecione um tipo de Pokémon"
                    )
                ])
            ])
        ], width=12, className="mb-4")
    ]),
    
    # Second row of graphs
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico_ataque_defesa"), width=6, className="mb-4"),
        dbc.Col(dcc.Graph(id="grafico_velocidade"), width=6, className="mb-4"),
    ]),
    
    # Stats table row
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

# Callbacks
@app.callback(
    Output('bar_tipo', 'figure'),
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
    return fig

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
     Output("grafico_velocidade", "figure")],
    [Input("tipo_selecionado", "value"),
     Input(ThemeSwitchAIO.ids.switch('theme'), 'value')]
)
def update_graphs(tipo_selecionado, theme):
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
        hover_data=['Name', 'HP', 'Speed']
    )
    fig1.update_layout(title_x=0.5)
    
    fig2 = px.histogram(
        df_filtrado, 
        x="Speed", 
        title=f"Distribuição de Velocidade - Tipo {tipo_selecionado}",
        template=template,
        labels={"Speed": "Velocidade"}
    )
    fig2.update_layout(title_x=0.5)
    
    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)