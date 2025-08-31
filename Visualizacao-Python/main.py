import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('ecommerce_estatistica.csv')
lista_genero = df['Gênero'].unique()
options = [{'label': genero, 'value': genero} for genero in lista_genero]

# Padroniza o campo Temporada
def padronizar_temporada(valor):
    if pd.isna(valor):
        return "não definido"

    # Converte para minúsculas e remove espaços extras
    valor = valor.lower().strip()

    # Substitui barras por hífens para uniformizar
    valor = valor.replace("/", "-")

    # Remove espaços duplicados
    valor = " ".join(valor.split())

    # Padroniza os casos específicos
    if "primavera-verão" in valor and "outono-inverno" in valor:
        return "primavera-verão/outono-inverno"
    elif "primavera-verão" in valor:
        return "primavera-verão"
    elif "outono-inverno" in valor:
        return "outono-inverno"
    else:
        return valor

df["Temporada"] = df["Temporada"].apply(padronizar_temporada)
sales_by_season = df.groupby('Temporada')['Preço'].sum().reset_index()


def cria_grafico(selecao_genero, df):
  filtro_genero = df[df['Gênero'].isin(selecao_genero)]
  df_agrupado = filtro_genero.groupby('Gênero', as_index=False, observed=True)['Preço'].sum()

  fig1 = px.bar(df_agrupado, x='Gênero', y='Preço', color='Gênero', color_discrete_sequence=px.colors.qualitative.Plotly)

  fig2 = px.histogram(df, x='Nota', nbins=30, title='Distribuição de Notas')

  fig3 = px.pie(sales_by_season, names='Temporada', title='Vendas por Temporada', hole=0.2, color_discrete_sequence=px.colors.sequential.RdBu)

  fig4 = px.scatter(df, x='Qtd_Vendidos_Cod', y='Preço', size='Qtd_Vendidos_Cod', color='Qtd_Vendidos_Cod', hover_name='Nota', title='Dispersão de Quantidade por Preço', size_max=60)
  fig4.update_layout(xaxis_title='Quantidade de Vendas')

  return fig1, fig2, fig3, fig4

# Criar App
def cria_app():
    app = Dash(__name__)
    app.layout = html.Div([
        html.H1('Dashboard Interativo'),
        html.Br(),
        html.H2('Gráfico de Vendas por Gênero'),
        dcc.Checklist(
            id='id_selecao_genero',
            options=options,
            value=[lista_genero[0]],
        ),
        dcc.Graph(id='id_grafico_barra'),
        dcc.Graph(id='id_grafico_histograma'),
        dcc.Graph(id='id_grafico_pizza'),
        dcc.Graph(id='id_grafico_dispersao')
    ])
    return app

# Executar App
if __name__ == '__main__':
    app = cria_app()

    @app.callback(
        [
            Output('id_grafico_barra', 'figure'),
            Output('id_grafico_histograma', 'figure'),
            Output('id_grafico_pizza', 'figure'),
            Output('id_grafico_dispersao', 'figure')
        ],
        [
            Input('id_selecao_genero', 'value')
        ]
    )
    def atualiza_grafico(selecao_genero):
        fig1, fig2, fig3, fig4 = cria_grafico(selecao_genero, df)
        return [fig1, fig2, fig3, fig4]
    app.run(debug=True, port=8050)