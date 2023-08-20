import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, defineDataLoader } from 'ice';
import '@chatui/core/es/styles/index.less';
// 引入组件
import Chat, { Bubble, useMessages, Icon, FileCard, toast, Progress } from '@chatui/core';
// 引入样式
import '@chatui/core/dist/index.css';

import { getUserId } from '@/utils/getUserInfo';
import FileUpload from '@/components/FileUpload';

import UserAvatar from '@/assets/user.png';
import AiAvatar from '@/assets/ai.png';
import Style from './index.module.css';

const initialMessages = [
  {
    type: 'text',
    content: { text: '主人好，我是智能助理，你的贴心小助手~' },
    user: { avatar: AiAvatar },
  },
  // {
  //   type: 'image',
  //   content: {
  //     picUrl: '//img.alicdn.com/tfs/TB1p_nirYr1gK0jSZR0XXbP8XXa-300-300.png',
  //   },
  // },
];

// 默认快捷短语，可选
const defaultQuickReplies = [
  {
    name: '你是谁？',
    isNew: true,
  },
  {
    name: '如何使用？',
    isHighlight: true,
  },
  {
    icon: 'message',
    name: '联系人工服务',
    // isNew: true,
    // isHighlight: true,
  },
];

export default function Index() {
  const [searchParams, setSearchParams] = useSearchParams();
  console.log('searchParams', searchParams.toString());
  const uid = searchParams.get('uid');
  const userId = uid || getUserId();
  // 消息列表
  const { messages, appendMsg, updateMsg, setTyping } = useMessages(initialMessages);
  const [waitFlag, setWaitFlag] = useState(false);
  const [knowledge, setKnowledge] = useState('');
  const uploadRef = useRef<any>(null);

  const handleResponse = (messagId) => (res) => {
    console.log('render res', res);
    if (res === 'error') {
      updateMsg(messagId, {
        type: 'text',
        content: { text: '不好意思，刚刚开小差了，请稍后再试！' },
        user: { avatar: AiAvatar },
      });
    } else if (res) {
      updateMsg(messagId, {
        type: 'text',
        content: { text: res },
        user: { avatar: AiAvatar },
      });
    }
    setTyping(false);
  }
  useEffect(() => {
    if (waitFlag) {
      setWaitFlag(false);
      console.log('messages', (messages));
      const lastMessage = messages[messages.length - 2];
      const last2Message = messages[messages.length - 3];
      if (lastMessage && lastMessage.content && !lastMessage.content.text && lastMessage.position === "left"
        && last2Message && last2Message.content && last2Message.content.text && last2Message.position === "right"
      ) {
        const params = {
          query: last2Message.content.text,
          userId: userId,
        };
        console.log('params', params);
        // agiRobotFetchStream(params, handleResponse(lastMessage._id))

        fetch('http://127.0.0.1:3006/api/v1/glm', {
          method: 'POST',
          mode: "cors",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            url: '', name: '', passwd: '', content: last2Message.content.text,
            knowledge: knowledge
          })
        }).then(response => response.json())
          .then(data => {
            console.log('res:', data);
            handleResponse(lastMessage._id)(data);
          })
          .catch(error => {
            console.error('Error:', error);
          });
      }
    }
  }, [waitFlag]);

  // 发送回调
  function handleSend(type, val) {
    if (type === 'text' && val.trim()) {
      // TODO: 发送请求
      appendMsg({
        type: 'text',
        content: { text: val },
        user: { avatar: UserAvatar },
        position: 'right',
      });

      appendMsg({
        type: 'text',
        content: { text: '' },
        user: { avatar: AiAvatar },
        position: 'left',
      });

      setTyping(true);
      setWaitFlag(true);

      // agiRobotFetchStream(params, handleResponse)
      // // 模拟回复消息
      // setTimeout(() => {
      //   appendMsg({
      //     type: 'text',
      //     content: { text: '亲，您遇到什么问题啦？请简要描述您的问题~' },
      //     user: { avatar: '//gw.alicdn.com/tfs/TB1DYHLwMHqK1RjSZFEXXcGMXXa-56-62.svg' },
      //   });
      // }, 1000);
    }
  }

  // 快捷短语回调，可根据 item 数据做出不同的操作，这里以发送文本消息为例
  function handleQuickReplyClick(item) {
    handleSend('text', item.name);
  }

  function renderMessageContent(msg) {
    const { type, content } = msg;

    // 根据消息类型来渲染
    switch (type) {
      case 'text':
        return <Bubble content={content.text} />;
      case 'file':
        return (<div>
          <FileCard file={content} extension="pdf" />
        </div>);
      case 'image':
        return (
          <Bubble type="image">
            <img src={content.picUrl} alt="" />
          </Bubble>
        );
      default:
        return null;
    }
  }

  function afterFileUpload({ filename, size }) {
    toast.success('上传成功')
    setKnowledge(filename);
    appendMsg({
      type: 'file',
      content: {
        name: filename,
        size,
      },
      user: { avatar: UserAvatar },
      position: 'right',
    });
    appendMsg({
      type: 'text',
      content: {
        text: '亲，您可以问我关于这个知识库的问题啦，我会尽力为您解答！'
      },
      user: { avatar: AiAvatar },
      position: 'left',
    });
  }

  function onToolbarClick(item, ctx) {
    // 如果点的是“相册”
    if (item.type === 'file') {
      uploadRef && uploadRef.current && uploadRef.current.click();
    }
    if (item.type === 'knowledge') {
      if (item.title == '福格模型') {
        setKnowledge('foggy.txt');
        appendMsg({
          type: 'text',
          content: {
            text: `亲，您可以问我关于这个${item.title}知识库的问题啦，我会尽力为您解答！`
          },
          user: { avatar: AiAvatar },
          position: 'left',
        });
      }
    }
    // 如果点的是“相册”
    if (item.type === 'image') {
      ctx.util.chooseImage({
        // multiple: true, // 是否可多选
        success(e) {
          if (e.files) { // 如果有 h5 上传的图
            const file = e.files[0];
            // 先展示图片
            ctx.appendMessage({
              type: 'image',
              content: {
                picUrl: URL.createObjectURL(file)
              },
              position: 'right'
            });

            // // 发起请求，具体自行实现，这里以 OCR 识别后返回文本为例
            // requestOcr({ file }).then(res => {
            //   ctx.postMessage({
            //     type: 'text',
            //     content: {
            //       text: res.text
            //     },
            //     quiet: true // 不展示
            //   });
            // });

          } else if (e.images) { // 如果有 app 上传的图
            // ..与上面类似
          }
        },
      });
    }
  }

  return (
    <div className={Style.container}>
      <FileUpload uploadRef={uploadRef} afterFileUpload={afterFileUpload} />
      <Chat
        navbar={{ title: '智能AI助理' }}
        messages={messages}
        renderMessageContent={renderMessageContent}
        quickReplies={defaultQuickReplies}
        onQuickReplyClick={handleQuickReplyClick}
        onSend={handleSend}
        toolbar={
          [
            {
              type: 'file',
              icon: 'plus',
              title: '知识库',
            },
            {
              type: 'knowledge',
              icon: 'file',
              title: '福格模型',
            },
          ]
        }
        onToolbarClick={onToolbarClick}
      />
    </div>
  );
}

// 页面的数据请求
export const dataLoader = defineDataLoader(async () => {
  // const data = await fetch('https://example.com/api/xxx');
  // return data;
});