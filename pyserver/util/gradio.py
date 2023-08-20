from gradio_client import Client
import json

glmClient = Client("https://modelscope.cn/api/v1/studio/AI-ModelScope/ChatGLM6B-unofficial/gradio/")

def queryGLMResult(prompt):
    trycnt =0
    while(trycnt < 20):
        try:
            (txt, outpath) = glmClient.predict(prompt, '', fn_index=0)
            print(outpath)
            with open(outpath) as f:
                content = f.read()
            break
        except:
            trycnt = trycnt + 1
            pass

    # print(result)
    cjson = json.loads(content)   
    return cjson[0][1]

# baichuanClient = Client("https://modelscope.cn/api/v1/studio/baichuan-inc/Baichuan-13B-Chatdemo/gradio/")

# def queryBaiChuanResult(prompt):
#     trycnt =0
#     while(trycnt < 20):
#         try:
#             (txt, outpath) = baichuanClient.predict(prompt, '', fn_index=0)
#             print(outpath)
#             f = open(outpath)
#             lines = f.read()
#             result = lines.encode('utf-8').decode('unicode_escape')
#             break
#         except:
#             trycnt = trycnt + 1
#             pass

#     print(result)  
#     #[["提取出下面问题中的年份和公司名称, 仅输出年份和公司名称即可，逗号分隔，无需返回其他内容，问题如下···2019年中国工商银行财务费用是多少元?", "2019,中国工商银行"]]
#     return result.split(',')[1].split(']')[0]