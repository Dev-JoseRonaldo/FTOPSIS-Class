import numpy as np
import pandas as pd
import json

class FuzzyTOPSIS:
    """
    Implementa��o do algoritmo Fuzzy TOPSIS para tomada de decis�o multicrit�rio
    adaptado para processar dados de entrada em formato JSON.
    """
    
    def __init__(self, json_data):
        """
        Inicializa o algoritmo Fuzzy TOPSIS com dados em formato JSON.
        
        Par�metros:
        -----------
        json_data : str ou dict
            Dados de entrada em formato JSON ou dicion�rio Python
        """
        # Carrega os dados JSON se for uma string
        if isinstance(json_data, str):
            self.data = json.loads(json_data)
        else:
            self.data = json_data
            
        # Extrai os par�metros do JSON
        params = self.data["parameters"]
        self.alternatives = params["alternatives"]
        self.criteria = params["criteria"]
        
        # Converte a matriz de desempenho para o formato necess�rio
        self.decision_matrix = self._convert_performance_matrix(params["performance_matrix"])
        
        # Converte os tipos de crit�rios para o formato necess�rio (1 para max, -1 para min)
        self.criteria_type = self._convert_criteria_types(params["criteria_types"])
        
        # Converte os pesos para o formato necess�rio
        self.weights = self._convert_weights(params["weights"])

    def _convert_performance_matrix(self, performance_dict):
        """
        Converte a matriz de desempenho do formato JSON para numpy array.
        
        Par�metros:
        -----------
        performance_dict : dict
            Matriz de desempenho no formato do JSON
            
        Retorna:
        --------
        numpy.ndarray
            Matriz de decis�o fuzzy triangular de formato (n_alternativas, n_criterios, 3)
        """
        n_alternatives = len(self.alternatives)
        n_criteria = len(self.criteria)
        
        # Inicializa a matriz de decis�o
        decision_matrix = np.zeros((n_alternatives, n_criteria, 3))
        
        # Preenche a matriz de decis�o
        for i, alt in enumerate(self.alternatives):
            for j, crit in enumerate(self.criteria):
                decision_matrix[i, j] = performance_dict[alt][j]
                
        return decision_matrix
    
    def _convert_criteria_types(self, criteria_types_dict):
        """
        Converte os tipos de crit�rios do formato JSON para array numpy.
        
        Par�metros:
        -----------
        criteria_types_dict : dict
            Tipos de crit�rios no formato do JSON
            
        Retorna:
        --------
        numpy.ndarray
            Array com os tipos de crit�rios (1 para max, -1 para min)
        """
        criteria_type = np.zeros(len(self.criteria))
        
        for j, crit in enumerate(self.criteria):
            criteria_type[j] = 1 if criteria_types_dict[crit] == "max" else -1
                
        return criteria_type
    
    def _convert_weights(self, weights_dict):
        """
        Converte os pesos do formato JSON para array numpy.
        
        Par�metros:
        -----------
        weights_dict : dict
            Pesos no formato do JSON
            
        Retorna:
        --------
        numpy.ndarray
            Array com os pesos fuzzy triangulares de formato (n_criterios, 3)
        """
        n_criteria = len(self.criteria)
        weights = np.zeros((n_criteria, 3))
        
        for j, crit in enumerate(self.criteria):
            weights[j] = weights_dict[crit]
                
        return weights
    
    def normalize_fuzzy_matrix(self, decision_matrix):
        """
        Normaliza a matriz de decis�o fuzzy.
        
        Par�metros:
        -----------
        decision_matrix : numpy.ndarray
            Matriz de decis�o fuzzy triangular
            
        Retorna:
        --------
        numpy.ndarray
            Matriz de decis�o fuzzy normalizada
        """
        n_alternatives = len(self.alternatives)
        n_criteria = len(self.criteria)
        
        normalized_matrix = np.zeros((n_alternatives, n_criteria, 3))
        
        for j in range(n_criteria):
            if self.criteria_type[j] > 0:  # Crit�rio de benef�cio (max)
                # Encontra o maior valor superior (u) para o crit�rio
                c_max = np.max(decision_matrix[:, j, 2])
                
                # Normaliza usando c_max para crit�rios de benef�cio
                for i in range(n_alternatives):
                    normalized_matrix[i, j, 0] = decision_matrix[i, j, 0] / c_max
                    normalized_matrix[i, j, 1] = decision_matrix[i, j, 1] / c_max
                    normalized_matrix[i, j, 2] = decision_matrix[i, j, 2] / c_max
            else:  # Crit�rio de custo (min)
                # Encontra o menor valor inferior (l) para o crit�rio
                c_min = np.min(decision_matrix[:, j, 0])
                
                # Normaliza usando c_min para crit�rios de custo
                for i in range(n_alternatives):
                    normalized_matrix[i, j, 0] = c_min / decision_matrix[i, j, 2]
                    normalized_matrix[i, j, 1] = c_min / decision_matrix[i, j, 1]
                    normalized_matrix[i, j, 2] = c_min / decision_matrix[i, j, 0]
        
        return normalized_matrix
    
    def calculate_weighted_matrix(self, normalized_matrix):
        """
        Calcula a matriz de decis�o fuzzy normalizada ponderada.
        
        Par�metros:
        -----------
        normalized_matrix : numpy.ndarray
            Matriz de decis�o fuzzy normalizada
            
        Retorna:
        --------
        numpy.ndarray
            Matriz de decis�o fuzzy normalizada ponderada
        """
        n_alternatives = len(self.alternatives)
        n_criteria = len(self.criteria)
        
        weighted_matrix = np.zeros((n_alternatives, n_criteria, 3))
        
        for i in range(n_alternatives):
            for j in range(n_criteria):
                # Multiplica��o de n�meros fuzzy triangulares
                weighted_matrix[i, j, 0] = normalized_matrix[i, j, 0] * self.weights[j, 0]
                weighted_matrix[i, j, 1] = normalized_matrix[i, j, 1] * self.weights[j, 1]
                weighted_matrix[i, j, 2] = normalized_matrix[i, j, 2] * self.weights[j, 2]
        
        return weighted_matrix
    
    def calculate_fpis_fnis(self, weighted_matrix):                     
        """
        Calcula a Solu��o Ideal Positiva Fuzzy (FPIS) e Solu��o Ideal Negativa Fuzzy (FNIS).
        
        Par�metros:
        -----------
        weighted_matrix : numpy.ndarray
            Matriz de decis�o fuzzy normalizada ponderada
            
        Retorna:
        --------
        tuple
            (FPIS, FNIS)
        """
        n_criteria = len(self.criteria)
        
        # Inicializa FPIS e FNIS
        fpis = np.zeros((n_criteria, 3))
        fnis = np.zeros((n_criteria, 3))
        
        for j in range(n_criteria):
            fpis[j] = [1, 1, 1]
            
                
        return fpis, fnis
    
    def calculate_distances(self, weighted_matrix, fpis, fnis):
        """
        Calcula as dist�ncias de cada alternativa para FPIS e FNIS.
        
        Par�metros:
        -----------
        weighted_matrix : numpy.ndarray
            Matriz de decis�o fuzzy normalizada ponderada
        fpis : numpy.ndarray
            Solu��o Ideal Positiva Fuzzy
        fnis : numpy.ndarray
            Solu��o Ideal Negativa Fuzzy
            
        Retorna:
        --------
        tuple
            (dist�ncias para FPIS, dist�ncias para FNIS)
        """
        n_alternatives = len(self.alternatives)
        n_criteria = len(self.criteria)
        
        # Corre��o: inicializa as dist�ncias como arrays
        fpis_distances = np.zeros(n_alternatives)
        fnis_distances = np.zeros(n_alternatives)
        
        for i in range(n_alternatives):
            fpis_dist_sum = 0
            fnis_dist_sum = 0
            
            for j in range(n_criteria):
                # Dist�ncia euclidiana entre n�meros fuzzy triangulares
                # Corre��o: f�rmula de dist�ncia
                fpis_dist_sum += np.sqrt((1/3) * ((weighted_matrix[i, j, 0] - fpis[j, 0])**2 + 
                                       (weighted_matrix[i, j, 1] - fpis[j, 1])**2 + 
                                       (weighted_matrix[i, j, 2] - fpis[j, 2])**2))
                
                fnis_dist_sum += np.sqrt((1/3) * ((weighted_matrix[i, j, 0] - fnis[j, 0])**2 + 
                                      (weighted_matrix[i, j, 1] - fnis[j, 1])**2 + 
                                      (weighted_matrix[i, j, 2] - fnis[j, 2])**2))
            
            # Calcula a raiz quadrada para obter a dist�ncia euclidiana
            fpis_distances[i] = fpis_dist_sum
            fnis_distances[i] = fnis_dist_sum
        
        # Normaliza��o das dist�ncias para obter os valores esperados
        
        return fpis_distances, fnis_distances
    
    def calculate_closeness_coefficients(self, fpis_distances, fnis_distances):
        """
        Calcula os coeficientes de proximidade para cada alternativa.
        
        Par�metros:
        -----------
        fpis_distances : numpy.ndarray
            Dist�ncias para Solu��o Ideal Positiva Fuzzy
        fnis_distances : numpy.ndarray
            Dist�ncias para Solu��o Ideal Negativa Fuzzy
            
        Retorna:
        --------
        numpy.ndarray
            Coeficientes de proximidade
        """

        closeness_coefficients = []

        for i in range(len(self.alternatives)):
            closeness_coefficients.append(fnis_distances[i]/(fnis_distances[i]+fpis_distances[i]))
        
        return closeness_coefficients
    
    def rank_alternatives(self):
        """
        Aplica o algoritmo Fuzzy TOPSIS para rankear as alternativas.
        
        Retorna:
        --------
        dict
            Resultados em formato JSON espec�fico
        """
        # Normaliza a matriz de decis�o
        normalized_matrix = self.normalize_fuzzy_matrix(self.decision_matrix)
        
        # Calcula a matriz ponderada
        weighted_matrix = self.calculate_weighted_matrix(normalized_matrix)
        
        # Calcula FPIS e FNIS
        fpis, fnis = self.calculate_fpis_fnis(weighted_matrix)
        
        # Calcula as dist�ncias
        fpis_distances, fnis_distances = self.calculate_distances(weighted_matrix, fpis, fnis)
        
        # Calcula os coeficientes de proximidade (agora s�o as dist�ncias normalizadas para FNIS)
        closeness_coefficients = self.calculate_closeness_coefficients(fpis_distances, fnis_distances)
        
        # Cria um DataFrame com os resultados
        results_df = pd.DataFrame({
            'Alternative': self.alternatives,
            'Proximity': closeness_coefficients,
            'Ideal_Distance': fpis_distances,
            'Negative_Ideal_Distance': fnis_distances
        })
        
        # Ordena pelo coeficiente de proximidade em ordem decrescente
        results_df = results_df.sort_values('Proximity', ascending=False)
        
        # Formata o JSON de sa�da conforme especificado
        results_json = {
            "results": {
                "proximities": {},
                "ranking": results_df['Alternative'].tolist(),
                "best_alternative": results_df['Alternative'].iloc[0],
                "distances": {}
            }
        }
        
        # Preenche as proximidades e dist�ncias para cada alternativa
        for _, row in results_df.iterrows():
            alt = row['Alternative']
            proximity = round(float(row['Proximity']), 2)  # Arredonda para 2 casas decimais
            ideal_distance = round(float(row['Ideal_Distance']), 2)
            negative_ideal_distance = round(float(row['Negative_Ideal_Distance']), 2)
            
            # Adiciona � estrutura JSON
            results_json["results"]["proximities"][alt] = proximity
            results_json["results"]["distances"][alt] = {
                "ideal": ideal_distance,
                "negative_ideal": negative_ideal_distance
            }
        
        return results_json

# Fun��o para processar a entrada JSON
def process_fuzzy_topsis(json_input):
    """
    Processa a entrada JSON e executa o algoritmo Fuzzy TOPSIS.
    
    Par�metros:
    -----------
    json_input : str ou dict
        Dados de entrada em formato JSON ou dicion�rio Python
        
    Retorna:
    --------
    dict
        Resultados em formato JSON espec�fico
    """
    try:
        # Inicializa o algoritmo Fuzzy TOPSIS com os dados JSON
        fuzzy_topsis = FuzzyTOPSIS(json_input)
        
        # Executa o algoritmo e obt�m os resultados
        results = fuzzy_topsis.rank_alternatives()
        
        return results
    
    except Exception as e:
        # Retorna erro em formato JSON
        return {
            "error": True,
            "message": str(e)
        }
    