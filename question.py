import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import os
import json
from simple_colors import *
import numpy as np
from tqdm import tqdm
from utils import load_json, PROJECT_ROOT_DIR, load_csv, get_file_with_prefix, load_jsonlines, list_dir

#class representing annotated data

DATASET_SOURCES = ['rosie', 'reddit', 'nq']

@dataclass
class Assumption:
    assumption_id: str
    assumption: str
    metadata: Optional[Dict]
    dataset: str
    question_id: str
    plausibility: int
    veracity: str
    evidence: str
    evidence_source: str
    inference_type: str = None
    
    def display(self):
        print(magenta(f'   {self.assumption} ({self.veracity})'))
    

@dataclass
class Question:
    question_id: str
    question: str
    annotator_data: str # {'answer_de_novo': int, 'inference_extraction': int, 'inference++': int}
    answer_de_novo: str
    answer_de_novo_sources: List[str]
    metadata: Optional[Dict]
    dataset: str # rosie, reddit, nq
    human_assumptions: List[Assumption]
    model_assumptions: Dict[str, List[Assumption]] # dict of model name to list of assumptions for that model
    
    def display(self):
        print(green(f'[{self.question_id}] {self.question}'))
        for i, a in enumerate(self.human_assumptions):
            a.display()
        


class MaternalHealthDataset:
    """
    Class to load the maternal health dataset
    """
    def __init__(self, questions: List[Question]) -> None:
        self.questions = questions
        self.question_lookup = {q.question_id: q for q in questions}
        
    def get_question_from_assumption_id(self, assumption_id: str) -> Question:
        return self.question_lookup[assumption_id.split('.')[0] + '.' + assumption_id.split('.')[1] + '.' + assumption_id.split('.')[2]]
    
    def get_question_from_question_id(self, question_id: str) -> Question:
        return self.question_lookup[question_id]
    
    def get_questions_from_dataset(self, dataset: str) -> List[Question]:
        return MaternalHealthDataset([q for q in self.questions if q.dataset == dataset])
    
    def get_assumptions_of_veracity(self, veracity: str) -> List[Assumption]:
        return [
            a for q in self.questions for a in q.human_assumptions if str(a.veracity).lower() == veracity.lower()
        ]


def load_generated_inferences(
    dataset: str,
    batch_num: int,
    consolidated_subq_dir='annotation/consolidate_subq/consolidated_data',
):
    assumptions = {}
    for i, q in enumerate(load_jsonlines(f'{consolidated_subq_dir}/{dataset}_{batch_num}_consolidated_subquestions.jsonl')):
        question_assumptions = {
            f'{dataset}.{batch_num}.{i}.{j}': Assumption(
                assumption_id=f'{dataset}.{batch_num}.{i}.{j}',
                assumption=a.strip(),
                metadata=None,
                dataset=dataset,
                question_id=f'{dataset}.{batch_num}.{i}',
                plausibility=None,
                veracity=None,
                evidence=None,
                evidence_source=None,
                inference_type=None
            ) for j, a in enumerate(q['inferences'])
        }
        assumptions[q['question'].strip()] = question_assumptions
    return assumptions
    
def load_inference_verification(
    dataset: str, 
    batch_num: int, 
    inference_verification_dir='annotation/inference_verification',
    consolidated_subq_dir='annotation/consolidate_subq/consolidated_data',
):
    inference_verification_annotation = get_file_with_prefix(os.path.join(inference_verification_dir, dataset), f'batch_{batch_num}')
    assumptions = load_generated_inferences(dataset, batch_num, consolidated_subq_dir)
    
    if not inference_verification_annotation:    
        return {k: list(v.values()) for k, v in assumptions.items()}
        
    verified_inferences = load_csv(inference_verification_annotation)
    questions = defaultdict(list)

    curr_question = None # if the question is nan, use the previous question
    question_num = -1
    for i, a in verified_inferences.iterrows():
        if pd.isna(a.question):
            question = curr_question
        else:
            question = a.question.strip()
            curr_question = question
            question_num+=1
        
        question_id = f'{dataset}.{batch_num}.{question_num}'
        assumption_id = f'{dataset}.{batch_num}.{question_num}.{len(questions[question])}'
        annotated_assumption = None
        if pd.isna(a.veracity):
            annotated_assumption = assumptions[question][assumption_id]
        else:
            plausibility = int(a.plausibility[0]) if not pd.isna(a.plausibility) else None
            veracity = a.veracity.title() if not pd.isna(a.veracity) else None
            evidence = a.evidence.strip() if not pd.isna(a.evidence) else None
            evidence_source=a.evidence_source_link.strip() if not pd.isna(a.evidence_source_link) else None
            annotated_assumption = Assumption(
                    assumption_id=assumption_id,
                    assumption=a.assumption,
                    metadata={'annotator_id_validation': os.path.basename(inference_verification_annotation).split('.')[0].split('_')[-1]},
                    dataset=dataset,
                    question_id=question_id,
                    plausibility=plausibility,
                    veracity=veracity,
                    evidence=evidence[1:-1] if evidence and (evidence.startswith('"') and evidence.endswith('"')) else evidence,
                    evidence_source=evidence_source,
                    inference_type=None
                )
        questions[question].append(annotated_assumption)

    return questions
        
    
def load_batch(
    dataset: str, 
    batch_num: int,
    question_dir: str='annotation/questions',
    de_novo_dir: str='annotation/answer_construction_de_novo',
    inference_verification_dir='annotation/inference_verification',
) -> List[Question]:
    
    print(f'Loading batch {batch_num} of {dataset}')
    batch_questions = []
    
    # annotations/questions is the ground truth for questions and sets the ids
    questions = load_csv(os.path.join(question_dir, dataset, f'batch_{batch_num}.csv'))
    assumptions = load_inference_verification(dataset, batch_num, inference_verification_dir)
    
    # loading de-novo answers
    de_novo_file = get_file_with_prefix(os.path.join(de_novo_dir, dataset), f'batch_{batch_num}')
    answers_de_novo = load_csv(de_novo_file)
    
    assert len(questions) == len(answers_de_novo) == len(assumptions)
    
    for i in range(len(questions)):
        question = questions.iloc[i]['question'].strip()
        answer = answers_de_novo.iloc[i]['answer'].strip()
        
        de_novo_same = question == answers_de_novo.iloc[i]['question'].strip()
        question_assumption_same = question.strip() in assumptions.keys()
        
        assert de_novo_same, print(i)
        assert question_assumption_same, print(question)
        
        batch_questions.append(
            Question(
                question_id=f'{dataset}.{batch_num}.{i}',
                question=question,
                annotator_data=os.path.basename(de_novo_file).split('.')[0].split('_')[-1],
                answer_de_novo=answer.strip(),
                answer_de_novo_sources=answers_de_novo.iloc[i]['sources'].split(','),
                metadata=questions.iloc[i]['metadata'],
                dataset=dataset,
                human_assumptions=assumptions[question.strip()],
                model_assumptions=None
            )
        )
    assert len(batch_questions) == 50, print(f'Batch {batch_num} of {dataset} has {len(batch_questions)} questions instead of 50.')
    return batch_questions

def load_dataset():
    all_questions = []
    for dataset in DATASET_SOURCES:
        num_batches = len(list_dir(f'annotation/questions/{dataset}'))
        all_questions.extend([q for bnum in range(1, num_batches+1) for q in load_batch(dataset, bnum)])
        
    return MaternalHealthDataset(all_questions)

def load_annotation_sample():
    annotation_sample_questions = MaternalHealthDataset([
        maternal_health_dataset.get_question_from_question_id(i) for i in set(load_csv('experiments/data_statistics/annotation_sample.csv').question_id)
    ])
    inference_type = load_csv('experiments/inference_type/annotation_sample_inference_type.csv')
    for i, row in inference_type.iterrows():
        question = annotation_sample_questions.get_question_from_question_id(row.question_id)
        question.inference_type = row.adjudicated_label
    return annotation_sample_questions
    


maternal_health_dataset = load_dataset()
annotation_sample_questions = load_annotation_sample()
