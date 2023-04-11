import matplotlib.pyplot as plt
import pandas as pd
import ipywidgets as widgets
import numpy as np


def crea_dataframe(data): #data -> ruta del archivo
    #creacion dataframe, elimina columnas Lat y Long 
    df = pd.read_csv(data,index_col="Country/Region",parse_dates=True).drop(["Lat","Long"],axis=1)

    #reduce la columna province/state con un groupby manteniendo los totales por pais
    df = df.groupby(level=0).sum(numeric_only=True)

    #parsear fechas
    fechas = []
    for i in df.columns:
        fechas.append(pd.to_datetime(i)) #añade a una lista la transformacion a timestamp de cada fecha
    df.columns = fechas #asigna a columnas la lista de fechas parseadas a timestamp

    return df

def eliminar_error(df,df_population):
    valores_error = []
    for pais in df.index:
        if pais not in df_population.index:
            valores_error.append(pais)
            df.drop(labels=pais, axis=0, inplace=True)


def crear_grafico(num): #crea el grafico dentro de cada hijo de la tabla
    if(pais1.value == pais2.value):
        display("selecciona paises distintos")
        
    with tabla.children[num]:

        #### aplicar aqui los filtros 
        
        fig, ax = plt.subplots(figsize=(14, 8), tight_layout=True, facecolor='#EEF')

        line, = ax.plot(dataframes_OCDE[num].loc[pais1.value, pd.to_datetime("2020-01-22"): pd.to_datetime("2022-04-10")],label=pais1.value)
        line2, = ax.plot(dataframes_OCDE[num].loc[pais2.value, pd.to_datetime("2020-01-22"): pd.to_datetime("2022-04-10")], label=pais2.value)
        plt.legend()
        ax.set_title(pais1.value+" vs "+pais2.value)
        plt.show()

def boton_presionado(dato): #elimina el grafico actual y crea otro grafico con los nuevos valores
    for i in range(0,3):
        with tabla.children[i]:
            tabla.children[i].clear_output()
            crear_grafico(i)
def main():
    df_confirmados = crea_dataframe("data/covid19_confirmados.csv") #creacion del df
    df_population = pd.read_csv("data/poblacion_mundial2020.csv") #dataframe de population
    df_population.rename(columns={"Country (or dependency)":"Country/Region"}, inplace=True) #Cambio del nombre de el indice de la columna
    df_population.set_index("Country/Region",inplace=True) #asignacion de "nuevo" nombre
    eliminar_error(df_confirmados,df_population)
    df_confirmados = pd.merge(df_confirmados,df_population, on="Country/Region")

    #creacion de siguientes dataframe y merge con population

    df_recuperados = crea_dataframe("data/covid19_recuperados.csv") #creacion del df
    eliminar_error(df_recuperados,df_population)
    df_recuperados = pd.merge(df_recuperados,df_population, on="Country/Region") #merge

    df_muertes = crea_dataframe("data/covid19_muertes.csv") #creacion del df
    eliminar_error(df_muertes,df_population)
    df_muertes = pd.merge(df_muertes,df_population, on="Country/Region") #merge

    #Continentes y codigo ISO2 archivo generado con chatgpt
    continentes = pd.read_csv("data/pais_cod_continente.csv",index_col="Country/Region")

    df_confirmados = pd.merge(df_confirmados,continentes,on="Country/Region")
    df_recuperados = pd.merge(df_recuperados,continentes,on="Country/Region")
    df_muertes = pd.merge(df_muertes,continentes,on="Country/Region")

    #dataframe de paises OCDE -> datos obtenidos con chatgpt
    df_OCDE_confirmados = pd.read_csv("data/paises_OCDE.csv",index_col="Country/Region")
    df_OCDE_confirmados = pd.merge(df_confirmados,df_OCDE_confirmados,on="Country/Region")

    df_OCDE_recuperados= pd.read_csv("data/paises_OCDE.csv",index_col="Country/Region")
    df_OCDE_recuperados = pd.merge(df_recuperados,df_OCDE_recuperados,on="Country/Region")

    df_OCDE_muertes = pd.read_csv("data/paises_OCDE.csv",index_col="Country/Region")
    df_OCDE_muertes = pd.merge(df_muertes,df_OCDE_muertes,on="Country/Region")

    dataframes_OCDE = {0: df_OCDE_confirmados,
                   1: df_OCDE_recuperados,
                   2: df_OCDE_muertes} #ayuda a acceder al df de forma mas facil
    
    pais1 = widgets.Dropdown(
        value='Chile', 
        options=df_OCDE_confirmados.index, 
        description='Pais 1'
    )

    pais2 = widgets.Dropdown( 
        options=df_OCDE_confirmados.index, 
        description='Pais 2'
    )

    selector_casos = widgets.RadioButtons(
        options=['Casos acumulados', 'Casos nuevos'],
        description='Seleccion de casos',
        disabled=False
    )

    selector_valores = widgets.RadioButtons(
        options=['Valores absolutos', 'Valores relativos'],
        description='Seleccion de casos',
        disabled=False
    )

    selector_fecha = widgets.RadioButtons(
        options=['Valores diarios', 'Valores semanales'],
        description='Seleccion de fecha',
        disabled=False
    )

    confirmar_paises = widgets.Button(description='confirmar paises')

    confirmar_filtros = widgets.Button(description='confirmar filtros')

    datos_tabla = ["Tasa incidencias", "Tasa recuperados","Tasa mortalidad"]
    tabla = widgets.Tab(children=[widgets.Output() for i in range(len(datos_tabla))])
    for i in range(len(datos_tabla)):
        tabla.set_title(i,datos_tabla[i])


    output = widgets.Output()

    fila1 = widgets.HBox([pais1,pais2,confirmar_paises,output])
    fila2 = widgets.HBox([selector_casos,selector_valores,selector_fecha,confirmar_filtros])

    display(widgets.VBox([fila1, fila2,output]))

    confirmar_paises.on_click(boton_presionado)
    # confirmar_filtros.on_click(boton_presionado)
    display(tabla)


def crear_dashboard():
    main()
