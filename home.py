import calendar
import numpy as np
import polars as pl
import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from funtions import process_data, types_barchart, max_spent_data, purchases_table

st.set_page_config(layout="wide")
st.header("Libreta de gastos")
st.markdown("---")
st.sidebar.header("Opciones")

spent_options = sorted(process_data()[0]['type'].unique().to_list())
payment_options = sorted(process_data()[0]['type_payment'].unique().to_list())

months_options = {
    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
    'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12,
}

options = st.sidebar.multiselect(
    "Selecciona un mes",
    options=months_options.keys(),
    key="month_selector"
)

months_list = []

for i in options:
    for j in months_options.keys():
        if i == j:
            months_list.append(months_options[j])
            #purchases_df = purchases_df.filter(pl.col('month') == months_options[j])

type_spent = st.sidebar.multiselect(
    "Selecciona un tipo de gasto", 
    options=spent_options,
    key="type_selector" 
)

type_payment = st.sidebar.multiselect(
    "Selecciona un tipo de pago", 
    options=payment_options,
    key="payment_selector" 
)

purchases_df = process_data(months_list, type_spent, type_payment)[0]
types_df = process_data()[1]

col1, col2 = st.columns(2)
barchart_df = types_barchart(purchases_df)[0]
total_spent = types_barchart(purchases_df)[1]
max_spent_df = max_spent_data(purchases_df, types_df)[0]
max_permitted_spend = max_spent_data(purchases_df, types_df)[1]

with col1:
    st.metric(label="Gasto total hasta la fecha", value=total_spent, border=True)

    fig_bar = px.bar(barchart_df, x="Tipo", y="Total", title="📊 Gastos por tipo")
    fig_bar.update_layout(
        height=400,
        xaxis={'categoryorder': 'array', 'categoryarray': spent_options}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.metric(label="Consumo maximo permitido", value=max_permitted_spend, border=True)

    def create_bullet_chart(df):
        fig = go.Figure()
        df = df.sort('Gasto maximo permitido', descending=False)
        
        for row in df.iter_rows(named=True):
            tipo = row['Tipo']
            total = row['Total']
            max_permitido = row['Gasto maximo permitido']
            porcentaje = (total / max_permitido) * 100
            
            fig.add_trace(go.Bar(
                y=[tipo],
                x=[max_permitido],
                name='Máximo permitido',
                orientation='h',
                marker=dict(color='lightgray'),
                hoverinfo='none',
                width=0.3
            ))
            
            fig.add_trace(go.Bar(
                y=[tipo],
                x=[total],
                name='Total gastado',
                orientation='h',
                marker=dict(color='royalblue'),
                text=[f"{porcentaje:.1f}%"],
                textposition='auto',
                hoverinfo='text',
                hovertext=f"Tipo: {tipo}<br>Total: {total:,}<br>Máximo: {max_permitido:,}<br>Consumido: {porcentaje:.1f}%",
                width=0.2
            ))
        
        fig.update_layout(
            barmode='overlay',
            title={
                'text': '📊Gasto maximo por cada tipo',
                'y':0.9,  
                'x':0.3, 
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title='Monto',
            yaxis_title='Tipo',
            showlegend=False,
            height=400,
            margin=dict(
                l=100, 
                r=50,
                t=80,
                b=50
            )
        )
        return fig

    bullet_chart = create_bullet_chart(max_spent_df)
    st.plotly_chart(bullet_chart, use_container_width=True)

purchases_table_df = purchases_table(purchases_df)
st.markdown("**📋 Compras realizadas**")
st.dataframe(purchases_table_df, use_container_width=True)
st.markdown("---")

#st.header("👨‍💻 About Me")
st.markdown("""
<style>
.about-me {
    line-height: 1.8;
    font-size: 16px;
}
.social-link {
    margin-left: 10px;
}
</style>

<div class="about-me">
<p><strong>Camilo Durán Gutiérrez</strong></p>
<p>📍 Colombia</p>
<p>✉️ <a href="mailto:camiloduran2195@gmail.com">camiloduran2195@gmail.com</a></p>

<p><strong>Connect with me:</strong></p>
<ul>
<li>🔗 GitHub: <a href="https://github.com/cajo95" target="_blank">github.com/cajo95</a></li>
<li>🌐 Portfolio: <a href="https://abiding-seat-cb1.notion.site/Camilo-Dur-n-Guti-rrez-1c390ac432c28028a12de3255a2c339d" target="_blank">Notion Portfolio</a></li>
<li>📸 Instagram: <a href="https://www.instagram.com/camilo_jdg/" target="_blank">@camilo_jdg</a></li>
</ul>
</div>
""", unsafe_allow_html=True)

# with st.expander("📩 Contact Form"):
#     st.write("Send me a message directly:")
#     contact_form = """
#     <form action="https://formsubmit.co/camiloduran2195@gmail.com" method="POST">
#         <input type="hidden" name="_captcha" value="false">
#         <input type="text" name="name" placeholder="Your name" required style="width:100%; padding:8px; margin-bottom:10px;">
#         <input type="email" name="email" placeholder="Your email" required style="width:100%; padding:8px; margin-bottom:10px;">
#         <textarea name="message" placeholder="Your message" style="width:100%; padding:8px; margin-bottom:10px; height:100px;"></textarea>
#         <button type="submit" style="background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius:4px;">Send Message</button>
#     </form>
#     """
#     st.markdown(contact_form, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 10px;">
    © 2025 Camilo Durán Gutiérrez | Data Science Portfolio
</div>
""", unsafe_allow_html=True)