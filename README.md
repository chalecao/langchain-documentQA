# LangChain揭秘之文档QA项目实战

视频教程：[LangChain揭秘之文档QA项目实战](https://study.163.com/course/viewCourse.htm?courseId=1213542817&providerId=400000000351011)

官方博客：[万维刀客](https://www.w3cdoc.com/)

## 适用人群
想学习Promp高级使用技巧，学习使用LangChain框架构建prompt工程的同学

## 课程概述
本课程从Prompt日常使用开始，介绍各种使用技巧。讲解最热门的Prompt工程框架LangChain构建Prompt原理方式，通过源码解读为你揭秘大模型背后的运作方式。
本课程目标：
- 帮助你学会如果使用Prompt，学习构造高阶Prompt技巧
- 了解如何构建Prompt工程
- 学习使用LangChain快速构建自己的Prompt工程
- 扩展自己的Tools和Agent
- 分享LangChain可视化搭建平台
课程连载中，更新节奏如下：
1. Prompt使用示例和境界，已更新
- 介绍prompt的基本使用方法，Prompt使用境界
2. LangChain的Chains，已更新
- 介绍Langchain的使用方法，学习DocumentQAChain和SequentialChain
- 介绍宪法链和合规链
3. LangChain使用Tools，已更新
- 介绍Prompt使用tools的方法，分析背后使用tools的原理
- 解读LangChain中使用tools的源代码
4. 实战-基于本地Faiss向量数据库的DocumentQA
- 讲解如何处理语料，如何进行向量化
- 讲解如何保存数据到本地Faiss向量数据库
- 讲解如何从Faiss查询相关数据
- 讲解Document流程原理

# 启动方法

前端基于react项目

## 启动前台

1. 安装依赖

``` javascript
npm install 
// 或者
cnpm install
```

2. 启动项目

```
npm run start
```

## 启动后台

后台基于python编写

``` python
cd pyserver
pip install -r requirements.txt

# 启动
python api.py
```
