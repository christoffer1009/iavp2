import pandas as pd


class Cluster:
    def __init__(self, id):
        self.id = id
        self.ocorrencias = pd.DataFrame(columns=['cor', 'nucleos', 'caudas'])
        self.filhos = []

    def add_filho(self, filho):
        self.filhos.append(filho)

    def remove_filho(self, filho):
        self.filhos.remove(filho)

    def get_filhos_ids(self):
        return [filho.id for filho in self.filhos]

    def add_ocorrencia(self, ocorrencia):
        self.ocorrencias = pd.concat([self.ocorrencias, ocorrencia], ignore_index=True)

    def remove_ocorrencia(self, ocorrencia):
        self.ocorrencias.remove(ocorrencia)

    def get_ocorrencias_ids(self):
        return [o.id for o in self.ocorrencias]

    def toString(self):
        filhos_ids = self.get_filhos_ids()
        return f"{self.id}: filhos: {filhos_ids}"


class Ocorrencia:
    def __init__(self, id, cor, nucleos, caudas):
        self.id = id
        self.cor = cor
        self.nucleos = nucleos
        self.caudas = caudas

    def toString(self):
        return f"{self.id}: cor: {self.cor} n_nucleos: {self.nucleos} caudas:{self.caudas}"


class Cobweb:
    def __init__(self, c0, ocorrencias):
        self.c0 = c0
        self.todas_ocorrencias = ocorrencias

    def calcula_p_atributo(self, atributo, ocorrencias):
        oc = ocorrencias
        count_dict = oc[atributo].value_counts().to_dict()
        total = sum(count_dict.values())
        probabilidades = {key: (count / total) ** 2 for key,
                          count in count_dict.items()}
        probabilidades['soma'] = sum(probabilidades.values())
        return probabilidades

    def calcula_p_cluster(self, cluster: Cluster):
        oc = cluster.ocorrencias
        colunas = oc.columns
        p_cluster = 0
        for c in colunas:
            p_dict = self.calcula_p_atributo(c, oc)
            total = p_dict["soma"]
            p_cluster += total
        return {'cluster':cluster.id, 'p': (p_cluster - self.calcula_p_total()) * len(oc)/len(self.todas_ocorrencias)}

    def calcula_p_total(self):
        oc = self.todas_ocorrencias
        colunas = self.todas_ocorrencias.columns
        p_total = 0
        for c in colunas:
            p_dict = self.calcula_p_atributo(c, oc)
            total = p_dict["soma"]
            p_total += total
        return p_total

    def calcula_uc(self, cluster: Cluster):
        total_p = 0
        for item in cluster.filhos:
            total_p += self.calcula_p_cluster(item)['p']
        return total_p / len(cluster.filhos)

    def start(self, cluster: Cluster, ocorrencia):
        if len(cluster.filhos) == 0:
            print('E FOLHA')
            c1 = Cluster("c1")
            c2 = Cluster("c2")


c0 = Cluster(0)
c1 = Cluster(1)
c2= Cluster(2)

c0.add_filho(c1)
c0.add_filho(c2)

ocorrencias = pd.read_csv('tabela.csv')
c1.add_ocorrencia(ocorrencias.iloc[[0]])
c1.add_ocorrencia(ocorrencias.iloc[[2]])
c2.add_ocorrencia(ocorrencias.iloc[[1]])

cobweb = Cobweb(c0, ocorrencias)
# print(cobweb.calcula_p_atributo("cor"))
# print(cobweb.calcula_p_atributo("nucleos"))
# print(cobweb.calcula_p_atributo("caudas"))

print(cobweb.calcula_p_cluster(c1))
print(cobweb.calcula_p_cluster(c2))
print(cobweb.calcula_uc(c0))