"""
Python3 code generated by Gerard Novell-Leruth
The code analyze the angles between plane of AL-ZN2-ZN3 from LDH and the plane of MBT ring (C2-C4-C6) from MBT between the
neighbor atoms of C2 atom. The geometry is read from a Gromacs format file (*.gro)
The multiprocessor is implemented to reduce the time to process a large number files (*.gro).
The code use the Gromacs geometry format (*.gro) using the Gromacs tool (trjconv) for each frame saved in *.trr file.
Read these files to read the geometries and analyse the angles that form between the planes and line vectors and
write the angles and their histogram file (*.dat).
"""
import numpy as np
import math
import sys
import os
import multiprocessing

#Read the .gro file
def lectura_archivo(arxiu):
    # Variables for the atom coordinates in NumPy array
    m_AL=np.array([],float)
    m_ZN2=np.array([],float)
    m_ZN3=np.array([],float)
    m_C2=np.array([],float)
    m_C4=np.array([],float)
    m_C6=np.array([], float)
# Read file and filter and capture the XYZ coordinates of specific atoms
    archivo = open(arxiu,'rt')
    for linea in archivo:
        if "AL" in linea:
            X,Y,Z = linea[21:45].split()[0:4]
            m_AL=np.append(m_AL,[X,Y,Z])
        if "ZN2" in linea:
            X,Y,Z = linea[21:45].split()[0:4]
            m_ZN2=np.append(m_ZN2,[X,Y,Z])
        if "ZN3" in linea:
            X,Y,Z = linea[21:45].split()[0:4]
            m_ZN3=np.append(m_ZN3,[X,Y,Z])
        if "C2" in linea:
            X,Y,Z = linea[21:45].split()[0:4]
            m_C2=np.append(m_C2,[X,Y,Z])
        if "C4" in linea:
            X, Y, Z = linea[21:45].split()[0:4]
            m_C4 = np.append(m_C4, [X, Y, Z])
        if "C6" in linea:
            X, Y, Z = linea[21:45].split()[0:4]
            m_C6 = np.append(m_C6, [X, Y, Z])
    archivo.close()
# Capture and manipulate the matrix of cell
    v1x,v2y,v3z,v1y,v1z,v2x,v2z,v3x,v3y = linea.split()
    m_cell=np.array([[v1x,v1y,v1z],[v2x,v2y,v2z],[v3x,v3y,v3z]],float)
    return(m_AL,m_ZN2,m_ZN3,m_C2,m_C4,m_C6,m_cell)

#replica matriz para evitar contornos
def matriz_pbc(matriz_A,matriz_celda):
# Displacement variables and construction of displacement matrix operator
    XX=np.append(np.array(matriz_celda[0],float),1)
    YY=np.append(np.array(matriz_celda[1],float),1)
    ZZ=np.append(np.array(matriz_celda[2],float),1)
    matriz_Anew=np.array(np.append(matriz_A,np.reshape(np.ones(matriz_A.shape[0]),(matriz_A.shape[0],1)),axis=1),float)
    matriz_operador=np.eye(4,4)
# displacement operations in 3D of the original coordinates of matriz_A in the cell unit (metriz_celda)
    for i in range(0,3):
        a=i-1
        for j in range(0,3):
            b=j-1
            for k in range(0,3):
                c=k-1
                desplazamiento=a*XX+b*YY+c*ZZ
                desplazamiento[3]=1
                matriz_operador[3]=desplazamiento
                m_pbc=np.dot(matriz_Anew,matriz_operador)
                m_pbc=m_pbc[:,:-1]
                if a==-1 and b==-1 and c==-1 :
                    m_resultado=np.array(m_pbc,float)
                else :
                    m_resultado=np.append(m_resultado,m_pbc,axis=0)
    return(m_resultado)

# Function to calculate de neighbour atoms and the vectors of plane and line to calculate the angle between them.
def angulo_molecula(j):
    # calulate distances
    distance_C2AL = np.sqrt(np.sum((np.asarray(matriz_C2[j],float)-np.asarray(matriz_nueva_AL,float))**2,axis=1))
    distance_C2ZN2 = np.sqrt(np.sum((np.asarray(matriz_C2[j],float)-np.asarray(matriz_nueva_ZN2,float))**2,axis=1))
    distance_C2ZN3 = np.sqrt(np.sum((np.asarray(matriz_C2[j],float)-np.asarray(matriz_nueva_ZN3,float))**2,axis=1))
    # locate the atoms of minimal distances
    indice_dC2AL=np.argmin(distance_C2AL)
    indice_dC2ZN2=np.argmin(distance_C2ZN2)
    indice_dC2ZN3=np.argmin(distance_C2ZN3)
    # Coordinates of atoms with minimal didstances
    XYZ_AL = np.asarray(matriz_nueva_AL[indice_dC2AL],float)
    XYZ_ZN2 = np.asarray(matriz_nueva_ZN2[indice_dC2ZN2],float)
    XYZ_ZN3 = np.asarray(matriz_nueva_ZN3[indice_dC2ZN3],float)
    XYZ_C2=np.asarray(matriz_C2[j],float)
    XYZ_C4=np.asarray(matriz_C4[j],float)
    XYZ_C6=np.asarray(matriz_C6[j],float)
    # Vectors of plane metal (AL-ZN2-ZN3) and line (Sterminal-N)
    plano_metal=np.cross((XYZ_ZN2-XYZ_AL),(XYZ_ZN3-XYZ_AL))
    plano_molecula=np.cross((XYZ_C4-XYZ_C2),(XYZ_C6-XYZ_C2))
    # Angle of two vectors
    angulo = np.rad2deg(np.arccos(np.clip(np.dot(plano_metal,plano_molecula)/np.linalg.norm(plano_metal)/np.linalg.norm(plano_molecula),-1,1)))
    return(angulo)


##################################################################
#PROGRAM:
"""
variables of program:
for execution: python Angles_LDH_MBTsn_parallel.py $PATH
$PATH is the path where is the date to extract the geometry information from trajectory files .trr  
frame_ini is the initial time of trajectori file extraction
frame_fin is the end time of trajectori file extraction
frame_step is the time step that is saved the trr file
archivo_nom is the name of file to extract the date without extension
NUM_CPU is the number of CPUs to process the angles calculations
"""
frame_ini=0
frame_fin=50000
frame_step=50
archivo_nom='md'
NUM_CPU=8

directori_nom = sys.argv[1]
archivo_TRR = directori_nom+'/'+archivo_nom+'.trr'
archivo_TPR = directori_nom+'/'+archivo_nom+'.tpr'
# Exercution of Gromacs tools for extract the geometry information from trajectory files (.trr)
commando='gmx trjconv -f '+archivo_TRR+' -s '+archivo_TPR+' -o test_.gro -b '+str(frame_ini)+' -e '+str(frame_fin)+' -pbc atom -ur tric -sep <<< 0'
os.system(commando)
commando=' for i in *.gro ; do gmx trjconv -f $i -s '+archivo_TPR+' -o tmp.gro -pbc mol -ur tric <<< 0 ; mv tmp.gro $i ; done '
os.system(commando)
# Extraction and processing data.
counter_files = int((frame_fin-frame_ini)/frame_step)
angulos=[]
for i in range(0,counter_files):
# Extraction of geometry data form gro files of trajectory extraction
    matriz_AL,matriz_ZN2,matriz_ZN3,matriz_C2,matriz_C4,matriz_C6,matriz_celda=lectura_archivo('test_'+str(i)+'.gro')
    matriz_AL=np.reshape(matriz_AL,(int(len(matriz_AL)/3),3))
    matriz_ZN2=np.reshape(matriz_ZN2,(int(len(matriz_ZN2)/3),3))
    matriz_ZN3=np.reshape(matriz_ZN3,(int(len(matriz_ZN3)/3),3))
    matriz_C2=np.reshape(matriz_C2,(int(len(matriz_C2)/3),3))
    matriz_C4=np.reshape(matriz_C4,(int(len(matriz_C4)/3),3))
    matriz_C6=np.reshape(matriz_C6,(int(len(matriz_C6)/3),3))
    matriz_celda=np.reshape(matriz_celda,(3,3))
# replication of cells to elimate the limits of cell
    matriz_nueva_AL=matriz_pbc(matriz_AL,matriz_celda)
    matriz_nueva_ZN2=matriz_pbc(matriz_ZN2,matriz_celda)
    matriz_nueva_ZN3=matriz_pbc(matriz_ZN3,matriz_celda)
# multiprocessing the angle calculation
    if __name__ == '__main__':
        pool = multiprocessing.Pool(processes=NUM_CPU)
        angulos.append(pool.map(angulo_molecula, range(0,len(matriz_C2))))
        pool.close()

datos=np.histogram(angulos,bins=180,range=(0,180),density=True)
# Save the angel distributions in a angles.dat
archivo_angulos=open('angles.dat','wt')
for k in range(0,len(angulos)):
    archivo_angulos.write(str(angulos[k])+'  \n')
archivo_angulos.close()
# Genarete and save the histogram of angle distribution in histogram.dat
archivo_histograma=open('histogram.dat','wt')
for l in range(0,180):
    archivo_histograma.write(str(datos[1][l]+0.5)+"   "+str(datos[0][l])+'  \n')
archivo_histograma.close()
