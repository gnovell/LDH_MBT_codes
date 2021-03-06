import numpy as np
import sys

def lectura_file(arxiu):
    #Lectura del archivo dat.
    d_l = []
    archivo = open(arxiu, 'rt')
    counter_linea = 0
    for linea in archivo:
        xx,yy,_=linea.split()
        d_l.append([xx,yy])
    archivo.close()
    return(np.array(d_l,float))


###################################################3
#input a file with a list of files
arxivos = sys.argv[1]
lista_arxivos = []
arxiu = open(arxivos,'rt')
for linea in arxiu:
    lista_arxivos.append(linea[:-1])
arxiu.close()
#read files and extract the data 
lista_data = []
for i in range(len(lista_arxivos)):
    arxiu = lista_arxivos[i]
    lista_data.append(lectura_file(arxiu))
#Concatenate and add results 
matriz_datos = np.concatenate(lista_data,axis=1)
matriz_resultados = np.zeros((len(matriz_datos),2),float)
matriz_resultados[::,0]=matriz_datos[::,0]
lista_results = []
for i in range(len(lista_arxivos)):
    lista_results.append([matriz_datos[::,2*i+1]])
matriz_suma=np.transpose(np.concatenate(lista_results))
matriz_resultados[::,1]=np.transpose(np.sum(matriz_suma,axis=1))
#Print results
for row in matriz_resultados:
    print(str(row[0])+"    "+str(row[1]))
