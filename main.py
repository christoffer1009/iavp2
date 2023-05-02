import pandas as pd
from typing import List

class Cluster:
    def __init__(self, id):
        self.id = id
        self.ocorrencias = pd.DataFrame(columns=['cor', 'nucleos', 'caudas'])
        self.filhos:List[Cluster] = []
        self.p_cluster = 0
        self.p_total= 0
        self.uc = 0

    def add_filho(self, filho):
        self.filhos.append(filho)

    def remove_filho(self, filho):
        self.filhos.remove(filho)

    # def get_filhos_ids(self):
    #     return [filho.id for filho in self.filhos]

    def add_ocorrencia(self, ocorrencia):
        self.ocorrencias = pd.concat(
            [self.ocorrencias, ocorrencia], ignore_index=True)

    # def remove_ocorrencia(self, ocorrencia):
    #     self.ocorrencias.remove(ocorrencia)

    # def get_ocorrencias_ids(self):
    #     return self.ocorrencias['id'].to_list()

    # def toString(self):
    #     filhos_ids = self.get_filhos_ids()
    #     return f"{self.id}: filhos: {filhos_ids}"

    def calcula_p_atributo(self, atributo, ocorrencias):
        oc = ocorrencias
        count_dict = oc[atributo].value_counts().to_dict()
        total = sum(count_dict.values())
        probabilidades = {key: (count / total) ** 2 for key,
                          count in count_dict.items()}
        probabilidades['soma'] = sum(probabilidades.values())
        return probabilidades

    def calcula_p_cluster(self):
        oc = self.ocorrencias
        colunas = oc.columns
        p_cluster = 0
        for c in colunas:
            p_dict = self.calcula_p_atributo(c, oc)
            total = p_dict["soma"]
            p_cluster += total
        self.p_cluster = p_cluster
        return {'cluster': self.id, 'p': p_cluster}

    def calcula_p_total(self, todas_ocorrencias):
        oc = todas_ocorrencias
        colunas = todas_ocorrencias.columns
        p_total = 0
        for c in colunas:
            p_dict = self.calcula_p_atributo(c, oc)
            total = p_dict["soma"]
            p_total += total
        self.p_total =p_total
        return p_total

    def calcula_uc(self, todas_ocorrencias):
        uc = 0
        for item in self.filhos:
            item.calcula_p_cluster()
            uc += (item.p_cluster - self.calcula_p_total(todas_ocorrencias)) * len(item.ocorrencias)/len(todas_ocorrencias)
        self.uc = uc / len(self.filhos) if len(self.filhos) > 0 else 3
        return uc


class Ocorrencia:
    def __init__(self, id, cor, nucleos, caudas):
        self.id = id
        self.cor = cor
        self.nucleos = nucleos
        self.caudas = caudas

    def toString(self):
        return f"{self.id}: cor: {self.cor} n_nucleos: {self.nucleos} caudas:{self.caudas}"


class Cobweb:
    def __init__(self, todas_ocorrencias):
        self.c0 = Cluster('c0')
        self.c0.uc = 0
        self.todas_ocorrencias =  pd.DataFrame(columns=['cor', 'nucleos', 'caudas'])

    def nova_ocorrencia(self, ocorrencia):
        self.todas_ocorrencias = pd.concat(
            [self.todas_ocorrencias, ocorrencia], ignore_index=True)
        
    def escolhe_situacao(self):
        pass
        

    def start(self, oc):
        c0 = self.c0
        self.nova_ocorrencia(oc)

        if len(c0.filhos)==0 and len(self.todas_ocorrencias)==1:
            c0.calcula_uc(self.todas_ocorrencias)
            
        elif len(c0.filhos)==0 and len(self.todas_ocorrencias)>1:
            c1 = Cluster('c1')
            c1.add_ocorrencia(self.todas_ocorrencias.iloc[[0]])
            
            c2=Cluster('c2')
            c2.add_ocorrencia(oc)
            
            c0.add_filho(c1)
            c0.add_filho(c2)            
        else:
            print("aqui")
            #c0.filhos[0].add_ocorrencia(oc)                
            c3=Cluster('c3')
            c3.add_ocorrencia(oc)
            c0.add_filho(c3)
        c0.calcula_uc(self.todas_ocorrencias)
        # print(self.todas_ocorrencias)
        print(f'p: {c0.p_total} uc: {c0.uc}')



# c1.add_ocorrencia(ocorrencias.iloc[[2]])
# c2.add_ocorrencia(ocorrencias.iloc[[1]])

ocorrencias = pd.read_csv('tabela.csv')
cobweb = Cobweb(ocorrencias)
cobweb.start(ocorrencias.iloc[[0]])
cobweb.start(ocorrencias.iloc[[1]])
cobweb.start(ocorrencias.iloc[[2]])

