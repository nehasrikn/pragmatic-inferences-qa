from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from pathlib import Path 
import argparse
import pandas as pd 
import json 
from tqdm import tqdm
from prompts import consolidation_prompt

def parse_list(x): 
    # remove the number in front of the subquestion/assumptions
    # if x is float,print x
    temp = [str(x)[3:].strip() for x in x.split('\n') if str(x) != '']
    return "\n".join(temp)



llm = ChatOpenAI(model_name="gpt-3.5-turbo",
                        max_tokens=1024,
                        temperature=0.0,
                        request_timeout=120)

prompt_template = PromptTemplate(template=consolidation_prompt, input_variables=["question", "assumptions", "subquestions"])
chain = LLMChain(llm=llm, prompt=prompt_template)


# process the human annotations and put them through this process: 
# take a filepath as input using argparse 
def add_arguments(parser): 
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--data_src", type=str, required=True)    
    parser.add_argument("--batch", type=str, required=True)

    return parser.parse_args()


def main(parser):
    args = add_arguments(parser)
    input_file = args.input_file
    df = pd.read_csv(input_file)
    

    # replace column names with easier ones 
    df.columns = ['question','metadata', 'subquestions', 'assumptions']
    print("columns were renamed as ", df.columns)

    output_file = Path(f"consolidated_data/{args.data_src}_{args.batch}_consolidated_subquestions.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:

        for index, row in tqdm(df.iterrows()):
            question = row['question']
            assumptions = parse_list(row['assumptions'])
            subquestions = parse_list(row['subquestions'])
            inferences = chain({"question": question, "assumptions": assumptions, "subquestions": subquestions}, return_only_outputs=True)
            inference_list = inferences['text'].split("\n")

            s = {"question": question, "assumptions": assumptions, "subquestions": subquestions, "inferences": inference_list}
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    main(parser)

