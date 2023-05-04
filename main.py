import pandas as pd
import copy
from typing import List


class Cluster:
    def __init__(self, id):
        self.id = id
        self.ocorrencias = pd.DataFrame(columns=['cor', 'nucleos', 'caudas'])
        self.filhos: List[Cluster] = []
        self.p_cluster = 0
        self.p_total = 0
        # self.uc = 0
        self.n_filhos = 0

    def add_filho(self, filho):
        self.filhos.append(filho)
        self.n_filhos += 1

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
        self.p_total = p_total
        return p_total


class Ocorrencia:
    def __init__(self, id, cor, nucleos, caudas):
        self.id = id
        self.cor = cor
        self.nucleos = nucleos
        self.caudas = caudas

    def toString(self):
        return f"{self.id}: cor: {self.cor} n_nucleos: {self.nucleos} caudas:{self.caudas}"


class Cobweb:
    def __init__(self):
        self.raiz = Cluster('raiz')
        self.uc = 0
        self.todas_ocorrencias = pd.DataFrame(
            columns=['cor', 'nucleos', 'caudas'])

    def nova_ocorrencia(self, ocorrencia):
        self.todas_ocorrencias = pd.concat(
            [self.todas_ocorrencias, ocorrencia], ignore_index=True)

    def calcula_uc(self):
        uc = 0
        for cluster in self.raiz.filhos:
            cluster.calcula_p_cluster()
            uc += (cluster.p_cluster - cluster.calcula_p_total(self.todas_ocorrencias)
                   ) * cluster.ocorrencias.shape[0]/self.todas_ocorrencias.shape[0]
        self.uc = uc / self.raiz.n_filhos if self.raiz.n_filhos > 0 else 3
        return self.uc

    def sao_iguais(dict1: dict, dict2: dict) -> bool:
        if set(dict1.keys()) != set(dict2.keys()):
            return False

        for key in dict1:
            if dict1[key] != dict2[key]:
                return False
        return True

    def escolhe_situacao(self):
        pass

    def calcula_s1(self, oc):
        # s1 colocar em cluster existente, baseado na posição do array
        s1 = []
        temp = copy.deepcopy(self)
        for i in range(temp.raiz.n_filhos):
            temp.raiz.filhos[i].add_ocorrencia(oc)
            uc = temp.calcula_uc()
            s1.append({'estrategia' : 's1', 'index' : i, 'uc' : uc})
            temp = copy.deepcopy(self)
        maior_uc = max(s1, key=lambda x: x["uc"])
        return maior_uc
    
    def fazer_s1(self, index: int, oc):
        self.raiz.filhos[index].add_ocorrencia(oc)
        self.calcula_uc()

    def fazer_s2(self, oc):
        cluster = Cluster(f'c{self.raiz.n_filhos + 1}')
        cluster.add_ocorrencia(oc)
        self.raiz.add_filho(cluster)
        self.calcula_uc()
    
    def calcula_s2(self, oc):
        # s2 colocar em novo cluster
        temp = copy.deepcopy(self)
        s2 = 0  
        cluster = Cluster(f'c{self.raiz.n_filhos+1}')
        cluster.add_ocorrencia(oc)
        temp.raiz.add_filho(cluster)
        s2 = temp.calcula_uc()
        return {'estrategia' : 's2', 'uc': s2}
    
    def calcula_s3(self, oc):
        # s3 merge clusters
        pass

    def calcula_s4(self, oc):
        # s4 split clusters
        pass

    def start(self, oc):
        raiz = self.raiz
        raiz.add_ocorrencia(oc)
        self.nova_ocorrencia(oc)
        
        if raiz.n_filhos == 0 and raiz.ocorrencias.shape[0] == 1:
            self.calcula_uc()

        elif raiz.n_filhos == 0 and raiz.ocorrencias.shape[0] > 1:
            c1 = Cluster('c1')
            c1.add_ocorrencia(raiz.ocorrencias.iloc[[0]])

            c2 = Cluster('c2')
            c2.add_ocorrencia(oc)

            raiz.add_filho(c1)
            raiz.add_filho(c2)
        else:
            s1 = self.calcula_s1(oc)                        
            s2 = self.calcula_s2(oc)                        
            ucs = [s1, s2]
            estrategia_esolhida = max(ucs, key=lambda x: x["uc"])
            if estrategia_esolhida['estrategia'] == 's1':
                self.fazer_s1(estrategia_esolhida['index'], oc)
            elif estrategia_esolhida['estrategia'] == 's2':
                self.fazer_s2(oc)
        self.calcula_uc()
        print(f'uc: {self.uc} filhos: {self.raiz.n_filhos}')
        print(f'{self.todas_ocorrencias}')

ocorrencias = pd.read_csv('tabela.csv')
cobweb = Cobweb()
cobweb.start(ocorrencias.iloc[[0]])
cobweb.start(ocorrencias.iloc[[1]])
cobweb.start(ocorrencias.iloc[[2]])
