import json
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Union
from utils.format_output import format_to_json

class FTOPSISProcessor:
    
    @staticmethod
    def load_json_data(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file {file_path} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {file_path}")

    @staticmethod
    def print_results(result: pd.DataFrame, title: str = "Results") -> None:
        print(f"\n{title}:")
        print(result.to_string(index=True, float_format="%.5f"))

    @staticmethod
    def print_trapezoidal_results(elements: list, closeness: dict, 
                                classification: dict, profile_mapping: dict) -> None:
        """Imprime os resultados do FTOPSIS trapezoidal formatado"""
        profiles = list(profile_mapping.values())
        
        elem_width = 10
        profile_width = 15
        class_width = 15
        
        # Cabeçalho
        header = f"{'Element':<{elem_width}}"
        for profile in profiles:
            header += f"{profile:<{profile_width}}"
        header += "Classification"
        print(header)
        
        # Linhas de dados
        for element in elements:
            cc = closeness[element]
            best_profile, best_cc = classification[element]
            
            row = f"{element:<{elem_width}}"
            for profile in profiles:
                row += f"{cc[profile]:<{profile_width}.5f}"
            row += f"{best_profile} ({best_cc:.5f})"
            
            print(row)

    @staticmethod
    def detect_fuzzy_type(data: Dict[str, Any]) -> str:
        """Detect if the JSON contains triangular or trapezoidal fuzzy numbers"""
        if 'linguistic_terms' in data:
            first_term = next(iter(data['linguistic_terms'].values()))
            if len(first_term) == 4:
                return 'trapezoidal'
        
        if 'linguistic_variables_alternatives' in data:
            first_term = next(iter(data['linguistic_variables_alternatives'].values()))
            if len(first_term) == 3:
                return 'triangular'
        
        raise ValueError("Could not determine fuzzy number type from JSON structure")

def trapezoidal_ftopsis_class(data: Dict[str, Any]) -> None:
    from ftopsis_class.trapezoidal_core import FuzzyNumber, FTOPSISClass, CriteriaType

    criteria_type = {k: CriteriaType[v] for k, v in data['criteria_type'].items()}
    
    ftopsis = FTOPSISClass(
        linguistic_terms=data['linguistic_terms'],
        weights=data['weights'],
        criteria_type=criteria_type,
        elements=data['elements'],
        criteria=data['criteria'],
        fuzzy_decision_matrix=data['fuzzy_decision_matrix'],
        reference_matrix=data['reference_matrix']
    )
    
    closeness, classification = ftopsis.run()
    
    print("\nRunning FTOPSIS-Class...")
    FTOPSISProcessor.print_trapezoidal_results(
        elements=data['elements'],
        closeness=closeness,
        classification=classification,
        profile_mapping=data['profile_mapping']
    )

def triangular_ftopsis_class(data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict]:
    from ftopsis_class.triangular_core import CriteriaType, FTOPSISClass as TriFTOPSIS

    linguistic_vars_alt = {k: np.array(v) for k, v in data['linguistic_variables_alternatives'].items()}
    linguistic_vars_weight = {k: np.array(v) for k, v in data['linguistic_variables_weights'].items()}

    decision_matrix = pd.DataFrame({
        k: [linguistic_vars_alt[val] for val in v]
        for k, v in data['decision_matrix'].items()
    })
    
    profile_matrix = pd.DataFrame({
        k: [linguistic_vars_alt[val] for val in v]
        for k, v in data['profile_matrix'].items()
    })

    weights = pd.DataFrame({k: [linguistic_vars_weight[v[0]]] for k, v in data['weights'].items()})
    criteria_type = {k: CriteriaType[v] for k, v in data['criteria_type'].items()}
    profile_mapping = {int(k): v for k, v in data['profile_mapping'].items()}

    norm_matrix = TriFTOPSIS.normalize_matrix(decision_matrix, criteria_type)
    weighted_matrix = TriFTOPSIS.weigh_matrix(norm_matrix, weights)
    final_matrix = TriFTOPSIS.round_weighted_normalized_matrix(weighted_matrix)

    norm_profile = TriFTOPSIS.normalize_matrix(profile_matrix, criteria_type)
    weighted_profile = TriFTOPSIS.weigh_matrix(norm_profile, weights)
    final_profile = TriFTOPSIS.round_weighted_normalized_matrix(weighted_profile)

    pos_sol, neg_sol = TriFTOPSIS.ideal_solution(final_profile, profile_mapping)
    pos_dist, neg_dist = TriFTOPSIS.distance_calculation(final_matrix, pos_sol, neg_sol)
    result = TriFTOPSIS.proximity_coefficient(pos_dist, neg_dist)

    result.index = data['suppliers']
    result['Classificação'] = result.idxmax(axis=1)
    json_output = format_to_json(result)

    FTOPSISProcessor.print_results(result)
    print("\nJSON Output:")
    print(json.dumps(json_output, indent=2, ensure_ascii=False))
    return result, json_output


def main() -> None:
    print("FTOPSIS Classification System")
    print("------------------------------")
    
    while True:
        file_path = 'data/json/triangular_input.json'
        
        try:
            data = FTOPSISProcessor.load_json_data(file_path)
            fuzzy_type = FTOPSISProcessor.detect_fuzzy_type(data)
            
            if fuzzy_type == 'triangular':
                triangular_ftopsis_class(data)
            else:
                trapezoidal_ftopsis_class(data)
            break
            
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {file_path}. Por favor, tente novamente.")
        except ValueError as e:
            print(f"Erro no arquivo: {str(e)}. Por favor, verifique o formato e tente novamente.")
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nErro: {str(e)}")
        exit(1)