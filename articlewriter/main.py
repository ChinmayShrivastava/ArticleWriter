import click
import os
import pickle
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from llama_index.llms import OpenAI
from prompts.general import PROMPT_TO_GENERATE_RESPONSES, PROMPT_TO_UPDATE_STATE
import ast
from dotenv import load_dotenv
load_dotenv()

def get_llm(model="gpt-3.5-turbo"):
    return OpenAI(model=model)

def _emb_fn():
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key='',
        model_name="text-embedding-ada-002"
    )

def return_topic_collection(topic):
    chroma_client = PersistentClient(path=f"rnd/data/{topic}/storage")
    emb_fn = _emb_fn()
    topic_collection = chroma_client.get_or_create_collection(name=topic, embedding_function=emb_fn, metadata={"hnsw:space": "cosine"})
    return topic_collection

def _query(query, topic_collection, n_results=10):
    return topic_collection.query(query_texts=[query], n_results=n_results)['ids'][0]

def ask_query(query, llm, topic, topic_collection, n_results=30):
    triplets_prompt = "\n".join(_query(query, topic_collection, n_results))
    prompt = PROMPT_TO_GENERATE_RESPONSES.replace("<<topic>>", topic).replace("<<triplets>>", triplets_prompt).replace("<<query>>", query)
    resp = llm.complete(prompt).text
    return resp

# get a list of all the folders under the rnd/data folder
def get_folders():
    folders = []
    # only get the direct subfolders to rnd/data
    for folder in os.listdir('rnd/data'):
        if os.path.isdir(os.path.join('rnd/data', folder)):
            folders.append(folder)
    return folders

def delete_vectors(ids, topic_collection):
    assert isinstance(ids, list)
    topic_collection.delete(
        ids=ids
    )

def update_state(ids, state, topic_collection):
    assert isinstance(ids, list)
    # delete the vectors
    delete_vectors(ids, topic_collection)
    for id in ids:
        state[id] = True
    return state

def state_agent(topic):
    # load the llm model
    llm = get_llm()
    # get the topic collection
    topic_collection = return_topic_collection(topic)
    # load the state_01.pkl file from the rnd/data/topic folder
    with open(os.path.join('rnd/data', topic, 'state_01.pkl'), 'rb') as f:
        state = pickle.load(f)
    while True:
        # user has two options: ask or update
        user_input = input("What do you want to do? (1: ask, 2: update): ")
        # user_input = '1'
        if user_input == '1':
            # ask
            query = input("What is your query?: ")
            resp = ask_query(query, llm, topic, topic_collection)
            click.echo(click.style(resp, fg='green'))
        elif user_input == '2':
            # update
            user_input = input("What is your input?: ")
            query_results = _query(user_input, topic_collection)
            query_results = [(x[0], x[1], x[2]) for x in [q.split('->') for q in query_results] if len(x) == 3]
            triplet_string = '\n'.join([f"id. {index} ({x[0]}, {x[1]}, {x[2]})" for x, index in zip(query_results, range(len(query_results)))])
            prompt = PROMPT_TO_UPDATE_STATE.format(topic=topic, triplets=triplet_string, user_input=user_input)
            resp = llm.complete(prompt).text
            # use ast to convert the string to a list of ids
            ids = ast.literal_eval(resp)
            # update the state
            ids_ = list(set(['->'.join(query_results[id]) for id in ids]))
            state = update_state(ids_, state, topic_collection)
            # print the totak numner of keys in state that are True
            print(f"Total number of triplets that are included: {sum(state.values())}")
            # save the state
            with open(os.path.join('rnd/data', topic, 'state_01.pkl'), 'wb') as f:
                pickle.dump(state, f)
            click.echo("State updated")
        else:
            # invalid input
            click.echo("Invalid input")

@click.command()
@click.option('--topic', prompt='Topic')
def main(topic):
    list_of_topics = get_folders()
    if topic in list_of_topics:
        state_agent(topic)
    else:
        # echo error
        print("Topic does not exist")

if __name__ == '__main__':
    main()
