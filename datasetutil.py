import os
import json
import random
from utils import write_jsonl

# v1
def traverse_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            random_sample_from_json(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            traverse_files(dir_path)
            
def random_sample_from_json(filepath):
    # Given json file,return a random sample
    if filepath.endswith(".json"):
        with open(filepath,"r") as jsonfile:
            data = json.load(jsonfile)
            sampledata = random.sample(data, 1)
            formatdata = json.dumps(data, indent=4, sort_keys=True)
            print(sampledata)


# updata v2
def sample_from_json() -> dict:
    # Given json file,return random sample
    filepath = "viper/datasets/GQA/sceneGraphs/sample_sceneGraphs.json"
    if filepath.endswith(".json"):
        with open(filepath,"r") as jsonfile:
            jsondata = json.load(jsonfile)
            sampledata = random.sample(jsondata, 1)
            formatdata = json.dumps(jsondata, indent=4, sort_keys=True)

    return sampledata

def convert2caption(jsondata):
    # print(json.dumps(jsondata,indent=4))
    caption = []
    for item_id,item_data in jsondata.items():
        # print(item_id,item_data)
        caption.append(f'This is {item_id}, {item_data["width"]}*{item_data["height"]}')
        for object_id, object_data in item_data["objects"].items():
            caption.append(f'{object_data["name"]}({object_id}),h:{object_data["h"]}, w:{object_data["w"]}, x:{object_data["x"]}, y:{object_data["y"]}')
            for relation in object_data["relations"]:
                caption.append(f'   {relation["name"]} {relation["object"]} ')
            caption.append('\n')
    for item in caption:
        print(item)

    pass

def sample_train_question(jsonpath):
    # jsonpath = ""
    sample = {}
    samplenum = 10
    with open(jsonpath,"r") as jsonfile:
        jsondata = json.load(jsonfile)
    imageID = set()
    for item_id, item_data in jsondata.items():
        imageID.add(item_data["imageId"])
    
    sampleID = random.sample(list(imageID),samplenum)
    for item_id, item_data in jsondata.items():
        if item_data["imageId"] in sampleID:
            sample.setdefault(item_data["imageId"],[]).append({"query":item_data["question"]})
        else: continue

    sample_question_path = "viper_impl/data/train_sample_question.jsonl"
    # if not os.path.exists(sample_question_path):
    #     os.makedirs(sample_question_path)

    querynum = 0
    for k,v in sample.items():
        writelist = []
        writelist.append({"imageid": k, "question": v})
        write_jsonl(sample_question_path, writelist, True)
        querynum += len(v)

    
    print(f"write to \"{sample_question_path}\" {samplenum} images and its {querynum} questions")



def main():
    jsondata = sample_from_json()
    convert2caption(jsondata)

if __name__ == '__main__':
    # filepath = "datasets/GQA"
    # traverse_files(filepath)
    sample_train_question("viper/datasets/GQA/questions1.2/train_balanced_questions.json")
    # main()

