import hash as h
import mse as mse
import codetime as ct
import json
import os
import myUtils as u
from typing import Callable 

import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

pathToHash = "../data/hash.json"
filepath =  "../data/src/SweetGirls.jpeg"

formats = ["heic","jxl","avif","webp", "qoi", "jpeg", "png"]

getHash = h.init()

def loadJson(path):
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
def saveJson(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def file_iterator(path: str)->Callable[[],str]:
    root_folder = path
    def  inner():
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                full_path = os.path.join(root, file)
                yield full_path
    return inner
def foreach_iteration(iter, func):
    for some in iter():
        func(some)
#цикл по массиву картинок из src
path_to_src = "../data/src"
if False:#первый запуск
    data = {}
    fi = file_iterator(path_to_src)
    for file_path in fi():
            hash = getHash(file_path)
            for key, value in hash.items():
                value["class"] = ""
                data[key] = value
    saveJson(pathToHash, data)
#конвертация и змер времени, сохранение в структуру
#расчет метрик, сохранение в сруктуру
path_to_out = "../data/out"

time_measurement = ct.init(path_to_out)
mse = mse.init(path_to_out)
if True:#нет смысла на тех же данных
    for format in formats:
        data_path = f'{path_to_out}/{format}/data.json'
        data = {}
        fi = file_iterator(path_to_src)
        for file_path in fi():
            time_res = time_measurement(file_path, format)
            for name, dictionary in time_res.items():
                    for key, value in dictionary.items():
                        if not (name in data):
                            data[name] = {}
                        data[name][key] = value
            mse_res = mse(file_path, format)
            for name, dictionary in mse_res.items():
                    for key, value in dictionary.items():
                        if not (name in data):
                            data[name] = {}
                        data[name][key] = value
        saveJson(data_path, data) 
if True:
    hash_data = loadJson("../data/hash.json")
    total_data = {}
    for format in formats:
        data_path = os.path.join(path_to_out, format,"")
        for root, _, files in os.walk(data_path):
            for file in files:
                if not (file.split('.')[-1] == "json"):
                    continue
                total_data[format] = loadJson(os.path.join(root, file))
    for format in formats:
        for image_name, value_hash in hash_data.items():
            total_data[format][image_name]["class"] = image_name[:1]
    total_table = []
    total_table.append(["format", "class", "tenc", "tdec", "size_before", "size_after", "CR", "mse", "psnr", "ssim"])
    for format in formats:
            for image_name, value_hash in hash_data.items():
                total_table.append([
                   str(format),
                   str(total_data[format][image_name]["class"]),
                   str(total_data[format][image_name]["tenc"]),
                   str(total_data[format][image_name]["tdec"]),
                   str(value_hash["size"]),
                   str(total_data[format][image_name]["size"]),
                   str(float(value_hash["size"])/float(total_data[format][image_name]["size"])),
                   str(total_data[format][image_name]["mse"]),
                   str(total_data[format][image_name]["psnr"]),
                   str(total_data[format][image_name]["ssim"]),]
                )
    csv_total = ""
    for dt in total_table:
        csv_total = csv_total + ";".join(dt)+"\n"
    csv_total = csv_total[:-1]
    print(csv_total)
if False:
    hash_data = loadJson("../data/hash.json")
    total_data = {}
    for format in formats:
        data_path = os.path.join(path_to_out, format,"")
        for root, _, files in os.walk(data_path):
            for file in files:
                if not (file.split('.')[-1] == "json"):
                    continue
                total_data[format] = loadJson(os.path.join(root, file))

    visualization_data = {}
    visualization_data["CrFormatClass"] = []
    visualization_data["ssimFormatClass"] = []
    visualization_data["psnrFormatClass"] = []
    visualization_data["AvgEncTime"] =[]
    visualization_data["AvgDecTime"] = []

    class_data = {}
    format_data = {}

    for format in formats:
        #средний ssim
        #средний tenc
        #средний tdec
        #средний psnr
        #внутри классов psnr и ssim
        format_data[format] = []
        class_data[format] = {}

        for image_name, value_hash in hash_data.items():
            cr = value_hash["size"]/total_data[format][image_name]["size"]
            bpp = total_data[format][image_name]["size"]/value_hash["pixels"]
            
            fd_temp = {}
            fd_temp["tenc"] = total_data[format][image_name]["tenc"]
            fd_temp["tdec"] = total_data[format][image_name]["tdec"]
            fd_temp["size"] = total_data[format][image_name]["size"]

            format_data[format].append(fd_temp)

            if not (value_hash["class"] in class_data[format]):
                class_data[format][value_hash["class"]] = list([])
            cd_temp = {}
            cd_temp["psnr"] = total_data[format][image_name]["psnr"]
            cd_temp["ssim"] = total_data[format][image_name]["ssim"]
            cd_temp["cr"] = cr
            
            class_data[format][value_hash["class"]].append(cd_temp)
    classes = {}
    for format in formats:
        tenc_avg = np.mean(list(map(lambda fd: fd["tenc"], format_data[format])))
        tdec_avg = np.mean(list(map(lambda fd: fd["tdec"], format_data[format])))
        size_avg = np.mean(list(map(lambda fd: fd["size"], format_data[format])))

        class_measurements = {"ssim":[],"psnr":[],"cr":[],}

        for k,v in class_data[format].items():
            img_class = str(k)
            classes[img_class] = 0
            ssim_avg = np.mean(list(map(lambda cd: cd["ssim"], class_data[format][img_class])))
            psnr_avg = np.mean(list(map(lambda cd: cd["psnr"], class_data[format][img_class])))
            cr_avg = np.mean(list(map(lambda cd: cd["cr"], class_data[format][img_class])))
            
            class_measurements["ssim"].append([img_class, ssim_avg])
            class_measurements["psnr"].append([img_class, psnr_avg])
            class_measurements["cr"].append([img_class, cr_avg])

        visualization_data["CrFormatClass"].append(class_measurements["cr"][0])
        visualization_data["psnrFormatClass"].append(class_measurements["psnr"][0])
        visualization_data["ssimFormatClass"].append(class_measurements["ssim"][0])
            
        
        visualization_data["AvgEncTime"].append([tenc_avg, size_avg])
        visualization_data["AvgDecTime"].append([tdec_avg, size_avg])
    pprint(visualization_data)
        #для каждого формата пихаем класс+значение    
            #зависимости скорости от размера
            #гистограмма класс+формат + вертикаль 
            #зависимости пснр + сим, алгоритм

    #зависимости скорости от размера        
    plt.subplot(2, 1, 1) 
    plt.xlabel("format")
    plt.title("encode")
    plt.ylabel("size (e8)/time")
    plt.plot(visualization_data["AvgEncTime"], label=["time","size"])
    plt.legend()
    plt.subplot(2, 1, 2)
    plt.plot(visualization_data["AvgDecTime"], label=["time","size"]) 
    plt.legend()
    plt.xlabel("format")
    plt.title("decode")
    plt.ylabel("size (e8)/time")
    plt.show()

    plt.hist(visualization_data["CrFormatClass"], label = formats)
    plt.legend()
    plt.title("Compress Rattio by class")
    plt.xlabel("avg value")
    plt.ylabel("avg value")
    plt.show()

    pprint(visualization_data)
