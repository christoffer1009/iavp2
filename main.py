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
        self.uc = 0
        self.n_filhos = 0

    def add_filho(self, filho):
        self.filhos.append(filho)
        self.n_filhos += 1

    def remove_filho(self, filho):
        self.filhos.remove(filho)

    def add_ocorrencia(self, ocorrencia):
        self.ocorrencias = pd.concat(
            [self.ocorrencias, ocorrencia], ignore_index=True)

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


class Cobweb:
    def __init__(self):
        self.raiz = Cluster('raiz')
        self.todas_ocorrencias = pd.DataFrame(
            columns=['cor', 'nucleos', 'caudas'])

    def nova_ocorrencia(self, ocorrencia):
        self.todas_ocorrencias = pd.concat(
            [self.todas_ocorrencias, ocorrencia], ignore_index=True)

    def calcula_uc(self, cluster):
        uc = 0
        for f in cluster.filhos:
            f.calcula_p_cluster()
            uc += (f.p_cluster - f.calcula_p_total(self.todas_ocorrencias)
                   ) * f.ocorrencias.shape[0]/self.todas_ocorrencias.shape[0]
        cluster.uc = uc / len(cluster.filhos) if len(cluster.filhos) > 0 else 3
        return cluster.uc

    def sao_iguais(dict1: dict, dict2: dict) -> bool:
        if set(dict1.keys()) != set(dict2.keys()):
            return False

        for key in dict1:
            if dict1[key] != dict2[key]:
                return False
        return True

    def calcula_melhor_filho(self, cluster, oc):
        # s1 colocar em cluster existente, baseado na posição do array
        uc_filhos = []
        temp = copy.deepcopy(cluster)
        for i in range(len(temp.filhos)):
            temp.filhos[i].add_ocorrencia(oc)
            uc = self.calcula_uc(temp)
            uc_filhos.append({'s': 'melhor', 'index': i, 'uc': uc})
            temp = copy.deepcopy(cluster)
        maior_uc = max(uc_filhos, key=lambda x: x["uc"])
        return maior_uc

    def calcula_novo_filho(self, cluster, oc):
        # s2 colocar em novo cluster
        temp = copy.deepcopy(cluster)
        uc_novo_cluster = 0
        novo_cluster = Cluster(f'c{len(cluster.filhos)+1}')
        novo_cluster.add_ocorrencia(oc)
        temp.add_filho(novo_cluster)
        uc_novo_cluster = self.calcula_uc(temp)
        return {'s': 'novo', 'uc': uc_novo_cluster}

    def estrategia_novo_filho(self, cluster, oc):
        novo_cluster = Cluster(f'c{len(cluster.filhos) + 1}')
        novo_cluster.add_ocorrencia(oc)
        cluster.add_filho(novo_cluster)
        self.calcula_uc(cluster)
        return cluster

    def calcula_merge(self, cluster: Cluster):
        if len(cluster.filhos) < 2:
            return {'uc': 0}
        temp = copy.deepcopy(cluster)
        merged = self.estrategia_merge(temp.filhos[0], temp.filhos[1])
        temp.add_filho(merged)
        temp.filhos.pop(0)
        temp.filhos.pop(0)
        return {'s': 'merge', 'uc': temp.uc}

    def estrategia_merge(self, cluster1: Cluster, cluster2: Cluster):
        novo_cluster = Cluster('c3')
        novo_cluster.ocorrencias = pd.concat(
            [cluster1.ocorrencias, cluster2.ocorrencias], ignore_index=True)
        novo_cluster.add_filho(cluster1)
        novo_cluster.add_filho(cluster2)
        return novo_cluster

    def calcula_split(self, cluster: Cluster):
        if len(cluster.filhos) == 0:
            return {'index': 0, 'uc': 0}
        uc_split = []
        temp = copy.deepcopy(cluster)
        for i in range(len(temp.filhos)):
            self.estrategia_split(temp, temp.filhos[i])
            uc = self.calcula_uc(temp)
            uc_split.append({'s': 'split', 'index': i, 'uc': uc})
            temp = copy.deepcopy(cluster)
        maior_uc = max(uc_split, key=lambda x: x["uc"])
        return maior_uc

    def estrategia_split(self, cluster_pai: Cluster, cluster: Cluster):
        for f in cluster.filhos:
            cluster_pai.add_filho(f)
        cluster_pai.filhos.remove(cluster)

    def start(self, cluster: Cluster, oc):
        self.nova_ocorrencia(oc)
        cluster.add_ocorrencia(oc)

        if len(cluster.filhos) == 0:
            c1 = Cluster('c1')
            c1.add_ocorrencia(oc)
            cluster.add_filho(c1)
            self.calcula_uc(cluster)
        else:
            melhor_filho = self.calcula_melhor_filho(cluster, oc)
            uc_novo_filho = self.calcula_novo_filho(cluster, oc)
            # merge = self.calcula_merge(cluster)
            # split = self.calcula_split(cluster)

            ucs = [melhor_filho, uc_novo_filho]
            s = max(ucs, key=lambda x: x['uc'])

            if s['s'] == 'novo':
                self.estrategia_novo_filho(cluster, oc)
                self.calcula_uc(cluster)
            elif s['s'] == 'melhor':
                cluster.filhos[melhor_filho['index']].add_ocorrencia(oc)
                self.calcula_uc(cluster)
            # elif s['s'] == 'merge':
            #     print('merge')
            #     c = self.estrategia_merge(
            #         cluster.filhos[0], cluster.filhos[1])
            #     cluster.add_filho(c)
            #     self.start(c, oc)
            # elif s['s'] == 'split':
            #     print('split')
            #     self.estrategia_split(
            #         cluster, cluster.filhos[split['index']])
            #     self.start(cluster, oc)

        print(str(cluster))


ocorrencias = pd.read_csv('tabela.csv')
raiz = Cluster('raiz')
cobweb = Cobweb()

for i in range(ocorrencias.shape[0]):
    cobweb.start(raiz, ocorrencias.iloc[[i]])
